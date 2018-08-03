# -*- coding: utf-8 -*-
import logging
import sqlite3
from collections import Counter, namedtuple
from datetime import date, datetime
from itertools import compress

from ..shared import convert_tobooleanvalue
from ...shared import DATABASE, LOCAL, TEMPLATE4, UTC, dateformat

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# =============
# Named tuples.
# =============
DefaultAlbum = namedtuple("DefaultAlbum", "rowid ripped artistsort albumsort artist genre application disc tracks utc_created bootleg origyear year album label upc utc_modified")
BootlegAlbum = namedtuple("BootlegAlbum", "rowid ripped artistsort albumsort artist genre application disc tracks utc_created bootleg bootleg_date bootleg_city bootleg_country bootleg_tour utc_modified")

# ==========
# Constants.
# ==========
FIELDS_SELECTORS = \
    {
        False: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
        True: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    }
NAMED_TUPLES = \
    {
        False: DefaultAlbum,
        True: BootlegAlbum
    }
HEADERS = \
    {
        False: ["Record", "Ripped", "Artistsort", "Albumsort", "Artist", "Genre", "Application", "Disc", "Tracks", "Created", "Bootleg", "Origyear", "Year", "Album", "Label", "UPC", "Modified"],
        True: ["Record", "Ripped", "Artistsort", "Albumsort", "Artist", "Genre", "Application", "Disc", "Tracks", "Created", "Bootleg", "BootlegDate", "BootlegCity", "BootlegCountry", "BootlegTour",
               "Modified"]
    }

# ==================
# SQLite3 converter.
# ==================
sqlite3.register_converter("boolean", convert_tobooleanvalue)


# ===========
# Decorators.
# ===========
# def validrippeddate(func):
# def wrapper(ts):
# try:
# result = func(ts)
# except ValueError:
# raise
# else:
# return result[0]

# return wrapper


# ==========
# Functions.
# ==========
def stringify(arg):
    if arg is None:
        return arg
    if isinstance(arg, int):
        return str(arg)
    if isinstance(arg, datetime):
        return dateformat(UTC.localize(arg).astimezone(LOCAL), TEMPLATE4)
    if isinstance(arg, date):
        return arg.strftime("%d/%m/%Y")
    return arg


def log_record(iterable):
    """

    :param iterable:
    :return:
    """
    in_logger = logging.getLogger("{0}.log_record".format(__name__))

    # 1. Initialiszations.
    isbootleg = iterable[10]

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


# =======================================
# Main functions for working with tables.
# =======================================
def deletelog(*uid, db=DATABASE):
    """

    :param uid:
    :param db:
    :return:
    """
    logger = logging.getLogger("{0}.deletelog".format(__name__))
    conn = sqlite3.connect(db)
    with conn:
        conn.executemany("DELETE FROM rippeddiscs WHERE rowid=?", [(rowid,) for rowid in uid])
    changes = conn.total_changes
    conn.close()
    logger.debug("%s records removed.", changes)
    if changes:
        for item in uid:
            logger.debug("Unique ID: {0:>4d}.".format(item))
    return changes


def get_totallogs(db=DATABASE):
    conn = sqlite3.connect(db)
    curs = conn.cursor()
    curs.execute("SELECT count(*) FROM rippeddiscs")
    count = curs.fetchone()[0]
    conn.close()
    return count


def selectlogs_fromuid(*uid, db=DATABASE):
    """

    :param uid:
    :param db: database where `rippinglog` is stored.
    :return:
    """
    for row in _selectlogs(db, uid=uid):
        yield row


def selectlogs_fromkeywords(db=DATABASE, **kwargs):
    """

    :param db:
    :param kwargs:
    :return:
    """
    for row in _selectlogs(db, **kwargs):
        yield row


def selectlogs_frommonth(*month, db=DATABASE):
    """

    :param month:
    :param db:
    :return:
    """
    for row in _selectlogs(db, rippedmonth=month):
        yield row


def selectlogs_fromyear(*year, db=DATABASE):
    """

    :param year:
    :param db:
    :return:
    """
    for row in _selectlogs(db, rippedyear=year):
        yield row


# def updatelog(*uid, db=DATABASE, **kwargs):
# """

# :param uid:
# :param db:
# :param kwargs:
# :return:
# """
# logger = logging.getLogger("{0}.updatelog".format(__name__))
# status, query, args = 0, "", []

# # 1. Map validation functions to table fields.
# functions = {"albumsort": valid_albumsort,
# "disc": valid_discnumber,
# "genre": valid_genre,
# "ripped": validrippeddate(valid_datetime),
# "origyear": valid_year,
# "tracks": valid_tracks,
# "upc": validproductcode,
# "year": valid_year}

# # 2. Validate input pairs.
# #    Change `selectors` values to accept/reject pairs:
# #       - "1": input value is accepted. Respective field will be updated.
# #       - "0": input value is rejected. Respective field won't be updated.
# pairs = dict(kwargs)
# keys = sorted(pairs.keys())
# selectors = [1] * len(pairs)
# for key in keys:
# error = False
# func = functions.get(key)
# if func:
# try:
# pairs[key] = func(pairs[key])
# except ValueError:
# error = True
# if error:
# selectors[keys.index(key)] = 0

# # 3. Build SQL statement.
# pairs = {k: v for k, v in pairs.items() if k in compress(keys, selectors)}
# for k, v in pairs.items():
# query = "{0}{1}=?, ".format(query, k)  # album=?, albumsort=?, "
# args.append(v)  # ["the album", "1.20170000.1"]

# # 4. Run SQL statement.
# #    Append modification date.
# if query:
# query = "{0}utc_modified=?, ".format(query)  # album=?, albumid=?, utc_modified=?, "
# args.append(UTC.localize(datetime.utcnow()).replace(tzinfo=None))  # ["the album", "1.20170000.1", datetime(2017, 10, 21, 16, 30, 45, tzinfo=timezone("utc"))]
# conn = sqlite3.connect(db)
# try:
# with conn:
# conn.executemany("UPDATE rippinglog SET {0} WHERE rowid=?".format(query[:-2]), [tuple(chain(args, (rowid,))) for rowid in uid])
# except (sqlite3.OperationalError, sqlite3.Error) as err:
# logger.exception(err)
# finally:
# status = conn.total_changes
# conn.close()
# logger.debug("{0:>3d} record(s) updated.".format(status))

# # 5. Return total changes.
# return status


def getartistsort(db=DATABASE):
    """

    :param db:
    :return:
    """
    c = Counter([row[1].artistsort for row in _selectlogs(db)])
    for k, v in c.items():
        yield k, v


def getgenre(db=DATABASE):
    """

    :param db:
    :return:
    """
    c = Counter([row[1].genre for row in _selectlogs(db)])
    for k, v in c.items():
        yield k, v


def get_rippeddiscsbymonth(db=DATABASE):
    c = Counter([dateformat(LOCAL.localize(row[1].ripped), "$Y$m") for row in _selectlogs(db)])
    for k, v in c.items():
        yield k, v


def get_rippeddiscsbyyear(db=DATABASE):
    c = Counter([dateformat(LOCAL.localize(row[1].ripped), "$Y") for row in _selectlogs(db)])
    for k, v in c.items():
        yield k, v


# ======================================================
# These functions mustn't be used from external scripts.
# ======================================================
def _selectlogs(db, **kwargs):
    """

    :param db: database where `rippeddiscs` table is stored.
    :param kwargs: additional arguments(s) to subset and/or to sort SQL statement results.
    :return:
    """
    in_logger = logging.getLogger("{0}._selectlogs".format(__name__))

    #  1. Initializations.
    where, rows, args = "", [], ()

    #  2. SELECT clause.
    select = "SELECT " \
             "rowid, " \
             "utc_ripped, " \
             "artistsort, " \
             "albumsort, " \
             "artist, " \
             "genre, " \
             "application, " \
             "discid, " \
             "tracks, " \
             "utc_created, " \
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
             "utc_modified " \
             "FROM rippeddiscs_vw "

    #  3. WHERE clause.

    #  3.a. Subset by `artistsort`.
    artistsort = kwargs.get("artistsort", [])
    if artistsort:
        where = "{0}(".format(where)
        for item in artistsort:
            where = "{0}lower(substr(albumid, 3, length(albumid) - 15)) LIKE ? OR ".format(where)
            args += ("%{0}%".format(item.lower()),)
        where = "{0}) AND ".format(where[:-4])

    # 3.b. Subset by `albumsort`.
    albumsort = kwargs.get("albumsort", [])
    if albumsort:
        where = "{0}(".format(where)
        for item in albumsort:
            where = "{0}substr(albumid, length(albumid) - 11) LIKE ? OR ".format(where)
            args += ("%{0}%".format(item),)
        where = "{0}) AND ".format(where[:-4])

    # 3.c. Subset by `artist`.
    artist = kwargs.get("artist", [])
    if artist:
        where = "{0}(".format(where)
        for item in artist:
            where = "{0}lower(artist) LIKE ? OR ".format(where)
            args += ("%{0}%".format(item.lower()),)
        where = "{0}) AND ".format(where[:-4])

    # 3.d. Subset by `genre`.
    genre = kwargs.get("genre", [])
    if genre:
        where = "{0}(".format(where)
        for item in genre:
            where = "{0}lower(genre)=? OR ".format(where)
            args += (item.lower(),)
        where = "{0}) AND ".format(where[:-4])

    # 3.e. Subset by `application`.
    application = kwargs.get("application", [])
    if application:
        where = "{0}(".format(where)
        for item in application:
            where = "{0}lower(application)=? OR ".format(where)
            args += (item.lower(),)
        where = "{0}) AND ".format(where[:-4])

    # 3.f. Subset by row ID.
    uid = kwargs.get("uid", [])
    if uid:
        where = "{0}(".format(where)
        for item in uid:
            where = "{0}rowid=? OR ".format(where)
            args += (item,)
        where = "{0}) AND ".format(where[:-4])

    # 3.g. Subset by `album`.
    album = kwargs.get("album", [])
    if album:
        where = "{0}(".format(where)
        for item in album:
            where = "{0}lower(album) LIKE ? OR ".format(where)
            args += ("%{0}%".format(item),)
        where = "{0}) AND ".format(where[:-4])

    # 3.h. Subset by `year`.
    year = kwargs.get("year", [])
    if year:
        where = "{0}(".format(where)
        for item in year:
            where = "{0}year=? OR ".format(where)
            args += (item,)
        where = "{0}) AND ".format(where[:-4])

    # 3.i. Subset by `ripped year`.
    rippedyear = kwargs.get("rippedyear", [])
    if rippedyear:
        where = "{0}(".format(where)
        for item in rippedyear:
            where = "{0}cast(strftime('%Y', ripped) AS INTEGER)=? OR ".format(where)
            args += (item,)
        where = "{0}) AND ".format(where[:-4])

    # 3.j. Subset by `ripped month`.
    rippedmonth = kwargs.get("rippedmonth", [])
    if rippedmonth:
        where = "{0}(".format(where)
        for item in rippedmonth:
            where = "{0}cast(strftime('%Y%m', ripped) AS INTEGER)=? OR ".format(where)
            args += (item,)
        where = "{0}) AND ".format(where[:-4])

    # 3.k. Subset by `label`.
    label = kwargs.get("label", [])
    if label:
        where = "{0}(".format(where)
        for item in label:
            where = "{0}lower(label) LIKE ? OR ".format(where)
            args += ("%{0}%".format(item),)
        where = "{0}) AND ".format(where[:-4])

    # 4. ORDER BY clause.
    orderby = "ORDER BY {0}".format(", ".join(kwargs.get("orderby", ["rowid"])))

    #  5. Build SQL statement.
    if where:
        where = "WHERE {0}".format(where[:-5])
    sql = "{0} {1}".format(select, orderby)
    if where:
        sql = "{0} {1} {2}".format(select, where, orderby)
    in_logger.debug(sql)
    in_logger.debug(args)

    #  6. Run SQL statement.
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute(sql, args):
        isbootleg = row[10]
        in_logger.debug("Bootleg is %s.", isbootleg)
        row = list(compress(row, FIELDS_SELECTORS[isbootleg]))
        rows.append(NAMED_TUPLES[isbootleg]._make(row))
        log_record(row)
    conn.close()
    for row in rows:
        yield row
