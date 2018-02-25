# -*- coding: utf-8 -*-
import json
import logging
import re
import sqlite3
from collections import Counter, namedtuple
from datetime import datetime
from itertools import chain, compress, groupby, repeat
from operator import itemgetter

from ...shared import DATABASE, LOCAL, TEMPLATE4, UTC, dateformat, getnearestmultiple, gettabs, validalbumsort, validdatetime, validdb, validdiscnumber, validgenre, validproductcode, validtracks, validyear
from ...xml import rippinglog_in

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# ========
# Classes.
# ========
class InsertRippingLog(object):
    """

    """
    logger = logging.getLogger("{0}.InsertRippingLog".format(__name__))

    def __init__(self, *logs):
        self._changes, _logs, now = 0, [], int(UTC.localize(datetime.utcnow()).timestamp())
        for log in logs:

            timestamp = now
            try:
                database, artist, origyear, year, album, disc, tracks, genre, upc, label, timestamp, application, albumsort, artistsort = log
            except ValueError:
                database, artist, origyear, year, album, disc, tracks, genre, upc, label, application, albumsort, artistsort = log

            # 1. Check if `database` is valid.
            try:
                database = validdb(database)
            except ValueError as err:
                self.logger.debug("Database: {0}".format(err))
                continue

            # 2. Check if `origyear` is valid.
            try:
                origyear = validyear(origyear)
            except ValueError as err:
                self.logger.debug("Origyear: {0}".format(err))
                continue

            # 3. Check if `year` is valid.
            try:
                year = validyear(year)
            except ValueError as err:
                self.logger.debug("Year: {0}".format(err))
                continue

            # 4. Check if `disc` is valid.
            try:
                disc = int(disc)
            except (ValueError, TypeError) as err:
                self.logger.debug("Disc: {0}".format(err))
                continue
            if not disc:
                self.logger.debug("Disc number must be greater than 0.")
                continue

            # 5. Check if `tracks` is valid.
            try:
                tracks = int(tracks)
            except (ValueError, TypeError) as err:
                self.logger.debug("Tracks: {0}".format(err))
                continue
            if not tracks:
                self.logger.debug("Total tracks number must be greater than 0.")
                continue

            # 6. Check if `genre` is valid.
            try:
                genre = validgenre(genre)
            except (ValueError, TypeError) as err:
                self.logger.debug("Genre: {0}".format(err))
                continue

            # 7. Check if `upc` is valid.
            try:
                upc = validproductcode(upc)
            except (ValueError, TypeError) as err:
                self.logger.debug("Product code: {0}".format(err))
                continue

            # 8. Check if `albumsort` is valid.
            try:
                albumsort = validalbumsort(albumsort)
            except (ValueError, TypeError) as err:
                self.logger.debug("Albumsort: {0}".format(err))
                continue

            # 9. Set `timestamp`.
            #    `timestamp` must be a local Unix epoch time.
            if not timestamp:
                timestamp = now

            # 10. Configure tuples gathering together log details.
            self.logger.debug(timestamp)
            self.logger.debug(artist)
            self.logger.debug(origyear)
            self.logger.debug(year)
            self.logger.debug(album)
            self.logger.debug(disc)
            self.logger.debug(tracks)
            self.logger.debug(genre)
            self.logger.debug(upc)
            self.logger.debug(label)
            self.logger.debug(application)
            self.logger.debug(albumsort)
            self.logger.debug(artistsort)
            _logs.append((database, datetime.fromtimestamp(timestamp), artist, origyear, year, album, disc, tracks, genre, upc, label, application, albumsort, artistsort, datetime.utcnow()))

        if _logs:
            self._changes, _logs = 0, dict((key, list(group)) for key, group in groupby(sorted(_logs, key=itemgetter(0)), key=itemgetter(0)))
            for key, group in _logs.items():
                group = [item[1:] for item in group]
                conn = sqlite3.connect(key)
                try:
                    with conn:
                        conn.executemany(
                                "INSERT INTO rippinglog (ripped, artist, origyear, year, album, disc, tracks, genre, upc, label, application, albumsort, artistsort, utc_created) "
                                "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", group)
                except sqlite3.IntegrityError:
                    pass
                finally:
                    self._changes += conn.total_changes
                    self.logger.debug("{0} records inserted into '{1}'.".format(conn.total_changes, key))
                    if self._changes:
                        for item in group:
                            self.logger.debug(item)
                    conn.close()

    @classmethod
    def fromjson(cls, fil):
        """

        :param fil:
        :return:
        """
        return cls(*json.load(fil))

    @classmethod
    def fromxml(cls, fil):
        """

        :param fil:
        :return:
        """
        return cls(*[(log.database,
                      log.artist,
                      log.origyear,
                      log.year,
                      log.album,
                      log.disc,
                      log.tracks,
                      log.genre,
                      log.upc,
                      log.label,
                      log.ripped,
                      log.application,
                      log.albumsort,
                      log.artistsort) for log in rippinglog_in(fil) if log.database])

    @property
    def changes(self):
        return self._changes


# ==========
# Functions.
# ==========
def logrecord(t, *, logginglevel="debug"):
    """

    :param t:
    :param logginglevel:
    :return:
    """
    tabsize, headers = 3, ["Record", "Ripped", "Artistsort", "Albumsort", "Artist", "Origyear", "Year", "Album", "Label", "Genre", "UPC", "Application", "Disc", "Tracks", "Created", "Modified"]
    width = getnearestmultiple(max([len(header) for header in headers]), multiple=tabsize)
    logger = logging.getLogger("{0}.logrecord".format(__name__))
    levels = {"default": logger.debug,
              "debug": logger.debug,
              "info": logger.info,
              "warning": logger.warning}

    # Split tuple structure to single variables.
    rowid, ripped, artistsort, albumsort, artist, origyear, year, album, label, genre, upc, application, disc, tracks, utc_created, utc_modified = t

    # Convert non-string variables to string.
    rowid = str(rowid)
    ripped = dateformat(LOCAL.localize(ripped), TEMPLATE4)
    origyear = str(origyear)
    year = str(year)
    utc_created = dateformat(UTC.localize(utc_created).astimezone(LOCAL), TEMPLATE4)
    if utc_modified:
        utc_modified = dateformat(UTC.localize(utc_modified).astimezone(LOCAL), TEMPLATE4)

    # Gathered together single variables into a tuple structure.
    thattuple = rowid, ripped, artistsort, albumsort, artist, origyear, year, album, label, genre, upc, application, disc, tracks, utc_created, utc_modified

    # Log variables tuple content.
    levels.get(logginglevel, "default")("================")
    levels.get(logginglevel, "default")("Selected record.")
    levels.get(logginglevel, "default")("================")
    for label, data in filter(lambda i: bool(i[1]), zip(headers, thattuple)):
        levels.get(logginglevel, "default")("{0}{1}: {2}".format(label, gettabs(width - len(label)), data).expandtabs(tabsize))


# =======================================
# Main functions for working with tables.
# =======================================
def insertfromfile(*files):
    """
    Insert ripping log(s) into `rippinglog` table.
    Logs are taken from JSON file-object(s) or XML file-object(s).

    :param files: file-object(s) where the logs are taken from.
    :return: database total changes.
    """
    logger = logging.getLogger("{0}.insertfromfile".format(__name__))
    root = "rippinglogs"
    regex1, regex2, regex3 = re.compile(r"^<([^>]+)>$"), re.compile(r"^</([^>]+)>$"), re.compile(r"^<\?xml[^>]+>$")
    status = 0

    for fil in files:
        structure, logs, beg_match, end_match, beg = "json", None, None, None, True

        # Simple file type detection: JSON (default type) or XML.
        for line in fil:
            if regex3.match(line.strip()):
                continue
            if beg:
                beg = False
                beg_match = regex1.match(line.strip())
            end_match = regex2.match(line.strip())
        if all([beg_match, end_match]):
            if all([beg_match.group(1).lower() == root, end_match.group(1).lower() == root]):
                structure = "xml"

        # Set cursor at the beginning of the file.
        fil.seek(0)

        # JSON file.
        if structure == "json":
            logs = InsertRippingLog.fromjson(fil)

        # XML file.
        elif structure == "xml":
            logs = InsertRippingLog.fromxml(fil)

        # Insert logs into database.
        status += logs.changes
        logger.debug("{0} records inserted.".format(status))

    return status


def insertfromargs(**kwargs):
    """
    Insert ripping log(s) into `rippinglog` table.
    Logs are taken from keywords arguments gathered together into a python dictionary.

    :param kwargs: field-value pairs.
    :return: database total changes.
    """
    return InsertRippingLog((kwargs.get("db"),
                             kwargs.get("artist"),
                             kwargs.get("origyear"),
                             kwargs.get("year"),
                             kwargs.get("album"),
                             kwargs.get("disc"),
                             kwargs.get("tracks"),
                             kwargs.get("genre"),
                             kwargs.get("upc"),
                             kwargs.get("label"),
                             kwargs.get("application"),
                             kwargs.get("albumsort"),
                             kwargs.get("artistsort"))).changes


def deletelog(*uid, db=DATABASE):
    """

    :param uid:
    :param db:
    :return:
    """
    status, conn = 0, sqlite3.connect(db)
    with conn:
        conn.executemany("DELETE FROM rippinglog WHERE rowid=?", [(rowid,) for rowid in uid])
        status = conn.total_changes
        logger = logging.getLogger("{0}.deletelog".format(__name__))
        logger.debug("{0} records removed.".format(status))
        if status:
            for item in uid:
                logger.debug("Unique ID: {0:>4d}.".format(item))
    return status


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

    :param uid:
    :param db: database where `rippinglog` is stored.
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
                 "ripped": validdatetime,
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
    c = Counter([row.artistsort for row in _selectlogs(db)])
    for k, v in c.items():
        yield k, v


def getgenre(db=DATABASE):
    """

    :param db:
    :return:
    """
    c = Counter([row.genre for row in _selectlogs(db)])
    for k, v in c.items():
        yield k, v


def rippedmonth(db=DATABASE):
    c = Counter([dateformat(LOCAL.localize(row.ripped), "$Y$m") for row in _selectlogs(db)])
    for k, v in c.items():
        yield k, v


def rippedyear(db=DATABASE):
    c = Counter([dateformat(LOCAL.localize(row.ripped), "$Y") for row in _selectlogs(db)])
    for k, v in c.items():
        yield k, v


def get_uploadedtracks(db=DATABASE):
    for file, utc_created, utc_uploaded in _gettracks(db):
        yield file, utc_created, utc_uploaded


def get_trackstoupload(db=DATABASE):
    for rowid, file, utc_created in _gettracks(db, uploaded=False):
        yield rowid, file, utc_created


def uploadtracks(*uid, db=DATABASE):
    return _updatetracks(db, *uid)


def insert_tracks(*files, db=DATABASE):
    """
    Alimenter la table `audiostation` lors de l'extraction des pistes d'un CD audio.

    :param files:
    :param db:
    :return:
    """
    logger = logging.getLogger("{0}.insert_tracks".format(__name__))
    changes = _inserttracks(db, *files)
    logger.debug(changes)
    return changes


def delete_tracks(*uid, db=DATABASE):
    logger = logging.getLogger("{0}.delete_tracks".format(__name__))
    changes = _deletetracks(db, *uid)
    logger.debug(changes)
    return changes


# ======================================================
# These functions mustn't be used from external scripts.
# ======================================================
def _selectlogs(db, **kwargs):
    """

    :param db: database where `rippinglog` table is stored.
    :param kwargs: additional arguments(s) to subset and/or to sort SQL statement results.
    :return:
    """
    logger = logging.getLogger("{0}._selectlogs".format(__name__))

    #  1. Initializations.
    record = namedtuple("record", "rowid ripped artistsort albumsort artist origyear year album label genre upc application disc tracks utc_created utc_modified")
    where, rows, args = "", [], ()

    #  2. SELECT clause.
    select = "SELECT a.rowid, a.* FROM rippinglog a"

    #  3. WHERE clause.

    #  3.a. Subset by `artistsort`.
    artistsort = kwargs.get("artistsort", [])
    if artistsort:
        where = "{0}(".format(where)
        for item in artistsort:
            where = "{0}lower(artistsort) LIKE ? OR ".format(where)
            args += ("%{0}%".format(item.lower()),)
        where = "{0}) AND ".format(where[:-4])

    # 3.b. Subset by `albumsort`.
    albumsort = kwargs.get("albumsort", [])
    if albumsort:
        where = "{0}(".format(where)
        for item in albumsort:
            where = "{0}albumsort LIKE ? OR ".format(where)
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
    logger.debug(sql)
    logger.debug(args)

    #  6. Run SQL statement.
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute(sql, args):
        rows.append(row)
        logrecord(row, logginglevel=kwargs.get("logginglevel", "debug"))
    conn.close()
    for row in rows:
        yield record._make(row)


def _inserttracks(db, *files):
    changes = 0
    if files:
        conn = sqlite3.connect(db)
        try:
            with conn:
                conn.executemany("INSERT INTO audiostation (file, utc_created) VALUES (?, ?)", zip(files, repeat(datetime.utcnow())))
        except sqlite3.OperationalError:
            pass
        finally:
            changes = conn.total_changes
            conn.close()
    return changes


def _gettracks(db, *, uploaded=True):
    d1 = {False: "rowid, file, utc_created", True: "file, utc_created, utc_uploaded"}
    d2 = {False: 0, True: 1}
    statement = "SELECT {0} FROM audiostation WHERE status=? ORDER BY utc_created".format(d1[uploaded])
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    files = [(row[0], row[1], row[2]) for row in conn.execute(statement, (d2[uploaded],))]
    conn.close()
    for file in files:
        yield file[0], file[1], file[2]


def _updatetracks(db, *uid, uploaded=True):
    changes, d = 0, {False: 0, True: 1}
    conn = sqlite3.connect(db)
    try:
        with conn:
            conn.executemany("UPDATE audiostation SET status=?, utc_uploaded=? WHERE rowid=?", zip(repeat(d[uploaded]), repeat(datetime.utcnow()), uid))
    except sqlite3.OperationalError:
        pass
    finally:
        changes = conn.total_changes
        conn.close()
    return changes


def _deletetracks(db, *uid):
    changes = 0
    if uid:
        conn = sqlite3.connect(db)
        try:
            with conn:
                conn.executemany("DELETE FROM audiostation WHERE uid=?", [(rowid,) for rowid in uid])
        except sqlite3.OperationalError:
            pass
        finally:
            changes = conn.total_changes
            conn.close()
    return changes
