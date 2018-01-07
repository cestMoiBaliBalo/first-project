# -*- coding: utf-8 -*-
import functools
import logging
import os
import sys
from logging.config import dictConfig

import yaml

from Applications.Database.Tables.shared import isdeltareached, update
from Applications.parsers import database_parser
from Applications.shared import zipfiles

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# 1. --> Define argument to force ZIP file creation.
database_parser.add_argument("-f", "--forced", action="store_true")

# 2. --> Logging.
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Applications.Database.Tables")

# 3. --> Constant(s).
UID = 123456799

# 4. --> Initialization(s).
status, arguments = 0, database_parser.parse_args()
zipfiles = functools.partial(zipfiles, r"F:\passwords.7z", r"C:\Users\Xavier\Documents\Database.kdbx", r"Y:\Database.key")
isdeltareached = functools.partial(isdeltareached, UID, "tasks")
update = functools.partial(update, UID, "tasks")

# 5. --> Main algorithm.
if isdeltareached(arguments.db) or arguments.forced:
    try:
        zipfiles()
    except OSError as err:
        logger.exception(err)
    else:
        if not arguments.forced:
            status = update(arguments.db)

# 6. --> Exit algorithm.
logger.info(status)
sys.exit(status)
