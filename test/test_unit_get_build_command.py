#!/usr/bin/env python

"""Unit test driver for get_build_command function
"""

from __future__ import print_function
import unittest
from doc_builder.build_commands import get_build_command

class TestGetBuildCommand(unittest.TestCase):
    """Test the get_build_command function"""

    def test_basic(self):
        """Tests basic usage"""
        build_command = get_build_command(build_dir="/path/to/foo",
                                          build_args="-j 4 html")
        expected = ["make", "BUILDDIR=/path/to/foo", "-j", "4", "html"]
        self.assertEqual(expected, build_command)

    def test_no_build_args(self):
        """Tests with no extra build args"""
        build_command = get_build_command(build_dir="/path/to/foo")
        expected = ["make", "BUILDDIR=/path/to/foo"]
        self.assertEqual(expected, build_command)

if __name__ == '__main__':
    unittest.main()
