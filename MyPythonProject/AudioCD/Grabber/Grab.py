# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import locale
import logging.config
import os
import sys
from contextlib import suppress
from functools import partial
from operator import contains

import yaml

from Applications.AudioCD.shared import upsert_audiotags
from Applications.parsers import tags_grabber
from Applications.shared import get_dirname, itemgetter_, mainscript, not_

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# Define French environment.
locale.setlocale(locale.LC_ALL, ("french", "fr_FR.ISO8859-1"))

# Define local constants.
LOGGERS = ["Applications.AudioCD", "MyPythonProject"]

# Define functions aliases.
abspath, basename, join, expandvars, splitext = os.path.abspath, os.path.basename, os.path.join, os.path.expandvars, os.path.splitext

# Parse arguments.
arguments = vars(tags_grabber.parse_args())

# Get audio tags processing profile.
with open(join(get_dirname(os.path.abspath(__file__), level=2), "Resources", "profiles.yml"), encoding="UTF_8") as stream:
    tags_config = yaml.load(stream)[arguments.get("tags_processing", "default")]

# Configure logging.
if tags_config.get("debug", False):
    with open(join(get_dirname(os.path.abspath(__file__), level=3), "Resources", "logging.yml"), encoding="UTF_8") as stream:
        log_config = yaml.load(stream, Loader=yaml.FullLoader)

    for item in LOGGERS:
        with suppress(KeyError):
            log_config["loggers"][item]["level"] = "DEBUG"

    logging.config.dictConfig(log_config)
    logger = logging.getLogger("MyPythonProject.AudioCD.Grabber.{0}".format(splitext(basename(abspath(__file__)))[0]))
    logger.debug(mainscript(__file__))

# Process tags from input file.
value, _ = upsert_audiotags(arguments["profile"],
                            arguments["source"],
                            arguments["sequence"],
                            *arguments.get("decorators", ()),
                            **dict(filter(not_(itemgetter_()(partial(contains, ["debug", "console"]))), tags_config.items())))
sys.exit(value)
