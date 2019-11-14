# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import locale
import logging.config
import os
from pathlib import Path

import yaml

from Applications.shared import APPEND, UTF8, get_dirname

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")

# ========
# Logging.
# ========
with open(os.path.join(get_dirname(os.path.abspath(__file__), level=3), "Resources", "logging.yml"), encoding=UTF8) as fp:
    config = yaml.load(fp, Loader=yaml.FullLoader)
logging.config.dictConfig(config)
logger = logging.getLogger("MyPythonProject.AudioCD.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

# ============
# Main script.
# ============

# Parse arguments.
parser = argparse.ArgumentParser()
parser.add_argument("path", help="String representing an audio file. Both path and name.")
parser.add_argument("action", help="Action code.", nargs="*")
arguments = parser.parse_args()

# Process digital audio file.
path = Path(arguments.path)
parts = len(list(path.parents))
dst = Path("//diskstation/music") / "/".join(path.parents[parts - 3].parts[1:]) / path.name[:12]
logger.debug("Copy audio file.")
logger.debug("\tFile        : %s".expandtabs(3), arguments.path)
logger.debug("\tDestination : %s".expandtabs(3), dst)
with open(Path(os.path.expandvars("%_COMPUTING%")) / "Resources" / "rippedtracks.txt", mode=APPEND, encoding=UTF8) as stream:
    stream.write(f"{arguments.path}|{dst}\n")
