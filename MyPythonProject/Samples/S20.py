# -*- coding: utf-8 -*-
import logging.config
import os

import yaml

from Applications.Database.AudioCD.shared import select

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))
logger = logging.getLogger("Applications.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

for record in select():
    logger.debug(record.rowid)
