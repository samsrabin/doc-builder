#!/usr/bin/env python

"""Functions to assist with testing git repositories"""

from __future__ import print_function
from test_helpers import check_call_suppress_output

def make_git_repo():
    """Turn the current directory into an empty git repository"""
    check_call_suppress_output(['git', 'init'])

def add_git_commit():
    """Add a git commit in the current directory"""
    with open('README', 'a') as myfile:
        myfile.write('more info')
    check_call_suppress_output(['git', 'add', 'README'])
    check_call_suppress_output(['git', 'commit', '-m', 'my commit message'])

def checkout_git_branch(branchname):
    """Checkout a new branch in the current directory"""
    check_call_suppress_output(['git', 'checkout', '-b', branchname])

def make_git_tag(tagname):
    """Make a lightweight tag at the current commit"""
    check_call_suppress_output(['git', 'tag', '-m', 'making a tag', tagname])

def checkout_git_ref(refname):
    """Checkout the given refname in the current directory"""
    check_call_suppress_output(['git', 'checkout', refname])
