# -*- coding: utf-8 -*-
import logging
import sqlite3
from collections import Counter, namedtuple
from datetime import date, datetime
from itertools import chain, compress

from ...shared import DATABASE, LOCAL, TEMPLATE4, UTC, dateformat, validalbumsort, validdatetime, validdiscnumber, validgenre, validproductcode, validtracks, validyear

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ========
# Classes.
# ========
# class InsertRippingLog(object):
#     """
#
#     """
#     logger = logging.getLogger("{0}.InsertRippingLog".format(__name__))
#
#     def __init__(self, *logs):
#         self._changes, _logs, timestamp = 0, [], int(UTC.localize(datetime.utcnow()).timestamp())
#         for log in logs:
#
#             try:
#                 database, artist, origyear, year, album, disc, tracks, genre, upc, label, timestamp, application, albumsort, artistsort = log
#             except ValueError:
#                 database, artist, origyear, year, album, disc, tracks, genre, upc, label, application, albumsort, artistsort = log
#
#             # 1. Check if `database` is valid.
#             try:
#                 database = validdb(database)
#             except ValueError as err:
#                 self.logger.debug("Tables: {0}".format(err))
#                 continue
#
#             # 2. Check if `origyear` is valid.
#             try:
#                 origyear = validyear(origyear)
#             except ValueError as err:
#                 self.logger.debug("Origyear: {0}".format(err))
#                 continue
#
#             # 3. Check if `year` is valid.
#             try:
#                 year = validyear(year)
#             except ValueError as err:
#                 self.logger.debug("Year: {0}".format(err))
#                 continue
#
#             # 4. Check if `disc` is valid.
#             try:
#                 disc = int(disc)
#             except (ValueError, TypeError) as err:
#                 self.logger.debug("Disc: {0}".format(err))
#                 continue
#             if not disc:
#                 self.logger.debug("Disc number must be greater than 0.")
#                 continue
#
#             # 5. Check if `tracks` is valid.
#             try:
#                 tracks = int(tracks)
#             except (ValueError, TypeError) as err:
#                 self.logger.debug("Tracks: {0}".format(err))
#                 continue
#             if not tracks:
#                 self.logger.debug("Total tracks number must be greater than 0.")
#                 continue
#
#             # 6. Check if `genre` is valid.
#             try:
#                 genre = validgenre(genre)
#             except (ValueError, TypeError) as err:
#                 self.logger.debug("Genre: {0}".format(err))
#                 continue
#
#             # 7. Check if `upc` is valid.
#             try:
#                 upc = validproductcode(upc)
#             except (ValueError, TypeError) as err:
#                 self.logger.debug("Product code: {0}".format(err))
#                 continue
#
#             # 8. Check if `albumsort` is valid.
#             try:
#                 albumsort = validalbumsort(albumsort)
#             except (ValueError, TypeError) as err:
#                 self.logger.debug("Albumsort: {0}".format(err))
#                 continue
#
#             # 9. Set `timestamp`.
#             #    `timestamp` must be a local Unix epoch time.
#             if not timestamp:
#                 timestamp = int(UTC.localize(datetime.utcnow()).timestamp())
#
#             # 10. Configure tuples gathering together log details.
#             self.logger.debug(timestamp)
#             self.logger.debug(artist)
#             self.logger.debug(origyear)
#             self.logger.debug(year)
#             self.logger.debug(album)
#             self.logger.debug(disc)
#             self.logger.debug(tracks)
#             self.logger.debug(genre)
#             self.logger.debug(upc)
#             self.logger.debug(label)
#             self.logger.debug(application)
#             self.logger.debug(albumsort)
#             self.logger.debug(artistsort)
#             _logs.append((database, datetime.fromtimestamp(timestamp), artist, origyear, year, album, disc, tracks, genre, upc, label, application, albumsort, artistsort, datetime.utcnow()))
#
#         if _logs:
#             self._changes, _logs = 0, dict((key, list(group)) for key, group in groupby(sorted(_logs, key=itemgetter(0)), key=itemgetter(0)))
#             for key, group in _logs.items():
#                 group = [item[1:] for item in group]
#                 conn = sqlite3.connect(key)
#                 try:
#                     with conn:
#                         conn.executemany(
#                                 "INSERT INTO rippinglog (ripped, artist, origyear, year, album, disc, tracks, genre, upc, label, application, albumsort, artistsort, utc_created) "
#                                 "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", group)
#                 except sqlite3.IntegrityError:
#                     pass
#                 finally:
#                     self._changes += conn.total_changes
#                     self.logger.debug("{0} records inserted into '{1}'.".format(conn.total_changes, key))
#                     if self._changes:
#                         for item in group:
#                             self.logger.debug(item)
#                     conn.close()
#
#     @classmethod
#     def fromjson(cls, fil):
#         """
#
#         :param fil:
#         :return:
#         """
#         return cls(*json.load(fil))
#
#     @classmethod
#     def fromxml(cls, fil):
#         """
#
#         :param fil:
#         :return:
#         """
#         return cls(*[(log.database,
#                       log.artist,
#                       log.origyear,
#                       log.year,
#                       log.album,
#                       log.disc,
#                       log.tracks,
#                       log.genre,
#                       log.upc,
#                       log.label,
#                       log.ripped,
#                       log.application,
#                       log.albumsort,
#                       log.artistsort) for log in rippinglog_in(fil) if log.database])
#
#     @property
#     def changes(self):
#         return self._changes

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
ATTRIBUTES = \
    {
        False: DefaultAlbum,
        True: BootlegAlbum
    }


# ===========
# Decorators.
# ===========
def validrippeddate(func):
    def wrapper(ts):
        try:
            result = func(ts)
        except ValueError:
            raise
        else:
            return result[0]

    return wrapper


# ==========
# Functions.
# ==========
def titi(arg):
    if arg is None:
        return arg
    if isinstance(arg, int):
        return str(arg)
    if isinstance(arg, datetime):
        return dateformat(UTC.localize(arg).astimezone(LOCAL), TEMPLATE4)
    if isinstance(arg, date):
        return arg.strftime("%d/%m/%Y")
    return arg


def format_record(iterable):
    """

    :param iterable:
    :return:
    """

    # 1. Constants.
    headers = \
        {
            False: ["Record", "Ripped", "Artistsort", "Albumsort", "Artist", "Genre", "Application", "Disc", "Tracks", "Created", "Bootleg", "Origyear", "Year", "Album", "Label", "UPC", "Modified"],
            True: ["Record", "Ripped", "Artistsort", "Albumsort", "Artist", "Genre", "Application", "Disc", "Tracks", "Created", "Bootleg", "BootlegDate", "BootlegCity", "BootlegCountry", "BootlegTour",
                   "Modified"]
        }

    # 2. Initializations.
    bootleg = iterable[10]

    # 3. Convert album attributes into strings attributes.
    album = list(map(titi, iterable))

    # 4. Configurer les entêtes adéquats en fonction des données présentes.
    #    Eliminer les entêtes des données à `None`.
    header = list(compress(headers[bootleg], map(lambda i: i is not None, album)))

    length = max([len(item) for item in header])
    for key, value in zip(header, filter(None, album)):
        yield "{0:<{1}}".format(key, length), value


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
    changes = 0
    with conn:
        conn.executemany("DELETE FROM rippeddiscs WHERE rowid=?", [(rowid,) for rowid in uid])
    changes = conn.total_changes
    conn.close()
    logger.debug("%s records removed.", changes)
    if changes:
        for item in uid:
            logger.debug("Unique ID: {0:>4d}.".format(item))
    return changes


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


def updatelog(*uid, db=DATABASE, **kwargs):
    """

    :param uid:
    :param db:
    :param kwargs:
    :return:
    """
    logger = logging.getLogger("{0}.updatelog".format(__name__))
    status, query, args = 0, "", []

    # 1. Map validation functions to table fields.
    functions = {"albumsort": validalbumsort,
                 "disc": validdiscnumber,
                 "genre": validgenre,
                 "ripped": validrippeddate(validdatetime),
                 "origyear": validyear,
                 "tracks": validtracks,
                 "upc": validproductcode,
                 "year": validyear}

    # 2. Validate input pairs.
    #    Change `selectors` values to accept/reject pairs:
    #       - "1": input value is accepted. Respective field will be updated.
    #       - "0": input value is rejected. Respective field won't be updated.
    pairs = dict(kwargs)
    keys = sorted(pairs.keys())
    selectors = [1] * len(pairs)
    for key in keys:
        error = False
        func = functions.get(key)
        if func:
            try:
                pairs[key] = func(pairs[key])
            except ValueError:
                error = True
        if error:
            selectors[keys.index(key)] = 0

    # 3. Build SQL statement.
    pairs = {k: v for k, v in pairs.items() if k in compress(keys, selectors)}
    for k, v in pairs.items():
        query = "{0}{1}=?, ".format(query, k)  # album=?, albumsort=?, "
        args.append(v)  # ["the album", "1.20170000.1"]

    # 4. Run SQL statement.
    #    Append modification date.
    if query:
        query = "{0}utc_modified=?, ".format(query)  # album=?, albumid=?, utc_modified=?, "
        args.append(UTC.localize(datetime.utcnow()).replace(tzinfo=None))  # ["the album", "1.20170000.1", datetime(2017, 10, 21, 16, 30, 45, tzinfo=timezone("utc"))]
        conn = sqlite3.connect(db)
        try:
            with conn:
                conn.executemany("UPDATE rippinglog SET {0} WHERE rowid=?".format(query[:-2]), [tuple(chain(args, (rowid,))) for rowid in uid])
        except (sqlite3.OperationalError, sqlite3.Error) as err:
            logger.exception(err)
        finally:
            status = conn.total_changes
            conn.close()
        logger.debug("{0:>3d} record(s) updated.".format(status))

    # 5. Return total changes.
    return status


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


def rippedmonth(db=DATABASE):
    c = Counter([dateformat(LOCAL.localize(row[1].ripped), "$Y$m") for row in _selectlogs(db)])
    for k, v in c.items():
        yield k, v


def rippedyear(db=DATABASE):
    c = Counter([dateformat(LOCAL.localize(row[1].ripped), "$Y") for row in _selectlogs(db)])
    for k, v in c.items():
        yield k, v


# ======================================================
# These functions mustn't be used from external scripts.
# ======================================================
def _selectlogs(db, **kwargs):
    """

    :param db: database where `rippinglog` table is stored.
    :param kwargs: additional arguments(s) to subset and/or to sort SQL statement results.
    :return:
    """
    _logger = logging.getLogger("{0}._selectlogs".format(__name__))

    #  1. Initializations.
    _where, _rows, _args = "", [], ()

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
             "is_bootleg AS bootleg, " \
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
    _artistsort = kwargs.get("artistsort", [])
    if _artistsort:
        _where = "{0}(".format(_where)
        for item in _artistsort:
            _where = "{0}lower(substr(albumid, 3, length(albumid) - 15)) LIKE ? OR ".format(_where)
            _args += ("%{0}%".format(item.lower()),)
        _where = "{0}) AND ".format(_where[:-4])

    # 3.b. Subset by `albumsort`.
    _albumsort = kwargs.get("albumsort", [])
    if _albumsort:
        _where = "{0}(".format(_where)
        for item in _albumsort:
            _where = "{0}substr(albumid, length(albumid) - 11) LIKE ? OR ".format(_where)
            _args += ("%{0}%".format(item),)
        _where = "{0}) AND ".format(_where[:-4])

    # 3.c. Subset by `artist`.
    _artist = kwargs.get("artist", [])
    if _artist:
        _where = "{0}(".format(_where)
        for item in _artist:
            _where = "{0}lower(artist) LIKE ? OR ".format(_where)
            _args += ("%{0}%".format(item.lower()),)
        _where = "{0}) AND ".format(_where[:-4])

    # 3.d. Subset by `genre`.
    _genre = kwargs.get("genre", [])
    if _genre:
        _where = "{0}(".format(_where)
        for item in _genre:
            _where = "{0}lower(genre)=? OR ".format(_where)
            _args += (item.lower(),)
        _where = "{0}) AND ".format(_where[:-4])

    # 3.e. Subset by `application`.
    _application = kwargs.get("application", [])
    if _application:
        _where = "{0}(".format(_where)
        for item in _application:
            _where = "{0}lower(application)=? OR ".format(_where)
            _args += (item.lower(),)
        _where = "{0}) AND ".format(_where[:-4])

    # 3.f. Subset by row ID.
    _uid = kwargs.get("uid", [])
    if _uid:
        _where = "{0}(".format(_where)
        for item in _uid:
            _where = "{0}rowid=? OR ".format(_where)
            _args += (item,)
        _where = "{0}) AND ".format(_where[:-4])

    # 3.g. Subset by `album`.
    _album = kwargs.get("album", [])
    if _album:
        _where = "{0}(".format(_where)
        for item in _album:
            _where = "{0}lower(album) LIKE ? OR ".format(_where)
            _args += ("%{0}%".format(item),)
        _where = "{0}) AND ".format(_where[:-4])

    # 3.h. Subset by `year`.
    _year = kwargs.get("year", [])
    if _year:
        _where = "{0}(".format(_where)
        for item in _year:
            _where = "{0}year=? OR ".format(_where)
            _args += (item,)
        _where = "{0}) AND ".format(_where[:-4])

    # 3.i. Subset by `ripped year`.
    _rippedyear = kwargs.get("rippedyear", [])
    if _rippedyear:
        _where = "{0}(".format(_where)
        for item in _rippedyear:
            _where = "{0}cast(strftime('%Y', ripped) AS INTEGER)=? OR ".format(_where)
            _args += (item,)
        _where = "{0}) AND ".format(_where[:-4])

    # 3.j. Subset by `ripped month`.
    _rippedmonth = kwargs.get("rippedmonth", [])
    if _rippedmonth:
        _where = "{0}(".format(_where)
        for item in _rippedmonth:
            _where = "{0}cast(strftime('%Y%m', ripped) AS INTEGER)=? OR ".format(_where)
            _args += (item,)
        _where = "{0}) AND ".format(_where[:-4])

    # 3.k. Subset by `label`.
    _label = kwargs.get("label", [])
    if _label:
        _where = "{0}(".format(_where)
        for item in _label:
            _where = "{0}lower(label) LIKE ? OR ".format(_where)
            _args += ("%{0}%".format(item),)
        _where = "{0}) AND ".format(_where[:-4])

    # 4. ORDER BY clause.
    _orderby = "ORDER BY {0}".format(", ".join(kwargs.get("orderby", ["rowid"])))

    #  5. Build SQL statement.
    if _where:
        _where = "WHERE {0}".format(_where[:-5])
    _sql = "{0} {1}".format(select, _orderby)
    if _where:
        _sql = "{0} {1} {2}".format(select, _where, _orderby)
    _logger.debug(_sql)
    _logger.debug(_args)

    #  6. Run SQL statement.
    _conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for _row in _conn.execute(_sql, _args):
        _bootleg = bool(_row[10])
        _row = list(compress(_row, FIELDS_SELECTORS[_bootleg]))
        _rows.append(ATTRIBUTES[_bootleg]._make(_row))
        _logger.debug("================")
        _logger.debug("Selected record.")
        _logger.debug("================")
        for _key, _value in format_record(_row):
            _logger.debug("%s: %s", _key, _value)
    _conn.close()
    for _row in _rows:
        yield _row
