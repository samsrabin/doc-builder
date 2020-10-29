"""
Functions with the main logic needed to build the command to build the docs
"""

import os
from doc_builder import sys_utils

# The Docker image used to build documentation via Docker
_DOCKER_IMAGE = "escomp/base"

# The top-level directory in the above docker image
_DOCKER_ROOT = "/home/user"

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

def get_build_command(build_dir, run_from_dir, build_target, num_make_jobs, docker_name=None):
    """Return a string giving the build command.

    Args:
    - build_dir: string giving path to directory in which we should build
        If this is a relative path, it is assumed to be relative to run_from_dir
    - run_from_dir: string giving absolute path from which the build_docs command was run
        This is needed when using Docker
    - build_target: string: target for the make command (e.g., "html")
    - num_make_jobs: int: number of parallel jobs
    - docker_name: string or None: if not None, uses a Docker container to do the build,
        with the given name
    """
    builddir_arg = "BUILDDIR={}".format(build_dir)
    build_command = ["make", builddir_arg, "-j", str(num_make_jobs), build_target]

    if docker_name is not None:
        if os.path.isabs(build_dir):
            build_dir_abs = build_dir
        else:
            build_dir_abs = os.path.normpath(os.path.join(run_from_dir, build_dir))
        # mount the Docker image in a directory that is a parent of both build_dir and run_from_dir
        docker_mountpoint = os.path.commonpath([build_dir_abs, run_from_dir])
        docker_workdir = run_from_dir.replace(docker_mountpoint, _DOCKER_ROOT, 1)
        docker_command = ["docker", "run",
                          "--name", docker_name,
                          "--volume", "{}:{}".format(docker_mountpoint, _DOCKER_ROOT),
                          "--workdir", docker_workdir,
                          "--rm",
                          _DOCKER_IMAGE]
        build_command = docker_command + build_command

    return build_command
