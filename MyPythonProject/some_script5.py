# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import logging.config
import os
import sqlite3
from Applications.Tables.shared import DatabaseConnection
from Applications.shared import DATABASE

import yaml

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))

with DatabaseConnection(DATABASE) as conn:
    conn.execute("UPDATE defaultalbums SET album=? WHERE album=?", ("Alive III", "Alive Iii"))
    print(conn.total_changes)
    conn.commit()
