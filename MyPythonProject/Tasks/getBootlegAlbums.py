# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import os
import sqlite3
from datetime import date
from itertools import compress
from pathlib import Path
from typing import Any, NamedTuple

import pandas  # type: ignore

from Applications.Tables.shared import DatabaseConnection, convert_tobooleanvalue
from Applications.parsers import database_parser
from Applications.shared import UTF8

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent
_MYANCESTOR = _MYPARENT.parents[1]

sqlite3.register_converter("boolean", convert_tobooleanvalue)

SELECTORS = [0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]
TRACK = NamedTuple("BootlegTrack", [("rowid", int),
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
                                    ("repository", str)])

# ================
# Parse arguments.
# ================
arguments = database_parser.parse_args()

# ============
# Main script.
# ============
with DatabaseConnection(db=arguments.db) as conn:
    collection = [TRACK(*row) for row in conn.execute("SELECT * FROM bootlegalbums_vw")]  # type: Any
collection = [tuple(compress(item, SELECTORS)) for item in collection]
collection = dict(zip(compress(TRACK._fields, SELECTORS), zip(*collection)))
df = pandas.DataFrame(collection)
df.index.name = "Record ID"
df.to_csv(_MYANCESTOR / "bootlegalbums.csv", encoding=UTF8, sep="|")
