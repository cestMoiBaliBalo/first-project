# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import logging.config
import os
import sys
from contextlib import suppress
from typing import Optional, Tuple

import yaml

from Applications.AudioCD.shared import set_audiotags
from Applications.parsers import tags_grabber
from Applications.shared import get_dirname, mainscript

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# Local constants.
LOGGERS = ["Applications.AudioCD", "MyPythonProject"]
MAPPING = {True: "debug", False: "info"}

# Functions aliases.
abspath, basename, join, expandvars, splitext = os.path.abspath, os.path.basename, os.path.join, os.path.expandvars, os.path.splitext

# Parse arguments.
arguments = vars(tags_grabber.parse_args())

# Get arguments.

# ----- Debug mode.
arg_debug = arguments.get("debug", False)  # type: bool

# ----- Output database.
arg_database = arguments.get("db")  # type: Optional[str]

# ----- Decorators.
arg_decorators = arguments.get("decorators", ())  # type: Tuple[str, ...]

# ----- Store both input and output tags?
arg_store_tags = arguments.get("store_tags", False)  # type: bool

# ----- Store tags sample?
arg_test = arguments.get("test", False)  # type: bool

# Configure logging.
with open(join(get_dirname(os.path.abspath(__file__), level=3), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    config = yaml.load(fp)
for item in LOGGERS:
    with suppress(KeyError):
        config["loggers"][item]["level"] = MAPPING[arg_debug].upper()
logging.config.dictConfig(config)
logger = logging.getLogger("MyPythonProject.AudioCD.Grabber.{0}".format(splitext(basename(abspath(__file__)))[0]))

# Grab tags from input file.
logger.debug(mainscript(__file__))
sys.exit(set_audiotags(arguments["profile"],
                       arguments["source"],
                       *arg_decorators,
                       db=arg_database,
                       db_albums=arguments.get("albums", False),
                       db_bootlegs=arguments.get("bootlegs", False),
                       store_tags=arg_store_tags,
                       test=arg_test))
