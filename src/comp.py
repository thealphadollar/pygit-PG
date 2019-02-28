"""
contains all the methods to compare remote and local master branch.
"""
import stat

from .indexing import read_object

def read_tree(sha1=None, data=None):
    """
    read tree object
    
    read tree object with given SHA-1 hex string or data
    
    :param sha1: SHA-1 of the tree object, defaults to None
    :param sha1: hex string, optional
    :param data: data of the tree object, defaults to None
    :param data: byte string, optional
    :raises TypeError: when neither data nor sha1 string provided
    :return: entries
    :rtype: string
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

def find_tree_objects(tree_sha1):
    """
    find hashes of all objects
    
    return set of sha-1 hashes of all objects in this tree (recursively), including
    the hash of the tree itself.
    
    :param tree_sha1: sha1 hash of the tree object
    :type tree_sha1: hex string
    :return: objects of the tree
    :rtype: list
    """

    objects = {tree_sha1}
    for mode, path, sha1 in read_tree(sha1=tree_sha1):
        if stat.S_ISDIR(mode):
            objects.update(find_tree_objects(sha1))
        else:
            objects.add(sha1)
    return objects

def find_commit_objects(commit_sha1):
    """
    find SHA-1 hashes of objects in the commit
    
    return set of SHA-1 hashes of all objects in this commit (recursively), 
    it's frees, it's parents and the hash of the commit itself.
    
    :param commit_sha1: SHA-1 hash of the commit
    :type commit_sha1: string
    :return: SHA-1 hash of the objects present in the commit
    :rtype: list
    """
    objects = {commit_sha1}
    obj_type, commit = read_object(commit_sha1)
    assert obj_type == 'commit'
    lines = commit.decode().splitlines()
    tree = next(l[5:45] for l in lines if l.startswith('tree '))
    objects.update(find_tree_objects(tree))
    parents = (l[7:47] for l in lines if l.startswith('parent '))
    for parent in parents:
        objects.update(find_commit_objects(parent))
    return objects

def find_missing_objects(local_sha1, remote_sha1):
    """
    find local objects not present in remote
    
    return set of SHA-1 hashes of objects in local commit that are missing
    at the remote (based on the given remote commit hash).
    
    :param local_sha1: SHA-1 of local commit
    :type local_sha1: string
    :param remote_sha1: SHA-1 of remote commit
    :type remote_sha1: string
    :return: set of SHA-1 hashes of local objects not in remote
    :rtype: list
    """

    local_objects = find_commit_objects(local_sha1)
    if remote_sha1 is None:
        return local_objects
    remote_objects = find_commit_objects(remote_sha1)
    return local_objects - remote_objects