# -*- coding: utf-8 -*-
import json
import logging
import re
import sqlite3
from collections import namedtuple
from datetime import datetime
from itertools import chain, compress, groupby
from operator import itemgetter

from ...shared import DATABASE, LOCAL, TEMPLATE4, UTC, dateformat, validalbumsort, validdiscnumber, validgenre, validproductcode, validdatetime, validtracks, validyear
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

    def __init__(self, *logs, db=DATABASE):
        self._changes, _logs, now = 0, [], int(UTC.localize(datetime.utcnow()).timestamp())
        for log in logs:

            timestamp = now
            try:
                artist, origyear, year, album, disc, tracks, genre, upc, label, timestamp, application, albumsort, artistsort = log
            except ValueError:
                artist, origyear, year, album, disc, tracks, genre, upc, label, application, albumsort, artistsort = log

            # Check if `origyear` is valid.
            try:
                origyear = validyear(origyear)
            except ValueError as err:
                self.logger.debug(err)
                continue

            # Check if `year` is valid.
            try:
                year = validyear(year)
            except ValueError as err:
                self.logger.debug(err)
                continue

            # Check if `disc` is valid.
            try:
                disc = int(disc)
            except (ValueError, TypeError) as err:
                self.logger.debug(err)
                continue
            if not disc:
                self.logger.debug("Disc number must be greater than 0.")
                continue

            # Check if `tracks` is valid.
            try:
                tracks = int(tracks)
            except (ValueError, TypeError) as err:
                self.logger.debug(err)
                continue
            if not tracks:
                self.logger.debug("Total tracks number must be greater than 0.")
                continue

            # Check if `genre` is valid.
            try:
                genre = validgenre(genre)
            except (ValueError, TypeError) as err:
                self.logger.debug(err)
                continue

            # Check if `upc` is valid.
            try:
                upc = validproductcode(upc)
            except (ValueError, TypeError) as err:
                self.logger.debug(err)
                continue

            # Check if `albumsort` is valid.
            try:
                albumsort = validalbumsort(albumsort)
            except (ValueError, TypeError) as err:
                self.logger.debug(err)
                continue

            # Set `timestamp`.
            # `timestamp` must be a local Unix epoch time.
            if not timestamp:
                timestamp = now

            _logs.append((datetime.fromtimestamp(timestamp), artist, origyear, year, album, disc, tracks, genre, upc, label, application, albumsort, artistsort, datetime.utcnow()))

        if _logs:
            conn = sqlite3.connect(db)
            with conn:
                conn.executemany(
                        "INSERT INTO rippinglog (ripped, artist, origyear, year, album, disc, tracks, genre, upc, label, application, albumsort, artistsort, utc_created) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
                        "?, ?, ?, ?)", _logs)
                self._changes = conn.total_changes
                self.logger.debug("{0} records inserted.".format(self._changes))
                if self._changes:
                    for item in _logs:
                        self.logger.debug(item)
            conn.close()

    @classmethod
    def fromjson(cls, fil, db=DATABASE):
        """

        :param fil:
        :param db:
        :return:
        """
        return cls(*json.load(fil), db=db)

    @classmethod
    def fromxml(cls, fil, db=DATABASE):
        """

        :param fil:
        :param db:
        :return:
        """
        return cls(*[(log.artist,
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
                      log.artistsort) for log in rippinglog_in(fil)], db=db)

    @property
    def changes(self):
        return self._changes


# ==========
# Functions.
# ==========
def logrecord(t, func):
    tab = 3
    rowid, ripped, artistsort, albumsort, artist, origyear, year, album, label, genre, upc, application, disc, tracks, utc_created, utc_modified = t
    logger = logging.getLogger("{0}.{1}".format(__name__, func))
    logger.info("----------------")
    logger.info("Selected record.")
    logger.info("----------------")
    logger.info("\tRecord\t\t: {0}".format(rowid).expandtabs(tab))
    logger.info("\tArtistSort\t: {0}".format(artistsort).expandtabs(tab))
    logger.info("\tAlbumSort\t: {0}".format(albumsort).expandtabs(tab))
    logger.info("\tArtist\t\t: {0}".format(artist).expandtabs(tab))
    logger.info("\tYear\t\t\t: {0}".format(year).expandtabs(tab))
    logger.info("\tAlbum\t\t\t: {0}".format(album).expandtabs(tab))
    logger.info("\tDisc\t\t\t: {0}".format(disc).expandtabs(tab))
    logger.info("\tTracks\t\t: {0}".format(tracks).expandtabs(tab))
    logger.info("\tGenre\t\t\t: {0}".format(genre).expandtabs(tab))
    logger.info("\tUPC\t\t\t: {0}".format(upc).expandtabs(tab))
    logger.info("\tLabel\t\t\t: {0}".format(label).expandtabs(tab))
    logger.info("\tRipped\t\t: {0}".format(dateformat(LOCAL.localize(ripped), TEMPLATE4)).expandtabs(tab))
    if utc_created:
        logger.info("\tCreated\t\t: {0}".format(dateformat(UTC.localize(utc_created), TEMPLATE4)).expandtabs(tab))
    if utc_modified:
        logger.info("\tModified\t\t: {0}".format(dateformat(UTC.localize(utc_modified), TEMPLATE4)).expandtabs(tab))


# =======================================
# Main functions for working with tables.
# =======================================
def insertfromfile(*files, db=DATABASE):
    """
    Insert ripping log(s) into `rippinglog` table.
    Logs are taken from JSON file-object(s) or XML file-object(s).

    :param files: file-object(s) where the logs are taken from.
    :param db: database where `rippinglog` table is stored.
    :return: database total changes.
    """
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
            logs = InsertRippingLog.fromjson(fil, db=db)

        # XML file.
        elif structure == "xml":
            logs = InsertRippingLog.fromxml(fil, db=db)

        # Insert logs into database.
        status += logs.changes

    return status


def insertfromargs(db=DATABASE, **kwargs):
    """
    Insert ripping log(s) into `rippinglog` table.
    Logs are taken from keywords arguments gathered together into a python dictionary.

    :param db: database where `rippinglog` table is stored.
    :param kwargs: field-value pairs.
    :return: database total changes.
    """
    return InsertRippingLog((kwargs.get("artist"),
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
                             kwargs.get("artistsort")), db=db).changes


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


def selectlogs(db=DATABASE, **kwargs):
    """

    :param db: database where `rippinglog` table is stored.
    :param kwargs: additional arguments(s) to subset and/or to sort SQL statement results.
    :return:
    """
    logger = logging.getLogger("{0}.selectlogs".format(__name__))

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
        logrecord(row, "selectlogs")
    conn.close()
    for row in rows:
        yield record._make(row)


def selectlog(*uid, db=DATABASE, **kwargs):
    """

    :param uid:
    :param db: database where `rippinglog` is stored.
    :param kwargs: additional arguments(s) to subset and/or to sort SQL statement results.
    :return:
    """
    for row in selectlogs(db=db, uid=uid, **kwargs):
        yield row


def selectlogsfrommonth(*month, db=DATABASE):
    """

    :param month:
    :param db:
    :return:
    """
    record = namedtuple("record", "rowid ripped artistsort albumsort artist origyear year album label genre upc application disc tracks utc_created utc_modified")
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute("SELECT a.rowid, a.* FROM rippinglog a ORDER BY ripped DESC"):
        logrecord(tuple(row), "selectlogsfrommonth")
        if int(LOCAL.localize(tuple(row)[1]).strftime("%Y%m")) in month:
            yield record._make(row)


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
    #    Change `selectors` values:
    #       - "1": input values is validated. Field will be updated.
    #       - "0": input values is rejected. Field won't be updated.
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
        args.append(UTC.localize(datetime.utcnow()))  # ["the album", "1.20170000.1", datetime(2017, 10, 21, 16, 30, 45, tzinfo=timezone("utc"))]
        conn = sqlite3.connect(db)
        try:
            with conn:
                conn.executemany("UPDATE rippinglog SET {0} WHERE rowid=?".format(query[:-2]), [tuple(chain(args, (rowid,))) for rowid in uid])
                status = conn.total_changes
        except (sqlite3.OperationalError, sqlite3.Error) as err:
            logger.exception(err)
        else:
            logger.debug("{0:>3d} record(s) updated.".format(status))
        finally:
            conn.close()

    # 5. Return table total changes.
    return status


def getmonths(db=DATABASE):
    """

    :param db:
    :return:
    """
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    reflist = sorted(set([(LOCAL.localize(row[0]).strftime("%Y%m"), LOCAL.localize(row[0]).strftime("%B").capitalize()) for row in conn.execute("SELECT ripped FROM rippinglog ORDER BY ripped DESC")]),
                     key=itemgetter(0))
    for key, group in groupby(reflist, key=lambda i: i[0][:4]):
        yield key, list(group)
