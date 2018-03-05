# -*- coding: utf-8 -*-
import argparse
import logging.config
import os
import sys

import yaml

from Applications.Database.AudioCD.shared import insertfromfile

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("tracks", type=argparse.FileType(mode="r", encoding="UTF_8"))
parser.add_argument("--debug", action="store_true")

# ==========
# Constants.
# ==========
MAPPING = {True: "debug", False: "info"}

# ================
# Initializations.
# ================
arguments = parser.parse_args()

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    config = yaml.load(fp)
try:
    config["loggers"]["Applications.Database.AudioCD"]["level"] = MAPPING[arguments.debug].upper()
except KeyError:
    pass
logging.config.dictConfig(config)
logger = logging.getLogger("Applications.Database.AudioCD")

# ===============
# Main algorithm.
# ===============
sys.exit(insertfromfile(arguments.tracks))
