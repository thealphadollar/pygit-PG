"""
implements init subcommand for git
"""

import os

from . import write_file

def init(repo):
    """
    initialises a repo
    
    creates all the directories and sub-directories for the repository
    
    :param repo: name of the repo
    :type repo: String
    """
    try:
        os.mkdir(repo)
        os.mkdir(os.path.join(repo, ".pygit"))
        for name in ['objects', 'refs', 'refs/heads']:
            os.mkdir(os.path.join(repo, ".git", name))
        write_file(os.path.join(repo, '.git', 'HEAD'), b'ref: refs/heads/master')
        print('initialized empty repository: %s', repo)
    except FileExistsError as _:
        print('directory with name %s already exists', repo)
