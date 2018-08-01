# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""
Log ripped audio CDs.
"""
import argparse
import logging.config
import os
from contextlib import suppress
from subprocess import run

import yaml

from Applications.Tables.RippedDiscs.shared import selectlogs_fromkeywords
from Applications.parsers import database_parser
from Applications.shared import UTF8

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ==========
# Constants.
# ==========
LOGGERS = ["Applications.Tables.RippedDiscs", "MyPythonProject"]
MAPPING = {True: "debug", False: "info"}

# =======
# Parser.
# =======
parser = argparse.ArgumentParser(parents=[database_parser], argument_default=argparse.SUPPRESS)
parser.add_argument("--console", action="store_true")
parser.add_argument("--debug", action="store_true")

# ================
# Parse arguments.
# ================
arguments = vars(parser.parse_args())

# ================
# Local functions.
# ================
basename, join, expandvars, splitext = os.path.basename, os.path.join, os.path.expandvars, os.path.splitext

# ========
# Logging.
# ========

# 1. Load logging configuration and adapt logger(s) level(s).
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding=UTF8) as fp:
    config = yaml.load(fp)
for logger in LOGGERS:
    with suppress(KeyError):
        config["loggers"][logger]["level"] = MAPPING[arguments.get("debug", False)].upper()

if arguments.get("console", False):

    # 2. Set up a specific stream handler.
    for logger in LOGGERS:
        with suppress(KeyError):
            config["loggers"][logger]["handlers"] = ["file", "console"]
    with suppress(KeyError):
        config["handlers"]["console"]["level"] = MAPPING[arguments.get("debug", False)].upper()

    # 3. Set up a specific filter for logging from "Applications.Tables.RippedDiscs" only.
    localfilter = {"localfilter": {"class": "logging.Filter", "name": "Applications.Tables.RippedDiscs"}}
    config["filters"] = localfilter
    config["handlers"]["console"]["filters"] = ["localfilter"]

# 4. Dump logging configuration.
with open(os.path.join(os.path.expandvars("%TEMP%"), "logging.yml"), mode="w", encoding=UTF8) as stream:
    yaml.dump(config, stream, indent=4, default_flow_style=False)

# 5. Declare logging configuration.
logging.config.dictConfig(config)

# 6. Declare logger.
logger = logging.getLogger("MyPythonProject.AudioCD.Views.{0}".format(splitext(basename(__file__))[0]))

# ===============
# Main algorithm.
# ===============
run("CLS", shell=True)
for log in selectlogs_fromkeywords(db=arguments["db"]):
    logger.debug("Album.")
    logger.debug("\t%s".expandtabs(3), log.artistsort)
    logger.debug("\t%s".expandtabs(3), log.albumsort)
