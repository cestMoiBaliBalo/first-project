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
from collections import namedtuple

import yaml

from Applications.AudioCD.shared import getmetadata
from patterns import REGEX, RenameWithTitle, RightTrim

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))
logger = logging.getLogger("MyPythonProject.AudioCD.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("track")
parser.add_argument("profiles", nargs="+", help="decorating profile(s)")
argument = parser.parse_args()

# ================
# Initializations.
# ================
AudioFile = namedtuple("AudioFile", "name extension found tags")
errorlevel = 1

# ===============
# Main algorithm.
# ===============
match = REGEX.match(os.path.basename(argument.track))
logger.debug("Match     : %s", match)
if match:
    name, found, tags, _ = getmetadata(argument.track)
    name, extension = os.path.splitext(os.path.basename(name))
    audiofile = AudioFile._make([name, extension, found, tags])
    if found:
        for profile in argument.profiles:
            if profile == "renamewithtitle":
                audiofile = RenameWithTitle(audiofile)
            elif profile == "righttrim":
                audiofile = RightTrim(audiofile)
    try:
        os.rename(src=r"{0}".format(argument.track), dst=r"{0}{1}{2}".format(os.path.join(os.path.dirname(argument.track), match.group(1)), audiofile.name, audiofile.extension))
    except FileNotFoundError as err:
        logger.exception(err)
    else:
        logger.debug(argument.track)
        logger.debug("%s%s%s", os.path.join(os.path.dirname(argument.track), match.group(1)), audiofile.name, audiofile.extension)
        errorlevel = 0
logger.debug("Errorlevel: %s", errorlevel)
logger.debug("\t0: succeeded.".expandtabs(4))
logger.debug("\t1: failed.".expandtabs(4))
sys.exit(errorlevel)
