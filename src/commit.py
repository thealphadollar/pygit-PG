"""
contains all the methods associated with writing a commit
"""

import os
import time

from . import read_file, write_file
from .indexing import read_index
from .objects import hash_object

def write_tree():
    """
    write a tree object
    
    write a tree object from the current index entries
    
    :return: hashed tree entries
    :rtype: hex string
    """

    tree_entries = []
    for entry in read_index():
        assert '/' not in entry.path, 'currently only supports a single, top-level directory'
    mode_path = '{:o} {}'.format(entry.mode, entry.path).encode()
    tree_entry = mode_path + b'\x00' + entry.sha1
    tree_entries.append(tree_entry)
    return hash_object(b''.join(tree_entries), 'tree')

def get_local_master_hash():
    """
    get current master 
    
    get current commit hash (SHA-1 string) of local master branch
    
    :return: current commit hash
    :rtype: SHA-1 string
    """

    master_path = os.path.join('.git', 'refs', 'heads', 'master')
    try:
        return read_file(master_path).decode().strip()
    except FileNotFoundError:
        return None
    
def commit(message, author=None):
    """
    commit the current state
    
    commit the current state of the index to master with given message
    
    :param message: commit message
    :type message: string
    :param author: author name and author email
    :param author: string, optional
    :return: commit hash
    :rtype: SHA-1 string
    """

    tree = write_tree()
    parent = get_local_master_hash()
    if author is None:
        author = '{} {}'.format(
            os.environ['GIT_AUTHOR_NAME'], os.environ['GIT_AUTHOR_EMAIL']
        )
    timestamp = int(time.mktime(time.localtime()))
    utc_offset = -time.timezone
    author_time = '{} {}{:02}{:02}'.format(
        timestamp,
        '+' if utc_offset > 0 else '-',
        abs(utc_offset) // 3600,
        (abs(utc_offset) // 60) % 60
    )

    lines = ['tree ' + tree]
    if parent:
        lines.append('parent ' + parent)

    lines.append('author {} {}'.format(author, author_time))
    lines.append('committer {} {}'.format(author, author_time))
    lines.append('')
    lines.append(message)
    lines.append('')
    data = '\n'.join(lines).encode()
    sha1 = hash_object(data, 'commit')
    master_path = os.path.join('.git', 'refs', 'heads', 'master')
    write_file(master_path, (sha1 + '\n').encode())
    print('committed to master : {:7}'.format(sha1))
    return sha1