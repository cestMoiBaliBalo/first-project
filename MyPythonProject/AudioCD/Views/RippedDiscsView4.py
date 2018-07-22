# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import logging.config
import os
import sqlite3
from contextlib import suppress
from operator import itemgetter
from subprocess import run

import yaml

from Applications.parsers import database_parser
from Applications.shared import DATABASE, UTF8

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ==========
# Constants.
# ==========
LOGGERS = ["MyPythonProject"]
MAPPING = {True: "debug", False: "info"}

# ================
# Local functions.
# ================
basename, join, expandvars, splitext = os.path.basename, os.path.join, os.path.expandvars, os.path.splitext

# =======
# Parser.
# =======
parser = argparse.ArgumentParser(parents=[database_parser], argument_default=argparse.SUPPRESS)
parser.set_defaults(console=True)
parser.set_defaults(debug=True)
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

    # 2. Set up a specific stream handler.
    for logger in LOGGERS:
        with suppress(KeyError):
            config["loggers"][logger]["handlers"] = ["file", "console"]
    with suppress(KeyError):
        config["handlers"]["console"]["level"] = MAPPING[arguments.get("debug", False)].upper()

    # 3. Set up a specific filter for logging from "MyPythonProject.AudioCD.Views" only.
    localfilter = {"localfilter": {"class": "logging.Filter", "name": "MyPythonProject.AudioCD.Views"}}
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
conn = sqlite3.connect(arguments.get("db", DATABASE))
conn.row_factory = sqlite3.Row
albums = sorted(
        [(row["month"], row["total"]) for row in conn.execute("SELECT a.month AS month, count(*) AS total FROM (SELECT strftime('%Y%m', utc_ripped) AS month FROM rippeddiscs_vw) a GROUP BY month")],
        key=itemgetter(0),
        reverse=True)
for month, total in albums:
    total = "{0:>2d}".format(total)
    logger.debug("%s: %s", month, total)
