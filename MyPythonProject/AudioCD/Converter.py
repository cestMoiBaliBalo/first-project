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
from Applications.AudioCD.shared import DFTPATTERN, filcontents
from Applications.shared import TemplatingEnvironment, UTF16, WRITE, left_justify, mainscript

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
logger = logging.getLogger("MyPythonProject.AudioCD.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

# =========
# Template.
# =========
_template = TemplatingEnvironment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "AudioCD", "Templates"))).environment.get_template("Tags")

# ================
# Initializations.
# ================
_tags = {}

# ============
# Main script.
# ============
logger.debug(mainscript(__file__))

# Get audio tags from dBpoweramp Batch Converter.
with open(argument.tags, encoding=UTF16) as fr:
    for line in filcontents(fr):
        _match = _REGEX.match(line)
        if _match:
            _tags[_match.group(1).rstrip().lower()] = _match.group(2)

# Log input tags.
pairs = sorted(_tags.items(), key=itemgetter(0))
if pairs:
    logger.debug("")
    logger.debug("==========")
    logger.debug("INPUT Tags")
    logger.debug("==========")
    keys, values = list(zip(*pairs))
    for key, value in zip(*[list(left_justify(keys)), values]):
        logger.debug("%s: %s", key, value)

# Process audio tags.
tags = dict(_tags)
if _tags:
    tags = patterns.DefaultTags(patterns.AudioTags(**_tags))
    for profile in argument.profiles:
        if profile.lower() == "albumsort":
            tags = patterns.AlbumSort(tags, argument.encoder)
        elif profile.lower() == "encodedfromlegalflac":
            tags = patterns.EncodedFromLegalFLAC(tags)
        elif profile.lower() == "encodedfromlegaldsd":
            tags = patterns.EncodedFromLegalDSD(tags)

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
