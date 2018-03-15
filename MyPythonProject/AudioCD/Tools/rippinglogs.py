# -*- coding: utf-8 -*-
import argparse
import logging.config
import os
import sqlite3
import sys

import yaml

from Applications.parsers import database_parser
from Applications.shared import grouper, prettyprint

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser(parents=[database_parser])
parser.add_argument("--pagenumber", type=int, default=1)
parser.add_argument("--itemsperpage", type=int, default=30)

# ==========
# Arguments.
# ==========
arguments = parser.parse_args()

# ===============
# Main algorithm.
# ===============
pagenumber = arguments.pagenumber
itemsperpage = arguments.itemsperpage
if pagenumber == 0:
    pagenumber = 1

conn = sqlite3.connect(arguments.db)
conn.row_factory = sqlite3.Row
logs = [(row["artistsort"],
         str(row["origyear"]),
         str(row["year"]),
         row["album"],
         row["genre"],
         row["label"],
         row["upc"],
         str(row["rowid"])) for row in conn.execute("SELECT artistsort, origyear, year, album, genre, ifnull(label, '') AS label, upc, rowid FROM rippinglog ORDER BY artistsort, albumsort")]
conn.close()

# Group by `itemsperpage`.
logs = list(grouper(prettyprint(*logs)[1], itemsperpage))

# Get total pages.
totalpages = len(logs)
if pagenumber > totalpages:
    pagenumber = totalpages

# Write into plain text file.
with open(os.path.join(os.path.expandvars("%TEMP%"), "rippinglogs.tmp"), mode="w", encoding="ISO-8859-1") as fw:
    for item in logs[pagenumber - 1]:
        if item:
            fw.write("{t[0]}{t[1]}{t[2]}{t[3]}{t[4]}{t[5]}{t[6]}|{t[7]}\n".format(t=item))
sys.exit(totalpages)
