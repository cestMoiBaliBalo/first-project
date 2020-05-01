# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
from subprocess import run
from tempfile import mkdtemp, mkstemp

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# -----
parser = argparse.ArgumentParser()
parser.add_argument("--files", action="store_true")
parser.add_argument("--glob", action="store_true")
arguments = parser.parse_args()

# -----
tmpdir = mkdtemp()

# -----
if arguments.files:

    # -----
    _, ymltmp = mkstemp(dir=tmpdir)
    print(ymltmp)

    # -----
    _, txttmp = mkstemp(dir=tmpdir)
    print(txttmp)

    # -----
    _, jsontmp = mkstemp(dir=tmpdir)
    print(jsontmp)

    # -----
    _, tmp = mkstemp(dir=tmpdir)
    print(tmp)

# -----
if arguments.glob:
    run(f"SETX _TMPDIR {tmpdir}")
    if arguments.files:
        run(f"SETX _TMPYML {ymltmp}")
        run(f"SETX _TMPTXT {txttmp}")
        run(f"SETX _TMPJSON {jsontmp}")
        run(f"SETX _TMPFIL {tmp}")
