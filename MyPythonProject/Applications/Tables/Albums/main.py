# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import csv
import locale
import logging.config
import os
import sys

import yaml

from Applications.Tables.Albums.shared import insert_defaultalbums_fromplaintext
from Applications.parsers import database_parser
from Applications.shared import get_dirname

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

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

parser = argparse.ArgumentParser(parents=database_parser)
parser.add_argument("tags", help="tags text file")
parser.add_argument("--encoding", nargs="?", default="UTF_8c")
parser.add_argument("--delimiter", nargs="?", default="|")
parser.add_argument("--escapechar", nargs="?", default="`")
parser.add_argument("--doublequote", action="store_True")
arguments = parser.parse_args()
sys.exit(insert_defaultalbums_fromplaintext(arguments.tags,
                                            db=arguments.database,
                                            encoding=arguments.encoding,
                                            delimiter=arguments.delimiter,
                                            escapechar=arguments.escapechar,
                                            doublequote=arguments.doublequote,
                                            quoting=csv.QUOTE_NONE))
