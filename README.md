This tool wraps the build command to build sphinx-based documentation.

The main purpose of this tool is to assist with building versioned
documentation, where the documentation builds land in subdirectories
named based on the source branch.

This should be run from the directory that contains the Makefile for
building the documentation.

Typical usage is:

   `./build_docs -r /path/to/doc/build/repo [-v DOC_VERSION] [-i INTERMEDIATE_PATH]`

   This will build the documentation in a subdirectory of the doc build
   repo, where the subdirectory is built from `INTERMEDIATE_PATH` (if
   given), and `DOC_VERSION`. If `DOC_VERSION` isn't given, it will be
   determined based on the git branch name in the doc source repository.

You can also explicitly specify the destination build path, with:

   `./build_docs -b /path/to/doc/build/repo/some/subdirectory`
