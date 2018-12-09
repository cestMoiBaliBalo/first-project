# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import locale
import logging.config
import os
import re
from contextlib import suppress
from operator import itemgetter
from pathlib import PurePath

import yaml
from jinja2 import FileSystemLoader

from Applications import patterns
from Applications.AudioCD.shared import DFTPATTERN
from Applications.shared import TemplatingEnvironment, UTF16, WRITE, left_justify, mainscript

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

locale.setlocale(locale.LC_ALL, ("french", "fr_FR.ISO8859-1"))

# ==========
# Constants.
# ==========
_THATFILE = PurePath(os.path.abspath(__file__))

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("tags")
parser.add_argument("encoder", choices=["FDK", "LAME"])
parser.add_argument("profiles", nargs="+", help="decorating profile(s)")
parser.add_argument("--debug", action="store_true")
argument = parser.parse_args()

# ==========
# Constants.
# ==========
_MAPPING = {True: "debug", False: "info"}
_REGEX = re.compile(DFTPATTERN, re.IGNORECASE)

# ========
# Logging.
# ========
with open(str(PurePath(_THATFILE.parent.parent.parent, "Resources", "logging.yml")), encoding="UTF_8") as fp:
    log_config = yaml.load(fp)
with suppress(KeyError):
    log_config["loggers"]["MyPythonProject"]["level"] = _MAPPING[argument.debug].upper()
logging.config.dictConfig(log_config)
logger = logging.getLogger("MyPythonProject.AudioCD.Converter.{0}".format(os.path.splitext(os.path.basename(str(_THATFILE)))[0]))

# =========
# Template.
# =========
_template = TemplatingEnvironment(loader=FileSystemLoader(str(PurePath(_THATFILE.parent.parent, "Templates")))).environment.get_template("Tags")

# ============
# Main script.
# ============
logger.debug(mainscript(str(_THATFILE)))

# Get audio tags from dBpoweramp Batch Converter.
tags = patterns.AudioTags.fromfile(argument.tags)

# Log input tags.
pairs = sorted(tags.items(), key=itemgetter(0))
if pairs:
    logger.debug("==========")
    logger.debug("INPUT Tags")
    logger.debug("==========")
    keys, values = list(zip(*pairs))
    for key, value in zip(*[list(left_justify(keys)), values]):
        logger.debug("%s: %s", key, value)

# Process audio tags.
tags = patterns.DefaultTags(tags)
for profile in argument.profiles:
    if profile.lower() == "albumsort":
        tags = patterns.AlbumSort(tags, argument.encoder)
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
    keys, values = list(zip(*pairs))
    for key, value in zip(*[list(left_justify(keys)), values]):
        logger.debug("%s: %s", key, value)

# Get back audio tags to dBpoweramp Batch Converter.
with open(argument.tags, mode=WRITE, encoding=UTF16) as fw:
    fw.write(_template.render(tags=dict(tags.items())))
