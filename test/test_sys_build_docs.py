#!/usr/bin/env python
"""
High-level system tests of the whole build_docs
"""

from __future__ import print_function

import unittest
import tempfile
import shutil
import os
from doc_builder import build_docs
from test.test_utils.git_helpers import (make_git_repo,
                                         add_git_commit,
                                         checkout_git_branch)

class TestBuildDocs(unittest.TestCase):
    """High-level system tests of build_docs"""

    # ------------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------------

    def setUp(self):
        """Set up temporary source and repo-root directories, and chdir to
        the source directory"""
        self._return_dir = os.getcwd()
        self._sourcedir = tempfile.mkdtemp()
        self._build_reporoot = tempfile.mkdtemp()
        os.chdir(self._sourcedir)

    def tearDown(self):
        os.chdir(self._return_dir)
        shutil.rmtree(self._sourcedir, ignore_errors=True)
        shutil.rmtree(self._build_reporoot, ignore_errors=True)

    def write_makefile(self):
        """Write a fake makefile in the current directory

        The 'html' target of this Makefile just results in the text
        'hello world' being written to BUILDDIR/testfile.
        """

        makefile_contents = """
html:
\t@echo "hello world" > $(BUILDDIR)/testfile
"""

        with open('Makefile', 'w') as makefile:
            makefile.write(makefile_contents)
            
    def assertFileContentsEqual(self, expected, filepath, msg=None):
        """Asserts that the contents of the file given by 'filepath' are equal to
        the string given by 'expected'. 'msg' gives an optional message to be
        printed if the assertion fails."""

        with open(filepath, 'r') as myfile:
            contents = myfile.read()

        self.assertEqual(expected, contents, msg=msg)

    # ------------------------------------------------------------------------
    # Begin tests
    # ------------------------------------------------------------------------

    def test_with_repo_root_and_intermediate_path(self):
        """Test with repo-root and intermediate-path specified, but doc-version not specified
        (so doc version needs to be determined via git commands)."""

        self.write_makefile()
        make_git_repo()
        add_git_commit()
        checkout_git_branch('foo_branch')
        intermediate_path = os.path.join("intermediate1", "intermediate2")
        build_path = os.path.join(self._build_reporoot,
                                  intermediate_path,
                                  "foo_branch")
        os.makedirs(build_path)

        args = ["--repo-root", self._build_reporoot,
                "--intermediate-path", intermediate_path]
        build_docs.main(args)

        self.assertFileContentsEqual(expected="hello world\n",
                                     filepath=os.path.join(build_path, "testfile"))

if __name__ == '__main__':
    unittest.main()
