# -*- coding: utf-8 -*-
import os
import sqlite3
from datetime import date, datetime
from string import Template
from typing import List, NamedTuple, Tuple, Union

from ..shared import DatabaseConnection, convert_tobooleanvalue
from ...shared import DATABASE

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# =============
# Named tuples.
# =============
Album = NamedTuple("Album", [("rowid", int),
                             ("albumid", str),
                             ("played", datetime),
                             ("played_year", int),
                             ("played_month", int),
                             ("played_year_month", int),
                             ("artistsort", str),
                             ("albumsort", str),
                             ("artist", str),
                             ("genre", str),
                             ("disc", int),
                             ("discs", int),
                             ("tracks", int),
                             ("bootleg", bool),
                             ("origyear", int),
                             ("year", int),
                             ("album", str),
                             ("label", str),
                             ("upc", str),
                             ("bootleg_date", date),
                             ("bootleg_city", str),
                             ("bootleg_country", str),
                             ("bootleg_tour", str),
                             ("cover", str)])

# ==========
# Constants.
# ==========
COVER = Template("albumart/$letter/$artistsort/$albumsort/iPod-Front.jpg")

# ==================
# SQLite3 converter.
# ==================
sqlite3.register_converter("boolean", convert_tobooleanvalue)


# ==================
# Private functions.
# ==================
def get_playeddiscs(db: str = DATABASE, **kwargs):
    for disc in _get_playeddiscs(db, **kwargs):
        yield disc


# ======================================================
# These interface mustn't be used from external scripts.
# ======================================================
def _get_playeddiscs(db: str, **kwargs):
    """

    :param db: database where `playeddiscs` table is stored.
    :param kwargs: additional arguments(s) to subset and/or to sort SQL statement results.
    :return:
    """

    #  1. Initializations.
    where, args = "", ()  # type: str, Tuple[Union[str, int], ...]

    #  2. SELECT clause.
    select: str = "SELECT " \
                  "rowid, " \
                  "albumid, " \
                  "played_date, " \
                  "played_year, " \
                  "played_month, " \
                  "played_year*100 + played_month AS played_year_month, " \
                  "artistsort, " \
                  "albumsort, " \
                  "artist, " \
                  "genre, " \
                  "discid, " \
                  "discs, " \
                  "tracks, " \
                  "is_bootleg, " \
                  "origyear, " \
                  "year, " \
                  "album, " \
                  "label, " \
                  "upc, " \
                  "bootleg_date, " \
                  "bootleg_city, " \
                  "bootleg_country, " \
                  "bootleg_tour " \
                  "FROM playeddiscs_vw "

    #  3. WHERE clause.

    # 3.a. Subset by `albumid`.
    albumid: List[str] = kwargs.get("albumid", [])
    if albumid:
        where = "{0}(".format(where)
        for item in albumid:
            where = "{0}albumid=? OR ".format(where)
            args += ("{0}".format(item),)
        where = "{0}) AND ".format(where[:-4])

    #  3.a. Subset by `artistsort`.
    artistsort: List[str] = kwargs.get("artistsort", [])
    if artistsort:
        where = "{0}(".format(where)
        for item in artistsort:
            where = "{0}lower(artistsort)=? OR ".format(where)
            args += ("%{0}%".format(item.lower()),)
        where = "{0}) AND ".format(where[:-4])

    # 3.b. Subset by `albumsort`.
    albumsort: List[str] = kwargs.get("albumsort", [])
    if albumsort:
        where = "{0}(".format(where)
        for item in albumsort:
            where = "{0}albumsort=? OR ".format(where)
            args += ("%{0}%".format(item),)
        where = "{0}) AND ".format(where[:-4])

    # 3.c. Subset by `genre`.
    genre: List[str] = kwargs.get("genre", [])
    if genre:
        where = "{0}(".format(where)
        for item in genre:
            where = "{0}lower(genre)=? OR ".format(where)
            args += (item.lower(),)
        where = "{0}) AND ".format(where[:-4])

    # 3.d. Subset by `played year`.
    playedyear: Union[Tuple[int], List[int]] = kwargs.get("playedyear", [])
    if playedyear:
        where = "{0}(".format(where)
        for item in playedyear:  # type: ignore
            where = "{0}cast(strftime('%Y', played) AS INTEGER)=? OR ".format(where)
            args += (item,)
        where = "{0}) AND ".format(where[:-4])

    # 3.e. Subset by `played month`.
    playedmonth: Union[Tuple[int], List[int]] = kwargs.get("playedmonth", [])
    if playedmonth:
        where = "{0}(".format(where)
        for item in playedmonth:  # type: ignore
            where = "{0}cast(strftime('%Y%m', played) AS INTEGER)=? OR ".format(where)
            args += (item,)
        where = "{0}) AND ".format(where[:-4])

    # 4. ORDER BY clause.
    # orderby: str = "ORDER BY {0}".format(", ".join(kwargs.get("orderby", ["rowid"])))

    #  5. Build SQL statement.
    sql = select  # type: str
    if where:
        sql = f"{select} WHERE {where[:-5]}"

    #  6. Run SQL statement.
    #     Callers are in charge of filtering fields depending on the returned albums quality (default or bootleg).
    #     Shared function main role consists only in returning all fields without applying any segmentation.
    rows = []
    with DatabaseConnection(db) as conn:
        for row in conn.execute(sql, args):
            cover = COVER.substitute(path=os.path.join(os.path.expandvars("%_MYDOCUMENTS%"), "Album Art"), letter=row["artistsort"][0], artistsort=row["artistsort"], albumsort=row["albumsort"])
            rows.append(Album._make((row["rowid"],
                                     row["albumid"],
                                     row["played_date"],
                                     row["played_year"],
                                     row["played_month"],
                                     row["played_year_month"],
                                     row["artistsort"],
                                     row["albumsort"],
                                     row["artist"],
                                     row["genre"],
                                     row["discid"],
                                     row["discs"],
                                     row["tracks"],
                                     row["is_bootleg"],
                                     row["origyear"],
                                     row["year"],
                                     row["album"],
                                     row["label"],
                                     row["upc"],
                                     row["bootleg_date"],
                                     row["bootleg_city"],
                                     row["bootleg_country"],
                                     row["bootleg_tour"],
                                     cover)))
    for row in rows:
        yield row
