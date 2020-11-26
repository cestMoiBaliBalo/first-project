# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import locale
import logging.config
import os
import sys
from contextlib import suppress
from operator import itemgetter
from pathlib import Path
from typing import List, Mapping, Tuple

import yaml

from Applications import patterns
from Applications.shared import TemplatingEnvironment, UTF16, UTF8, WRITE, mainscript, pprint_mapping

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")

# ==========
# Constants.
# ==========
_MAPPING = {True: "debug", False: "info"}  # type: Mapping[bool, str]

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
with open(_MYPARENT.parents[1] / "Resources" / "logging.yml", encoding=UTF8) as fp:
    log_config = yaml.load(fp, Loader=yaml.FullLoader)
with suppress(KeyError):
    log_config["loggers"]["MyPythonProject"]["level"] = _MAPPING[argument.debug].upper()
logging.config.dictConfig(log_config)
logger = logging.getLogger("MyPythonProject.AudioCD.Converter.{0}".format(_MYNAME))

# =========
# Template.
# =========
_template = TemplatingEnvironment(path=_MYPARENT.parent / "Templates")

# ============
# Main script.
# ============
logger.debug(mainscript(_ME))
logger.debug(argument.tags)

# Get audio tags from dBpoweramp Batch Converter.
try:
    tags = patterns.AudioMetadata.fromfile(argument.tags)
except FileNotFoundError:
    logger.debug("%s can't be found!", argument.tags)
    sys.exit(100)

# Log input tags.
pairs = sorted(tags, key=itemgetter(0))  # type: List[Tuple[str, str]]
if pairs:
    logger.debug("==========")
    logger.debug("INPUT Tags")
    logger.debug("==========")
    for key, value in pprint_mapping(*pairs):
        logger.debug("%s: %s", key, value)

# Process audio tags.
tags = patterns.RemoveData(tags)
for profile in argument.profiles:
    if profile.lower() == "albumsort":
        tags = patterns.AlbumSort(tags, argument.encoder)
    elif profile.lower() == "encodedfromflac":
        tags = patterns.EncodedFromFLACFile(tags)
    elif profile.lower() == "encodedfromhdtracksflac":
        tags = patterns.EncodedFromHDtracksFLACFile(tags)
    elif profile.lower() == "encodedfromnugsflac":
        tags = patterns.EncodedFromNugsFLACFile(tags)
    elif profile.lower() == "encodedfromnugsdsd":
        tags = patterns.EncodedFromNugsDSDFile(tags)

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
sys.exit(0)
