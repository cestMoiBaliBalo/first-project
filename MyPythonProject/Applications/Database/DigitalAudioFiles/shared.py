# -*- coding: ISO-8859-1 -*-
import re
import json
import sqlite3
import logging
import argparse
from itertools import chain
from datetime import datetime
from ...shared import DATABASE
from contextlib import suppress
from collections import MutableSequence, namedtuple
from ..shared import Boolean, adapt_boolean, convert_boolean

__author__ = 'Xavier ROSSET'


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


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="table")

# ----- Table "ALBUMS".
parser_updatalb = subparsers.add_parser("albums")
parser_updatalb.add_argument("uid", type=int, nargs="+")
parser_updatalb.add_argument("--artist", help="Artist", action=DictArguments)
parser_updatalb.add_argument("--year", help="Year", type=int, action=DictArguments)
parser_updatalb.add_argument("--album", help="Album title", action=DictArguments)
parser_updatalb.add_argument("--genre", help="Genre", action=DictArguments)
parser_updatalb.add_argument("--discs", help="Discs number", type=int, action=DictArguments)

# ----- Table "TRACKS".
parser_updattck = subparsers.add_parser("tracks")
parser_updattck.add_argument("uid", type=int, nargs="+")
parser_updattck.add_argument("--title", help="Title", action=DictArguments)

# ----- Table "DISCS".
parser_updatdsc = subparsers.add_parser("discs")
parser_updatdsc.add_argument("uid", type=int, nargs="+")
parser_updatdsc.add_argument("--field", help="Define here the field to update", action=DictArguments)

# ----- Table "RIPPINGLOG".
parser_updatrip = subparsers.add_parser("rippinglog")
parser_updatrip.add_argument("uid", type=int, nargs="+")
parser_updatrip.add_argument("--field", help="Define here the field to update", action=DictArguments)


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


def select(db=DATABASE):
    record = namedtuple("record", "rowid albumid artist year album discs genre live bootleg incollection language upc encodingyear created origyear discid tracks trackid title")
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute("SELECT a.rowid, a.albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, encodingyear, a.created, origyear, b.discid, b.tracks, trackid, title "
                            "FROM albums a "
                            "JOIN discs b ON a.albumid=b.albumid "
                            "JOIN tracks c ON a.albumid=c.albumid AND b.discid=c.discid "
                            "ORDER BY a.albumid, b.discid, c.trackid"):
        yield record._make(row)


def select2(db=DATABASE):
    record = namedtuple("record", "rowid albumid artist year album discs genre live bootleg incollection language upc encodingyear created origyear discid tracks trackid title")
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute("SELECT a.rowid, a.albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, encodingyear, a.created, origyear, b.discid, b.tracks, trackid, title "
                            "FROM albums a "
                            "JOIN discs b ON a.albumid=b.albumid "
                            "JOIN tracks c ON a.albumid=c.albumid AND b.discid=c.discid "
                            "ORDER BY a.created DESC, a.albumid, b.discid, c.trackid"):
        yield record._make(row)


def selectfromartist(db=DATABASE, artist=None):
    print(artist)
    record = namedtuple("record", "rowid albumid")
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    statement = "SELECT rowid, albumid FROM albums ORDER BY albumid"
    argument = ()
    if artist:
        statement = "SELECT rowid, albumid FROM albums WHERE lower(substr(albumid, 3, length(albumid) - 2 - 13))=? OR lower(artist)=? ORDER BY albumid"  # A.Adams, Byran.1.19870000.1
        argument = (artist.lower(), artist.lower())
    print(argument)
    for row in conn.execute(statement, argument):
        yield record._make(row)


def selectfromgenre(genre, db=DATABASE):
    record = namedtuple("record", "rowid albumid")
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute("SELECT rowid, albumid FROM albums WHERE lower(genre)=? ORDER BY albumid", (genre.lower(),)):
        yield record._make(row)


def selectfromuid(uid, db=DATABASE):
    record = namedtuple("record", "rowid albumid")
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute("SELECT rowid, albumid FROM albums WHERE rowid=? ORDER BY albumid", (uid,)):
        yield record._make(row)


def selectalbums(db=DATABASE, albumid=None):

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


def selectdiscs(db=DATABASE, albumid=None, discid=None):

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


def selecttracks(db=DATABASE, albumid=None, discid=None, trackid=None):

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


def deletefromuid(uid, db=DATABASE):

    albumid, acount, dcount, tcount, discs, tracks, conn = None, 0, 0, 0, [], [], sqlite3.connect(db)
    conn.row_factory = sqlite3.Row

    for row in conn.execute("SELECT albumid FROM albums WHERE rowid=?", (uid,)):
        albumid = row["albumid"]
        for drow in conn.execute("SELECT rowid, discid FROM discs WHERE albumid=?", (row["albumid"],)):
            discs.append(drow["rowid"])
            for trow in conn.execute("SELECT rowid FROM tracks WHERE albumid=? AND discid=?", (row["albumid"], drow["discid"])):
                tracks.append(trow["rowid"])

    try:
        with conn:

            # TRACKS table.
            conn.executemany("DELETE FROM tracks WHERE rowid=?", [(i,) for i in tracks])
            tcount = conn.total_changes

            # DISCS table.
            conn.executemany("DELETE FROM discs WHERE rowid=?", [(i,) for i in discs])
            dcount = conn.total_changes - tcount

            # ALBUMS table.
            conn.execute("DELETE FROM albums WHERE rowid=?", (uid,))
            acount = conn.total_changes - tcount - dcount

    except (sqlite3.Error, ValueError):
        return albumid, 0, 0, 0

    return albumid, acount, dcount, tcount


def deletealbumsfromuid(*uid, db=DATABASE):

    status, conn = 0, sqlite3.connect(db)
    with conn:
        conn.executemany("DELETE FROM albums WHERE rowid=?", [(i,) for i in uid])
        status = conn.total_changes
    return status


def deletediscsfromuid(*uid, db=DATABASE):

    status, conn = 0, sqlite3.connect(db)
    with conn:
        conn.executemany("DELETE FROM discs WHERE rowid=?", [(i,) for i in uid])
        status = conn.total_changes
    return status


def deletetracksfromuid(*uid, db=DATABASE):

    status, conn = 0, sqlite3.connect(db)
    with conn:
        conn.executemany("DELETE FROM tracks WHERE rowid=?", [(i,) for i in uid])
        status = conn.total_changes
    return status


def updatealbum(*uid, db=DATABASE, **kwargs):

    logger = logging.getLogger("{0}.updatealbum".format(__name__))
    status, query, args = 0, "", []
    for k, v in kwargs.items():
        query = "{0}{1}=?, ".format(query, k)  # album=?, albumid=?, "
        args.append(v)  # ["the album", "T.Toto.1.19840000.1.D1.T01.NNN"]
    conn = sqlite3.connect(db)
    try:
        with conn:
            conn.executemany("UPDATE albums SET {0} WHERE rowid=?".format(query[:-2]), [tuple(chain(args, (rowid,))) for rowid in uid])
            # [("the album", "T.Toto.1.19840000.1.D1.T01.NNN", 1), ("the album", "T.Toto.1.19840000.1.D1.T01.NNN", 2), ("the album", "T.Toto.1.19840000.1.D1.T01.NNN", 3)]
            status = conn.total_changes
    except (sqlite3.OperationalError, sqlite3.Error) as err:
        logger.exception(err)
    else:
        logger.debug("{0:>3d} record(s) updated.".format(status))
    return status


def updatelastplayed(*uid, db=DATABASE):

    status, conn = 0, sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    rows = chain.from_iterable([[(datetime.utcnow(), row["count"] + 1, rowid) for row in conn.execute("SELECT count FROM albums WHERE rowid=?", (rowid,))] for rowid in uid])
    with conn:
        conn.executemany("UPDATE albums SET played=?, count=? WHERE rowid=?", rows)
        status = conn.total_changes
    return status


def getlastplayed(db=DATABASE):
    record = namedtuple("record", "rowid albumid artist year album discs genre live bootleg incollection language upc encodingyear created origyear played count")
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute("SELECT rowid, albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, encodingyear, created, origyear, played, count FROM albums ORDER BY played DESC"):
        yield record._make(row)

def getartist(db=DATABASE):
    record = namedtuple("record", "artistid artist")
    conn = sqlite3.connect(db)
    for row in conn.execute("SELECT substr(albumid, 3, length(albumid) - 2 - 13), artist FROM albums ORDER BY albumid"):
        yield record._make(row)
