#!/usr/bin/env python

"""
Implementation of the top-level logic for build_docs.
"""

from __future__ import print_function
import subprocess
import argparse
from doc_builder.build_commands import get_build_dir, get_build_command

def commandline_options(cmdline_args=None):
    """Process the command-line arguments.

    cmdline_args, if present, should be a string giving the command-line
    arguments. This is typically just used for testing.
    """

    description = """
This tool wraps the build command to build sphinx-based documentation.

The main purpose of this tool is to assist with building versioned
documentation, where the documentation builds land in subdirectories
named based on the source branch.

This should be run from the directory that contains the Makefile for
building the documentation.

Typical usage is:

   ./build_docs -r /path/to/doc/build/repo [-v DOC_VERSION] [-i INTERMEDIATE_PATH]

   This will build the documentation in a subdirectory of the doc build
   repo, where the subdirectory is built from INTERMEDIATE_PATH (if
   given), and DOC_VERSION. If DOC_VERSION isn't given, it will be
   determined based on the git branch name in the doc source repository.

You can also explicitly specify the destination build path, with:

   ./build_docs -b /path/to/doc/build/repo/some/subdirectory
"""

    parser = argparse.ArgumentParser(
        description = description,
        formatter_class = argparse.RawTextHelpFormatter)

    parser.add_argument("build_args", nargs="?", default="-j 4 html",
                        help="Arguments to the make command.\n"
                        "Default is '-j 4 html'")

    dir_group = parser.add_mutually_exclusive_group(required=True)

    dir_group.add_argument("-b", "--build-dir", default=None,
                           help="Full path to the directory in which the doc build should go.")

    dir_group.add_argument("-r", "--repo-root", default=None,
                           help="Root directory of the repository holding documentation builds.")

    parser.add_argument("-v", "--doc-version", default=None,
                        help="Version name to build, corresponding to a directory name under repo root.\n"
                        "Not applicable if --build-dir is specified.")

    parser.add_argument("-i", "--intermediate-path", default="",
                        help="Intermediate path elements between repo root and version directory.\n"
                        "Not applicable if --build-dir is specified.")

    options = parser.parse_args(cmdline_args)
    return options

def run_build_command(build_command):
    """Echo and then run the given build command"""
    build_command_str = ' '.join(build_command)
    print(build_command_str)
    subprocess.check_call(build_command)

def main(cmdline_args=None):
    """Top-level function implementing build_docs.

    cmdline_args, if present, should be a string giving the command-line
    arguments. This is typically just used for testing.
    """
    opts = commandline_options(cmdline_args)
    build_dir = get_build_dir(build_dir = opts.build_dir,
                              repo_root = opts.repo_root,
                              version = opts.doc_version,
                              intermediate_path = opts.intermediate_path)
    build_command = get_build_command(build_dir = build_dir,
                                      build_args = opts.build_args)
    run_build_command(build_command = build_command)
