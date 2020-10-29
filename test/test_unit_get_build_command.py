#!/usr/bin/env python3

"""Unit test driver for get_build_command function
"""

import unittest
from doc_builder.build_commands import get_build_command

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

    def test_docker(self):
        """Tests usage with use_docker=True"""
        build_command = get_build_command(build_dir="/path/to/foorepos/foodocs/versions/main",
                                          run_from_dir="/path/to/foorepos/foocode/doc",
                                          build_target="html",
                                          num_make_jobs=4,
                                          docker_name='foo')
        expected = ["docker", "run",
                    "--name", "foo",
                    "--volume", "/path/to/foorepos:/home/user",
                    "--workdir", "/home/user/foocode/doc",
                    "--rm",
                    "escomp/base",
                    "/bin/bash", "-c",
                    # Note that the following two lines are all one long string
                    "sudo mkdir -p /path/to && sudo ln -s /home/user /path/to/foorepos && "
                    "make BUILDDIR=/path/to/foorepos/foodocs/versions/main -j 4 html"]
        self.assertEqual(expected, build_command)

    def test_docker_relpath(self):
        """Tests usage with use_docker=True, with a relative path to build_dir"""
        build_command = get_build_command(build_dir="../../foodocs/versions/main",
                                          run_from_dir="/path/to/foorepos/foocode/doc",
                                          build_target="html",
                                          num_make_jobs=4,
                                          docker_name='foo')
        expected = ["docker", "run",
                    "--name", "foo",
                    "--volume", "/path/to/foorepos:/home/user",
                    "--workdir", "/home/user/foocode/doc",
                    "--rm",
                    "escomp/base",
                    "/bin/bash", "-c",
                    # Note that the following two lines are all one long string
                    "sudo mkdir -p /path/to && sudo ln -s /home/user /path/to/foorepos && "
                    "make BUILDDIR=../../foodocs/versions/main -j 4 html"]
        self.assertEqual(expected, build_command)

if __name__ == '__main__':
    unittest.main()
