#!/usr/bin/env python

"""Unit test driver for get_build_dir function
"""

from __future__ import print_function

import unittest
try:
    # For python2; needs pip install mock
    import mock
except ImportError:
    # For python3
    from unittest import mock
import os
from test.test_utils.sys_utils_fake import make_fake_isdir
from doc_builder.build_commands import get_build_dir

class TestGetBuildDir(unittest.TestCase):
    """Test the get_build_dir function
    """
    # Allow long method names
    # pylint: disable=invalid-name

    def test_with_builddir(self):
        """If given a build_dir, should return that"""
        build_dir = get_build_dir(build_dir="/path/to/foo",
                                  repo_root=None,
                                  version=None)
        self.assertEqual("/path/to/foo", build_dir)

    def test_builddir_and_reporoot(self):
        """If given both build_dir and repo_root, should raise an exception"""
        with self.assertRaises(RuntimeError):
            _ = get_build_dir(build_dir="/path/to/foo",
                              repo_root="/path/to/repo",
                              version=None)

    def test_builddir_and_version(self):
        """If given both build_dir and version, should raise an exception"""
        with self.assertRaises(RuntimeError):
            _ = get_build_dir(build_dir="/path/to/foo",
                              repo_root=None,
                              version="v1.0")

    def test_no_builddir_or_reporoot(self):
        """If given neither build_dir nor repo_root, should raise an exception"""
        with self.assertRaises(RuntimeError):
            _ = get_build_dir(build_dir=None,
                              repo_root=None,
                              version=None)

    def test_reporoot_and_version(self):
        """If given both repo_root and version, should return correct build_dir"""
        with mock.patch('os.path.isdir') as mock_isdir:
            path_to_repo = os.path.join("path", "to", "repo")
            # /path/to/repo exists; with version specified explicitly,
            # /path/to/repo/v1.0 doesn't need to exist
            mock_isdir.side_effect = make_fake_isdir(
                dirs_exist=[path_to_repo])
            build_dir = get_build_dir(build_dir=None,
                                      repo_root=path_to_repo,
                                      version="v1.0")
        expected = os.path.join(path_to_repo, "v1.0")
        self.assertEqual(expected, build_dir)

    def test_reporoot_and_version_dir_not_exist(self):
        """If given repo_root and version, with repo_root not existing, should raise an
        exception.
        """
        with mock.patch('os.path.isdir') as mock_isdir:
            path_to_parent = os.path.join("path", "to", "parent")
            path_to_repo = os.path.join(path_to_parent, "repo")
            # /path/to/parent exists, but not /path/to/parent/repo
            mock_isdir.side_effect = make_fake_isdir(
                dirs_exist=[path_to_parent])
            with self.assertRaises(RuntimeError):
                _ = get_build_dir(build_dir=None,
                                  repo_root=path_to_repo,
                                  version="v1.0")

    def test_reporoot_no_version(self):
        """If given repo_root but no version, get version from git branch"""
        with mock.patch('doc_builder.sys_utils.git_current_branch') as mock_git_current_branch:
            with mock.patch('os.path.isdir') as mock_isdir:
                mock_git_current_branch.return_value = (True, 'release-v2.0')
                path_to_repo = os.path.join("path", "to", "repo")
                expected = os.path.join(path_to_repo, "release-v2.0")
                mock_isdir.side_effect = make_fake_isdir(
                    dirs_exist=[path_to_repo, expected])
                build_dir = get_build_dir(build_dir=None,
                                          repo_root=path_to_repo,
                                          version=None)

        self.assertEqual(expected, build_dir)

    def test_reporoot_no_version_git_branch_problem(self):
        """If given repo_root but no version, with a problem getting git
        branch, should raise an exception."""
        with mock.patch('doc_builder.sys_utils.git_current_branch') as mock_git_current_branch:
            mock_git_current_branch.return_value = (False, '')
            with self.assertRaises(RuntimeError):
                _ = get_build_dir(build_dir=None,
                                  repo_root="/path/to/repo",
                                  version=None)

    def test_reporoot_no_version_dir_not_exist(self):
        """If given repo_root but no version, with the expected
        directory not existing, should raise an exception."""
        with mock.patch('doc_builder.sys_utils.git_current_branch') as mock_git_current_branch:
            with mock.patch('os.path.isdir') as mock_isdir:
                mock_git_current_branch.return_value = (True, 'release-v2.0')
                path_to_repo = os.path.join("path", "to", "repo")
                # /path/to/repo exists, but /path/to/repo/release-v2.0 does not
                mock_isdir.side_effect = make_fake_isdir(
                    dirs_exist=[path_to_repo])
                with self.assertRaises(RuntimeError):
                    _ = get_build_dir(build_dir=None,
                                      repo_root=path_to_repo,
                                      version=None)


if __name__ == '__main__':
    unittest.main()
