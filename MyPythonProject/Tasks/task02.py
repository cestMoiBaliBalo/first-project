# -*- coding: utf-8 -*-
from Applications.Database.Tables.shared import isdeltareached, update
from Applications.parsers import dbparser
from Applications.shared import zipfiles
from logging.config import dictConfig
import functools
import logging
import yaml
import sys
import os

__author__ = 'Xavier ROSSET'


#  1. --> Define argument to force ZIP file creation.
dbparser.add_argument("-f", "--forced", action="store_true")

#  2. --> Logging.
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Applications.shared.zipfiles")

#  3. --> Constant(s).
UID = 123456799

#  4. --> Initialization(s).
status, arguments = 0, dbparser.parse_args()
zipfiles = functools.partial(zipfiles, r"F:\passwords.7z", r"C:\Users\Xavier\Documents\Database.kdbx", r"Y:\Database.key")
isdeltareached = functools.partial(isdeltareached, UID, "rundates")
update = functools.partial(update, UID, "rundates")

#  5. --> Main algorithm.
if isdeltareached(arguments.database) or arguments.forced:
    try:
        zipfiles()
    except OSError as err:
        logger.exception(err)
    else:
        if not arguments.forced:
            status = update(arguments.database)

#  6. --> Exit algorithm.
logger.info(status)
sys.exit(status)
