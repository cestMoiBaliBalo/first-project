# -*- coding: utf-8 -*-
import argparse
import sqlite3
import logging.config
import os

import yaml

from Applications.parsers import database_parser

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))

parser = argparse.ArgumentParser(parents=[database_parser], argument_default=argparse.SUPPRESS)
parser.add_argument("key", choices=["artistsort", "artist", "origyear", "year", "genre"])
parser.add_argument("--artistsort")
parser.add_argument("--artist")
parser.add_argument("--year")
parser.add_argument("--genre")

arguments = parser.parse_args()

select, where, args = "SELECT DISTINCT {0} FROM rippinglog".format(arguments.key), "", ()

_artistsort = vars(arguments).get("artistsort", None)
_artist = vars(arguments).get("artist", None)
_year = vars(arguments).get("year", None)
_genre = vars(arguments).get("genre", None)

if _artistsort:
    where = "{0}lower(artistsort)=? AND ".format(where)
    args += (_artistsort.lower(),)
if _artist:
    where = "{0}lower(artist)=? AND ".format(where)
    args += (_artist.lower(),)
if _genre:
    where = "{0}lower(genre)=? AND ".format(where)
    args += (_genre.lower(),)
if _year:
    where = "{0}year=? AND ".format(where)
    args += (_year,)
if where:
    select = "{0} WHERE {1}".format(select, where[:-5])
select = "{0} ORDER BY {1}".format(select, arguments.key)
# print(select)
# print(args)

conn = sqlite3.connect(arguments.db, detect_types=sqlite3.PARSE_DECLTYPES)
with open(os.path.join(os.path.expandvars("%TEMP%"), "{0}.txt".format(arguments.key)), mode="w", encoding="ISO-8859-1") as fw:
    for row in conn.execute(select, args):
        fw.write("{0}\n".format(row[0]))
conn.close()
