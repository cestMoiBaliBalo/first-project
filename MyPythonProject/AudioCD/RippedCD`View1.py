# -*- coding: utf-8 -*-
"""
Log ripped audio CDs list.
"""
from Applications.Database.AudioCD.shared import select
from Applications.shared import validdb, UTF8
from logging.config import dictConfig
import argparse
import logging
import yaml
import os

__author__ = 'Xavier ROSSET'


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding=UTF8) as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Applications.AudioCD.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("database", nargs="?", default=os.path.join(os.path.expandvars("%_COMPUTING%"), "database.db"), type=validdb)


# ================
# Initializations.
# ================
arguments = parser.parse_args()


# ===============
# Main algorithm.
# ===============
for row in select(db=arguments.database):
    logger.info(row)
