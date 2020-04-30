# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name
import argparse
import locale
import logging.config
import os
from pathlib import Path

import yaml

from Applications.shared import APPEND, UTF8

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")

# ========
# Logging.
# ========
with open(_MYPARENT.parents[1] / "Resources" / "logging.yml", encoding=UTF8) as fp:
    config = yaml.load(fp, Loader=yaml.FullLoader)
logging.config.dictConfig(config)
logger = logging.getLogger("MyPythonProject.AudioCD.{0}".format(_MYNAME))


# ==============
# Local classes.
# ==============
class GetPath(argparse.Action):
    """

    """

    def __init__(self, option_strings, dest, **kwargs):
        super(GetPath, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, list(map(Path, values)))


# ============
# Main script.
# ============

# Parse arguments.
parser = argparse.ArgumentParser()
parser.add_argument("path", help="String representing an audio file. Both path and name.", action=GetPath, nargs="+")
parser.add_argument("--output", type=argparse.FileType(mode=APPEND, encoding=UTF8))
arguments = parser.parse_args()

# Get output file.
output = arguments.output
if not arguments.output:
    output = open(_MYPARENT.parents[2] / "Resources" / "rippedtracks.txt", mode=APPEND, encoding=UTF8)

# Process digital audio file.
for path in arguments.path:
    parts = len(list(path.parents))
    dst = Path("//diskstation/music") / "/".join(path.parents[parts - 3].parts[1:]) / path.name[:12]
    logger.debug("Copy audio file.")
    logger.debug("\tFile        : %s".expandtabs(3), path)
    logger.debug("\tDestination : %s".expandtabs(3), dst)
    output.write(f"{Path(_MYPARENT.parent / 'Templates').resolve()}|T00a|{path}|{dst}\n")
