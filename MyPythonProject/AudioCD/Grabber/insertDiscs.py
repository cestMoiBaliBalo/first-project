# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import logging.config
import os
import sys
from contextlib import suppress
from pathlib import Path

import yaml

from Applications.Tables.Albums.shared import insert_discs_fromjson
from Applications.shared import UTF8

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("file", type=argparse.FileType(mode="r", encoding="UTF_8"))
parser.add_argument("--debug", action="store_true")

# ==========
# Constants.
# ==========
LOGGERS = ["Applications.Tables.Albums"]
MAPPING = {True: "debug", False: "info"}

# ================
# Initializations.
# ================
arguments = parser.parse_args()

# ========
# Logging.
# ========
with open(_MYPARENT.parents[1] / "Resources" / "logging.yml", encoding=UTF8) as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)
for logger in LOGGERS:
    with suppress(KeyError):
        config["loggers"][logger]["level"] = MAPPING[arguments.debug].upper()
logging.config.dictConfig(config)

# ===============
# Main algorithm.
# ===============
sys.exit(insert_discs_fromjson(arguments.file))
