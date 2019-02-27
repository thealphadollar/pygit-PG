"""
contains all the methods to compare remote and local master branch.
"""

from .indexing import read_object

def read_tree(sha1=None, data=None):
    """
    read tree object
    
    read tree object with given SHA-1 hex string or data
    
    :param sha1: SHA-1 of the tree object, defaults to None
    :param sha1: hex string, optional
    :param data: data of the tree object, defaults to None
    :param data: byte string, optional
    :raises TypeError: [description]
    :return: [description]
    :rtype: [type]
    """

    if sha1 is not None:
        obj_type, data = read_object(sha1)
        assert obj_type == 'tree', 'object {} is not tree'.format(obj_type)
    elif data is None:
        raise TypeError('must specify "sha1" or "data"')
    i = 0
    entries = []
    for _ in range(1000):
        end = data.find(b'\x00')
        if end == -1:
            break
        mode_str, path = data[i:end].decode().split()
        mode = int(mode_str, 8)
        digest = data[end+1:end+21]
        entries.append(mode, path, digest.hex())
        i = end+1+20
    return entries