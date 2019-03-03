"""
contain all methods related to push operation
"""

import os
from .objects import read_object
from .conn_handler import get_remote_master_branch, build_lines_data, http_request, extract_lines
from .comp import find_missing_objects
from .commit import get_local_master_hash
import enum
import zlib
import struct
import hashlib

class ObjectType(enum.Enum):
    """
    Object type enumerator
    """

    commit = 1
    tree = 2
    blob = 3

def encode_pack_object(obj):
    """
    encode a single object
    
    encode a single object for a pack file and return bytes (variable-length header
    followed by compressed data bytes)
    
    :param obj: object to be encoded
    :type obj: ObjType
    :return: encoded object
    :rtype: bytes
    """

    obj_type, data = read_object(obj)
    type_num = ObjectType[obj_type].value
    size = len(data)
    byte = (type_num << 4) | (size & 0x0f)
    size >>= 4
    header = []
    while size:
        header.append(byte | 0x80)
        byte = size & 0x7f
        size >>= 7
    header.append(byte)
    return bytes(header) + zlib.compress(data)

def create_pack(objects):
    """
    create pack from objects
    
    create pack file containing all objects in given set of 
    SHA-1 hashes, return data bytes of full pack file
    
    :param objects: objects to be packed
    :type objects: ObjectType
    :return: pack of objects
    :rtype: SHA-1 string
    """
    header = struct.pack('!4sLL', b'PACK', 2, len(objects))
    body = b''.join(encode_pack_object(o) for o in sorted(objects))
    contents = header + body
    sha1 = hashlib.sha1(contents).digest()
    data = contents + sha1
    return data

def push(git_url, username=None, password=None):
    """
    push master branch to given git repo URL
    
    :param git_url: url to the git repository
    :type git_url: string
    :param username: git username, defaults to None
    :param username: string, optional
    :param password: git password, defaults to None
    :param password: string, optional
    :return: remote sha-1 commit string and missing objects
    :rtype: tuple
    """

    if username is None:
        username = os.environ['GIT_USERNAME']
    if password is None:
        password = os.environ['GIT_PASSWORD']
    remote_sha1 = get_remote_master_branch(git_url, username, password)
    local_sha1 = get_local_master_hash()
    missing = find_missing_objects(local_sha1, remote_sha1)
    print('updating remote master from {} to {} ({} object {})'.format(
        remote_sha1 or 'no commits', local_sha1, len(missing), 
        '' if len(missing) == 1 else 's'
    ))
    lines = ['{} {} refs/heads/master\x00 report-status'.format(
            remote_sha1 or ('0'*40), local_sha1
        ).encode()]
    data = build_lines_data(lines)+create_pack(missing)
    url = git_url + '/git-receive-pack'
    response = http_request(url, username, password, data=data)
    lines = extract_lines(response)
    assert len(lines) >= 2, 'expected at least 2 lines, got {}'.format(len(lines))
    assert lines[0] == b'unpack ok\n', "expected line 1 b'ok refs/heads/master\n', got: {}".format(
        lines[1])
    assert lines[1] == b'ok refs/heads/master\n', "expected line 2 b'ok refs/heads/master\n', got: {}".format(
        lines[1])
    return (remote_sha1, missing)