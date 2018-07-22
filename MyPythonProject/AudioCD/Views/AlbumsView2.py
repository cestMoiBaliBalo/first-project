# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""
Log digital albums.
"""
import argparse
import logging.config
import os
import sys
from contextlib import suppress
from subprocess import run

import yaml

from Applications.Tables.Albums.shared import getalbumheader
from Applications.parsers import database_parser
from Applications.shared import DATABASE, UTF8

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ==========
# Constants.
# ==========
LOGGERS = ["Applications.Tables.Albums", "MyPythonProject"]
MAPPING = {True: "debug", False: "info"}

# =======
# Parser.
# =======
parser = argparse.ArgumentParser(parents=[database_parser], argument_default=argparse.SUPPRESS)
parser.add_argument("--console", action="store_true")
parser.add_argument("--debug", action="store_true")

# ================
# Initializations.
# ================
arguments = vars(parser.parse_args())

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

    # 2. Set up a specific stream handler if required.
    for logger in LOGGERS:
        with suppress(KeyError):
            config["loggers"][logger]["handlers"] = ["file", "console"]
    with suppress(KeyError):
        config["handlers"]["console"]["level"] = MAPPING[arguments.get("debug", False)].upper()

    # 3. Set up a specific filter for logging from "Applications.Tables.Albums.shared.getalbumheader" only.
    localfilter = {"localfilter": {"class": "logging.Filter", "name": "Applications.Tables.Albums.shared.getalbumheader"}}
    config["filters"] = localfilter
    config["handlers"]["console"]["filters"] = ["localfilter"]

# 4. Dump logging configuration.
with open(os.path.join(os.path.expandvars("%TEMP%"), "logging.yml"), mode="w", encoding=UTF8) as stream:
    yaml.dump(config, stream, indent=4, default_flow_style=False)

# 5. Declare logging configuration.
logging.config.dictConfig(config)

# ===============
# Main algorithm.
# ===============
run("CLS", shell=True)
albums = list(getalbumheader(arguments.get("db", DATABASE)))
if albums:
    sys.exit(0)
sys.exit(100)
