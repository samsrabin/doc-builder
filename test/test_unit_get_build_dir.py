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
    import unittest.mock as mock
import os
from doc_builder.build_dir import get_build_dir
from doc_builder import sys_utils

class TestGetBuildDir(unittest.TestCase):
    """Test the get_build_dir function
    """

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

    def test_builddir_and_intermediatepath(self):
        """If given both build_dir and intermediate_path, should raise an exception"""
        with self.assertRaises(RuntimeError):
            _ = get_build_dir(build_dir="/path/to/foo",
                              repo_root=None,
                              version=None,
                              intermediate_path="bar")

    def test_no_builddir_or_reporoot(self):
        """If given neither build_dir nor repo_root, should raise an exception"""
        with self.assertRaises(RuntimeError):
            _ = get_build_dir(build_dir=None,
                              repo_root=None,
                              version=None)

    def test_reporoot_and_version(self):
        """If given both repo_root and version, should return correct build_dir"""
        build_dir = get_build_dir(build_dir=None,
                                  repo_root="/path/to/repo",
                                  version="v1.0")
        expected = os.path.join("/path/to/repo", "v1.0")
        self.assertEqual(expected, build_dir)

    def test_reporoot_and_version_and_intermediatepath(self):
        """If given repo_root, version and intermediate_path, should return correct build_dir"""
        build_dir = get_build_dir(build_dir=None,
                                  repo_root="/path/to/repo",
                                  version="v1.0",
                                  intermediate_path="foo")
        expected = os.path.join("/path/to/repo", "foo", "v1.0")
        self.assertEqual(expected, build_dir)

    def test_reporoot_no_version(self):
        """If given repo_root but no version, get version from git branch"""
        with mock.patch('doc_builder.sys_utils.git_current_branch') as mock_git_current_branch:
            with mock.patch('doc_builder.sys_utils.dir_exists') as mock_dir_exists:
                mock_git_current_branch.return_value = (True, 'release-v2.0')
                mock_dir_exists.return_value = True
                build_dir = get_build_dir(build_dir=None,
                                          repo_root="/path/to/repo",
                                          version=None)
                expected = os.path.join("/path/to/repo", "release-v2.0")
                mock_dir_exists.assert_called_with(expected)

        self.assertEqual(expected, build_dir)

    def test_reporoot_no_version_git_branch_problem(self):
        """If given repo_root but no version, with a problem getting git
        branch, should raise an exception."""
        with mock.patch('doc_builder.sys_utils.git_current_branch') as mock_git_current_branch:
            mock_git_current_branch.return_value = (False, '')
            with self.assertRaises(RuntimeError):
                build_dir = get_build_dir(build_dir=None,
                                          repo_root="/path/to/repo",
                                          version=None)

    def test_reporoot_no_version_dir_not_exist(self):
        """If given repo_root but no version, with the expected
        directory not existing, should raise an exception."""
        with mock.patch('doc_builder.sys_utils.git_current_branch') as mock_git_current_branch:
            with mock.patch('doc_builder.sys_utils.dir_exists') as mock_dir_exists:
                mock_git_current_branch.return_value = (True, 'release-v2.0')
                mock_dir_exists.return_value = False
                with self.assertRaises(RuntimeError):
                    build_dir = get_build_dir(build_dir=None,
                                              repo_root="/path/to/repo",
                                              version=None)
                expected = os.path.join("/path/to/repo", "release-v2.0")
                mock_dir_exists.assert_called_with(expected)


if __name__ == '__main__':
    unittest.main()
