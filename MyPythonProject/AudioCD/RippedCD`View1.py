# -*- coding: utf-8 -*-
"""
Log ripped audio CDs.
"""
import argparse
import logging.config
import os
import sys
from contextlib import suppress

import yaml

from Applications.Database.AudioCD.shared import selectlogs_fromkeywords
from Applications.parsers import database_parser, loglevel_parser
from Applications.shared import UTF8

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# =======
# Parser.
# =======
parser = argparse.ArgumentParser(parents=[database_parser, loglevel_parser])
parser.add_argument("-c", "--console", action="store_true")

# ================
# Initializations.
# ================
arguments = parser.parse_args()

# ========
# Logging.
# ========

# 1. Load logging configuration and adapt logger(s) level(s).
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding=UTF8) as fp:
    config = yaml.load(fp)
for logger in ["Applications.Database.AudioCD", "Database"]:
    with suppress(KeyError):
        config["loggers"][logger]["level"] = arguments.loglevel.upper()

# 2. Set up a specific stream handler if required.
if arguments.console:

    # 2.a. Define `audiocd_console` as second stream handler for `Applications.Database.AudioCD`.
    with suppress(KeyError):
        config["loggers"]["Applications.Database.AudioCD"]["handlers"] = ["file", "audiocd_console"]

    # 2.b. Set up `audiocd_console` for `Applications.Database.AudioCD`.
    config["handlers"]["audiocd_console"] = {}
    config["handlers"]["audiocd_console"]["class"] = "logging.StreamHandler"
    config["handlers"]["audiocd_console"]["formatter"] = "default"
    config["handlers"]["audiocd_console"]["filters"] = ["audiocd"]
    config["handlers"]["audiocd_console"]["level"] = "INFO"
    config["handlers"]["audiocd_console"]["stream"] = r"ext://sys.stdout"

    # 2.c. Define `audiocd` filter.
    config["filters"]["audiocd"] = {}
    config["filters"]["audiocd"]["class"] = "logging.Filter"
    config["filters"]["audiocd"]["name"] = "Applications.Database.AudioCD"

# 4. Declare logging configuration.
logging.config.dictConfig(config)

# ===============
# Main algorithm.
# ===============
logs = list(selectlogs_fromkeywords(db=arguments.db))
if logs:
    sys.exit(0)
sys.exit(100)
