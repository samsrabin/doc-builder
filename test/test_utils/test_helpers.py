#!/usr/bin/env python

"""General-purpose functions to help with testing"""

import os
import subprocess

def check_call_suppress_output(args):
    """Make a check_call call with the given args, suppressing all output"""
    devnull = open(os.devnull, 'w')
    subprocess.check_call(args, stdout=devnull, stderr=devnull)
