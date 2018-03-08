# -*- coding: utf-8 -*-
import argparse
import logging.config
import os
import sqlite3

import yaml

from Applications.parsers import database_parser

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))

parser = argparse.ArgumentParser(parents=[database_parser], argument_default=argparse.SUPPRESS)
arguments = parser.parse_args()

conn = sqlite3.connect(arguments.db, detect_types=sqlite3.PARSE_DECLTYPES)
with open(os.path.join(os.path.expandvars("%TEMP%"), "titi.txt"), mode="w", encoding="ISO-8859-1") as fw:
    for row in conn.execute("SELECT artistsort, origyear, year, album, rowid FROM rippinglog ORDER BY artistsort, albumsort"):
        fw.write("{0}     {1}     {2}     {3}|{4}\n".format(row[0], row[1], row[2], row[3], row[4]))
conn.close()
