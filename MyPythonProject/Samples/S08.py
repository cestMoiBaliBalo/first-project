# -*- coding: utf-8 -*-
import os
import yaml
import logging
import sqlite3
import datetime
from logging.config import dictConfig
from Applications.shared import dateformat, TEMPLATE1, TEMPLATE2, TEMPLATE3, UTC, LOCAL, DATABASE

__author__ = 'Xavier ROSSET'


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Default.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))


# ===============
# Main algorithm.
# ===============
c = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
c.row_factory = sqlite3.Row
with c:
    c.execute("DROP TABLE IF EXISTS mytable")
    c.execute("CREATE TABLE IF NOT EXISTS mytable (id INTEGER PRIMARY KEY ASC AUTOINCREMENT, ts TIMESTAMP NOT NULL)")
    c.execute("INSERT INTO mytable (ts) VALUES (?)", (datetime.datetime.utcnow(),))
    for row in c.execute("SELECT id, ts FROM mytable ORDER BY id"):
        logger.debug("# ----- #")
        logger.debug(row["id"])
        if isinstance(row["ts"], datetime.datetime):
            logger.debug(dateformat(UTC.localize(row["ts"]), TEMPLATE1))
            logger.debug(dateformat(UTC.localize(row["ts"]).astimezone(LOCAL), TEMPLATE1))
            logger.debug(dateformat(UTC.localize(row["ts"]).astimezone(LOCAL), TEMPLATE2))
            logger.debug(dateformat(UTC.localize(row["ts"]).astimezone(LOCAL), TEMPLATE3))
