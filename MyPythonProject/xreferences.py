# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import json
import logging.config
import os
import sqlite3
from contextlib import ExitStack, suppress
from operator import itemgetter

import yaml

from Applications.Tables.XReferences.shared import get_database_albums, get_drive_albums
from Applications.Tables.shared import convert_tobooleanvalue
from Applications.shared import get_dirname

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# -----
LOGGERS = ["Applications.Tables"]

# -----
with open(os.path.join(get_dirname(os.path.abspath(__file__), level=1), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    config = yaml.load(fp)
for item in LOGGERS:
    with suppress(KeyError):
        config["loggers"][item]["level"] = "INFO"
logging.config.dictConfig(config)

# -----
sqlite3.register_converter("boolean", convert_tobooleanvalue)

# -----
drive = sorted(sorted(sorted(sorted(set(get_drive_albums()), key=itemgetter(6)), key=itemgetter(7)), key=itemgetter(1)), key=itemgetter(0))
database = sorted(sorted(sorted(sorted(set(get_database_albums()), key=itemgetter(6)), key=itemgetter(7)), key=itemgetter(1)), key=itemgetter(0))

# -----
with ExitStack() as stack:
    f1 = stack.enter_context(open(os.path.join(os.path.expandvars("%TEMP%"), "drive.json"), mode="w", encoding="UTF_8"))
    f2 = stack.enter_context(open(os.path.join(os.path.expandvars("%TEMP%"), "database.json"), mode="w", encoding="UTF_8"))
    json.dump(drive, f1, ensure_ascii=False, indent=4)
    json.dump(database, f2, ensure_ascii=False, indent=4)
