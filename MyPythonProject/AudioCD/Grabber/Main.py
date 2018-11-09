# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import logging.config
import os
import sys
from contextlib import suppress

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

# Configure logging.
with open(join(get_dirname(os.path.abspath(__file__), level=3), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    config = yaml.load(fp)
for item in LOGGERS:
    with suppress(KeyError):
        config["loggers"][item]["level"] = MAPPING[arguments.get("debug", False)].upper()
logging.config.dictConfig(config)
logger = logging.getLogger("MyPythonProject.AudioCD.Grabber.{0}".format(splitext(basename(abspath(__file__)))[0]))

# Grab tags from input file.
logger.debug(mainscript(__file__))
sys.exit(set_audiotags(arguments["profile"],
                       arguments["source"],
                       *arguments.get("decorators", ()),
                       db=arguments.get("db"),
                       db_albums=arguments.get("albums", False),
                       db_bootlegs=arguments.get("bootlegs", False),
                       store_tags=arguments.get("store_tags", False),
                       drive_tags=arguments.get("drive_tags"),
                       test=arguments.get("test", False)))
