"""
deals with functions that handle objects
"""

import os
import sys
import stat
import hashlib
import zlib

from . import write_file, read_file


def hash_object(data, obj_type, write=True):
    """
    hash object
    
    compute hash of object data of give type and write to object store if 
    "write" is True. Return SHA-1 object hash as hex string.
    
    :param data: data of the file
    :type data: string
    :param obj_type: type of the object passes [blob/commit/tree]
    :type obj_type: string
    :param write: creation of path/file inside git directory, defaults to True
    :param write: bool, optional
    """
    header = '{} {}'.format(obj_type, len(data).encode())
    full_data = header + b'\x00' + data
    sha1 = hashlib.sha1(full_data).hexdigest()
    if write:
        path = os.path.join('.git', 'objects', sha1[:2], sha1[2:])
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            write_file(path, zlib.compress(full_data))
    return sha1

def find_object(sha1_prefix):
    """
    find object by hash prefix
    
    Find object with give SHA1 prefix and return the path to the object.
    If no such path found, raises ValueError
    
    :param sha1_prefix: SHA1 prefix of the object
    :type sha1_prefix: HexString
    """
    if len(sha1_prefix)<2:
        raise ValueError('hash prefix must be greater than 2 characters')
    obj_dir = os.path.join('.git', 'objects', sha1_prefix[:2])
    rest = sha1_prefix[2:]
    objects = [name for name in os.listdir(obj_dir) if name.startswith(rest)]
    if not objects:
        raise ValueError('object {!r} not found!'.format(sha1_prefix))
    if len(objects) >= 2:
        raise ValueError('multiple objects with the hash prefix {!r} found!'.format(sha1_prefix))
    return os.path.join(obj_dir, objects[0])

def read_object(sha1_prefix):
    """
    read object by the provided sha1_prefix
    
    Read object with the given SHA1 prefix and return tuple of object type and
    the data in the object
    
    :param sha1_prefix: SHA1 prefix generated for the file
    :type sha1_prefix: HexString
    :return: object type and data inside the object
    :rtype: tuple
    """

    path = find_object(sha1_prefix)
    full_data = zlib.decompress(read_file(path))
    null_index = full_data.index(b'\x00')
    header = full_data[:null_index]
    obj_type, size_str = header.decode().split()
    size = int(size_str)
    data = full_data[null_index+1:]
    assert size == len(data), 'expected size {}, got {} bytes'.format(
        size, len(data)
    )
    return (obj_type, data)

def cat_file(mode, sha1_prefix):
    obj_type, data = read_file(sha1_prefix)
    if mode in ['commit', 'tree', 'blob']:
        if obj_type != mode:
            raise ValueError('expected object type {}, got {}'.format(
                mode, obj_type
            ))
        sys.stdout.buffer.write(data)
    elif mode == 'size':
        print(len(data))
    elif mode == 'type':
        print(len(obj_type))
    elif mode == 'pretty':
        if obj_type in ['commit', 'blob']:
            sys.stdout.buffer.write(data)
        elif obj_type == 'tree':
            for mode, path, sha1 in read_tree(data=data):
                type_str = 'tree' if stat.S_ISDIR(mode) else 'blob'
                print('{:06o} {} {}\t{}'.format(
                    mode, type_str, sha1, path
                    ))
        else:
            assert False, 'unhandled object type {!r}'.format(obj_type)
    else:
        raise ValueError('unexpected mode {!r}'.format(mode))