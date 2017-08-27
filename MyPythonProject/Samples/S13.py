# -*- coding: utf-8 -*-
import os
import yaml
import logging
import argparse
from logging.config import dictConfig
from Applications.AudioCD.shared import audiofilesinfolder

__author__ = 'Xavier ROSSET'


# ==========
# Arguments.
# ==========
parser = argparse.ArgumentParser()
parser.add_argument("folder")
arguments = parser.parse_args()


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Default.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))


# ===============
# Main algorithm.
# ===============
for fil, audioobj, tags in audiofilesinfolder(folder=arguments.folder):
    logger.debug(fil)
    for k, v in tags.items():
        logger.debug("{0}: {1}".format(k, v))
