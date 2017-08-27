# -*- coding: utf-8 -*-
import os
import yaml
import logging
from logging.config import dictConfig
from Applications.shared import filesinfolder
from Applications.parsers import zipfile

__author__ = "Xavier ROSSET"


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Default.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))


# ==========
# Arguments.
# ==========
arguments = zipfile.parse_args()


# ===============
# Main algorithm.
# ===============
for fil in filesinfolder(*arguments.extensions, folder=arguments.source):
    logger.debug(fil)
