# -*- coding: utf-8 -*-
"""
Log ripped audio CDs.
"""
import logging.config
import os
import sys

import yaml

from Applications.Database.AudioCD.shared import selectlogs
from Applications.parsers import database_parser
from Applications.shared import UTF8

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding=UTF8) as fp:
    logging.config.dictConfig(yaml.load(fp))
logger = logging.getLogger("Applications.Database.AudioCD")

# ================
# Initializations.
# ================
arguments = database_parser.parse_args()

# ===============
# Main algorithm.
# ===============
logs = list(selectlogs(db=arguments.db, logginglevel="info"))
if logs:
    sys.exit(0)
sys.exit(100)
