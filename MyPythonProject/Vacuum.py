# -*- coding: utf-8 -*-
import sqlite3

from Applications.parsers import database_parser

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# =================
# Arguments parser.
# =================
arguments = database_parser.parse_args()

# ===============
# Main algorithm.
# ===============
conn = sqlite3.connect(arguments.db)
conn.execute("VACUUM")
conn.close()
