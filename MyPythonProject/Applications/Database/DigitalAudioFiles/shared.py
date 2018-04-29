# -*- coding: ISO-8859-1 -*-
# pylint: disable=invalid-name
import json
import logging
import os
import re
import sqlite3
import sys
from collections import MutableSequence, OrderedDict, namedtuple
from contextlib import suppress
from datetime import datetime
from functools import partial
from itertools import accumulate, chain, groupby, repeat
from operator import itemgetter
from string import Template
from subprocess import run

import jinja2

from ..shared import ToBoolean, adapt_booleanvalue, convert_tobooleanvalue
from ...parsers import subset_parser
from ...shared import DATABASE, LOCAL, TemplatingEnvironment, UTC, left_justify, rjustify, validdatetime, validdb, validgenre, validproductcode, validyear
from ...xml import digitalalbums_in

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

# ==========
# Constants.
# ==========
SORT = {
    "rowid": "a.rowid",
    "albumid": "a.albumid",
    "artist": "a.artist",
    "origyear": "a.origyear",
    "year": "a.year",
    "album": "a.album",
    "discs": "a.discs",
    "discid": "b.discid",
    "tracks": "b.tracks",
    "trackid": "c.trackid",
    "utc_created": "a.utc_created",
    "created": "a.utc_created",
    "utc_modified": "a.utc_modified",
    "modified": "a.utc_modified",
    "utc_played": "a.utc_played",
    "played": "a.utc_played",
    "count": "a.played",
    "label": "a.label",
    "genre": "a.genre",
    "title": "c.title",
}

# ====================
# Regular expressions.
# ====================
REX = re.compile(r"^(\w+)(?: (ASC|DESC))?$", re.IGNORECASE)


# ========
# Classes.
# ========
class InsertDigitalAlbum(MutableSequence):
    """

    """
    logger = logging.getLogger("{0}.InsertDigitalAlbum".format(__name__))

    def __init__(self, *tracks):
        self._tracks = []
        for track in tracks:

            # 0. Check if `database` is valid.
            try:
                database = validdb(track.database)
            except ValueError as err:
                self.logger.debug(err)
                continue

            # 1. Check if `year` is valid.
            try:
                year = validyear(track.year)
            except ValueError as err:
                self.logger.debug(err)
                continue

            # 2. Check if `genre` is valid.
            try:
                genre = validgenre(track.genre)
            except ValueError as err:
                self.logger.debug(err)
                continue

            # 3. Check if `discnumber` is valid.
            try:
                discnumber = int(track.discnumber)
            except ValueError as err:
                self.logger.debug(err)
                continue

            # 4. Check if `totaldiscs` is valid.
            try:
                totaldiscs = int(track.totaldiscs)
            except ValueError as err:
                self.logger.debug(err)
                continue

            # 5. Check if `tracknumber` is valid.
            try:
                tracknumber = int(track.tracknumber)
            except ValueError as err:
                self.logger.debug(err)
                continue

            # 6. Check if `totaltracks` is valid.
            try:
                totaltracks = int(track.totaltracks)
            except ValueError as err:
                self.logger.debug(err)
                continue

            # 7. Check if `product code` is valid.
            upc = ""
            if track.upc:
                try:
                    upc = validproductcode(track.upc)
                except ValueError as err:
                    self.logger.debug(err)
                    continue

            # 8. Check `origyear`.
            try:
                origyear = validyear(track.origyear)
            except ValueError as err:
                self.logger.debug(err)
                origyear = 0

            # 9. Set records creation date. Stored into local time zone.

            # 9.a. `albums` records.
            album_created = UTC.localize(datetime.utcnow()).astimezone(LOCAL)
            with suppress(AttributeError):
                album_created = UTC.localize(datetime.utcfromtimestamp(track.album_created)).astimezone(LOCAL)

            # 9.b. `discs` records.
            disc_created = UTC.localize(datetime.utcnow()).astimezone(LOCAL)
            with suppress(AttributeError):
                disc_created = UTC.localize(datetime.utcfromtimestamp(track.disc_created)).astimezone(LOCAL)

            # 9.c. `tracks` records.
            track_created = UTC.localize(datetime.utcnow()).astimezone(LOCAL)
            with suppress(AttributeError):
                track_created = UTC.localize(datetime.utcfromtimestamp(track.track_created)).astimezone(LOCAL)

            # 10. Set album last played date. Stored into UTC time zone.
            lastplayeddate = None
            with suppress(AttributeError):
                lastplayeddate = track.lastplayed
            if lastplayeddate:
                lastplayeddate = datetime.utcfromtimestamp(int(lastplayeddate))
                self.logger.debug("Last played date: %s", UTC.localize(lastplayeddate).astimezone(LOCAL))

            # 11. Set album played count.
            playedcount = "0"
            with suppress(AttributeError):
                playedcount = track.playedcount
            if playedcount:
                playedcount = int(playedcount)
                self.logger.debug("Played count: %s", playedcount)

            # 12. Split attributes into three tuples respective to the three focused tables.

            # 12.a. `albums` table.
            albums_tuple = (track.albumid[:-11], track.artist, year, track.album, totaldiscs, genre, ToBoolean(track.live), ToBoolean(track.bootleg), ToBoolean(track.incollection), track.language, upc,
                            album_created, origyear, lastplayeddate, playedcount)

            # 12.b. `discs` table.
            discs_tuple = (track.albumid[:-11], discnumber, totaltracks, disc_created)

            # 12.c. `tracks` table.
            tracks_tuple = (track.albumid[:-11], discnumber, tracknumber, track.title, track_created)

            # 13. Gather tuples together into a single list.
            self._tracks.append((database, albums_tuple, discs_tuple, tracks_tuple))

        self.logger.debug(self._tracks)
        if self._tracks:
            self._tracks = sorted(sorted(sorted(sorted(self._tracks, key=lambda i: i[3][2]), key=lambda i: i[3][1]), key=lambda i: i[3][0]), key=itemgetter(0))

    @classmethod
    def fromxml(cls, fil):
        """

        :param fil:
        :return:
        """
        return cls(*list(digitalalbums_in(fil)))

    @classmethod
    def fromjson(cls, fil):
        """

        :param fil:
        :return:
        """
        onetrack = namedtuple("onetrack",
                              "database albumid albumsort titlesort artist year album genre discnumber totaldiscs label tracknumber totaltracks title live bootleg incollection upc language origyear")
        return cls(*[onetrack._make(track) for track in json.load(fil)])

    def __getitem__(self, item):
        return self._tracks[item]

    def __setitem__(self, key, value):
        self._tracks[key] = value

    def __delitem__(self, key):
        del self._tracks[key]

    def __len__(self):
        return len(self._tracks)

    def insert(self, index, value):
        self._tracks.insert(index, value)


# ==========
# Functions.
# ==========
def translate_orderfield(match):
    if match:
        item = SORT.get(match.group(1))
        if not item:
            return item
        if match.group(2):
            item = "{0} {1}".format(item, match.group(2).upper())
        return item


# =======================================
# Main functions for working with tables.
# =======================================
def filterfunc(item, artistsort=None, albumsort=None, artist=None):
    """

    :param item:
    :param artistsort:
    :param albumsort:
    :param artist:
    :return:
    """
    if any([artistsort, albumsort, artist]):
        if artistsort and item.albumid[2:-13] not in artistsort:
            return False
        if albumsort and item.albumid[-12:] not in albumsort:
            return False
        if artist and item.artist not in artist:
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
    regex1, regex2, regex3 = re.compile(r"^<([^>]+)>$"), re.compile(r"^</([^>]+)>$"), re.compile(r"^<\?xml[^>]+>$")
    root, changes = "albums", [(0, 0, 0)]
    for file in files:
        structure, tracks, beg_match, end_match, beg = "json", None, None, None, True

        # Simple file type detection: JSON (default type) or XML.
        for line in file:
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
        file.seek(0)

        # JSON file.
        if structure == "json":
            tracks = InsertDigitalAlbum.fromjson(file)

        # XML file.
        elif structure == "xml":
            tracks = InsertDigitalAlbum.fromxml(file)

        if tracks:
            for key, group in groupby(tracks, key=itemgetter(0)):
                group = list(group)
                logger.debug(key)
                logger.debug(group)
                for _, album, disc, track in group:

                    for item in album:
                        logger.debug(item)
                    for item in disc:
                        logger.debug(item)
                    for item in track:
                        logger.debug(item)

                    acount, dcount, tcount = 0, 0, 0
                    conn = sqlite3.connect(key)
                    with conn:

                        # Update TRACKS table.
                        try:
                            conn.execute("INSERT INTO tracks (albumid, discid, trackid, title, created) VALUES (?, ?, ?, ?, ?)", track)
                            tcount = conn.total_changes
                            logger.debug("Table `tracks`: %s records inserted.", tcount)
                        except sqlite3.IntegrityError:
                            pass

                        # Update DISCS table.
                        try:
                            conn.execute("INSERT INTO discs (albumid, discid, tracks, created) VALUES (?, ?, ?, ?)", disc)
                            dcount = conn.total_changes - tcount
                            logger.debug("Table `discs`: %s records inserted.", dcount)
                        except sqlite3.IntegrityError:
                            pass

                        # Update ALBUMS table.
                        try:
                            conn.execute("INSERT INTO albums (albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, utc_created, origyear, utc_played, played) "
                                         "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", album)
                            acount = conn.total_changes - dcount - tcount
                            logger.debug("Table `albums`: %s records inserted.", acount)
                        except sqlite3.IntegrityError:
                            pass

                        # Store total changes.
                        changes.append((tcount, dcount, acount))

                    conn.close()

    if len(changes) > 1:
        return [list(accumulate(item))[-1] for item in zip(*changes)]
    return list(chain.from_iterable(changes))


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
    func = partial(filterfunc, artistsort=kwargs.get("artistsort"), albumsort=kwargs.get("albumsort"), artist=kwargs.get("artist"))
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
                   int(LOCAL.localize(item.utc_created).timestamp()),
                   item.album) for item in filter(func, _getalbumdetail(db)))
    albumslist = sorted(sorted(sorted(sorted(albumslist, key=itemgetter(4)), key=itemgetter(3)), key=itemgetter(2)), key=lambda i: (i[0], i[1]))
    for album in albumslist:
        logger.debug("----------------")
        logger.debug("Selected record.")
        logger.debug("----------------")
        logger.debug("\tArtistsort\t: {0}".format(album[0]).expandtabs(tabsize))
        logger.debug("\tAlbumsort\t: {0}".format(album[2]).expandtabs(tabsize))
        logger.debug("\tTitle\t\t\t: {0}".format(album[5]).expandtabs(tabsize))
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


def getalbumheader(db=DATABASE, albumid=None, **kwargs):
    """
    Get album detail matching the input primary key.

    :param albumid: Requested primary key.
    :param db: Database storing `albums` table.
    :return: Album detail gathered into a namedtuple.
    """
    logger = logging.getLogger("{0}.getalbumheader".format(__name__))
    tabsize, rows = 3, []
    # """
    headers = list(left_justify(["\t{0}".format(item).expandtabs(tabsize) for item in ["Row ID", "Album ID", "Artist", "Origyear", "Year", "Album"]]))
    # """
    digitalalbum = namedtuple("digitalalbum", "rowid albumid artist origyear album discs label genre upc year live bootleg incollection language utc_created utc_modified utc_played played")
    # """
    for row in _getalbumdetail(db, albumid=albumid, **kwargs):
        rows.append((row.rowid,
                     row.albumid,
                     row.artist,
                     row.origyear,
                     row.album,
                     row.discs,
                     row.label,
                     row.genre,
                     row.upc,
                     row.year,
                     row.live,
                     row.bootleg,
                     row.incollection,
                     row.language,
                     row.utc_created,
                     row.utc_modified,
                     row.utc_played,
                     row.played))
    # """
    for row in OrderedDict.fromkeys(rows).keys():
        row = digitalalbum._make(row)
        logger.debug("----------------")
        logger.debug("Selected record.")
        logger.debug("----------------")
        for key, value in zip(headers, (row.rowid, row.albumid, row.artist, row.origyear, row.year, row.album)):
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
    record = namedtuple("record", "rowid albumid discid tracks")

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
        rows.append(row)
    conn.close()
    for row in rows:
        yield record._make(row)


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
    record, args, where, orderby, sql, rows = namedtuple("record", "rowid albumid discid trackid title"), (), "", "", "SELECT rowid, albumid, discid, trackid, title FROM tracks ", []

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
        rows.append(row)
    conn.close()
    for row in rows:
        yield record._make(row)


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
    changes, conn = 0, sqlite3.connect(db)
    with conn:
        conn.executemany("DELETE FROM albums WHERE rowid=?", [(i,) for i in uid])
        changes = conn.total_changes
    return changes


def deletedischeader(*uid, db=DATABASE):
    """
    Delete disc(s) from `discs` table.

    :param uid: List of ROWID.
    :param db: Database storing `discs` table.
    :return: Total changes.
    """
    changes, conn = 0, sqlite3.connect(db)
    with conn:
        conn.executemany("DELETE FROM discs WHERE rowid=?", [(i,) for i in uid])
        changes = conn.total_changes
    conn.close()
    return changes


def deletetrack(*uid, db=DATABASE):
    """
    Delete track(s) from `tracks` table.

    :param uid: List of  ROWID.
    :param db: Database storing `tracks` table.
    :return: Total changes.
    """
    changes, conn = 0, sqlite3.connect(db)
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

    # 4. Get album ID.
    curs = conn.cursor()
    curs.execute("SELECT albumid FROM albums WHERE rowid=?", (uid,))
    try:
        inp_albumid = curs.fetchone()[0]
    except TypeError:
        inp_albumid = None

    # 5. Get album, discs and tracks hieharchy if album ID is updated.
    if "albumid" in kwargs:
        curs = conn.cursor()
        curs.execute("SELECT albumid FROM albums WHERE rowid=?", (uid,))
        try:
            albumid = curs.fetchone()[0]
        except TypeError:
            albumid = None
        if albumid:
            for drow in conn.execute("SELECT rowid, discid FROM discs WHERE albumid=?", (albumid,)):
                discs.append(drow["rowid"])
                for trow in conn.execute("SELECT rowid FROM tracks WHERE albumid=? AND discid=?", (albumid, drow["discid"])):
                    tracks.append(trow["rowid"])
    logger.debug(tracks)
    logger.debug(discs)

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
            albcount = conn.total_changes

            if "albumid" in kwargs:
                # DISCS table.
                conn.executemany("UPDATE discs SET albumid=? WHERE rowid=?", [(kwargs["albumid"], i) for i in discs])
                dsccount = conn.total_changes - albcount

                # TRACKS table.
                conn.executemany("UPDATE tracks SET albumid=? WHERE rowid=?", [(kwargs["albumid"], i) for i in tracks])
                trkcount = conn.total_changes - albcount - dsccount

    except sqlite3.OperationalError as err:
        logger.exception(err)
        albcount, dsccount, trkcount = 0, 0, 0

    except sqlite3.IntegrityError as err:
        logger.exception(err)

    finally:
        logger.info("ALBUMS table: {0:>3d} record(s) updated.".format(albcount))
        logger.info("DISCS table : {0:>3d} record(s) updated.".format(dsccount))
        logger.info("TRACKS table: {0:>3d} record(s) updated.".format(trkcount))
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
            changes = conn.total_changes
    except sqlite3.OperationalError as err:
        logger.exception(err)
        changes = 0
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
    record = namedtuple("record", "rowid albumid artist year album discs genre live bootleg incollection language upc utc_created origyear utc_played played")
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute(
            "SELECT rowid, albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, utc_created, origyear, utc_played, played FROM albums ORDER BY played DESC"):
        yield record._make(row)


def getartist(db=DATABASE):
    """

    :param db:
    :return:
    """
    record = namedtuple("record", "artistid artist")
    conn = sqlite3.connect(db)
    for row in conn.execute("SELECT substr(albumid, 3, length(albumid) - 15), artist FROM albums ORDER BY albumid"):
        yield record._make(row)


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
    record = namedtuple("record",
                        "rowid albumid artist origyear album discs label genre upc year live bootleg incollection language utc_created utc_modified utc_played played discid tracks trackid title track_rowid")
    where, rows, args = "", [], ()

    #  2. SELECT clause.
    select = "SELECT a.rowid, a.albumid, a.artist, a.origyear, a.album, a.discs, a.label, a.genre, a.upc, a.year, a.live, a.bootleg, a.incollection, a.language, a.utc_created, a.utc_modified, a.utc_played, " \
             "a.played, b.discid, b.tracks, c.trackid, c.title, c.rowid " \
             "FROM albums a " \
             "JOIN discs b ON a.albumid=b.albumid " \
             "JOIN tracks c ON a.albumid=c.albumid AND b.discid=c.discid"

    #  3. WHERE clause.

    #  3.a. Subset by `artistsort`.
    artistsort = kwargs.get("artistsort", [])
    if artistsort:
        where = "{0}(".format(where)
        for item in artistsort:
            where = "{0}lower(substr(a.albumid, 3, length(a.albumid) - 15)) LIKE ? OR ".format(where)
            args += ("%{0}%".format(item.lower()),)
        where = "{0}) AND ".format(where[:-4])

    # 3.b. Subset by `albumsort`.
    albumsort = kwargs.get("albumsort", [])
    if albumsort:
        where = "{0}(".format(where)
        for item in albumsort:
            where = "{0}substr(a.albumid, length(a.albumid) - 11, 12) LIKE ? OR ".format(where)
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

    # 3.d. Subset by ROWID.
    uid = kwargs.get("uid", [])
    if uid:
        where = "{0}(".format(where)
        for item in uid:
            where = "{0}a.rowid=? OR ".format(where)
            args += (item,)
        where = "{0}) AND ".format(where[:-4])

    # 3.e. Subset by `album`.
    album = kwargs.get("album", [])
    if album:
        where = "{0}(".format(where)
        for item in album:
            where = "{0}lower(album) LIKE ? OR ".format(where)
            args += ("%{0}%".format(item),)
        where = "{0}) AND ".format(where[:-4])

    # 3.f. Subset by `year`.
    year = kwargs.get("year", [])
    if year:
        where = "{0}(".format(where)
        for item in year:
            where = "{0}year=? OR ".format(where)
            args += (item,)
        where = "{0}) AND ".format(where[:-4])

    # 3.g. Subset by `albumid`.
    albumid = kwargs.get("albumid", [])
    if albumid:
        where = "{0}(".format(where)
        for item in albumid:
            where = "{0}a.albumid LIKE ? OR ".format(where)
            args += ("%{0}%".format(item),)
        where = "{0}) AND ".format(where[:-4])

    # 3.h. Subset by `live`.
    live = kwargs.get("live", None)
    if live is not None:
        where = "{0}live=? AND ".format(where)
        args += (d[live],)

    # 3.i. Subset by `bootleg`.
    bootleg = kwargs.get("bootleg", None)
    if bootleg is not None:
        where = "{0}bootleg=? AND ".format(where)
        args += (d[bootleg],)

    # 3.j. Subset by `incollection`.
    incollection = kwargs.get("incollection", None)
    if incollection is not None:
        where = "{0}incollection=? AND ".format(where)
        args += (d[incollection],)

    # 4. ORDER BY clause.
    logger.debug(kwargs.get("orderby"))
    orderby = "ORDER BY a.albumid, b.discid, c.trackid"
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
        rows.append(row)
    conn.close()
    for row in rows:
        yield record._make(row)


def _getalbumid(db, **kwargs):
    """
    """
    d = {"default": "lower($(field))=?", "rowid": "$(field)=?"}
    record = namedtuple("record", "rowid albumid")
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
        rows = curs.fetchall()
    finally:
        conn.close()
    for row in rows:
        yield record._make(row)


# ===============================================
# Main algorithm if module is run as main script.
# ===============================================
if __name__ == "__main__":

    def getalbum(item):
        return item[0][1][0][1][0][-1]


    TEMPLATE = TemplatingEnvironment(loader=jinja2.FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Database", "DigitalAudioFiles")))
    TEMPLATE.set_environment(globalvars={"local": LOCAL,
                                         "utc": UTC},
                             filters={"getalbum": getalbum,
                                      "rjustify": rjustify})

    arguments = subset_parser.parse_args()
    filters = {key: value for key, value in vars(arguments).items() if key in ["artistsort", "albumsort", "artist"]}
    run("CLS", shell=True)
    for directory in sys.path:
        print(directory)
    print(TEMPLATE.environment.get_template("T01").render(content=getgroupedalbums(db=arguments.db, artistsort=filters.get("artistsort"), albumsort=filters.get("albumsort"), artist=filters.get("artist"))))
    sys.exit(0)
