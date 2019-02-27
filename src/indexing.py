"""
stores functions related to indexing of file and storing them
"""

import collections
import hashlib
import os
import struct
import difflib
import operator

from . import read_file, write_file
from .objects import hash_object, read_object

# Data for one entry in the git index (.git/index)
IndexEntry = collections.namedtuple('IndexEntry', [
    'ctime_s', 'ctime_n', 'mtime_s', 'mtime_n', 'dev', 'ino', 'mode', 'uid',
    'gid', 'size', 'sha1', ''
])

def read_index():
    """
    read git index file to get list of IndexEntry objects

    returns a list of IndexEntry objects.
    
    """
    try:
        data = read_file(os.path.join(".git", 'index'))
    except FileNotFoundError:
        return []

    digest = hashlib.sha1(data[:-20]).digest()
    assert digest == data[-20:], 'invalid index checksum'
    signature, version, num_entries = struct.unpack('!4sLL', data[:12])
    assert signature == b'DIRC', 'invalid index signature {}'.format(signature)
    assert version == 2, 'unknown index version {}'.format(version)

    entry_data = data[12:-20]
    entries = []
    i = 0
    while i+62 < len(entry_data):
        fields_end = i+62
        fields = struct.unpack('!LLLLLLLLLL20sH', entry_data[i:fields_end])
        path_end = entry_data.index(b'\x00', fields_end)
        path = entry_data[fields_end:path_end]
        entry = IndexEntry(*(fields+(path.decode(),)))
        entries.append(entry)
        entry_len = ((62+len(path)+8)//8)*8
        i += entry_len
    assert len(entries) == num_entries, 'number of entries {} is not correct'.format(len(entries))
    return entries

def ls_files(details=False):
    """
    print list of files

    print list of files in index along with details such as mode, SHA-1, and stage number
    
    :param details: to print extra details, defaults to False
    :param details: bool, optional
    """
    for entry in read_index():
        if details:
            stage = (entry.flags >> 12) & 3
            print('{:6o} {} {:}\t{}'.format(
                entry.mode, entry.sha1.hex(), stage, entry.path))

def get_status():
    """
    provides status of the working copy
        
    get status of working copy, return tuple of (changed paths, new_paths, deleted_paths)
    """
    paths = set()
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d != '.git']
        for file in files:
            path = os.path.join(root,file)
            path = path.replace('\\', '/')
            if path.startswith('./'):
                path = path[2:]
            paths.add(path)
        entries_by_path = {e.path: e for e in read_index()}
        entry_paths = set(entries_by_path)
        changed = {p for p in (paths & entry_paths) 
            if hash_object(read_file(p), 'blob', write=False) != entries_by_path[p].sha1.hex()}
        new = paths - entry_paths
        deleted = entry_paths - paths
        return (sorted(changed), sorted(new), sorted(deleted))

def status():
    """
    show status of the working copy
    """

    changed, new, deleted = get_status()
    if changed:
        print('changed files:')
        for path in changed:
            print('\t', path)
    if new:
        print('new files:')
        for path in new:
            print('\t', path)
    if deleted:
        print('deleted files:')
        for path in deleted:
            print('\t', path)

def diff():
    """
    shows diff
    
    shows the difference between the files present in the working copy and the index
    """
    changed, _, _ = get_status()
    entries_by_path = {e.path: e for e in read_index()}

    for i, path in enumerate(changed):
        sha1 = entries_by_path[path].sha1.hex()
        obj_type, data = read_object(sha1)
        assert obj_type == 'blob', 'inavlid object type'
        index_lines = data.decode().splitlines()
        working_lines = read_file(path).decode().splitlines()
        diff_lines = difflib.unified_diff(
            index_lines, working_lines,
            '{} (index)'.format(path),
            '{} (working copy)'.format(path),
            lineterm=''
        )
        for line in diff_lines:
            print(line)
        if i < (len(changed) - 1):
            print('-'*70)

def write_index(entries):
    """
    write IndexEntry
    
    writes list of IndexEntry objects to git index file
    
    :param entries: [description]
    :type entries: [type]
    """

    packed_entries = []
    for entry in entries:
        entry_head = struct.pack('!LLLLLLLLLL20sH',
        entry.ctime_s, entry.ctime_n, entry.mtime_s, entry.mtime_n, entry.dev, entry.ino, 
        entry.mode, entry.uid, entry.gid, entry.size, entry.sha1, entry.flags)
        path = entry.path.encode()
        length = ((62 + len(path))//8) * 8
        packed_entry = entry_head + path + b'\x00' * (length - 62 - len(path))
        packed_entries.append(packed_entry)
    header = struct.pack('!4sLL', b'DIRC', len(entries))
    all_data = header + b''.join(packed_entries)
    digest = hashlib.sha1(all_data).digest()
    write_file(os.path.join('.git', 'index'), all_data + digest)

def add(paths):
    paths = [p.replace('\\', '/') for p in paths]
    all_entries = read_index()
    entries = [e for e in all_entries if e.path not in paths]
    for path in paths:
        sha1 = hash_object(read_file(path), 'blob')
        st = os.stat(path)
        flags = len(path.encode())
        assert flags < (1 << 12)
        entry = IndexEntry(
            int(st.st_ctime), 0, int(st.st_mtime), 0, st.st_dev, st.st_ino, st.st_mode,
            st.st_uid, st.st_gid, st.st_size, bytes.fromhex(sha1), flags, path
        )
        entries.append(entry)
    entries.sort(key=operator.attrgetter('path'))
    write_index(entries)