# -*- coding: utf-8 -*-
import logging
import sqlite3
from collections import Counter
from contextlib import ExitStack, suppress
from datetime import date, datetime
from itertools import compress
from typing import Iterable, List, NamedTuple, Tuple, Union

from ..shared import DatabaseConnection, close_database, convert_tobooleanvalue
from ...shared import DATABASE, LOCAL, UTC, format_date, stringify

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# =============
# Named tuples.
# =============
Album = NamedTuple("Album", [("rowid", int),
                             ("albumid", str),
                             ("ripped", datetime),
                             ("year_ripped", int),
                             ("month_ripped", int),
                             ("artistsort", str),
                             ("albumsort", str),
                             ("artist", str),
                             ("genre", str),
                             ("application", str),
                             ("disc", int),
                             ("tracks", int),
                             ("created_date", datetime),
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
                             ("modified_date", datetime)])

# ==========
# Constants.
# ==========
FIELDS_SELECTORS = \
    {
        False: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
        True: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1]
    }
HEADERS = \
    {
        False: ["Record", "AlbumID", "Ripped", "Artistsort", "Albumsort", "Artist", "Genre", "Application", "Disc", "Tracks", "Created", "Bootleg", "Origyear", "Year", "Album", "Label", "UPC", "Modified"],
        True: ["Record", "AlbumID", "Ripped", "Artistsort", "Albumsort", "Artist", "Genre", "Application", "Disc", "Tracks", "Created", "Bootleg", "Album", "BootlegDate", "BootlegCity", "BootlegCountry",
               "BootlegTour", "Modified"]
    }

# ==================
# SQLite3 converter.
# ==================
sqlite3.register_converter("boolean", convert_tobooleanvalue)


# ==========
# Functions.
# ==========
def log_record(iterable):
    """

    :param iterable:
    :return:
    """
    in_logger = logging.getLogger("{0}.log_record".format(__name__))

    # 1. Initializations.
    isbootleg = iterable[13]

    # 2. Convert album attributes into strings attributes.
    attributes = list(map(stringify, iterable))

    # 3. Configurer les entêtes adéquats en fonction des données présentes.
    #    Eliminer les entêtes des données à `None`.
    headers = list(compress(HEADERS[isbootleg], map(lambda i: i is not None, attributes)))

    # 4. Log record.
    length = max(len(item) for item in headers)
    in_logger.debug("================")
    in_logger.debug("Selected record.")
    in_logger.debug("================")
    for key, value in zip(headers, filter(None, attributes)):
        key = "{0:<{1}}".format(key, length)
        in_logger.debug("%s: %s", key, value)


# ========================================
# Main interfaces for working with tables.
# ========================================
def delete_rippeddiscs(*uid: int, db: str = DATABASE) -> int:
    """

    :param uid:
    :param db:
    :return:
    """
    logger = logging.getLogger("{0}.delete_rippeddiscs".format(__name__))
    with ExitStack() as stack:
        conn = stack.enter_context(DatabaseConnection(db))
        stack.enter_context(conn)
        try:
            conn.executemany("DELETE FROM rippeddiscs WHERE rowid=?", [(rowid,) for rowid in uid])
        except sqlite3.IntegrityError as err:
            logger.exception(err)
            stack.pop_all()
            stack.callback(close_database, conn)
        finally:
            changes = conn.total_changes  # type: int
    logger.debug("%s records removed.", changes)
    return changes


def get_rippeddiscs(db: str = DATABASE, **kwargs):
    for disc in _get_rippeddiscs(db, **kwargs):
        yield disc


def get_rippeddiscs_uid(db: str = DATABASE, **kwargs) -> Iterable[Tuple[int, str, str, str, int, int, str, str]]:
    for uid, artistsort, albumsort, genre, disc, tracks, ripped in ((row.rowid, row.artistsort, row.albumsort, row.genre, row.disc, row.tracks, row.ripped) for row in _get_rippeddiscs(db, **kwargs)):
        yield uid, artistsort, albumsort, genre, disc, tracks, format_date(UTC.localize(ripped).astimezone(LOCAL), template="%Y"), format_date(UTC.localize(ripped).astimezone(LOCAL),
                                                                                                                                               template="%d/%m/%Y %H:%M:%S %Z (UTC%z)")


def get_total_rippeddiscs(db: str = DATABASE) -> int:
    count: int = 0
    with DatabaseConnection(db) as conn:
        curs = conn.execute("SELECT count(*) FROM rippeddiscs")
        with suppress(TypeError):
            (count,) = curs.fetchone()
    return count


def get_rippeddiscs_from_month(*month: int, db: str = DATABASE):
    """

    :param month:
    :param db:
    :return:
    """
    for row in _get_rippeddiscs(db, rippedmonth=month):
        yield row


def get_rippeddiscs_from_year(*year: int, db: str = DATABASE):
    """

    :param year:
    :param db:
    :return:
    """
    for row in _get_rippeddiscs(db, rippedyear=year):
        yield row


def aggregate_rippeddiscs_by_month(db: str = DATABASE) -> Iterable[Tuple[str, int]]:
    c = Counter(format_date(UTC.localize(row.ripped).astimezone(LOCAL), template="$Y$m") for row in _get_rippeddiscs(db))
    for k, v in c.items():
        yield k, v


def aggregate_rippeddiscs_by_year(db: str = DATABASE) -> Iterable[Tuple[str, int]]:
    c = Counter(format_date(UTC.localize(row.ripped).astimezone(LOCAL), template="$Y") for row in _get_rippeddiscs(db))
    for k, v in c.items():
        yield k, v


def aggregate_rippeddiscs_by_artistsort(db: str = DATABASE) -> Iterable[Tuple[str, int]]:
    c = Counter(row.artistsort for row in _get_rippeddiscs(db))
    for k, v in c.items():
        yield k, v


def aggregate_rippeddiscs_by_genre(db: str = DATABASE) -> Iterable[Tuple[str, int]]:
    c = Counter(row.genre for row in _get_rippeddiscs(db))
    for k, v in c.items():
        yield k, v


# =======================================================
# These interfaces mustn't be used from external scripts.
# =======================================================
def _get_rippeddiscs(db: str, **kwargs):
    """

    :param db: database where `rippeddiscs` table is stored.
    :param kwargs: additional arguments(s) to subset and/or to sort SQL statement results.
    :return:
    """
    in_logger = logging.getLogger("{0}._get_rippeddiscs".format(__name__))

    #  1. Initializations.
    where, args = "", ()  # type: str, Tuple[Union[str, int], ...]

    #  2. SELECT clause.
    select: str = "SELECT " \
                  "rowid, " \
                  "albumid, " \
                  "ripped_date, " \
                  "ripped_year, " \
                  "ripped_month, " \
                  "artistsort, " \
                  "albumsort, " \
                  "artist, " \
                  "genre, " \
                  "application, " \
                  "discid, " \
                  "tracks, " \
                  "created_date, " \
                  "is_bootleg, " \
                  "origyear, " \
                  "year, " \
                  "album, " \
                  "label, " \
                  "upc, " \
                  "bootleg_date, " \
                  "bootleg_city, " \
                  "bootleg_country, " \
                  "bootleg_tour, " \
                  "modified_date " \
                  "FROM rippeddiscs_vw "

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

    # 3.d. Subset by `ripped year`.
    rippedyear: Union[Tuple[int], List[int]] = kwargs.get("rippedyear", [])
    if rippedyear:
        where = "{0}(".format(where)
        for item in rippedyear:  # type: ignore
            where = "{0}cast(strftime('%Y', ripped) AS INTEGER)=? OR ".format(where)
            args += (item,)
        where = "{0}) AND ".format(where[:-4])

    # 3.e. Subset by `ripped month`.
    rippedmonth: Union[Tuple[int], List[int]] = kwargs.get("rippedmonth", [])
    if rippedmonth:
        where = "{0}(".format(where)
        for item in rippedmonth:  # type: ignore
            where = "{0}cast(strftime('%Y%m', ripped) AS INTEGER)=? OR ".format(where)
            args += (item,)
        where = "{0}) AND ".format(where[:-4])

    # 4. ORDER BY clause.
    # orderby: str = "ORDER BY {0}".format(", ".join(kwargs.get("orderby", ["rowid"])))

    #  5. Build SQL statement.
    sql = select  # type: str
    if where:
        sql = f"{select} WHERE {where[:-5]}"
    in_logger.debug(sql)
    in_logger.debug(args)

    #  6. Run SQL statement.
    #     Callers are in charge of filtering fields depending on the returned albums quality (default or bootleg).
    #     Shared function main role consists only in returning all fields without applying any segmentation.
    rows = []
    with DatabaseConnection(db) as conn:
        for row in conn.execute(sql, args):
            # is_bootleg = row["is_bootleg"]
            # row = list(compress(row, FIELDS_SELECTORS[is_bootleg]))
            # if not is_bootleg:
                # rows.append(DefaultAlbum._make(row))
            # else:
                # rows.append(BootlegAlbum._make(row))  # type: ignore
            rows.append(Album._make(row))
            log_record(row)
    for row in rows:
        yield row
