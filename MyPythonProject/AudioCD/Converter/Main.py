# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import logging.config
import os
import re
from contextlib import suppress
from operator import itemgetter

import yaml
from jinja2 import FileSystemLoader

import patterns
from Applications.AudioCD.shared import DFTPATTERN
from Applications.shared import TemplatingEnvironment, UTF16, WRITE, left_justify, mainscript, get_dirname

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("tags")
parser.add_argument("encoder", choices=["AAC", "LAME"])
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
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    config = yaml.load(fp)
with suppress(KeyError):
    config["loggers"]["MyPythonProject"]["level"] = _MAPPING[argument.debug].upper()
logging.config.dictConfig(config)
logger = logging.getLogger("MyPythonProject.AudioCD.Converter.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

# =========
# Template.
# =========
_template = TemplatingEnvironment(loader=FileSystemLoader(os.path.join(get_dirname(os.path.abspath(__file__), level=2), "Grabber"))).environment.get_template("Tags")

# ============
# Main script.
# ============
logger.debug(mainscript(__file__))

# Get audio tags from dBpoweramp Batch Converter.
tags = patterns.AudioTags.fromfile(argument.tags)

# Log input tags.
pairs = sorted(tags.items(), key=itemgetter(0))
if pairs:
    logger.debug("")
    logger.debug("==========")
    logger.debug("INPUT Tags")
    logger.debug("==========")
    keys, values = list(zip(*pairs))
    for key, value in zip(*[list(left_justify(keys)), values]):
        logger.debug("%s: %s", key, value)

# Process audio tags.
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
    logger.debug("")
    logger.debug("===========")
    logger.debug("OUTPUT Tags")
    logger.debug("===========")
    keys, values = list(zip(*pairs))
    for key, value in zip(*[list(left_justify(keys)), values]):
        logger.debug("%s: %s", key, value)

# Get back audio tags to dBpoweramp Batch Converter.
with open(argument.tags, mode=WRITE, encoding=UTF16) as fw:
    fw.write(_template.render(tags=tags))
