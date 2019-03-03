"""
contains the driver for command line arguments handling and driving methods
"""

import sys
import argparse

from .indexing import add, diff, hash_object, ls_files, get_status
from .objects import cat_file, read_file
from .commit import commit
from .init import init
from .push import push

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(dest='command', metavar="command")
    sub_parsers.required = True

    sub_parser = sub_parsers.add_parser('add', help="add file(s) to index")
    sub_parser.add_argument('paths', nargs='+', metavar='path', help='path(s) of files to add')

    sub_parser = sub_parsers.add_parser('cat-file', help='display contents of object')
    valid_modes = ['commit', 'tree', 'blob', 'size', 'type', 'pretty']
    sub_parser.add_argument('mode', choices=valid_modes, help='object type (commit, tree, blob) or display mode (size, type, pretty)')
    sub_parser.add_argument('hash_prefix', help='SHA-1 hash (or hash prefix) of object to display')

    sub_parser = sub_parsers.add_parser('commit', help="commit current state of index to master branch")
    sub_parser.add_argument('-a', '--author', help="commit author in format 'A U Thor <author@example.com>' (uses GIT_AUTHOR_NAME and GIT_USER_NAME environment variables by default)")
    sub_parser.add_argument('-m', '--message', help="message for the commit")

    sub_parser = sub_parsers.add_parser('diff', help="show diff of files changed (between index and working copy")

    sub_parser = sub_parsers.add_parser('hash-object', help="hash contents of given path (and optionally write to object store)")
    sub_parser.add_argument('path', help='path of file to hash')
    sub_parser.add_argument('-t', choices=['commit', 'tree', 'blob'], default='blob', dest="type", help="type of object (default %(default)r)")
    sub_parser.add_argument('-w', action='store_true', dest="write", help='write object to object storage')

    sub_parser = sub_parsers.add_parser('init', help="initialize a new repo")
    sub_parser.add_argument('repo', help="directory name for new repo")

    sub_parser = sub_parsers.add_parser('ls-files', help="list all files in index")
    sub_parser.add_argument('-s', '--stage', action='store_true', help="show object details (mode, hash, and stage number) in addition to path")

    sub_parser = sub_parsers.add_parser('push', help="push master branch to given git server url")
    sub_parser.add_argument('git_url', help="URL of git repo")
    sub_parser.add_argument('-p', '--password', help="password to use for authentication, default is GIT_PASSWORD env variable")
    sub_parser.add_argument('-u', '--username', help="username to use for authentication, default is GIT_USERNAME env variable")

    sub_parser = sub_parsers.add_parser('status', help="show status of working copy")

    args = parser.parse_args(args=None, namespace=None)
    if args.command == 'add':
        add(args.paths)
    elif args.command == 'cat-file':
        try:
            cat_file(args.mode, args.hash_prefix)
        except ValueError as error:
            print(error, file=sys.stderr)
    elif args.command == 'commit':
        commit(args.message, args.author)
    elif args.command == 'diff':
        diff()
    elif args.command == "hash-object":
        sha1 = hash_object(read_file(args.path), args.type, write=args.write)
        print(sha1)
    elif args.command == "init":
        init(args.repo)
    elif args.command == "ls-files":
        ls_files(args.stage)
    elif args.command == "push":
        push(args.git_url, args.username, args.password)
    elif args.command == "status":
        get_status()
    else:
        assert False, 'unexpected command {!r}'.format(args.command)