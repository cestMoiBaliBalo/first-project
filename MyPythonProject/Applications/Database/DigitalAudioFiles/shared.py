# -*- coding: ISO-8859-1 -*-

import argparse
import json
import logging
import re
import sqlite3
from collections import MutableSequence, namedtuple
from contextlib import suppress
from datetime import datetime
from itertools import chain

from ..shared import Boolean, adapt_boolean, convert_boolean
from ...shared import DATABASE

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ================
# SQLite3 adapter.
# ================
sqlite3.register_adapter(Boolean, adapt_boolean)

# ==================
# SQLite3 converter.
# ==================
sqlite3.register_converter("boolean", convert_boolean)

# ==========
# Constants.
# ==========
GENRES = ["Rock", "Hard Rock", "Heavy Metal", "Trash Metal", "Alternative Rock", "Black Metal", "Progressive Rock", "French Pop"]


# ========
# Classes.
# ========
class DictArguments(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super(DictArguments, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        with suppress(AttributeError):
            d = getattr(namespace, "args")
        d[self.dest] = values
        setattr(namespace, "args", d)


class InsertTracksfromFile(MutableSequence):
    def __init__(self, fil, seconds):
        self._seq = []
        for index, albumsort, titlesort, artist, year, album, genre, discnumber, totaldiscs, label, tracknumber, totaltracks, title, live, bootleg, incollection, upc, encodingyear, titlelanguage, origyear \
                in json.load(fil):

            # Check if year is valid.
            try:
                year = validyear(year)
            except ValueError:
                continue

            # Check if discnumber is valid.
            try:
                discnumber = int(discnumber)
            except ValueError:
                continue

            # Check if totaldiscs is valid.
            try:
                totaldiscs = int(totaldiscs)
            except ValueError:
                continue

            # Check if tracknumber is valid.
            try:
                tracknumber = int(tracknumber)
            except ValueError:
                continue

            # Check if totaltracks is valid.
            try:
                totaltracks = int(totaltracks)
            except ValueError:
                continue

            # Check if product code is valid.
            try:
                upc = validbarcode(upc)
            except ValueError:
                continue

            # Check if genre is valid.
            try:
                genre = validgenre(genre)
            except ValueError:
                continue

            # Set origyear.
            try:
                origyear = validyear(origyear)
            except ValueError:
                origyear = 0

            # Set encodingyear.
            try:
                encodingyear = validyear(encodingyear)
            except ValueError:
                encodingyear = 0

            timestamp = datetime.now()
            if seconds:
                timestamp = datetime.fromtimestamp(seconds)
            tupalbum = (index[:-11], artist, year, album, totaldiscs, genre, Boolean(live), Boolean(bootleg), Boolean(incollection), titlelanguage, upc, encodingyear, timestamp, origyear)
            tupdisc = (index[:-11], discnumber, totaltracks, timestamp)
            tuptrack = (index[:-11], discnumber, tracknumber, title, timestamp)
            self._seq.append([tupalbum, tupdisc, tuptrack])

    def __getitem__(self, item):
        return self._seq[item]

    def __setitem__(self, key, value):
        self._seq[key] = value

    def __delitem__(self, key):
        del self._seq[key]

    def __len__(self):
        return len(self._seq)

    def insert(self, index, value):
        self._seq.insert(index, value)


# ==========
# Functions.
# ==========
def validyear(s):
    regex = re.compile(r"^(19[6-9]|20[0-2])\d$")
    if not regex.match(s):
        raise ValueError('"{0}" is not a valid year'.format(s))
    return int(s)


def validbarcode(s):
    regex = re.compile("^\d{12,13}$")
    if s:
        if not regex.match(s):
            raise ValueError('"{0}" is not a valid barcode'.format(s))
    return s


def validgenre(s):
    if s.lower() not in (genre.lower() for genre in GENRES):
        raise ValueError('"{0}" is not a valid genre'.format(s))
    return s


# =======================================
# Main functions for working with tables.
# =======================================
def insertfromfile(fil, db=DATABASE, seconds=None):
    statusss = []
    tracks = InsertTracksfromFile(fil, seconds)
    logger = logging.getLogger("{0}.insertfromfile".format(__name__))
    if len(tracks):
        for album, disc, track in tracks:
            statuss, acount, dcount, tcount = [], 0, 0, 0

            conn = sqlite3.connect(db)
            try:
                with conn:

                    # TRACKS table.
                    try:
                        conn.execute("INSERT INTO tracks (albumid, discid, trackid, title, created) VALUES (?, ?, ?, ?, ?)", track)
                        tcount = conn.total_changes
                        logger.debug("TRACKS: {0} records inserted.".format(tcount))
                    except sqlite3.IntegrityError:
                        pass

                    # DISCS table.
                    try:
                        conn.execute("INSERT INTO discs (albumid, discid, tracks, created) VALUES (?, ?, ?, ?)", disc)
                        dcount = conn.total_changes - tcount
                        logger.debug("DISCS: {0} records inserted.".format(dcount))
                    except sqlite3.IntegrityError:
                        pass

                    # ALBUMS table.
                    try:
                        conn.execute("INSERT INTO albums (albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, encodingyear, created, origyear) "
                                     "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", album)
                        acount = conn.total_changes - tcount - dcount
                        logger.debug("ALBUMS: {0} records inserted.".format(acount))
                    except sqlite3.IntegrityError:
                        pass

                    statuss = [tcount, dcount, acount]

            except sqlite3.Error:
                statuss = [0, 0, 0]

            statusss.append(tuple(statuss))
    return statusss


def getalbumdetail(db=DATABASE):
    """
    Get digital audio albums detail.

    :param db: Database storing digital audio tables.
    :return: Digital audio albums detail sorted by album ID, disc ID, track ID.
    """
    record = namedtuple("record", "rowid albumid artist year album discs genre live bootleg incollection language upc encodingyear created origyear discid tracks trackid title count")
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute(
            "SELECT a.rowid, a.albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, encodingyear, a.created, origyear, b.discid, b.tracks, trackid, title, a.count "
            "FROM albums a "
            "JOIN discs b ON a.albumid=b.albumid "
            "JOIN tracks c ON a.albumid=c.albumid AND b.discid=c.discid "
            "ORDER BY a.albumid, b.discid, c.trackid"):
        yield record._make(row)


def getalbumalternativedetail(db=DATABASE):
    """
    Get digital audio albums detail.

    :param db: Database storing digital audio tables.
    :return: Digital audio albums detail sorted by descending creation date, album ID, disc ID, track ID.
    """
    record = namedtuple("record", "rowid albumid artist year album discs genre live bootleg incollection language upc encodingyear created origyear discid tracks trackid title count")
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute(
            "SELECT a.rowid, a.albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, encodingyear, a.created, origyear, b.discid, b.tracks, trackid, title, a.count "
            "FROM albums a "
            "JOIN discs b ON a.albumid=b.albumid "
            "JOIN tracks c ON a.albumid=c.albumid AND b.discid=c.discid "
            "ORDER BY a.created DESC, a.albumid, b.discid, c.trackid"):
        yield record._make(row)


def getalbumidfromartist(db=DATABASE, artist=None):
    """
    Get album(s) ID matching the input artist.

    :param artist: Requested artist.
    :param db: Database storing `albums` table.
    :return: Album(s) unique ID list.
    """
    record = namedtuple("record", "rowid albumid")
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    statement = "SELECT rowid, albumid FROM albums ORDER BY albumid"
    argument = ()
    if artist:
        statement = "SELECT rowid, albumid FROM albums WHERE lower(substr(albumid, 3, length(albumid) - 2 - 13))=? OR lower(artist)=? ORDER BY albumid"  # A.Adams, Byran.1.19870000.1
        argument = (artist.lower(), artist.lower())
    for row in conn.execute(statement, argument):
        yield record._make(row)


def getalbumidfromgenre(genre, db=DATABASE):
    """
    Get album(s) ID matching the input genre.

    :param genre: Requested genre.
    :param db: Database storing `albums` table.
    :return: Album(s) unique ID list.
    """
    record = namedtuple("record", "rowid albumid")
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute("SELECT rowid, albumid FROM albums WHERE lower(genre)=? ORDER BY albumid", (genre.lower(),)):
        yield record._make(row)


def getalbumid(uid, db=DATABASE):
    """
    Get album ID matching the input unique row ID.

    :param uid: Requested row ID.
    :param db: Database storing `albums` table.
    :return: Album unique ID.
    """
    record = namedtuple("record", "rowid albumid")
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute("SELECT rowid, albumid FROM albums WHERE rowid=? ORDER BY albumid", (uid,)):
        yield record._make(row)


def getalbumheader(db=DATABASE, albumid=None):
    """
    Get album detail matching the input unique row ID.

    :param albumid: Requested row ID.
    :param db: Database storing `albums` table.
    :return: Album unique ID.
    """
    sql, where, args = "SELECT rowid, albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, encodingyear, created, origyear, played, count FROM albums ", "", ()
    record = namedtuple("record", "rowid albumid artist year album discs genre live bootleg incollection language upc encodingyear created origyear played count")

    # 1. Get one album.
    if albumid:
        where = "{0}albumid=?".format(where)
        args += (albumid,)

    # 2. Run SQL statement.
    statement = "{0}ORDER BY rowid".format(sql)
    if where:
        statement = "{0}WHERE {1}".format(sql, where)
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute(statement, args):
        yield record._make(row)


def getdischeader(db=DATABASE, albumid=None, discid=None):
    """
    Get disc(s) detail matching both the input unique album ID and the disc unique ID.

    :param db: Database storing `discs` table.
    :param albumid: Requested album unique ID. Optional.
    :param discid: Requested disc unique ID. Optional.
    :return: Yield a tuple composed of row unique ID, album unique ID, disc unique ID and track unique ID.
    """
    sql, where, order, args = "SELECT rowid, albumid, discid, tracks FROM discs ", "", "", ()
    record = namedtuple("record", "rowid albumid discid tracks")

    # 1. Get one album.
    if albumid:
        where = "{0}albumid=? and ".format(where)
        order = discid
        args += (albumid,)

    # 2. Get one disc.
    if albumid and discid:
        where = "{0}discid=? and ".format(where)
        args += (discid,)

    # 3. Run SQL statement.
    statement = "{0}ORDER BY rowid".format(sql)
    if where:
        statement = "{0}WHERE {1}".format(sql, where)
        statement = statement[:-4]
    if order:
        statement = "{0}ORDER BY {1}".format(statement, order)
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute(statement, args):
        yield record._make(row)


def gettrack(db=DATABASE, albumid=None, discid=None, trackid=None):
    """
    Get track(s) detail matching both the input unique album ID, the disc unique ID and the track unique ID.

    :param db: Database storing `discs` table.
    :param albumid: Requested album unique ID. Optional.
    :param discid: Requested disc unique ID. Optional.
    :param trackid: Requested track unique ID. Optional.
    :return: Yield a tuple composed of row unique ID, album unique ID, disc unique ID, track unique ID and title.
    """
    record, args, where, order, sql = namedtuple("record", "rowid albumid discid trackid title"), (), "", "", "SELECT rowid, albumid, discid, trackid, title FROM tracks "

    # 1. Get one album.
    if albumid:
        where = "{0}albumid=? and ".format(where)
        order = "discid, trackid"
        args += (albumid,)

    # 2. Get one disc.
    if albumid and discid:
        where = "{0}discid=? and ".format(where)
        order = "trackid"
        args += (discid,)

    # 3. Get one track.
    if albumid and discid and trackid:
        where = "{0}trackid=? and ".format(where)
        args += (trackid,)

    # 4. Run SQL statement.
    statement = "{0}ORDER BY rowid".format(sql)
    if where:
        statement = "{0}WHERE {1}".format(sql, where)
        statement = statement[:-4]
    if order:
        statement = "{0}ORDER BY {1}".format(statement, order)
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute(statement, args):
        yield record._make(row)


def deletealbum(db=DATABASE, uid=None, albumid=None):
    """
    Delete a digital album.

    :param db: Database storing `albums`, `discs` and `tracks` tables.
    :param uid: `albums` row unique ID. Optional. Used as hieharchy starting point.
    :param albumid: `albums` album unique ID. Optional. Used as hieharchy starting point.
    :return: Tuple composed of deleted album unique ID, `albums` total change(s), `discs` total change(s) and `tracks` total change(s).
    """

    # 1. Initialize variables.
    acount, dcount, tcount, discs, tracks, inp_uid, inp_albumid = 0, 0, 0, [], [], uid, albumid

    # 2. Connect to database.
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row

    # 3. Get the album ID if the received key is the record unique ID.
    if uid:
        for row in conn.execute("SELECT albumid FROM albums WHERE rowid=?", (inp_uid,)):
            inp_albumid = row["albumid"]

    # 4. Get the record unique ID if the received key is the album ID.
    if albumid:
        for row in conn.execute("SELECT rowid FROM albums WHERE albumid=?", (inp_albumid,)):
            inp_uid = row["rowid"]

    # 5. Get records unique IDs respective to both `discs` and `tracks` table.
    for drow in conn.execute("SELECT rowid, discid FROM discs WHERE albumid=?", (inp_albumid,)):
        discs.append(drow["rowid"])
        for trow in conn.execute("SELECT rowid FROM tracks WHERE albumid=? AND discid=?", (inp_albumid, drow["discid"])):
            tracks.append(trow["rowid"])

    # 6. Update tables.
    try:
        with conn:

            # TRACKS table.
            conn.executemany("DELETE FROM tracks WHERE rowid=?", [(i,) for i in tracks])
            tcount = conn.total_changes

            # DISCS table.
            conn.executemany("DELETE FROM discs WHERE rowid=?", [(i,) for i in discs])
            dcount = conn.total_changes - tcount

            # ALBUMS table.
            conn.execute("DELETE FROM albums WHERE rowid=?", (inp_uid,))
            acount = conn.total_changes - tcount - dcount

    except (sqlite3.Error, ValueError):
        return inp_albumid, 0, 0, 0

    # 7. Return total changes.
    return inp_albumid, acount, dcount, tcount


def deletealbumheader(*uid, db=DATABASE):
    """
    Delete album(s) from `albums` table.

    :param uid: Album(s) row(s) ID.
    :param db: Database storing `albums` table.
    :return: Total changes.
    """
    status, conn = 0, sqlite3.connect(db)
    with conn:
        conn.executemany("DELETE FROM albums WHERE rowid=?", [(i,) for i in uid])
        status = conn.total_changes
    return status


def deletedischeader(*uid, db=DATABASE):
    """
    Delete disc(s) from `discs` table.

    :param uid: Disc(s) row(s) ID.
    :param db: Database storing `discs` table.
    :return: Total changes.
    """
    status, conn = 0, sqlite3.connect(db)
    with conn:
        conn.executemany("DELETE FROM discs WHERE rowid=?", [(i,) for i in uid])
        status = conn.total_changes
    return status


def deletetrack(*uid, db=DATABASE):
    """
    Delete track(s) from `tracks` table.

    :param uid: Track(s) row(s) ID.
    :param db: Database storing `tracks` table.
    :return: Total changes.
    """
    status, conn = 0, sqlite3.connect(db)
    with conn:
        conn.executemany("DELETE FROM tracks WHERE rowid=?", [(i,) for i in uid])
        status = conn.total_changes
    return status


def updatealbum(uid, db=DATABASE, **kwargs):
    """
    Update record(s) from `albums` table.

    Can be propagated to both `discs`and `tracks` tables if album unique ID is updated.
    :param uid: `albums` row unique ID. Used as hieharchy starting point.
    :param db: Database storing `albums` table.
    :param kwargs: key-value pairs enumerating field-value to update.
    :return: Tuple composed of `albums` total change(s), `discs` total change(s) and `tracks` total change(s).
    """

    # 1.Define logger.
    logger = logging.getLogger("{0}.updatealbum".format(__name__))

    # 2. Initialize variables.
    acount, dsccount, tcount, query, inp_albumid, albumid, args, discs, tracks = 0, 0, 0, "", "", "", list(), list(), list()

    # 3. Connect to database.
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row

    # 4. Get album ID.
    for row in conn.execute("SELECT albumid FROM albums WHERE rowid=?", (uid,)):
        inp_albumid = row["albumid"]

    # 5. Get album, discs and tracks hieharchy if album ID is updated.
    if "albumid" in kwargs:
        for row in conn.execute("SELECT albumid FROM albums WHERE rowid=?", (uid,)):
            albumid = row["albumid"]
        if albumid:
            for drow in conn.execute("SELECT rowid, discid FROM discs WHERE albumid=?", (albumid,)):
                discs.append(drow["rowid"])
                for trow in conn.execute("SELECT rowid FROM tracks WHERE albumid=? AND discid=?", (albumid, drow["discid"])):
                    tracks.append(trow["rowid"])
        logger.debug(tracks)
        logger.debug(discs)

    # 6. Convert last played Unix epoch time into python datetime object.
    if "played" in kwargs:
        if isinstance(kwargs["played"], int):
            kwargs["played"] = datetime.utcfromtimestamp(kwargs["played"])
        elif isinstance(kwargs["played"], str) and kwargs["played"].isdigit():
            kwargs["played"] = datetime.utcfromtimestamp(int(kwargs["played"]))
        elif isinstance(kwargs["played"], datetime):
            pass
        else:
            del kwargs["played"]

    # 7. Update played count if increment by 1.
    icount, count = kwargs.get("icount", False), 0
    if icount:
        for row in conn.execute("SELECT count FROM albums WHERE rowid=?", (uid,)):
            count = row["count"] + 1
        kwargs["count"] = count

    # 8. Update played count if decrement by 1.
    dcount, count = kwargs.get("dcount", False), 0
    if dcount:
        for row in conn.execute("SELECT count FROM albums WHERE rowid=?", (uid,)):
            count = row["count"] - 1
        if count < 0:
            count = 0
        kwargs["count"] = count

    # 9. Set query.
    if "icount" in kwargs:
        del kwargs["icount"]
    if "dcount" in kwargs:
        del kwargs["dcount"]
    logger.debug(kwargs)
    for k, v in kwargs.items():
        query = "{0}{1}=?, ".format(query, k)  # album=?, albumid=?, "
        args.append(v)  # ["the album", "T.Toto.1.19840000.1.D1.T01.NNN"]
    args += (uid,)
    logger.debug(query)
    logger.debug(args)

    # 10. Update `albums` table.
    #     Update may be propagated to both `discs` and `tracks` tables.
    try:
        with conn:

            # ALBUMS table.
            conn.execute("UPDATE albums SET {0} WHERE rowid=?".format(query[:-2]), args)  # ["the album", "T.Toto.1.19840000.1.D1.T01.NNN", 1]
            acount = conn.total_changes

            if "albumid" in kwargs:
                # DISCS table.
                conn.executemany("UPDATE discs SET albumid=? WHERE rowid=?", [(kwargs["albumid"], i) for i in discs])
                dsccount = conn.total_changes - acount

                # TRACKS table.
                conn.executemany("UPDATE tracks SET albumid=? WHERE rowid=?", [(kwargs["albumid"], i) for i in tracks])
                tcount = conn.total_changes - acount - dsccount

    except (sqlite3.OperationalError, sqlite3.Error) as err:
        logger.exception(err)
        return "", 0, 0, 0

    # 11. Return total changes.
    logger.info("ALBUMS table: {0:>3d} record(s) updated.".format(acount))
    logger.info("DISCS table: {0:>3d} record(s) updated.".format(dsccount))
    logger.info("TRACKS table: {0:>3d} record(s) updated.".format(tcount))
    return inp_albumid, acount, dsccount, tcount


def updatelastplayeddate(*uid, db=DATABASE):
    status, conn = 0, sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    rows = chain.from_iterable([[(datetime.utcnow(), row["count"] + 1, rowid) for row in conn.execute("SELECT count FROM albums WHERE rowid=?", (rowid,))] for rowid in uid])
    with conn:
        conn.executemany("UPDATE albums SET played=?, count=? WHERE rowid=?", rows)
        status = conn.total_changes
    return status


def getlastplayeddate(db=DATABASE):
    record = namedtuple("record", "rowid albumid artist year album discs genre live bootleg incollection language upc encodingyear created origyear played count")
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute(
            "SELECT rowid, albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, encodingyear, created, origyear, played, count FROM albums ORDER BY played DESC"):
        yield record._make(row)


def getartist(db=DATABASE):
    record = namedtuple("record", "artistid artist")
    conn = sqlite3.connect(db)
    for row in conn.execute("SELECT substr(albumid, 3, length(albumid) - 2 - 13), artist FROM albums ORDER BY albumid"):
        yield record._make(row)
