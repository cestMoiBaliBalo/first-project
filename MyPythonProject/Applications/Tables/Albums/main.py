# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import locale
import logging.config
import os
import sys
from pathlib import Path

import yaml

from .shared import insert_defaultdiscs_fromplaintext
from ...parsers import database_parser
from ...shared import UTF8

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

# ===========================
# Load logging configuration.
# ===========================
with open(_MYPARENT.parents[2] / "Resources" / "logging.yml", encoding=UTF8) as stream:
    logging.config.dictConfig(yaml.load(stream, Loader=yaml.FullLoader))

# ==============
# Get arguments.
# ==============
parser = argparse.ArgumentParser(parents=[database_parser])
parser.add_argument("tags", help="tags plain text file created by MP3Tags or any other application")
parser.add_argument("--encoding", nargs="?", default="UTF_8")
parser.add_argument("--delimiter", nargs="?", default="|")
parser.add_argument("--doublequote", action="store_true")
parser.add_argument("--escapechar", nargs="?", default="`")
parser.add_argument("--quoting", nargs="?", default="3", type=int, choices=[0, 1, 2, 3])
arguments = parser.parse_args()

# ================
# Run main script.
# ================
sys.exit(insert_defaultdiscs_fromplaintext(arguments.tags,
                                           encoding=arguments.encoding,
                                           delimiter=arguments.delimiter,
                                           doublequote=arguments.doublequote,
                                           escapechar=arguments.escapechar,
                                           quoting=arguments.quoting))
