#!/usr/bin/env python
"""
Utility to get the path to the build directory

Main function here is get_build_dir
"""

from __future__ import print_function
import os
from doc_builder import sys_utils

def get_build_dir(build_dir=None, repo_root=None, version=None,
                  intermediate_path=""):
    """Return a string giving the path to the build directory

    If build_dir is specified, simply use that.

    Otherwise, repo_root must be given. If version is also given, then
    the build directory will be:
        os.path.join(repo_root, intermediate_path, version).
    If version is not given, then determine version by getting the
    current git branch; then use the above path specification.
    """

    if build_dir is not None:
        if repo_root is not None:
            raise RuntimeError("Cannot specify both build-dir and repo-root")
        if version is not None:
            raise RuntimeError("Cannot specify both build-dir and version")
        if intermediate_path:
            raise RuntimeError("Cannot specify both build-dir and intermediate-path")
        return build_dir

    if repo_root is None:
        raise RuntimeError("Must specify either build-dir or repo-root")

    if version is None:
        version_explicit = False
        branch_found, version = sys_utils.git_current_branch()
        if not branch_found:
            raise RuntimeError("Problem determining version based on git branch; "
                               "set --version on the command line.")
    else:
        version_explicit = True

    build_dir = os.path.join(repo_root, intermediate_path, version)
    if not version_explicit:
        if not os.path.isdir(build_dir):
            # FIXME(wjs, 2018-05-22) Improve this message
            raise RuntimeError("directory doesn't exist")

    return build_dir
