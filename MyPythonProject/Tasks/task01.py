# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import functools
import logging.config
import os
import sys
from subprocess import run

import yaml

from Applications.Database.Tables.shared import isdeltareached, update
from Applications.parsers import database_parser

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# 1. --> Logging.
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))
logger = logging.getLogger("Applications.Database.Tables")

# 2. --> Constant(s).
UID = 123456798

# 3. --> Initialization(s).
status, arguments = 0, database_parser.parse_args()
isdeltareached = functools.partial(isdeltareached, UID, "tasks", db=arguments.db)
update = functools.partial(update, UID, "tasks", db=arguments.db)

# 4. --> Main algorithm.
if isdeltareached():
    process = run([r"C:\Program Files\Sandboxie\Start.exe", r"/box:GNUCash", "delete_sandbox_silent"])
    logger.info(process.returncode)
    if not process.returncode:
        status = update()

# 5. --> Exit algorithm.
logger.info(status)
sys.exit(status)
