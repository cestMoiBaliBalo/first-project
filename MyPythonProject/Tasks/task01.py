# -*- coding: utf-8 -*-
import functools
import logging
import os
import sys
from logging.config import dictConfig
from subprocess import run

import yaml

from Applications.Database.Tables.shared import isdeltareached, update
from Applications.parsers import database_parser

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

#  1. --> Logging.
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Applications.Database.Tables")

#  2. --> Constant(s).
UID = 123456798

#  3. --> Initialization(s).
status, arguments = 0, database_parser.parse_args()
isdeltareached = functools.partial(isdeltareached, UID, "rundates")
update = functools.partial(update, UID, "rundates")

#  4. --> Main algorithm.
if isdeltareached(arguments.db):
    process = run(["C:\Program Files\Sandboxie\Start.exe", "/box:GNUCash", "delete_sandbox_silent"])
    logger.debug(process.returncode)
    if not process.returncode:
        status = update(arguments.db)

# 5. --> Exit algorithm.
logger.debug(status)
sys.exit(status)
