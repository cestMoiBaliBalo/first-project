# -*- coding: ISO-8859-1 -*-
# pylint: disable=invalid-name
import json
import logging
import os
import re
import sqlite3
import sys
from collections import namedtuple
from contextlib import ContextDecorator, ExitStack
from contextlib import suppress
from datetime import datetime
from functools import partial
from itertools import compress, groupby, product, repeat, starmap
from operator import itemgetter
from string import Template
from subprocess import run

import jinja2
import yaml

from ..shared import ToBoolean, adapt_booleanvalue, convert_tobooleanvalue
from ...parsers import subset_parser
from ...shared import DATABASE, LOCAL, TEMPLATE4, TemplatingEnvironment, UTC, dateformat, left_justify, rjustify, validdatetime

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ================
# SQLite3 adapter.
# ================
sqlite3.register_adapter(ToBoolean, adapt_booleanvalue)

# ==================
# SQLite3 converter.
# ==================
sqlite3.register_converter("boolean", convert_tobooleanvalue)


# ========================
# Miscellaneous functions.
# ========================
def check_defaultalbum(item):
    """

    :param item:
    :return:
    """
    # Check `item` content.
    return True


def check_bootlegalbum(item):
    """

    :param item:
    :return:
    """
    # Check `item` content.
    return True


def toboolean(*args):
    """

    :param args:
    :return:
    """

    def inner_func(arg):
        returned = arg
        try:
            lower_arg = arg.lower()
        except AttributeError:
            pass
        else:
            if lower_arg in ["n", "y"]:
                returned = ToBoolean(arg)
        return returned

    return tuple(map(inner_func, args))


def merge(item):
    """
    
    :param item: 
    :return: 
    """
    table, track = item
    return (table,) + track


def translate_orderfield(match):
    if match:
        item = SORT.get(match.group(1))
        if not item:
            return item
        if match.group(2):
            item = "{0} {1}".format(item, match.group(2).upper())
        return item


# ==========
# Constants.
# ==========
COVER = Template("albumart/$letter/$artistsort/$albumsort/iPod-Front.jpg")
FUNCTIONS = {"defaultalbums": check_defaultalbum,
             "bootlegalbums": check_bootlegalbum}
# TABLES = {"defaultalbums": ["artists", "albums", "discs", "tracks", "defaultalbums"],
#           "bootlegalbums": ["artists", "albums", "discs", "tracks", "bootlegalbums"]}
# SELECTORS = {"defaultalbums": {"artists": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
#                                "albums": [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1],
#                                "discs": [0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
#                                "tracks": [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0],
#                                "rippeddiscs": [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                                "defaultalbums": [0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
#              "bootlegalbums": {"artists": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
#                                "albums": [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
#                                "discs": [0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                                "tracks": [0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                                "rippeddiscs": [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                                "bootlegalbums": [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
#                                "bootlegdiscs": [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
#                                "bonuses": [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]}}
# STATEMENTS = {
#     "default": {
#         "artists": "INSERT INTO artists (artistsort, artist) VALUES (?, ?)",
#         "albums": "INSERT INTO albums (albumid, discs, genreid, is_bootleg, is_deluxe, languageid, artistsort, in_collection) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
#         "discs": "INSERT INTO discs (albumid, discid, tracks, is_live) VALUES (?, ?, ?, ?)",
#         "tracks": "INSERT INTO tracks (albumid, discid, trackid, is_bonus, is_live, title) VALUES (?, ?, ?, ?, ?, ?)",
#         "rippeddiscs": "INSERT INTO rippeddiscs (albumid, discid) VALUES (?, ?)",
#         "bootlegalbums": "INSERT INTO bootlegalbums (albumid, bootleg_date, bootleg_city, bootleg_countryid, bootleg_tour, bootleg_providerid, bootleg_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
#         "bootlegdiscs": "INSERT INTO bootlegdiscs (albumid, discid, disc_reference) VALUES (?, ?, ?)",
#         "bonuses": "INSERT INTO bonuses (albumid, discid, trackid, bootleg_date, bootleg_city, bootleg_countryid, bootleg_tour) VALUES (?, ?, ?, ?, ?, ?, ?)",
#         "defaultalbums": "INSERT INTO defaultalbums (albumid, origyear, year, album, label, upc) VALUES (?, ?, ?, ?, ?, ?)"},
#     "bootlegalbums": {
#         "albums": "INSERT INTO albums (albumid, discs, genreid, is_bootleg, languageid, artistsort, in_collection) VALUES (?, ?, ?, ?, ?, ?, ?)"}}
SORT = {"rowid": "album_rowid",
        "created": "utc_created",
        "modified": "utc_modified"}
with open(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tables", "configuration.yml"), encoding="UTF_8") as stream:
    config = yaml.load(stream)
statements = config["statements"]
selectors = config["selectors"]
tables = config["tables"]

# ====================
# Regular expressions.
# ====================
REX = re.compile(r"^(\w+)(?: (ASC|DESC))?$", re.IGNORECASE)


# ========
# Classes.
# ========
class DatabaseConnection(ContextDecorator):
    def __init__(self, db=DATABASE):
        self.database = db

    def __enter__(self):
        self.conn = sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


# class InsertDigitalAlbum(MutableSequence):
#     """

# """
# logger = logging.getLogger("{0}.InsertDigitalAlbum".format(__name__))

# @classmethod
# def fromjson(cls, fil):
#     """

# :param fil:
# :return:
# """
# onetrack = namedtuple("onetrack",
#                       "database albumid albumsort titlesort artist year album genre discnumber totaldiscs label tracknumber totaltracks title live bootleg incollection upc language origyear")
# return cls(*[onetrack._make(track) for track in json.load(fil)])
# return cls(*json.load(fil))

# def __init__(self, *tracks):
#     self._tracks, _selectors = [], []
#     for _ in tracks:
#         _selectors.append(True)
#     _tracks = list(compress(tracks, _selectors))
#     for track in _tracks:
#         track.extend([datetime.utcnow(), datetime.utcnow()])
#         self._tracks.extend(track)

# 0. Check if `database` is valid.
# try:
#     database = validdb(track.database)
# except ValueError as err:
#     self.logger.debug(err)
#     continue

# 1. Check if `year` is valid.
# try:
#     year = validyear(track.year)
# except ValueError as err:
#     self.logger.debug(err)
#     continue

# 2. Check if `genre` is valid.
# try:
#     genre = validgenre(track.genre)
# except ValueError as err:
#     self.logger.debug(err)
#     continue

# 3. Check if `discnumber` is valid.
# try:
#     discnumber = int(track.discnumber)
# except ValueError as err:
#     self.logger.debug(err)
#     continue

# 4. Check if `totaldiscs` is valid.
# try:
#     totaldiscs = int(track.totaldiscs)
# except ValueError as err:
#     self.logger.debug(err)
#     continue

# 5. Check if `tracknumber` is valid.
# try:
#     tracknumber = int(track.tracknumber)
# except ValueError as err:
#     self.logger.debug(err)
#     continue

# 6. Check if `totaltracks` is valid.
# try:
#     totaltracks = int(track.totaltracks)
# except ValueError as err:
#     self.logger.debug(err)
#     continue

# 7. Check if `product code` is valid.
# upc = ""
# if track.upc:
#     try:
#         upc = validproductcode(track.upc)
#     except ValueError as err:
#         self.logger.debug(err)
#         continue

# 8. Check `origyear`.
# try:
#     origyear = validyear(track.origyear)
# except ValueError as err:
#     self.logger.debug(err)
#     origyear = 0

# 9. Set records creation date. Stored into local time zone.

# 9.a. `albums` records.
# album_created = datetime.utcnow()
# with suppress(AttributeError):
#     album_created = datetime.utcfromtimestamp(track.album_created)

# 9.b. `discs` records.
# disc_created = datetime.utcnow()
# with suppress(AttributeError):
#     disc_created = datetime.utcfromtimestamp(track.disc_created)

# 9.c. `tracks` records.
# track_created = datetime.utcnow()
# with suppress(AttributeError):
#     track_created = datetime.utcfromtimestamp(track.track_created)

# 10. Set album last played date. Stored into UTC time zone.
# lastplayeddate = None
# with suppress(AttributeError):
#     lastplayeddate = track.lastplayed
# if lastplayeddate:
#     lastplayeddate = datetime.utcfromtimestamp(int(lastplayeddate))
#     self.logger.debug("Last played date: %s", UTC.localize(lastplayeddate).astimezone(LOCAL))

# 11. Set album played count.
# playedcount = "0"
# with suppress(AttributeError):
#     playedcount = track.playedcount
# if playedcount:
#     playedcount = int(playedcount)
#     self.logger.debug("Played count: %s", playedcount)


# 12. Split attributes into three tuples respective to the three focused tables.

# 12.a. `albums` table.
# albums_tuple = (track.albumid[:-11], track.artist, year, track.album, totaldiscs, genre, ToBoolean(track.live), ToBoolean(track.bootleg), ToBoolean(track.incollection), track.language, upc,
#                 album_created, origyear, lastplayeddate, playedcount)

# 12.b. `discs` table.
# discs_tuple = (track.albumid[:-11], discnumber, totaltracks, disc_created)

# 12.c. `tracks` table.
# tracks_tuple = (track.albumid[:-11], discnumber, tracknumber, track.title, track_created)

# 13. Gather tuples together into a single list.
# self._tracks.append((database, albums_tuple, discs_tuple, tracks_tuple))

# self.logger.debug(self._tracks)
# if self._tracks:
#     self._tracks = sorted(sorted(sorted(sorted(self._tracks, key=lambda i: i[3][2]), key=lambda i: i[3][1]), key=lambda i: i[3][0]), key=itemgetter(0))

# def __getitem__(self, item):
#     return self._tracks[item]
#
# def __setitem__(self, key, value):
#     self._tracks[key] = value
#
# def __delitem__(self, key):
#     del self._tracks[key]
#
# def __len__(self):
#     return len(self._tracks)
#
# def insert(self, index, value):
#     self._tracks.insert(index, value)


# =======================================
# Main functions for working with tables.
# =======================================
def filterfunc(item, artistsort=None, albumsort=None):
    """

    :param item:
    :param artistsort:
    :param albumsort:
    :return:
    """
    if any([artistsort, albumsort]):
        if artistsort and item.albumid[2:-13] not in artistsort:
            return False
        if albumsort and item.albumid[-12:] not in albumsort:
            return False
    return True


def insertfromfile(*files):
    """
    Insert digital album(s) into the digital audio base.
    Albums are taken from JSON file-object(s) or XML file-object(s).

    :param files: file-object(s) where the albums are taken from.
    :return: database total changes.
    """
    logger = logging.getLogger("{0}.insertfromfile".format(__name__))
    tracks, total_changes = [], 0
    for file in files:
        tracks.extend(json.load(file))
    for profile, group1 in groupby(sorted(sorted(tracks, key=itemgetter(1)), key=itemgetter(0)), key=itemgetter(0)):
        primary_group = starmap(toboolean, list(filter(FUNCTIONS[profile], group1)))
        for database, secondary_group in groupby(primary_group, key=itemgetter(1)):
            with ExitStack() as stack:
                conn = stack.enter_context(DatabaseConnection(database))
                stack.enter_context(conn)
                tracks = list(map(merge, product(TABLES[profile], secondary_group)))
                statements = STATEMENTS.get(profile, STATEMENTS["default"])
                logger.debug(profile)
                logger.debug(statements)

                # Shared tables.
                for track in tracks:
                    table = track[0]
                    logger.debug(table)
                    logger.debug(track)
                    with suppress(sqlite3.IntegrityError):
                        conn.execute(statements.get(table, STATEMENTS["default"][table]), tuple(compress(track, SELECTORS[profile][table])))

                # "rippeddiscs" table.
                table = "rippeddiscs"
                for track in filter(lambda i: i[0].lower() == "discs", filter(lambda i: i[5] == 1, tracks)):
                    logger.debug(track)
                    with suppress(sqlite3.IntegrityError):
                        conn.execute(statements.get(table, STATEMENTS["default"][table]), tuple(compress(track, SELECTORS[profile][table])))

                # "bonuses" table.
                table = "bonuses"
                for track in filter(lambda i: i[8].bool, filter(lambda i: i[1].lower() == "bootlegalbums", tracks)):
                    with suppress(sqlite3.IntegrityError):
                        conn.execute(statements.get(table, STATEMENTS["default"][table]), tuple(compress(track, SELECTORS[profile][table])))

                # "bootlegdiscs" table.
                table = "bootlegdiscs"
                for track in filter(lambda i: i[27] is not None, filter(lambda i: i[1].lower() == "bootlegalbums", tracks)):
                    with suppress(sqlite3.IntegrityError):
                        conn.execute(statements.get(table, STATEMENTS["default"][table]), tuple(compress(track, SELECTORS[profile][table])))

                total_changes = conn.total_changes

    return total_changes


def getalbumdetail(db=DATABASE, **kwargs):
    for row in _getalbumdetail(db, **kwargs):
        yield row


def getgroupedalbums(db=DATABASE, **kwargs):
    """

    :param db:
    :param kwargs:
    :return:
    """
    logger = logging.getLogger("{0}.getgroupedalbums".format(__name__))
    tabsize = 3
    func = partial(filterfunc, artistsort=kwargs.get("artistsort"), albumsort=kwargs.get("albumsort"))
    albumslist = ((item.albumid[2:-13],
                   item.artist,
                   item.albumid[-12:],
                   item.discid,
                   item.trackid,
                   item.title,
                   item.genre,
                   item.live,
                   item.bootleg,
                   item.incollection,
                   UTC.localize(item.utc_created).astimezone(LOCAL).strftime("%d/%m/%Y %H:%M:%S %Z (UTC%z)"),
                   item.album) for item in filter(func, _getalbumdetail(db)))
    albumslist = sorted(sorted(sorted(sorted(albumslist, key=itemgetter(4)), key=itemgetter(3)), key=itemgetter(2)), key=lambda i: (i[0], i[1]))
    for album in albumslist:
        logger.debug("----------------")
        logger.debug("Selected record.")
        logger.debug("----------------")
        logger.debug("\tArtistsort\t: %s".expandtabs(tabsize), album[0])
        logger.debug("\tAlbumsort\t: %s".expandtabs(tabsize), album[2])
        logger.debug("\tTitle\t\t\t: %s".expandtabs(tabsize), album[5])
    for artistsort, artist, albums in ((artistsort, artist,
                                        [(albumid,
                                          [(discid,
                                            [(trackid, list(sssgroup)) for trackid, sssgroup in groupby(ssgroup, key=itemgetter(4))]) for discid, ssgroup in groupby(subgroup, key=itemgetter(3))]) for
                                         albumid, subgroup in
                                         groupby(group, key=itemgetter(2))]) for (artistsort, artist), group in groupby(albumslist, key=lambda i: (i[0], i[1]))):
        yield artistsort, artist, albums


def getalbumidfromartist(arg=None, db=DATABASE):
    """
    Get album(s) ID matching the input artist.

    :param arg: Requested artist.
    :param db: Database storing `albums` table.
    :return: Album(s) unique ID list.
    """
    kwargs = dict()
    if arg:
        kwargs = dict(artist=arg, artistsort=arg)
    for row in _getalbumid(db, **kwargs):
        yield row


def getalbumidfromgenre(arg=None, db=DATABASE):
    """
    Get album(s) ID matching the input genre.

    :param arg: Requested genre.
    :param db: Database storing `albums` table.
    :return: Album(s) unique ID list.
    """
    kwargs = dict()
    if arg:
        kwargs = dict(genre=arg)
    for row in _getalbumid(db, **kwargs):
        yield row


def getalbumidfromalbumsort(arg=None, db=DATABASE):
    """
    Get album(s) ID matching the input albumsort.

    :param arg: Requested albumsort.
    :param db: Database storing `albums` table.
    :return: Album(s) unique ID list.
    """
    kwargs = dict()
    if arg:
        kwargs = dict(albumsort=arg)
    for row in _getalbumid(db, **kwargs):
        yield row


def checkalbumid(albumid, *, db=DATABASE):
    conn = sqlite3.connect(db)
    curs = conn.cursor()
    curs.execute("SELECT count(*) FROM albums WHERE albumid=?", (albumid,))
    count = curs.fetchone()[0]
    conn.close()
    return bool(count)


def getalbumid(uid, *, db=DATABASE):
    """
    Get album ID matching the input unique ROWID.

    :param uid: Requested ROWID.
    :param db: Database storing `albums` table.
    :return: Album unique ID.
    """
    for row in _getalbumid(db, rowid=uid):
        yield row


def getrowid(*albumid, db=DATABASE):
    """
    Get `albums` ROWID matching the input primary keys.

    :param albumid: List of primary keys.
    :param db: Database storing `albums` table.
    :return: List of matching ROWID.
    """
    results = []
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    for value1, value2 in [(key.lower(), "%{0}%".format(key.lower())) for key in albumid]:
        for row in conn.execute("SELECT rowid, albumid FROM albums WHERE lower(albumid)=? OR lower(albumid) LIKE ?", (value1, value2)):
            results.append((row["rowid"], row["albumid"]))
    conn.close()
    if results:
        for rowid, albumid in results:
            yield rowid, albumid


def getalbumheader(db=DATABASE, **kwargs):
    """
    Get album detail matching the input primary key.

    :param db:
    :param kwargs:
    :return: Album detail gathered into a namedtuple.
    """
    logger = logging.getLogger("{0}.getalbumheader".format(__name__))
    tabsize = 3
    # """
    headers = list(left_justify(["\t{0}".format(item).expandtabs(tabsize) for item in ["Row ID", "Album ID", "ArtistSort", "AlbumSort", "Artist", "Album", "Cover", "Genre", "Created"]]))
    # """
    Album = namedtuple("Album", "rowid albumid artistsort albumsort artist discs genre bootleg incollection language utc_created utc_modified album cover")
    # """
    albums = [(row.rowid,
               row.albumid,
               row.artistsort,
               row.albumsort,
               row.artist,
               row.discs,
               row.genre,
               row.bootleg,
               row.incollection,
               row.language,
               row.utc_created,
               row.utc_modified,
               row.album,
               COVER.substitute(path=os.path.join(os.path.expandvars("%_MYDOCUMENTS%"), "Album Art"), letter=row.artistsort[0], artistsort=row.artistsort, albumsort=row.albumsort))
              for row in _getalbumdetail(db, **kwargs)]
    albums = sorted(set(albums), key=itemgetter(1))
    # """
    for album in albums:
        row = Album._make(album)
        logger.debug("================")
        logger.debug("Selected record.")
        logger.debug("================")
        for key, value in zip(headers,
                              (row.rowid, row.albumid, row.artistsort, row.albumsort, row.artist, row.album, row.cover, row.genre, dateformat(UTC.localize(row.utc_created).astimezone(LOCAL), TEMPLATE4))):
            logger.debug("%s: %s", key, value)
        yield row


def getdischeader(db=DATABASE, albumid=None, discid=None):
    """
    Get disc detail matching primary keys.

    :param db: Database storing `discs` table.
    :param albumid: album primary key. Optional.
    :param discid: disc primary key. Optional.
    :return: Yield a tuple composed of ROWID, album unique ID, disc unique ID and track unique ID.
    """
    sql, where, orderby, args, rows = "SELECT rowid, albumid, discid, tracks FROM discs ", "", "", (), []
    Disc = namedtuple("Disc", "rowid albumid discid tracks")

    # 1. Get one album.
    if albumid:
        where = "{0}albumid=? AND ".format(where)
        orderby = discid
        args += (albumid,)

    # 2. Get one disc.
    if albumid and discid:
        where = "{0}discid=? AND ".format(where)
        args += (discid,)

    # 3. Run SQL statement.
    statement = "{0}ORDER BY rowid".format(sql)
    if where:
        statement = "{0}WHERE {1} ORDER BY rowid".format(sql, where[:-5])
        if orderby:
            statement = "{0}WHERE {1} ORDER BY {2}".format(sql, where[:-5], orderby)
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute(statement, args):
        rows.append(Disc._make(row))
    conn.close()
    for row in rows:
        yield row


def getplayedcount(albumid, *, db=DATABASE):
    conn = sqlite3.connect(db)
    curs = conn.cursor()
    curs.execute("SELECT rowid, played FROM albums WHERE albumid=?", (albumid,))
    try:
        rowid, played = curs.fetchone()
    except TypeError:
        rowid, played = None, 0
    finally:
        conn.close()
    return rowid, played


def gettrack(db=DATABASE, albumid=None, discid=None, trackid=None):
    """
    Get track(s) detail matching both the input unique album ID, the disc unique ID and the track unique ID.

    :param db: Database storing `discs` table.
    :param albumid: Requested album unique ID. Optional.
    :param discid: Requested disc unique ID. Optional.
    :param trackid: Requested track unique ID. Optional.
    :return: Yield a tuple composed of ROWID, album unique ID, disc unique ID, track unique ID and title.
    """
    Track, args, where, orderby, sql, rows = namedtuple("Track", "rowid albumid discid trackid title"), (), "", "", "SELECT rowid, albumid, discid, trackid, title FROM tracks ", []

    # 1. Get one album.
    if albumid:
        where = "{0}albumid=? AND ".format(where)
        orderby = "discid, trackid"
        args += (albumid,)

    # 2. Get one disc.
    if albumid and discid:
        where = "{0}discid=? AND ".format(where)
        orderby = "trackid"
        args += (discid,)

    # 3. Get one track.
    if albumid and discid and trackid:
        where = "{0}trackid=? AND ".format(where)
        args += (trackid,)

    # 4. Run SQL statement.
    statement = "{0}ORDER BY rowid".format(sql)
    if where:
        statement = "{0}WHERE {1} ORDER BY rowid".format(sql, where[:-5])
        if orderby:
            statement = "{0}WHERE {1} ORDER BY {2}".format(sql, where[:-5], orderby)
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute(statement, args):
        rows.append(Track._make(row))
    conn.close()
    for row in rows:
        yield row


def deletealbum(db=DATABASE, uid=None, albumid=None):
    """
    Delete a digital album.

    :param db: Database storing `albums`, `discs` and `tracks` tables.
    :param uid: `albums` ROWID. Optional. Used as hieharchy starting point.
    :param albumid: `albums` album unique ID. Optional. Used as hieharchy starting point.
    :return: Tuple composed of deleted album unique ID, `albums` total change(s), `discs` total change(s) and `tracks` total change(s).
    """

    # 1.Define logger.
    logger = logging.getLogger("{0}.deletealbum".format(__name__))

    # 1. Initialize variables.
    acount, dcount, tcount, discs, tracks, inp_uid, inp_albumid = 0, 0, 0, [], [], uid, albumid

    # 2. Connect to database.
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

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

    except sqlite3.IntegrityError as err:
        logger.exception(err)

    finally:
        logger.info("ALBUMS table: {0:>3d} record(s) deleted.".format(acount))
        logger.info("DISCS table : {0:>3d} record(s) deleted.".format(dcount))
        logger.info("TRACKS table: {0:>3d} record(s) deleted.".format(tcount))

    # 7. Return total changes.
    return inp_albumid, acount, dcount, tcount


def deletealbumheader(*uid, db=DATABASE):
    """
    Delete album(s) from `albums` table.

    :param uid: List of ROWID.
    :param db: Database storing `albums` table.
    :return: Total changes.
    """
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA foreign_keys = ON")
    for i in uid:
        with suppress(sqlite3.IntegrityError):
            conn.execute("DELETE FROM albums WHERE rowid=?", (i,))
    changes = conn.total_changes
    conn.commit()
    conn.close()
    return changes


def deletedischeader(*uid, db=DATABASE):
    """
    Delete disc(s) from `discs` table.

    :param uid: List of ROWID.
    :param db: Database storing `discs` table.
    :return: Total changes.
    """
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA foreign_keys = ON")
    for i in uid:
        with suppress(sqlite3.IntegrityError):
            conn.execute("DELETE FROM discs WHERE rowid=?", (i,))
    changes = conn.total_changes
    conn.commit()
    conn.close()
    return changes


def deletetrack(*uid, db=DATABASE):
    """
    Delete track(s) from `tracks` table.

    :param uid: List of  ROWID.
    :param db: Database storing `tracks` table.
    :return: Total changes.
    """
    conn = sqlite3.connect(db)
    with conn:
        conn.executemany("DELETE FROM tracks WHERE rowid=?", [(i,) for i in uid])
    changes = conn.total_changes
    conn.close()
    return changes


def updatealbum(uid, db=DATABASE, **kwargs):
    """
    Update record from `albums` table.

    Can be propagated to both `discs`and `tracks` tables if album unique ID is updated.
    :param uid: `albums` ROWID. Used as hieharchy starting point.
    :param db: Database storing `albums` table.
    :param kwargs: key-value pairs enumerating field-value to update.
    :return: Tuple composed of `albums` total change(s), `discs` total change(s) and `tracks` total change(s).
    """
    d = {False: 0, True: 1}

    # 1.Define logger.
    logger = logging.getLogger("{0}.updatealbum".format(__name__))

    # 2. Initialize variables.
    albcount, dsccount, trkcount, query, args, discs, tracks = 0, 0, 0, "", [], [], []

    # 3. Connect to database.
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    # 4. Get album ID.
    curs = conn.cursor()
    curs.execute("SELECT albumid FROM albums WHERE rowid=?", (uid,))
    try:
        inp_albumid = curs.fetchone()[0]
    except TypeError:
        inp_albumid = None

    # 5. Get album, discs and tracks hieharchy if album ID is updated.
    # if "albumid" in kwargs:
    #     curs = conn.cursor()
    #     curs.execute("SELECT albumid FROM albums WHERE rowid=?", (uid,))
    #     try:
    #         albumid = curs.fetchone()[0]
    #     except TypeError:
    #         albumid = None
    #     if albumid:
    #         for drow in conn.execute("SELECT rowid, discid FROM discs WHERE albumid=?", (albumid,)):
    #             discs.append(drow["rowid"])
    #             for trow in conn.execute("SELECT rowid FROM tracks WHERE albumid=? AND discid=?", (albumid, drow["discid"])):
    #                 tracks.append(trow["rowid"])
    # logger.debug(tracks)
    # logger.debug(discs)

    # 6. Convert last played Unix epoch time into python datetime object.
    if "utc_played" in kwargs:
        try:
            kwargs["utc_played"] = LOCAL.localize(validdatetime(kwargs["utc_played"])[1]).astimezone(UTC).replace(tzinfo=None)
        except ValueError:
            del kwargs["utc_played"]

    # 7. Update played count if increment by 1.
    icount = kwargs.get("icount", False)
    if icount:
        curs = conn.cursor()
        curs.execute("SELECT played FROM albums WHERE rowid=?", (uid,))
        kwargs["played"] = curs.fetchone()[0] + 1
        del kwargs["icount"]

    # 8. Update played count if decrement by 1.
    dcount = kwargs.get("dcount", False)
    if dcount:
        curs = conn.cursor()
        curs.execute("SELECT played FROM albums WHERE rowid=?", (uid,))
        played = curs.fetchone()[0] - 1
        if played < 0:
            played = 0
        kwargs["played"] = played
        del kwargs["dcount"]

    # 9. Adapt `live` tag value from boolean to integer.
    if "live" in kwargs:
        kwargs["live"] = d[kwargs["live"]]

    # 10. Adapt `bootleg` tag value from boolean to integer.
    if "bootleg" in kwargs:
        kwargs["bootleg"] = d[kwargs["bootleg"]]

    # 11. Adapt `incollection` tag value from boolean to integer.
    if "incollection" in kwargs:
        kwargs["incollection"] = d[kwargs["incollection"]]

    # 12. Set query.
    logger.debug(kwargs)
    for k, v in kwargs.items():
        query = "{0}{1}=?, ".format(query, k)  # album=?, albumid=?, "
        args.append(v)  # ["the album", "T.Toto.1.19840000.1.D1.T01.NNN"]
    if query:
        query = "{0}utc_modified=?, ".format(query)  # album=?, albumid=?, utc_modified=?, "
        args.append(UTC.localize(datetime.utcnow()).replace(tzinfo=None))  # ["the album", "T.Toto.1.19840000.1.D1.T01.NNN", datetime(2017, 10, 21, 16, 30, 45, tzinfo=timezone("utc"))]
    args += (uid,)
    logger.debug(query)
    logger.debug(args)

    # 13. Update `albums` table.
    #     Update may be propagated to both `discs` and `tracks` tables.
    try:
        with conn:

            # ALBUMS table.
            conn.execute("UPDATE albums SET {0} WHERE rowid=?".format(query[:-2]), args)  # ["the album", "T.Toto.1.19840000.1.D1.T01.NNN", 1]

            # DISCS table.
            # conn.executemany("UPDATE discs SET albumid=? WHERE rowid=?", [(kwargs["albumid"], i) for i in discs])
            # dsccount = conn.total_changes - albcount

            # TRACKS table.
            # conn.executemany("UPDATE tracks SET albumid=? WHERE rowid=?", [(kwargs["albumid"], i) for i in tracks])
            # trkcount = conn.total_changes - albcount - dsccount

    except (sqlite3.OperationalError, sqlite3.IntegrityError) as err:
        logger.exception(err)

    else:
        albcount = conn.total_changes

    finally:
        logger.info("ALBUMS table: {0:>3d} record(s) updated.".format(albcount))
        # logger.info("DISCS table : {0:>3d} record(s) updated.".format(dsccount))
        # logger.info("TRACKS table: {0:>3d} record(s) updated.".format(trkcount))
        conn.close()

    # 14. Return total changes.
    return inp_albumid, albcount, dsccount, trkcount


def updatetrack(uid, db=DATABASE, **kwargs):
    """
    Update record from `tracks` table.

    :param uid: `tracks` ROWID.
    :param db: Database storing `tracks` table.
    :param kwargs: key-value pairs enumerating field-value to update.
    :return: `tracks` total change(s).
    """

    # 1.Define logger.
    logger = logging.getLogger("{0}.updatetrack".format(__name__))

    # 2. Initialize variables.
    changes, query, args = 0, "", []

    # 3. Connect to database.
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    # 4. Set query.
    logger.debug(kwargs)
    for k, v in kwargs.items():
        query = "{0}{1}=?, ".format(query, k)
        args.append(v)
    args += (uid,)
    logger.debug(query)
    logger.debug(args)

    # 5. Update `tracks` table.
    try:
        with conn:
            conn.execute("UPDATE tracks SET {0} WHERE rowid=?".format(query[:-2]), args)
    except (sqlite3.OperationalError, sqlite3.IntegrityError) as err:
        logger.exception(err)
    else:
        changes = conn.total_changes
    finally:
        logger.info("TRACKS table: {0:>3d} record(s) updated.".format(changes))
        conn.close()

    # 6. Return total changes.
    return uid, changes


# ============================
# CherryPy specific functions.
# ============================
def updatelastplayeddate(*rowid, db=DATABASE):
    """

    :param rowid:
    :param db:
    :return:
    """
    changes, counts = 0, []
    conn = sqlite3.connect(db)
    curs = conn.cursor()
    for row in rowid:
        curs.execute("SELECT played FROM albums WHERE rowid=?", (row,))
        try:
            played = curs.fetchone()[0]
        except TypeError:
            played = 0
        counts.append(played + 1)

    with conn:
        conn.executemany("UPDATE albums SET utc_played=?, played=? WHERE rowid=?", list(zip(repeat((datetime.utcnow())), counts, rowid)))
        changes = conn.total_changes
    conn.close()
    return changes


def getlastplayeddate(db=DATABASE):
    """

    :param db:
    :return:
    """
    Album, albums = namedtuple("Album", "rowid albumid artist origyear year album discs genre upc bootleg live incollection language utc_created utc_played played"), []
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute(
            "SELECT 0, albumid, artist, origyear, year, album, 0, genre, upc, 0, 0, 1, NULL, NULL, utc_played, played "
            "FROM played_albums_vw1 "
            "ORDER BY played DESC"):
        albums.append(Album._make(row))
    conn.close()
    for album in albums:
        yield album


def getartist(db=DATABASE):
    """

    :param db:
    :return:
    """
    Album, albums = namedtuple("Album", "artistid artist"), []
    conn = sqlite3.connect(db)
    for row in conn.execute("SELECT DISTINCT alb.artistsort, art.artist FROM albums alb JOIN artists art ON alb.artistsort=art.artistsort ORDER BY alb.artistsort"):
        albums.append(Album._make(row))
    conn.close()
    for album in albums:
        yield album


def get_genres(db=DATABASE):
    """
    
    :param db: 
    :return: 
    """
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    genres = [(row["genre"], row["genreid"]) for row in conn.execute("SELECT genre, genreid FROM genres ORDER BY genreid")]
    conn.close()
    for genre in genres:
        yield genre


def get_languages(db=DATABASE):
    """
    
    :param db: 
    :return: 
    """
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    languages = [(row["language"], row["languageid"]) for row in conn.execute("SELECT language, languageid FROM languages ORDER BY languageid")]
    conn.close()
    for language in languages:
        yield language


def get_supports(db=DATABASE):
    """
    
    :param db: 
    :return: 
    """
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    supports = [(row["support"], row["supportid"]) for row in conn.execute("SELECT support, supportid FROM supports ORDER BY supportid")]
    conn.close()
    for support in supports:
        yield support


def get_countries(db=DATABASE):
    """
    
    :param db: 
    :return: 
    """
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    countries = [(row["country"], row["countryid"]) for row in conn.execute("SELECT country, countryid FROM countries ORDER BY countryid")]
    conn.close()
    for country in countries:
        yield country


def get_providers(db=DATABASE):
    """

    :param db:
    :return:
    """
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    providers = [(row["provider"], row["providerid"]) for row in conn.execute("SELECT provider, providerid FROM providers ORDER BY providerid")]
    conn.close()
    for provider in providers:
        yield provider


# ====================================================
# This function mustn't be used from external scripts.
# ====================================================
def _getalbumdetail(db, **kwargs):
    """
    Get digital audio albums detail.

    :param db: Database storing digital audio tables.
    :return: Digital audio albums detail sorted by album ID, disc ID, track ID.
    """
    logger = logging.getLogger("{0}._getalbumdetail".format(__name__))
    d = {False: 0, True: 1}

    #  1. Initializations.
    Track = namedtuple("Track",
                       "rowid track_rowid albumid albumsort discs deluxe bootleg incollection language discid tracks live_disc trackid title live bonus artistsort artist origyear year album label genre upc "
                       "utc_created utc_modified utc_played played")
    where, rows, args = "", [], ()

    #  2. SELECT clause.
    select = "SELECT album_rowid, " \
             "track_rowid, " \
             "albumid, " \
             "albumsort, " \
             "discs, " \
             "is_deluxe, " \
             "is_bootleg, " \
             "in_collection, " \
             "language, " \
             "discid, " \
             "tracks, " \
             "is_live_disc, " \
             "trackid, " \
             "title, " \
             "is_live_track, " \
             "is_bonus, " \
             "artistsort, " \
             "artist, " \
             "origyear, " \
             "year, " \
             "album, " \
             "label, " \
             "genre, " \
             "upc, " \
             "utc_created, " \
             "utc_modified, " \
             "utc_played, " \
             "played " \
             "FROM tracks_vw"

    #  3. WHERE clause.

    # 3.a. Subset by album ROWID.
    uid = kwargs.get("uid", [])
    if uid:
        where = "{0}(".format(where)
        for item in uid:
            where = "{0}album_rowid=? OR ".format(where)
            args += (item,)
        where = "{0}) AND ".format(where[:-4])

    # 3.b. Subset by `albumid`.
    albumid = kwargs.get("albumid", [])
    if albumid:
        where = "{0}(".format(where)
        for item in albumid:
            where = "{0}albumid LIKE ? OR ".format(where)
            args += ("%{0}%".format(item),)
        where = "{0}) AND ".format(where[:-4])

    # 3.c. Subset by `artistsort`.
    artistsort = kwargs.get("artistsort", [])
    if artistsort:
        where = "{0}(".format(where)
        for item in artistsort:
            where = "{0}lower(substr(albumid, 3, length(albumid) - 15)) LIKE ? OR ".format(where)
            args += ("%{0}%".format(item.lower()),)
        where = "{0}) AND ".format(where[:-4])

    # 3.d. Subset by `albumsort`.
    albumsort = kwargs.get("albumsort", [])
    if albumsort:
        where = "{0}(".format(where)
        for item in albumsort:
            where = "{0}substr(albumid, length(albumid) - 11, 12) LIKE ? OR ".format(where)
            args += ("%{0}%".format(item),)
        where = "{0}) AND ".format(where[:-4])

    # 3.e. Subset by `artist`.
    artist = kwargs.get("artist", [])
    if artist:
        where = "{0}(".format(where)
        for item in artist:
            where = "{0}lower(artist)=? OR ".format(where)
            args += (item.lower(),)
        where = "{0}) AND ".format(where[:-4])

    # 3.f. Subset by `genre`.
    genre = kwargs.get("genre", [])
    if genre:
        where = "{0}(".format(where)
        for item in genre:
            where = "{0}lower(genre)=? OR ".format(where)
            args += (item.lower(),)
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

    # 3.i. Subset by `origyear`.
    year = kwargs.get("origyear", [])
    if year:
        where = "{0}(".format(where)
        for item in year:
            where = "{0}origyear=? OR ".format(where)
            args += (item,)
        where = "{0}) AND ".format(where[:-4])

    # 3.j. Subset by `live`.
    live = kwargs.get("live", None)
    if live is not None:
        where = "{0}is_live_track=? AND ".format(where)
        args += (d[live],)

    # 3.k. Subset by `bootleg`.
    bootleg = kwargs.get("bootleg", None)
    if bootleg is not None:
        where = "{0}is_bootleg=? AND ".format(where)
        args += (d[bootleg],)

    # 4. ORDER BY clause.
    logger.debug(kwargs.get("orderby"))
    orderby = "ORDER BY albumid, discid, trackid"
    mylist = list(filter(None, map(REX.sub, repeat(translate_orderfield), kwargs.get("orderby", ["albumid", "discid", "trackid"]))))
    if mylist:
        orderby = "ORDER BY {0}".format(", ".join(mylist))

    # 5. Build SQL statement.
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
        rows.append(Track._make(row))
    conn.close()
    for row in rows:
        yield row


def _getalbumid(db, **kwargs):
    """
    """
    d = {"default": "lower($(field))=?", "rowid": "$(field)=?"}
    Album = namedtuple("Album", "rowid albumid")
    statement, where, args, rows = "SELECT rowid, albumid FROM albums", "", (), []
    for key, value in kwargs.items():
        where = "{0}{1} OR ".format(where, Template(d.get(key, d["default"])).substitute(field=key))
        try:
            args += (value.lower(),)
        except AttributeError:
            args += (value,)
    if where:
        statement = "{0} WHERE ({1}) ORDER BY albumid".format(statement, where[:-4])
    conn = sqlite3.connect(db)
    curs = conn.cursor()
    try:
        curs.execute(statement, args)
    except sqlite3.OperationalError:
        pass
    else:
        rows = Album._make(curs.fetchall())
    finally:
        conn.close()
    for row in rows:
        yield row


# ===============================================
# Main algorithm if module is run as main script.
# ===============================================
if __name__ == "__main__":

    def getalbum(item):
        return item[0][1][0][1][0][-1]


    def getcreated(item):
        return item[0][1][0][1][0][-2]


    TEMPLATE = TemplatingEnvironment(loader=jinja2.FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tables", "Albums")))
    TEMPLATE.set_environment(globalvars={"local": LOCAL,
                                         "utc": UTC},
                             filters={"getalbum": getalbum,
                                      "getcreated": getcreated,
                                      "rjustify": rjustify})

    arguments = subset_parser.parse_args()
    filters = {key: value for key, value in vars(arguments).items() if key in ["artistsort", "albumsort"]}
    run("CLS", shell=True)
    for directory in sys.path:
        print(directory)
    print(TEMPLATE.environment.get_template("T01").render(content=getgroupedalbums(db=arguments.db, artistsort=filters.get("artistsort"), albumsort=filters.get("albumsort"))))
    sys.exit(0)
