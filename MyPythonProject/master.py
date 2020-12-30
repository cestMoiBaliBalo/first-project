# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import json
import os
import sqlite3
from datetime import datetime
from pprint import PrettyPrinter

from Applications.parsers import database_parser
from Applications.shared import LOCAL, TEMPLATE2, UTC, WRITE, format_date

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser(parents=[database_parser])
parser.add_argument("--table", default="sqlite_master")
parser.add_argument("--print", action="store_true")

# ==========
# Constants.
# ==========
OUTFILE = os.path.join(os.path.expandvars("%TEMP%"), "sqlite_master.json")

# ================
# Initializations.
# ================
pp, arguments = PrettyPrinter(indent=4, width=160), parser.parse_args()

# ===============
# Main algorithm.
# ===============

# 1. Ouverture de la connexion à la base de données.
conn = sqlite3.connect(arguments.db)

# 2. Restitution des tables.
r = [format_date(UTC.localize(datetime.utcnow()).astimezone(LOCAL), template=TEMPLATE2), list(conn.execute("SELECT * FROM {table} ORDER BY rowid".format(table=arguments.table)))]
if arguments.print:
    pp.pprint(r)
with open(OUTFILE, mode=WRITE) as fp:
    json.dump(r, fp, indent=4, ensure_ascii=False)

# 3. Fermeture de la connexion à la base de données.
conn.close()
