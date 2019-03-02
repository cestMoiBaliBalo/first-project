# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import locale
import logging.config
import os
from pathlib import PureWindowsPath

import yaml

from Applications.shared import get_dirname

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

that_file = os.path.abspath(__file__)

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "french")

# ===========================
# Load logging configuration.
# ===========================
with open(os.path.join(get_dirname(os.path.abspath(__file__), level=3), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))

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
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "rippedtracks.txt"), "a", encoding="UTF-8") as stream:
    stream.write(f"{arguments.audiofile}|{dst}\r\n")
