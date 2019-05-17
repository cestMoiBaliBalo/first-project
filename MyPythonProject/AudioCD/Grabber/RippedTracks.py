# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import os
from pathlib import PureWindowsPath

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

that_file = os.path.abspath(__file__)

# ============
# Main script.
# ============

# Parse arguments.
parser = argparse.ArgumentParser()
parser.add_argument("audiofile")
arguments = parser.parse_args()

# Store digital audio file.
path = PureWindowsPath(arguments.audiofile)
parts = len(list(path.parents))
dst = PureWindowsPath("//diskstation/music") / path.parents[parts - 3].parts[1] / path.parents[parts - 3].parts[2] / path.name[:12]
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "rippedtracks.txt"), mode="a", encoding="UTF_8") as stream:
    stream.write(f"{arguments.audiofile}|{dst}\n")