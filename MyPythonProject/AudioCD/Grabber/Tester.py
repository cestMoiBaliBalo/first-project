# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import json
import logging.config
import os
from contextlib import ExitStack, suppress
from subprocess import run

import yaml

from Applications.Tables.Albums.shared import insertfromfile
from Applications.parsers import SetDatabase
from Applications.shared import DATABASE, UTF16, UTF8
from Main import get_tags

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# =================
# Global constants.
# =================
LOGGERS = ["Applications.AudioCD", "MyPythonProject"]
TXTTAGS = os.path.join(os.path.expandvars("%TEMP%"), "tags.txt")
JSONTAGS = os.path.join(os.path.expandvars("%TEMP%"), "tags.json")

# ================
# Parse arguments.
# ================
parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
group = parser.add_mutually_exclusive_group()
parser.set_defaults(console=True)
parser.set_defaults(debug=True)
parser.add_argument("source", help="UTF-8 encoded JSON tags file", type=argparse.FileType(encoding=UTF8))
parser.add_argument("profile", help="ripping profile")
parser.add_argument("decorators", nargs="*", help="decorating profile(s)")
group.add_argument("--albums", nargs="?", const=True, default=False, action=SetDatabase, help="prepare an UTF-8 encoded JSON file for inserting data into defaultalbums table")
group.add_argument("--bootlegs", nargs="?", const=True, default=False, action=SetDatabase, help="prepare an UTF-8 encoded JSON file for inserting data into bootlegalbums table")
parser.add_argument("--insert", action="store_true", help="insert data into database from an UTF-8 encoded JSON file")
parser.add_argument("--database", dest="db")
parser.add_argument("--store_tags", action="store_true")

# ==============
# Get arguments.
# ==============
arguments = vars(parser.parse_args())

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding=UTF8) as fp:
    config = yaml.load(fp)

# -----
if arguments.get("debug", False):
    for logger in LOGGERS:
        with suppress(KeyError):
            config["loggers"][logger]["level"] = "DEBUG"

# -----
if arguments.get("console", False):

    # Set up a specific stream handler.
    for logger in LOGGERS:
        with suppress(KeyError):
            config["loggers"][logger]["handlers"] = ["file", "console"]
    with suppress(KeyError):
        config["handlers"]["console"]["level"] = "DEBUG"

    # Set up a specific filter for logging from "Applications.AudioCD.shared" only.
    localfilter = {"class": "logging.Filter", "name": "Applications.AudioCD.shared"}
    config["filters"]["localfilter"] = localfilter
    config["handlers"]["console"]["filters"] = ["localfilter"]

# Dump logging configuration.
with open(os.path.join(os.path.expandvars("%TEMP%"), "logging.yml"), mode="w", encoding=UTF8) as stream:
    yaml.dump(config, stream, indent=2, default_flow_style=False)

# -----
logging.config.dictConfig(config)
logger = logging.getLogger("MyPythonProject.AudioCD.Grabber.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

# ================
# Initializations.
# ================
returns = []

# ============
# Main script.
# ============
run("CLS", shell=True)
tags = json.load(arguments.get("source"))
for item in tags:

    # ----- Create an UTF-16-LE encoded plain text file displaying tags as key/value pairs.
    with open(TXTTAGS, mode="w", encoding=UTF16) as fw:
        for k, v in item.items():
            fw.write("{0}={1}\n".format(k.lower(), v))

    # ----- Create an "AudioCDTags object" gathering together audio tags.
    #       Create an UTF-8 encoded JSON file for database insertions if required.
    with open(TXTTAGS, mode="r+", encoding=UTF16) as fr:
        returned = get_tags(arguments.get("profile"),
                            fr,
                            *arguments.get("decorators", ()),
                            db=arguments.get("db", DATABASE),
                            db_albums=arguments.get("albums", False),
                            db_bootlegs=arguments.get("bootlegs", False),
                            store_tags=arguments.get("store_tags", False))
        logger.debug(returned)
        returns.append(returned)

# ----- Insert tags into database if required.
if arguments.get("insert", False):
    if not any(returns):
        stack = ExitStack()
        try:
            fr = stack.enter_context(open(JSONTAGS, encoding=UTF8))
        except FileNotFoundError as exception:
            logger.exception(exception)
        else:
            with stack:
                logger.debug(insertfromfile(fr))