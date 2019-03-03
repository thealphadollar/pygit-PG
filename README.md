# pygit-PG
A PlayGround To Learn The Working Of VCS By Developing One Myself

## Why?

I wanted to learn how version control system works behind the scenes and decided the best way would be to actually make a minimal one to understand the working.

In this project I've implemented basic functions of git following the tutorial provided at [behhoyt.com[(https://benhoyt.com/writings/pygit/).

It was a learning experience in terms of both technical skills and confidence: it was eye-opening that how easy the concepts are behind an application
such as version control system which is used almost all the time; in every single project.

> The usability of a project is independent of it's complexity.

## What all does this do?

Since my main aim was learning the behind the scene concepts, I made the bare bone and this is almost non-functional except for learning purposes.

It implements the below functions:

```bash
usage: __main__.py [-h] command ...

positional arguments:
  command
    add        add file(s) to index
    cat-file   display contents of object
    commit     commit current state of index to master branch
    diff       show diff of files changed (between index and working copy
    hash-object
               hash contents of given path (and optionally write to object
               store)
    init       initialize a new repo
    ls-files   list all files in index
    push       push master branch to given git server url
    status     show status of working copy

optional arguments:
  -h, --help   show this help message and exit
```

## Contributing

This project is a good to learn the working of version control system and implement new features. One is also welcome to improve the current code, as well as Command line interface.

The code has been well commented with docstrings explaining all the inputs, outputs and side-effects of a method.

[HELP] A setup.py file is highly needed to make pygit work across system.