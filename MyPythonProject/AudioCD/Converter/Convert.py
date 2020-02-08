# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import locale
import logging.config
import os
from contextlib import suppress
from operator import itemgetter
from pathlib import PurePath
from typing import List, Mapping, Tuple

import yaml

from Applications import patterns
from Applications.shared import TemplatingEnvironment, UTF16, WRITE, mainscript, pprint_mapping

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

locale.setlocale(locale.LC_ALL, "")

# ==========
# Constants.
# ==========
_MAPPING = {True: "debug", False: "info"}  # type: Mapping[bool, str]
# _REGEX = re.compile(DFTPATTERN, re.IGNORECASE)  # type: # Any
_THATFILE = PurePath(os.path.abspath(__file__))  # type: PurePath

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("tags")
parser.add_argument("encoder", choices=["FDK", "LAME"])
parser.add_argument("profiles", nargs="+", help="decorating profile(s)")
parser.add_argument("--debug", action="store_true")
argument = parser.parse_args()

# ========
# Logging.
# ========
with open(os.fspath(_THATFILE.parents[2] / "Resources" / "logging.yml"), encoding="UTF_8") as fp:
    log_config = yaml.load(fp, Loader=yaml.FullLoader)
with suppress(KeyError):
    log_config["loggers"]["MyPythonProject"]["level"] = _MAPPING[argument.debug].upper()
logging.config.dictConfig(log_config)
logger = logging.getLogger("MyPythonProject.AudioCD.Converter.{0}".format(_THATFILE.stem))

# =========
# Template.
# =========
_template = TemplatingEnvironment(path=os.fspath(_THATFILE.parents[1] / "Templates"))

# ============
# Main script.
# ============
logger.debug(mainscript(os.fspath(_THATFILE)))

# Get audio tags from dBpoweramp Batch Converter.
tags = patterns.AudioTags.fromfile(argument.tags)

# Log input tags.
pairs = sorted(tags.items(), key=itemgetter(0))  # type: List[Tuple[str, str]]
if pairs:
    logger.debug("==========")
    logger.debug("INPUT Tags")
    logger.debug("==========")
    for key, value in pprint_mapping(*pairs):
        logger.debug("%s: %s", key, value)

# Process audio tags.
tags = patterns.DefaultTags(tags)
for profile in argument.profiles:
    if profile.lower() == "albumsort":
        tags = patterns.AlbumSort(tags, argument.encoder)
    elif profile.lower() == "encodedfromflac":
        tags = patterns.EncodedFromFLACFile(tags)
    elif profile.lower() == "encodedfromlegalflac":
        tags = patterns.EncodedFromLegalFLACFile(tags)
    elif profile.lower() == "encodedfromlegaldsd":
        tags = patterns.EncodedFromLegalDSDFile(tags)

# Log output tags.
pairs = sorted(tags.items(), key=itemgetter(0))
if pairs:
    logger.debug("===========")
    logger.debug("OUTPUT Tags")
    logger.debug("===========")
    for key, value in pprint_mapping(*pairs):
        logger.debug("%s: %s", key, value)

# Get back audio tags to dBpoweramp Batch Converter.
with open(argument.tags, mode=WRITE, encoding=UTF16) as fw:
    fw.write(_template.get_template("Tags").render(tags=dict(tags.items())))
