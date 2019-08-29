# -*- coding: utf-8 -*-
import argparse
import logging.config
import os
import sys
from contextlib import suppress

import yaml

from Applications.Tables.Albums.shared import insert_albums_fromjson
from Applications.shared import get_dirname

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("tags", type=argparse.FileType(mode="r", encoding="UTF_8"))
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
with open(os.path.join(get_dirname(os.path.abspath(__file__), level=2), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    config = yaml.load(fp, Loader=yaml.FullLoader)
for logger in LOGGERS:
    with suppress(KeyError):
        config["loggers"][logger]["level"] = MAPPING[arguments.debug].upper()
logging.config.dictConfig(config)

# ===============
# Main algorithm.
# ===============
sys.exit(insert_albums_fromjson(arguments.tags))
