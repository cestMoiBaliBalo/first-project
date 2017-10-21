# -*- coding: utf-8 -*-
"""
Log ripped audio CDs list.
"""
import logging
import os
from logging.config import dictConfig

import yaml

from Applications.Database.AudioCD.shared import selectlogs
from Applications.parsers import database_parser
from Applications.shared import LOCAL, TEMPLATE4, UTF8, dateformat

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding=UTF8) as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Applications.AudioCD.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

# ================
# Initializations.
# ================
arguments = database_parser.parse_args()

# ===============
# Main algorithm.
# ===============
for row in selectlogs(db=arguments.db):
    logger.info("# {0:>2d} ========== #".format(row.id))
    logger.info("Artistsort : {0}".format(row.artistsort))
    logger.info("Albumsort  : {0}".format(row.albumsort))
    logger.info("Artist     : {0}".format(row.artist))
    logger.info("Year       : {0}".format(row.year))
    logger.info("Album      : {0}".format(row.album))
    logger.info("UPC        : {0}".format(row.upc))
    logger.info("Genre      : {0}".format(row.genre))
    logger.info("Application: {0}".format(row.application))
    logger.info("Ripped     : {0}".format(dateformat(LOCAL.localize(row.ripped), TEMPLATE4)))
