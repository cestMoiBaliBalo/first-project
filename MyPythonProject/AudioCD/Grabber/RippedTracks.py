# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
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

# ========
# Logging.
# ========
with open(os.path.join(get_dirname(os.path.abspath(__file__), level=3), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    config = yaml.load(fp, Loader=yaml.FullLoader)
logging.config.dictConfig(config)
logger = logging.getLogger("MyPythonProject.AudioCD.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

# ============
# Main script.
# ============

# Parse arguments.
parser = argparse.ArgumentParser()
parser.add_argument("audiofile")
arguments = parser.parse_args()
logger.debug(arguments.audiofile)

# Store digital audio file.
path = PureWindowsPath(arguments.audiofile)
parts = len(list(path.parents))
dst = PureWindowsPath("//diskstation/music") / path.parents[parts - 3].parts[1] / path.parents[parts - 3].parts[2] / path.name[:12]
logger.debug(dst)
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "rippedtracks.txt"), mode="a", encoding="UTF_8") as stream:
    stream.write(f"{arguments.audiofile}|{dst}\n")
