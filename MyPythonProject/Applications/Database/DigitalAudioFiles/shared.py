# -*- coding: ISO-8859-1 -*-
import argparse
import json
import logging
import os
import re
import sqlite3
import sys
from collections import MutableSequence, namedtuple
from contextlib import suppress
from datetime import datetime
from functools import partial
from itertools import accumulate, chain, groupby
from operator import itemgetter

import jinja2

from ..shared import Boolean, adapt_boolean, convert_boolean
from ...parsers import database_parser
from ...shared import DATABASE, LOCAL, TemplatingEnvironment, UTC, validgenre, validproductcode, validyear
from ...xml import digitalalbums_in

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


class InsertDigitalAlbum(MutableSequence):
    """

    """
    logger = logging.getLogger("{0}.InsertDigitalAlbum".format(__name__))

    def __init__(self, *tracks):
        self._tracks = []
        for track in tracks:

            #  1. Check if `year` is valid.
            try:
                year = validyear(track.year)
            except ValueError:
                continue

            # 2. Check if `genre` is valid.
            try:
                genre = validgenre(track.genre)
            except ValueError:
                continue

            # 3. Check if `discnumber` is valid.
            try:
                discnumber = int(track.discnumber)
            except ValueError:
                continue

            # 4. Check if `totaldiscs` is valid.
            try:
                totaldiscs = int(track.totaldiscs)
            except ValueError:
                continue

            # 5. Check if `tracknumber` is valid.
            try:
                tracknumber = int(track.tracknumber)
            except ValueError:
                continue

            # 6. Check if `totaltracks` is valid.
            try:
                totaltracks = int(track.totaltracks)
            except ValueError:
                continue

            # 7. Check if `product code` is valid.
            try:
                upc = validproductcode(track.upc)
            except ValueError:
                continue

            # 8. Check `encodingyear`.
            try:
                encodingyear = validyear(track.encodingyear)
            except ValueError:
                encodingyear = 0

            # 9. Check `origyear`.
            try:
                origyear = validyear(track.origyear)
            except ValueError:
                origyear = 0

            # 10. Set records creation date. Stored into local time zone.

            # 10.a. `albums` records.
            album_created = UTC.localize(datetime.utcnow()).astimezone(LOCAL)
            try:
                album_created = UTC.localize(datetime.utcfromtimestamp(track.album_created)).astimezone(LOCAL)
            except AttributeError:
                pass

            # 10.b. `discs` records.
            disc_created = UTC.localize(datetime.utcnow()).astimezone(LOCAL)
            try:
                disc_created = UTC.localize(datetime.utcfromtimestamp(track.disc_created)).astimezone(LOCAL)
            except AttributeError:
                pass

            # 10.c. `tracks` records.
            track_created = UTC.localize(datetime.utcnow()).astimezone(LOCAL)
            try:
                track_created = UTC.localize(datetime.utcfromtimestamp(track.track_created)).astimezone(LOCAL)
            except AttributeError:
                pass

            # 11. Set album last played date. Stored into UTC time zone.
            lastplayeddate = None
            try:
                lastplayeddate = track.lastplayed
            except AttributeError:
                pass
            if lastplayeddate:
                lastplayeddate = datetime.utcfromtimestamp(int(lastplayeddate))
                self.logger.debug("Last played date: {0}".format(UTC.localize(lastplayeddate).astimezone(LOCAL)))

            # 12. Set album played count.
            playedcount = "0"
            try:
                playedcount = track.playedcount
            except AttributeError:
                pass
            if playedcount:
                playedcount = int(playedcount)
                self.logger.debug("Played count: {0}".format(playedcount))

            # 13. Split attributes into three tuples respective to the three focused tables.

            # 13.a. `albums` table.
            albums_tuple = (
                track.albumid[:-11], track.artist, year, track.album, totaldiscs, genre, Boolean(track.live), Boolean(track.bootleg), Boolean(track.incollection), track.language, upc, encodingyear,
                album_created,
                origyear, lastplayeddate, playedcount)

            # 13.b. `discs` table.
            discs_tuple = (track.albumid[:-11], discnumber, totaltracks, disc_created)

            # 13.c. `tracks` table.
            tracks_tuple = (track.albumid[:-11], discnumber, tracknumber, track.title, track_created)

            self._tracks.append((albums_tuple, discs_tuple, tracks_tuple))

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
                              "albumid albumsort titlesort artist year album genre discnumber totaldiscs label tracknumber totaltracks title live bootleg incollection upc encodingyear language origyear")
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


def insertfromfile(*files, db=DATABASE):
    """
    Insert digital album(s) into the digital audio base.
    Albums are taken from JSON file-object(s) or XML file-object(s).

    :param files: file-object(s) where the albums are taken from.
    :param db: database where the digital audio base is stored.
    :return: database total changes.
    """
    logger = logging.getLogger("{0}.insertfromfile".format(__name__))
    regex1, regex2, regex3 = re.compile(r"^<([^>]+)>$"), re.compile(r"^</([^>]+)>$"), re.compile(r"^<\?xml[^>]+>$")
    root, status = "albums", [(0, 0, 0)]
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
            for album, disc, track in tracks:

                for item in album:
                    logger.debug(item)
                for item in disc:
                    logger.debug(item)
                for item in track:
                    logger.debug(item)

                acount, dcount, tcount = 0, 0, 0
                conn = sqlite3.connect(db)
                with conn:

                    # Update TRACKS table.
                    try:
                        conn.execute("INSERT INTO tracks (albumid, discid, trackid, title, created) VALUES (?, ?, ?, ?, ?)", track)
                        tcount = conn.total_changes
                        logger.debug("Table `tracks`: {0} records inserted.".format(tcount))
                    except sqlite3.IntegrityError:
                        pass

                    # Update DISCS table.
                    try:
                        conn.execute("INSERT INTO discs (albumid, discid, tracks, created) VALUES (?, ?, ?, ?)", disc)
                        dcount = conn.total_changes - tcount
                        logger.debug("Table `discs`: {0} records inserted.".format(dcount))
                    except sqlite3.IntegrityError:
                        pass

                    # Update ALBUMS table.
                    try:
                        conn.execute("INSERT INTO albums (albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, encodingyear, created, origyear, played, count) "
                                     "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", album)
                        acount = conn.total_changes - dcount - tcount
                        logger.debug("Table `albums`: {0} records inserted.".format(acount))
                    except sqlite3.IntegrityError:
                        pass

                    # Store total changes.
                    status.append((tcount, dcount, acount))

                conn.close()
    if len(status) > 1:
        return [list(accumulate(item))[-1] for item in zip(*status)]
    return list(chain(status))


def getalbumdetail(db=DATABASE, **kwargs):
    """
    Get digital audio albums detail.

    :param db: Database storing digital audio tables.
    :return: Digital audio albums detail sorted by album ID, disc ID, track ID.
    """
    logger = logging.getLogger("{0}.getalbumdetail".format(__name__))

    #  1. Initializations.
    record = namedtuple("record", "rowid albumid artist year album discs genre live bootleg incollection language upc encodingyear created origyear played count discid tracks trackid title")
    where, rows, args = "", [], ()

    #  2. SELECT clause.
    select = "SELECT a.rowid, a.albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, encodingyear, a.created, origyear, a.played, a.count, b.discid, b.tracks, trackid, " \
             "title " \
             "FROM albums a " \
             "JOIN discs b ON a.albumid=b.albumid " \
             "JOIN tracks c ON a.albumid=c.albumid AND b.discid=c.discid"

    #  3. WHERE clause.

    #  3.a. Subset by `artistsort`.
    artistsort = kwargs.get("artistsort", [])
    if artistsort:
        where = "{0}(".format(where)
        for item in artistsort:
            where = "{0}lower(substr(a.albumid, 3, length(a.albumid) - 2 - 13)) LIKE ? OR ".format(where)
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

    # 3.d. Subset by row ID.
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

    # 3.g. Subset by `artistsort`.
    albumid = kwargs.get("albumid", [])
    if albumid:
        where = "{0}(".format(where)
        for item in albumid:
            where = "{0}a.albumid LIKE ? OR ".format(where)
            args += ("%{0}%".format(item),)
        where = "{0}) AND ".format(where[:-4])

    # 4. ORDER BY clause.
    orderby = "ORDER BY c.albumid, c.discid, c.trackid"

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
    conn.close()
    for row in rows:
        yield record._make(row)


def getgroupedalbums(db=DATABASE, **kwargs):
    """

    :param db:
    :param kwargs:
    :return:
    """
    logger = logging.getLogger("{0}.getgroupedalbums".format(__name__))
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
                   int(LOCAL.localize(item.created).timestamp()),
                   item.album) for item in filter(func, getalbumdetail(db)))
    albumslist = sorted(sorted(sorted(sorted(albumslist, key=itemgetter(4)), key=itemgetter(3)), key=itemgetter(2)), key=lambda i: (i[0], i[1]))
    for album in albumslist:
        logger.info("----------------")
        logger.info("Selected record.")
        logger.info("----------------")
        logger.debug("\tArtistsort\t: {0}".format(album[0]).expandtabs(3))
        logger.debug("\tAlbumsort\t: {0}".format(album[2]).expandtabs(3))
        logger.debug("\tTitle\t\t\t: {0}".format(album[5]).expandtabs(3))
    for artistsort, artist, albums in ((artistsort, artist,
                                        [(albumid,
                                          [(discid,
                                            [(trackid, list(sssgroup)) for trackid, sssgroup in groupby(ssgroup, key=itemgetter(4))]) for discid, ssgroup in groupby(subgroup, key=itemgetter(3))]) for
                                         albumid, subgroup in
                                         groupby(group, key=itemgetter(2))]) for (artistsort, artist), group in groupby(albumslist, key=lambda i: (i[0], i[1]))):
        yield artistsort, artist, albums


def getalbumidfromartist(db=DATABASE, artist=None):
    """
    Get album(s) ID matching the input artist.

    :param artist: Requested artist.
    :param db: Database storing `albums` table.
    :return: Album(s) unique ID list.
    """
    record = namedtuple("record", "rowid albumid")
    argument, rows = (), []
    statement = "SELECT rowid, albumid FROM albums ORDER BY albumid"
    if artist:
        statement = "SELECT rowid, albumid FROM albums WHERE lower(substr(albumid, 3, length(albumid) - 2 - 13))=? OR lower(artist)=? ORDER BY albumid"
        argument = (artist.lower(), artist.lower())
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute(statement, argument):
        rows.append(row)
    conn.close()
    for row in rows:
        yield record._make(row)


def getalbumidfromgenre(genre, db=DATABASE):
    """
    Get album(s) ID matching the input genre.

    :param genre: Requested genre.
    :param db: Database storing `albums` table.
    :return: Album(s) unique ID list.
    """
    record = namedtuple("record", "rowid albumid")
    rows = []
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute("SELECT rowid, albumid FROM albums WHERE lower(genre)=? ORDER BY albumid", (genre.lower(),)):
        rows.append(row)
    conn.close()
    for row in rows:
        yield record._make(row)


def getalbumid(uid, db=DATABASE):
    """
    Get album ID matching the input unique row ID.

    :param uid: Requested row ID.
    :param db: Database storing `albums` table.
    :return: Album unique ID.
    """
    record, rows = namedtuple("record", "rowid albumid"), []
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute("SELECT rowid, albumid FROM albums WHERE rowid=?", (uid,)):
        rows.append(row)
    conn.close()
    for row in rows:
        yield record._make(row)


def getalbumheader(db=DATABASE, albumid=None, **kwargs):
    """
    Get album detail matching the input unique row ID.

    :param albumid: Requested row ID.
    :param db: Database storing `albums` table.
    :return: Album unique ID.
    """
    logger = logging.getLogger("{0}.getalbumheader".format(__name__))
    record = namedtuple("record", "rowid albumid artist year album discs genre live bootleg incollection language upc encodingyear created origyear played count")
    rows = []
    for row in getalbumdetail(db=db, albumid=albumid, **kwargs):
        rows.append((row.rowid,
                     row.albumid,
                     row.artist,
                     row.year,
                     row.album,
                     row.discs,
                     row.genre,
                     row.live,
                     row.bootleg,
                     row.incollection,
                     row.language,
                     row.upc,
                     row.encodingyear,
                     row.created,
                     row.origyear,
                     row.played,
                     row.count))
    for row in sorted(set(rows), key=itemgetter(1)):
        logger.info("----------------")
        logger.info("Selected record.")
        logger.info("----------------")
        logger.debug("\tRecord\t: {0}".format(row[0]).expandtabs(3))
        logger.debug("\tAlbum ID\t: {0}".format(row[1]).expandtabs(3))
        logger.debug("\tArtist\t: {0}".format(row[2]).expandtabs(3))
        logger.debug("\tYear\t\t: {0}".format(row[3]).expandtabs(3))
        logger.debug("\tAlbum\t\t: {0}".format(row[4]).expandtabs(3))
    for row in sorted(set(rows), key=itemgetter(1)):
        yield record._make(row)


def getdischeader(db=DATABASE, albumid=None, discid=None):
    """
    Get disc(s) detail matching both the input unique album ID and the disc unique ID.

    :param db: Database storing `discs` table.
    :param albumid: Requested album unique ID. Optional.
    :param discid: Requested disc unique ID. Optional.
    :return: Yield a tuple composed of row unique ID, album unique ID, disc unique ID and track unique ID.
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


def gettrack(db=DATABASE, albumid=None, discid=None, trackid=None):
    """
    Get track(s) detail matching both the input unique album ID, the disc unique ID and the track unique ID.

    :param db: Database storing `discs` table.
    :param albumid: Requested album unique ID. Optional.
    :param discid: Requested disc unique ID. Optional.
    :param trackid: Requested track unique ID. Optional.
    :return: Yield a tuple composed of row unique ID, album unique ID, disc unique ID, track unique ID and title.
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
    logger.info("DISCS table : {0:>3d} record(s) updated.".format(dsccount))
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


# ========
# Parsers.
# ========
subset_parser = argparse.ArgumentParser(parents=[database_parser])
subset_parser.add_argument("--artistsort", nargs="*", help="Subset digital albums by artistsort.")
subset_parser.add_argument("--albumsort", nargs="*", help="Subset digital albums by albumsort.")
subset_parser.add_argument("--artist", nargs="*", help="Subset digital albums by artist.")

# ============================================
# Main algorithm if module run as main script.
# ============================================
if __name__ == "__main__":

    def getalbum(item):
        return item[0][1][0][1][0][-1]


    TEMPLATE = TemplatingEnvironment(loader=jinja2.FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Database", "DigitalAudioFiles")))
    TEMPLATE.set_environment(globalvars={"local": LOCAL,
                                         "utc": UTC},
                             filters={"getalbum": getalbum})

    arguments = subset_parser.parse_args()
    filters = {key: value for key, value in vars(arguments).items() if key in ["artistsort", "albumsort", "artist"]}
    for directory in sys.path:
        print(directory)
    print(TEMPLATE.environment.get_template("T01").render(content=getgroupedalbums(db=arguments.db, artistsort=filters.get("artistsort"), albumsort=filters.get("albumsort"), artist=filters.get("artist"))))
    sys.exit(0)
