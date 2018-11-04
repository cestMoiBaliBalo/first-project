# -*- coding: utf-8 -*-
"""
Script used by dBpoweramp Audio CD ripping application.
1. For renaming an input audio file from the track title.
2. For renaming an input audio file from a subset taken from the file name.
"""
# pylint: disable=invalid-name
import argparse
import logging.config
import os
import sys
from contextlib import suppress
from typing import Any, Mapping, NamedTuple

import yaml

from Applications.AudioCD.shared import getmetadata
from patterns import REGEX, RenameWithTitle, RightTrim

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("track")
parser.add_argument("profiles", nargs="+", help="decorating profile(s)")
parser.add_argument("--debug", action="store_true")
argument = parser.parse_args()

# ==========
# Constants.
# ==========
MAPPING = {True: "debug", False: "info"}

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    config = yaml.load(fp)
for item in ["Applications.AudioCD", "MyPythonProject.AudioCD"]:
    with suppress(KeyError):
        config["loggers"][item]["level"] = MAPPING[argument.debug].upper()
logging.config.dictConfig(config)
logger = logging.getLogger("MyPythonProject.AudioCD.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

# ================
# Initializations.
# ================
AudioFile = NamedTuple("AudioFile", [("name", str), ("extension", str), ("found", bool), ("tags", Mapping[str, Any])])
errorlevel = 0

# ===============
# Main algorithm.
# ===============
match = REGEX.match(os.path.basename(argument.track))
if match:
    name, found, tags, _ = getmetadata(argument.track)
    if found:
        name, extension = os.path.splitext(os.path.basename(name))
        audiofile = AudioFile._make([name, extension, found, tags])
        for profile in argument.profiles:
            if profile.lower() == "renamewithtitle":
                audiofile = RenameWithTitle(audiofile)
            elif profile.lower() == "righttrim":
                audiofile = RightTrim(audiofile)
        if f"{match.group(1)}.{audiofile.name}" != name:
            source = argument.track  # type: str
            destination = r"{0}{1}{2}".format(os.path.join(os.path.dirname(argument.track), match.group(1)), audiofile.name, audiofile.extension)  # type: str
            try:
                os.rename(src=source, dst=destination)
            except FileNotFoundError as error:
                errorlevel = 1
                logger.exception(error)
            else:
                logger.debug("Rename audio file.")
                logger.debug('From: "%s"', source)
                logger.debug('To  : "%s"', destination)
sys.exit(errorlevel)
