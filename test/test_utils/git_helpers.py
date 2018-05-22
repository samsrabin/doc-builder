#!/usr/bin/env python

"""Functions to assist with testing git repositories"""

from __future__ import print_function
import subprocess
import os

def make_git_repo():
    """Turn the current directory into an empty git repository"""
    _check_call_suppress_output(['git', 'init'])

def add_git_commit():
    """Add a git commit in the current directory"""
    with open('README', 'a') as myfile:
        myfile.write('more info')
    _check_call_suppress_output(['git', 'add', 'README'])
    _check_call_suppress_output(['git', 'commit', '-m', 'my commit message'])

def checkout_git_branch(branchname):
    """Checkout a new branch in the current directory"""
    _check_call_suppress_output(['git', 'checkout', '-b', branchname])

def make_git_tag(tagname):
    """Make a lightweight tag at the current commit"""
    _check_call_suppress_output(['git', 'tag', '-m', 'making a tag', tagname])

def checkout_git_ref(refname):
    """Checkout the given refname in the current directory"""
    _check_call_suppress_output(['git', 'checkout', refname])

def _check_call_suppress_output(args):
    """Make a check_call call with the given args, suppressing all output"""
    devnull = open(os.devnull, 'w')
    subprocess.check_call(args, stdout=devnull, stderr=devnull)
