#!/usr/bin/env python3

"""Unit test driver for get_build_command function
"""

import unittest
from unittest.mock import patch
from doc_builder.build_commands import get_build_command

# Allow names that pylint doesn't like, because otherwise I find it hard
# to make readable unit test names
# pylint: disable=invalid-name

# pylint: disable=line-too-long

class TestGetBuildCommand(unittest.TestCase):
    """Test the get_build_command function"""

    def test_basic(self):
        """Tests basic usage"""
        build_command = get_build_command(build_dir="/path/to/foo",
                                          run_from_dir="/irrelevant/path",
                                          build_target="html",
                                          num_make_jobs=4,
                                          docker_name=None)
        expected = ["make", "BUILDDIR=/path/to/foo", "-j", "4", "html"]
        self.assertEqual(expected, build_command)

    @patch('os.path.expanduser')
    def test_docker(self, mock_expanduser):
        """Tests usage with use_docker=True"""
        mock_expanduser.return_value = "/path/to/username"
        build_command = get_build_command(build_dir="/path/to/username/foorepos/foodocs/versions/main",
                                          run_from_dir="/path/to/username/foorepos/foocode/doc",
                                          build_target="html",
                                          num_make_jobs=4,
                                          docker_name='foo')
        expected = ["docker", "run",
                    "--name", "foo",
                    "--volume", "/path/to/username:/home/user/mounted_home",
                    "--workdir", "/home/user/mounted_home/foorepos/foocode/doc",
                    "-t",
                    "--rm",
                    "escomp/base",
                    "/bin/bash", "-c",
                    # Note that the following three lines are all one long string
                    #
                    # Also note that this will currently fail on Windows, because we don't
                    # include the link command there (if need be, we could include some
                    # platform logic in this unit test, but actually, there may be bigger
                    # issues on Windows due to the paths in this unit test being
                    # Posix-style rather than Windows-style)
                    "sudo mkdir -p /path/to && "
                    "sudo ln -s /home/user/mounted_home /path/to/username && "
                    "make BUILDDIR=/home/user/mounted_home/foorepos/foodocs/versions/main -j 4 html"]
        self.assertEqual(expected, build_command)

    @patch('os.path.expanduser')
    def test_docker_relpath(self, mock_expanduser):
        """Tests usage with use_docker=True, with a relative path to build_dir"""
        mock_expanduser.return_value = "/path/to/username"
        build_command = get_build_command(build_dir="../../foodocs/versions/main",
                                          run_from_dir="/path/to/username/foorepos/foocode/doc",
                                          build_target="html",
                                          num_make_jobs=4,
                                          docker_name='foo')
        expected = ["docker", "run",
                    "--name", "foo",
                    "--volume", "/path/to/username:/home/user/mounted_home",
                    "--workdir", "/home/user/mounted_home/foorepos/foocode/doc",
                    "-t",
                    "--rm",
                    "escomp/base",
                    "/bin/bash", "-c",
                    # Note that the following three lines are all one long string
                    #
                    # Also note that this will currently fail on Windows, because we don't
                    # include the link command there (if need be, we could include some
                    # platform logic in this unit test, but actually, there may be bigger
                    # issues on Windows due to the paths in this unit test being
                    # Posix-style rather than Windows-style)
                    "sudo mkdir -p /path/to && "
                    "sudo ln -s /home/user/mounted_home /path/to/username && "
                    "make BUILDDIR=/home/user/mounted_home/foorepos/foodocs/versions/main -j 4 html"]
        self.assertEqual(expected, build_command)

    @patch('os.path.expanduser')
    def test_docker_builddir_not_in_home(self, mock_expanduser):
        """If build_dir is not in the user's home directory, should raise an exception"""
        mock_expanduser.return_value = "/path/to/username"
        with self.assertRaisesRegex(
                RuntimeError,
                "build directory must reside under your home directory"):
            _ = get_build_command(build_dir="/path/to/other/foorepos/foodocs/versions/main",
                                  run_from_dir="/path/to/username/foorepos/foocode/doc",
                                  build_target="html",
                                  num_make_jobs=4,
                                  docker_name='foo')

    @patch('os.path.expanduser')
    def test_docker_runfromdir_not_in_home(self, mock_expanduser):
        """If run_from_dir is not in the user's home directory, should raise an exception"""
        mock_expanduser.return_value = "/path/to/username"
        with self.assertRaisesRegex(
                RuntimeError,
                "build_docs must be run from somewhere within your home directory"):
            _ = get_build_command(build_dir="/path/to/username/foorepos/foodocs/versions/main",
                                  run_from_dir="/path/to/other/foorepos/foocode/doc",
                                  build_target="html",
                                  num_make_jobs=4,
                                  docker_name='foo')


if __name__ == '__main__':
    unittest.main()
