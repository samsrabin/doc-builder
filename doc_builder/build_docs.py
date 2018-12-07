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

This tool should be put somewhere in your path. Then it should be run
from the directory that contains the Makefile for building the
documentation.

Typical usage is:

   ./build_docs -r /path/to/doc/build/repo [-v DOC_VERSION]

   This will build the documentation in a subdirectory of the doc build repo, where the
   subdirectory is built from DOC_VERSION. If DOC_VERSION isn't given, it will be
   determined based on the git branch name in the doc source repository.

   In the above example, documentation will be built in:
   /path/to/doc/build/repo/versions/DOC_VERSION

You can also explicitly specify the destination build path, with:

   ./build_docs -b /path/to/doc/build/repo/some/subdirectory
"""

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("build_target", nargs="?", default="html",
                        help="Target for the make command.\n"
                        "Default is 'html'.")

    dir_group = parser.add_mutually_exclusive_group(required=True)

    dir_group.add_argument("-b", "--build-dir", default=None,
                           help="Full path to the directory in which the doc build should go.")

    dir_group.add_argument("-r", "--repo-root", default=None,
                           help="Root directory of the repository holding documentation builds.\n"
                           "(If there are other path elements between the true repo root and\n"
                           "the 'versions' directory, those should be included in this path.)")

    parser.add_argument("-v", "--doc-version", nargs='+', default=[None],
                        help="Version name to build,\n"
                        "corresponding to a directory name under repo root.\n"
                        "Not applicable if --build-dir is specified.\n"
                        "Multiple versions can be specified, in which case a build\n"
                        "will be done for each version (with the same source).")

    parser.add_argument("-c", "--clean", action="store_true",
                        help="Before building, run 'make clean'.")

    parser.add_argument("--num-make-jobs", default=4,
                        help="Number of parallel jobs to use for the make process.\n"
                        "Default is 4.")

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

    # Note that we do a separate build for each version. This is
    # inefficient (assuming that the desired end result is for the
    # different versions to be identical), but was an easy-to-implement
    # solution to add convenience for building multiple versions of
    # documentation with short build times (i.e., rather than requiring
    # you to rerun build_docs multiple times). If this
    # multiple-versions-at-once option starts to be used a lot, we could
    # reimplement it to build just one version then copy the builds to
    # the other versions (if that gives the correct end result).
    for version in opts.doc_version:

        build_dir = get_build_dir(build_dir=opts.build_dir,
                                  repo_root=opts.repo_root,
                                  version=version)

        if opts.clean:
            clean_command = get_build_command(build_dir=build_dir,
                                              build_target="clean",
                                              num_make_jobs=opts.num_make_jobs)
            run_build_command(build_command=clean_command)

        build_command = get_build_command(build_dir=build_dir,
                                          build_target=opts.build_target,
                                          num_make_jobs=opts.num_make_jobs)
        run_build_command(build_command=build_command)
