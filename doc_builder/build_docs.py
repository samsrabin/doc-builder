"""
Implementation of the top-level logic for build_docs.
"""

import subprocess
import argparse
import os
import random
import string
import sys
import signal
from doc_builder.build_commands import get_build_dir, get_build_command, DOCKER_IMAGE

def commandline_options(cmdline_args=None):
    """Process the command-line arguments.

    cmdline_args, if present, should be a string giving the command-line
    arguments. This is typically just used for testing.
    """

    description = """
This tool wraps the build command to build sphinx-based documentation.

This tool assists with creating the correct documentation build commands
in cases including:
- Building the documentation from a Docker container
- Building versioned documentation, where the documentation builds land
  in subdirectories named based on the source branch

This tool should be put somewhere in your path. Then it should be run
from the directory that contains the Makefile for building the
documentation.

Simple usage is:

    build_docs -b /path/to/doc/build/repo/some/subdirectory [-c] [-d] [-i]

    Common additional flags are:
    -c: Before building, run 'make clean'
    -d: Use the escomp/base Docker container to build the documentation

Usage for automatically determining the subdirectory in which to build,
based on the version indicated by the current branch, is:

    ./build_docs -r /path/to/doc/build/repo [-v DOC_VERSION]

    This will build the documentation in a subdirectory of the doc build
    repo, where the subdirectory is built from DOC_VERSION. If
    DOC_VERSION isn't given, it will be determined based on the git
    branch name in the doc source repository.

    In the above example, documentation will be built in:
    /path/to/doc/build/repo/versions/DOC_VERSION

    This usage also accepts the optional arguments described above.
"""

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter)

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

    parser.add_argument("-d", "--build-with-docker", action="store_true",
                        help="Use the {docker_image} Docker container to build the documentation,\n"
                        "rather than relying on locally-installed versions of Sphinx, etc.\n"
                        "This assumes that Docker is installed and running on your system.\n"
                        "\n"
                        "NOTE: This mounts your home directory in the Docker image.\n"
                        "Therefore, both the current directory (containing the Makefile for\n"
                        "building the documentation) and the documentation build directory\n"
                        "must reside somewhere within your home directory.".format(
                            docker_image=DOCKER_IMAGE))

    parser.add_argument("-t", "--build-target", default="html",
                        help="Target for the make command.\n"
                        "Default is 'html'.")

    parser.add_argument("--num-make-jobs", default=4,
                        help="Number of parallel jobs to use for the make process.\n"
                        "Default is 4.")

    parser.add_argument("-w", "--warnings-as-warnings", action="store_true",
                        help="Treat sphinx warnings as warnings, not errors.")

    options = parser.parse_args(cmdline_args)
    return options

def run_build_command(build_command):
    """Echo and then run the given build command"""
    build_command_str = ' '.join(build_command)
    print(build_command_str)
    subprocess.check_call(build_command)

def setup_for_docker():
    """Do some setup for running with docker

    Returns a name that should be used in the docker run command
    """

    docker_name = 'build_docs_' + ''.join(random.choice(string.ascii_lowercase) for _ in range(8))

    # It seems that, if we kill the build_docs process with Ctrl-C, the docker process
    # continues. Handle that by implementing a signal handler. There may be a better /
    # more pythonic way to handle this, but this should work.
    def sigint_kill_docker(signum, frame):
        """Signal handler: kill docker process before exiting"""
        # pylint: disable=unused-argument
        docker_kill_cmd = ["docker", "kill", docker_name]
        subprocess.check_call(docker_kill_cmd)
        sys.exit(1)
    signal.signal(signal.SIGINT, sigint_kill_docker)

    return docker_name

def main(cmdline_args=None):
    """Top-level function implementing build_docs.

    cmdline_args, if present, should be a string giving the command-line
    arguments. This is typically just used for testing.
    """
    opts = commandline_options(cmdline_args)

    if opts.build_with_docker:
        # We potentially reuse the same docker name for multiple docker processes: the
        # clean and the actual build. However, since a given process should end before the
        # next one begins, and because we use '--rm' in the docker run command, this
        # should be okay.
        docker_name = setup_for_docker()
    else:
        docker_name = None

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
                                              run_from_dir=os.getcwd(),
                                              build_target="clean",
                                              num_make_jobs=opts.num_make_jobs,
                                              docker_name=docker_name)
            run_build_command(build_command=clean_command)

        build_command = get_build_command(build_dir=build_dir,
                                          run_from_dir=os.getcwd(),
                                          build_target=opts.build_target,
                                          num_make_jobs=opts.num_make_jobs,
                                          docker_name=docker_name,
                                          warnings_as_warnings=opts.warnings_as_warnings,
                                          )
        run_build_command(build_command=build_command)
