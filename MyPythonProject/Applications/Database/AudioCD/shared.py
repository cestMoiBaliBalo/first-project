# -*- coding: ISO-8859-1 -*-
import json
import logging
import re
import sqlite3
from collections import MutableSequence, namedtuple
from datetime import datetime
from itertools import chain, groupby
from operator import itemgetter

from ...shared import DATABASE, LOCAL, TEMPLATE4, UPCREGEX, UTC, dateformat

__author__ = 'Xavier ROSSET'

# ==========
# Constants.
# ==========
GENRES = ["Rock", "Hard Rock", "Heavy Metal", "Trash Metal", "Alternative Rock", "Black Metal", "Progressive Rock", "French Pop"]


# ========
# Classes.
# ========
class InsertTracksfromFile(MutableSequence):
    def __init__(self, fil):
        self._seq = []
        for artist, year, album, genre, productcode, albumsort, artistsort in json.load(fil):

            # Check if year is valid.
            try:
                year = validyear(year)
            except ValueError:
                continue

            # Check if genre is valid.
            try:
                genre = validgenre(genre)
            except ValueError:
                continue

            # Check if productcode is valid.
            try:
                productcode = validproductcode(productcode)
            except ValueError:
                continue

            # Check if albumsort is valid.
            try:
                albumsort = validalbumsort(albumsort)
            except ValueError:
                continue

            timestamp = datetime.now()
            # if seconds:
            #     timestamp = datetime.fromtimestamp(seconds)
            self._seq.append((timestamp, artist, year, album, productcode, genre, "dBpoweramp 15.1", albumsort, artistsort))

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


def validgenre(s):
    if s.lower() not in (genre.lower() for genre in GENRES):
        raise ValueError('"{0}" is not a valid genre'.format(s))
    return s


def validalbumsort(s):
    regex = re.compile("^(?=[\d.]+$)(?=.\.[^.]+\..$)(?=\d\.\d{8}\.\d$).\.(?:19[6-9]|20[01])\d{5}\..$")
    if not regex.match(s):
        raise ValueError('"{0}" is not a valid albumsort'.format(s))
    return s


def validproductcode(s):
    regex = re.compile(UPCREGEX)
    if s:
        if not regex.match(s):
            raise ValueError('"{0}" is not a valid productcode'.format(s))
    return s


def logrecord(t, func):
    rowid, ripped, artist, year, album, upc, genre, application, albumsort, artistsort = t
    logger = logging.getLogger("{0}.{1}".format(__name__, func))
    logger.info("----------------")
    logger.info("Selected record.")
    logger.info("----------------")
    logger.info("\tRowID\t\t\t: {0}".format(rowid).expandtabs(3))
    logger.info("\tRipped\t\t: {0}".format(dateformat(LOCAL.localize(ripped), TEMPLATE4)).expandtabs(3))
    logger.info("\tArtist\t\t: {0}".format(artist).expandtabs(3))
    logger.info("\tYear\t\t\t: {0}".format(year).expandtabs(3))
    logger.info("\tAlbum\t\t\t: {0}".format(album).expandtabs(3))
    logger.info("\tUPC\t\t\t: {0}".format(upc).expandtabs(3))
    logger.info("\tGenre\t\t\t: {0}".format(genre).expandtabs(3))
    logger.info("\tAlbumSort\t: {0}".format(albumsort).expandtabs(3))
    logger.info("\tArtistSort\t: {0}".format(artistsort).expandtabs(3))


# =======================================
# Main functions for working with tables.
# =======================================
def insertfromfile(fil, db=DATABASE):
    status, tracks = 0, InsertTracksfromFile(fil)
    if len(tracks):
        conn = sqlite3.connect(db)
        with conn:
            conn.executemany("INSERT INTO rippinglog (ripped, artist, year, album, upc, genre, application, albumsort, artistsort) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", tracks)
            status = conn.total_changes
            logger = logging.getLogger("{0}.insertfromfile".format(__name__))
            logger.debug("{0} records inserted.".format(status))
            if status:
                for item in tracks:  # "item" est un tuple.
                    logger.debug(item)
    return status


def insertfromargs(db=DATABASE, **kwargs):
    temp_dict = {key: value for key, value in kwargs.items() if key in ["artist", "year", "album", "upc", "genre", "application", "albumsort", "artistsort"]}
    temp_dict.update(ripped=datetime.fromtimestamp(int(kwargs.get("ripped", UTC.localize(datetime.utcnow()).astimezone(LOCAL).timestamp()))))
    fields = ", ".join(sorted(temp_dict.keys()))
    placeholders = ", ".join(["?"] * len(temp_dict))
    values = ([item[1] for item in sorted(temp_dict.items(), key=itemgetter(0))],)
    statement = "INSERT INTO rippinglog ({0}) VALUES({1})".format(fields, placeholders)
    logger = logging.getLogger("{0}.insertfromargs".format(__name__))
    logger.debug(statement)
    logger.debug(values)
    conn = sqlite3.connect(db)
    with conn:
        conn.executemany(statement, values)
        status = conn.total_changes
        logger.debug("{0} records inserted.".format(status))
    return status


def deletelog(*uid, db=DATABASE):
    status, conn = 0, sqlite3.connect(db)
    with conn:
        conn.executemany("DELETE FROM rippinglog WHERE id=?", [(item,) for item in uid])
        status = conn.total_changes
        logger = logging.getLogger("{0}.deletelog".format(__name__))
        logger.debug("{0} records removed.".format(status))
        if status:
            for item in uid:
                logger.debug("Unique ID: {0:>4d}.".format(item))
    return status


def selectlogs(db=DATABASE):
    record = namedtuple("record", "rowid ripped artist year album upc genre application albumsort artistsort")
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute("SELECT * FROM rippinglog ORDER BY ripped, artistsort, albumsort"):
        logrecord(tuple(row), "select")
        yield record._make(row)


def selectlog(*uid, db=DATABASE):
    record = namedtuple("record", "rowid ripped artist year album upc genre application albumsort artistsort")
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    curs = conn.cursor()
    for rowid in uid:
        curs.execute("SELECT * FROM rippinglog WHERE rowid=?", (rowid,))
        yield record._make(curs.fetchall()[0])


def selectlogsfrommonth(*month, db=DATABASE):
    record = namedtuple("record", "rowid ripped artist year album upc genre application albumsort artistsort")
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute("SELECT * FROM rippinglog ORDER BY ripped DESC"):
        logrecord(tuple(row), "selectlogsfrommonth")
        if int(LOCAL.localize(tuple(row)[1]).strftime("%Y%m")) in month:
            yield record._make(row)


def updatelog(*uid, db=DATABASE, **kwargs):
    logger = logging.getLogger("{0}.update".format(__name__))
    status, query, args = 0, "", []

    if "ripped" in kwargs:
        if isinstance(kwargs["ripped"], int):
            kwargs["ripped"] = datetime.fromtimestamp(kwargs["ripped"])
        elif isinstance(kwargs["ripped"], str) and kwargs["ripped"].isdigit():
            kwargs["ripped"] = datetime.fromtimestamp(int(kwargs["ripped"]))
        elif isinstance(kwargs["ripped"], datetime):
            pass
        else:
            del kwargs["ripped"]

    for k, v in kwargs.items():
        query = "{0}{1}=?, ".format(query, k)  # album=?, albumid=?, "
        args.append(v)  # ["the album", "T.Toto.1.19840000.1.D1.T01.NNN"]
    conn = sqlite3.connect(db)
    try:
        with conn:
            conn.executemany("UPDATE rippinglog SET {0} WHERE rowid=?".format(query[:-2]), [tuple(chain(args, (rowid,))) for rowid in uid])
            # [("the album", "T.Toto.1.19840000.1.D1.T01.NNN", 1), ("the album", "T.Toto.1.19840000.1.D1.T01.NNN", 2), ("the album", "T.Toto.1.19840000.1.D1.T01.NNN", 3)]
            status = conn.total_changes
    except (sqlite3.OperationalError, sqlite3.Error) as err:
        logger.exception(err)
    else:
        logger.debug("{0:>3d} record(s) updated.".format(status))
    return status


def getmonths(db=DATABASE):
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    reflist = sorted(set([(LOCAL.localize(row[0]).strftime("%Y%m"), LOCAL.localize(row[0]).strftime("%B").capitalize()) for row in conn.execute("SELECT ripped FROM rippinglog ORDER BY ripped DESC")]),
                     key=itemgetter(0))
    for key, group in groupby(reflist, key=lambda i: i[0][:4]):
        yield key, list(group)
