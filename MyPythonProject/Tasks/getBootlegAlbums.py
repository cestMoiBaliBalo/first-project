# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import csv
import os
import sqlite3
from datetime import date
from itertools import compress
from pathlib import Path
from typing import Any, List, NamedTuple

from Applications.Tables.shared import DatabaseConnection, convert_tobooleanvalue
from Applications.parsers import database_parser
from Applications.shared import CustomDialect, UTF8, WRITE

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent
_MYANCESTOR = _MYPARENT.parents[1]

sqlite3.register_converter("boolean", convert_tobooleanvalue)

MAPPING = {"bootleg": {"headers": ["Albumid",
                                   "Artistsort",
                                   "Albumsort",
                                   "DiscID",
                                   "Discs",
                                   "TrackID",
                                   "Tracks",
                                   "Title",
                                   "Album",
                                   "Genre",
                                   "Bonus",
                                   "Support",
                                   "Bootlegtrack_Year",
                                   "Bootlegtrack_Month",
                                   "Bootlegtrack_Day",
                                   "Bootlegtrack_Date",
                                   "Bootlegtrack_City",
                                   "Bootlegtrack_Tour",
                                   "Bootlegtrack_Country",
                                   "RepositoryID",
                                   "Repository"],
                       "fields": NamedTuple("Track", [("rowid", int),
                                                      ("albumid", str),
                                                      ("artistsort", str),
                                                      ("artist", str),
                                                      ("albumsort", str),
                                                      ("discid", int),
                                                      ("discs", int),
                                                      ("trackid", int),
                                                      ("tracks", int),
                                                      ("title", str),
                                                      ("album", str),
                                                      ("genre", str),
                                                      ("is_bootlegs", bool),
                                                      ("is_disc_live", bool),
                                                      ("is_disc_bonus", bool),
                                                      ("is_track_live", bool),
                                                      ("is_track_bonus", bool),
                                                      ("support", str),
                                                      ("bootlegtrack_year", int),
                                                      ("bootlegtrack_month", int),
                                                      ("bootlegtrack_day", int),
                                                      ("bootlegtrack_date", str),
                                                      ("bootlegtrack_city", str),
                                                      ("bootlegtrack_tour", str),
                                                      ("bootlegtrack_country", int),
                                                      ("created_date", date),
                                                      ("ripped_date", date),
                                                      ("ripped_year", int),
                                                      ("ripped_month", int),
                                                      ("played_date", date),
                                                      ("played_year", int),
                                                      ("played_month", int),
                                                      ("played", int),
                                                      ("bootlegalbum_countryid", int),
                                                      ("bootlegtrack_countryid", int),
                                                      ("repositoryid", int),
                                                      ("repository", str)]),
                       "file": "bootlegalbums.csv",
                       "selectors": [0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
                       "statement": "SELECT * FROM bootlegalbums_vw"}}

# ================
# Parse arguments.
# ================
parser = argparse.ArgumentParser(parents=[database_parser])
parser.add_argument("albums", choices=["bootleg"], nargs="+")
arguments = parser.parse_args()

# ============
# Main script.
# ============
for albums in arguments.albums:
    file = MAPPING[albums]["file"]  # type: str
    headers = MAPPING[albums]["headers"]  # type: List[str]
    selectors = MAPPING[albums]["selectors"]  # type: List[int]
    statement = MAPPING[albums]["statement"]  # type: str
    Row = MAPPING[albums]["fields"]
    with DatabaseConnection(db=arguments.db) as conn:
        collection = [Row(*row) for row in conn.execute(statement)]  # type: Any
        collection = [tuple(compress(item, selectors)) for item in collection]
        collection = [dict(zip(headers, item)) for item in collection]
        with open(_MYANCESTOR / file, mode=WRITE, encoding=UTF8, newline="") as stream:
            dict_writer = csv.DictWriter(stream, headers, dialect=CustomDialect())
            dict_writer.writeheader()
            dict_writer.writerows(collection)
