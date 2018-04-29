# -*- coding: utf-8 -*-
import argparse
import logging.config
import os
import sys
from contextlib import suppress
from itertools import accumulate

import yaml

from Applications.Database.DigitalAudioFiles.shared import insertfromfile

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
with suppress(KeyError):
    config["loggers"]["Applications.Database.DigitalAudioFiles"]["level"] = MAPPING[arguments.debug].upper()
logging.config.dictConfig(config)
logger = logging.getLogger("Applications.Database.DigitalAudioFiles")

# ===============
# Main algorithm.
# ===============
sys.exit(list(accumulate(insertfromfile(arguments.tracks)))[-1])
