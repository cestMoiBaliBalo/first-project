# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import locale
import logging.config
import os
import sys

import yaml

from .shared import insert_defaultalbums_fromplaintext
from ...parsers import database_parser
from ...shared import get_dirname

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_THATFILE = os.path.abspath(__file__)

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")

# ===========================
# Load logging configuration.
# ===========================
with open(os.path.join(get_dirname(_THATFILE, level=4), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp, Loader=yaml.FullLoader))

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
sys.exit(insert_defaultalbums_fromplaintext(arguments.tags,
                                            encoding=arguments.encoding,
                                            delimiter=arguments.delimiter,
                                            doublequote=arguments.doublequote,
                                            escapechar=arguments.escapechar,
                                            quoting=arguments.quoting))
