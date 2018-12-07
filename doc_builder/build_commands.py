#!/usr/bin/env python
"""
Functions with the main logic needed to build the command to build the docs
"""

from __future__ import print_function
import os
from doc_builder import sys_utils

def get_build_dir(build_dir=None, repo_root=None, version=None):
    """Return a string giving the path to the build directory.

    If build_dir is specified, simply use that.

    Otherwise, repo_root must be given. If version is also given, then
    the build directory will be:
        os.path.join(repo_root, "versions", version).
    If version is not given, then determine version by getting the
    current git branch; then use the above path specification.

    Error-checking on directory existence:
    - If build_dir is given, then no error checking is done
    - Otherwise, we ensure that repo_root/versions exists
      - If version is not given, then we also ensure that
        repo_root/versions/version exists, for the determined version.
    """

    if build_dir is not None:
        if repo_root is not None:
            raise RuntimeError("Cannot specify both build-dir and repo-root")
        if version is not None:
            raise RuntimeError("Cannot specify both build-dir and version")
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

    build_dir_no_version = os.path.join(repo_root, "versions")
    if not os.path.isdir(build_dir_no_version):
        raise RuntimeError("Directory {} doesn't exist".format(build_dir_no_version))
    build_dir = os.path.join(build_dir_no_version, version)
    if not version_explicit:
        if not os.path.isdir(build_dir):
            message = """
Directory {build_dir} doesn't exist yet.
If this is where you really want to build the documentation, rerun adding the
command-line argument '--doc-version {version}'""".format(build_dir=build_dir,
                                                          version=version)
            raise RuntimeError(message)

    return build_dir

def get_build_command(build_dir, build_target, num_make_jobs):
    """Return a string giving the build command.

    Args:
    - build_dir: string giving path to directory in which we should build
    - build_target: string: target for the make command (e.g., "html")
    - num_make_jobs: int: number of parallel jobs
    """
    builddir_arg = "BUILDDIR={}".format(build_dir)
    build_command = ["make", builddir_arg, "-j", str(num_make_jobs), build_target]
    return build_command
