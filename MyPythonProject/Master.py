# -*- coding: utf-8 -*-
import argparse
import sqlite3
import json
import os
from datetime import datetime
from pprint import PrettyPrinter
from Applications.shared import dateformat, TEMPLATE2, UTC, LOCAL, WRITE

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========
def validdb(arg):
    if not os.path.exists(arg):
        raise argparse.ArgumentTypeError('"{0}" doesn\'t exist.'.format(arg))
    return arg


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--db", dest="database", default=os.path.join(os.path.expandvars("%_COMPUTING%"), "database.db"), type=validdb)
parser.add_argument("-t", "--table", default="sqlite_master")
parser.add_argument("-p", "--print", action="store_true")


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

#  1. Ouverture de la connexion à la base de données.
conn = sqlite3.connect(arguments.database)

#  2. Restitution des tables.
r = [dateformat(UTC.localize(datetime.utcnow()).astimezone(LOCAL), TEMPLATE2), list(conn.execute("SELECT * FROM {table} ORDER BY rowid".format(table=arguments.table)))]
if arguments.print:
    pp.pprint(r)
with open(OUTFILE, mode=WRITE) as fp:
    json.dump(r, fp, indent=4, ensure_ascii=False)

#  3. Fermeture de la connexion à la base de données.
conn.close()
