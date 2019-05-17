# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import locale
import logging.config
import os
import sys
from contextlib import suppress
from operator import contains

import yaml

from Applications.AudioCD.shared import upsert_audiotags
from Applications.parsers import tags_grabber
from Applications.shared import get_dirname, getitem_, mainscript, partial_

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# Function for setting additional keywords arguments.
@getitem_(index=0)
@partial_(["debug", "console"])
def set_kwargs(a, b):
    return not contains(a, b.lower())


# Define French environment.
locale.setlocale(locale.LC_ALL, ("french", "fr_FR.ISO8859-1"))

# Local constants.
LOGGERS = ["Applications.AudioCD", "MyPythonProject"]

# Functions aliases.
abspath, basename, join, expandvars, splitext = os.path.abspath, os.path.basename, os.path.join, os.path.expandvars, os.path.splitext

# Parse arguments.
arguments = vars(tags_grabber.parse_args())

# Get audio tags processing profile.
with open(join(get_dirname(os.path.abspath(__file__), level=2), "Resources", "profiles.yml"), encoding="UTF_8") as stream:
    tags_config = yaml.load(stream)[arguments.get("tags_processing", "no_tags_processing")]

# Configure logging.
if tags_config.get("debug", False):
    with open(join(get_dirname(os.path.abspath(__file__), level=3), "Resources", "logging.yml"), encoding="UTF_8") as stream:
        log_config = yaml.load(stream)

    for item in LOGGERS:
        with suppress(KeyError):
            log_config["loggers"][item]["level"] = "DEBUG"

    if tags_config.get("console", False):

        # Set up a specific stream handler.
        for item in LOGGERS:
            with suppress(KeyError):
                log_config["loggers"][item]["handlers"] = ["file", "console"]
        with suppress(KeyError):
            log_config["handlers"]["console"]["level"] = "DEBUG"

        # Set up a specific filter for logging from "Applications.AudioCD.shared" only.
        localfilter, audiocd_filter = {}, {"class": "logging.Filter", "name": "Applications.AudioCD.shared"}
        localfilter["localfilter"] = audiocd_filter
        log_config["filters"] = localfilter
        log_config["handlers"]["console"]["filters"] = ["localfilter"]

    logging.config.dictConfig(log_config)
    logger = logging.getLogger("MyPythonProject.AudioCD.Grabber.{0}".format(splitext(basename(abspath(__file__)))[0]))
    logger.debug(mainscript(__file__))

# Process tags from input file.
sys.exit(upsert_audiotags(arguments["profile"],
                          arguments["source"],
                          *arguments.get("decorators", ()),
                          **dict(filter(set_kwargs, tags_config.items()))))