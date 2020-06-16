# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import os
from itertools import repeat
from subprocess import run
from tempfile import mkdtemp, mkstemp

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# -----
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="action")

# -----
parser_dir = subparsers.add_parser("dir")
parser_dir.add_argument("--prefix", "-p", default=os.path.expandvars("%TEMP%"), nargs="?")
parser_dir.add_argument("--glob", "-g", action="store_true")
parser_dir.add_argument("--files", "-f", action="count")

# -----
parser_fil = subparsers.add_parser("fil")
parser_fil.add_argument("--prefix", "-p", default=os.path.expandvars("%TEMP%"), nargs="?")
parser_fil.add_argument("--files", "-f", action="count")

# -----
arguments = parser.parse_args()

# -----
if arguments.action == "dir":
    tmpdir = mkdtemp(dir=arguments.prefix)
    print(tmpdir)
    if arguments.glob:
        run(f"SETX _TMPDIR {tmpdir}")
    if arguments.files:
        for _, fil in map(mkstemp, repeat(None), repeat(None), [tmpdir] * arguments.files, repeat(False)):
            print(fil)

files = 1
if arguments.action == "fil":
    if arguments.files:
        files = arguments.files
    for _, fil in map(mkstemp, repeat(None), repeat(None), [arguments.prefix] * files, repeat(False)):
        print(fil)
