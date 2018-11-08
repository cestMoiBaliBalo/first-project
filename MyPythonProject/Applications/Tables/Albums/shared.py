# -*- coding: ISO-8859-1 -*-
# pylint: disable=invalid-name
import csv
import json
import logging
import os
import re
import sqlite3
from collections import Counter, namedtuple
from contextlib import ExitStack, suppress
from datetime import datetime
from itertools import chain, compress, groupby, product, starmap
from operator import itemgetter
from string import Template
from typing import Any, Iterable, List, Mapping, NamedTuple, Optional, Tuple, Union

import yaml
from dateutil.parser import parse

from ..shared import DatabaseConnection, ToBoolean, adapt_booleanvalue, close_database, convert_tobooleanvalue, run_statement, set_setclause, set_whereclause_album, set_whereclause_disc, set_whereclause_track
from ...shared import DATABASE, LOCAL, TEMPLATE4, UTC, get_dirname, get_readabledate

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
def datetime_converter(bytstr):
    chrstr = bytstr.decode("ascii")
    datobj = parse(chrstr)
    with suppress(ValueError):
        datobj = UTC.localize(parse(chrstr))
    return get_readabledate(datobj.astimezone(LOCAL), template=TEMPLATE4)


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

    def wrapper(arg):
        returned = arg
        try:
            lower_arg = arg.lower()
        except AttributeError:
            pass
        else:
            if lower_arg in ["n", "y"]:
                returned = ToBoolean(arg)
        return returned

    return tuple(map(wrapper, args))


def merge(item):
    """

    :param item:
    :return:
    """
    table, track = item
    return (table,) + track


# ==========
# Constants.
# ==========
COVER = Template("albumart/$letter/$artistsort/$albumsort/iPod-Front.jpg")
FUNCTIONS = {"defaultalbums": check_defaultalbum,
             "bootlegalbums": check_bootlegalbum}
SORT = {"rowid": "album_rowid",
        "created": "utc_created",
        "modified": "utc_modified"}

# ====================
# Regular expressions.
# ====================
REX = re.compile(r"^(\w+)(?: (ASC|DESC))?$", re.IGNORECASE)


# ========================================
# Main interfaces for working with tables.
# ========================================
def insert_albums(*iterables) -> int:
    return _insert_albums(*iterables)


def insert_albums_fromjson(*jsonfiles) -> int:
    """

    :param jsonfiles:
    :return:
    """
    return _insert_albums(*chain.from_iterable([json.load(file) for file in jsonfiles]))


def insert_defaultalbums_fromplaintext(*txtfiles, db: str = DATABASE) -> int:
    """

    :param txtfiles:
    :param db:
    :return:
    """
    tracks = []
    fieldnames = ["albumid",
                  "discnumber",
                  "tracknumber",
                  "totaldiscs",
                  "totaltracks",
                  "origyear",
                  "year",
                  "album",
                  "genre",
                  "label",
                  "upc",
                  "is_bonustrack",
                  "is_livedisc",
                  "is_livetrack",
                  "is_bootleg",
                  "is_deluxe",
                  "titlelanguage",
                  "title",
                  "artistsort",
                  "artist",
                  "is_incollection"]
    with ExitStack() as stack:
        files = [stack.enter_context(open(file, encoding="UTF_8_SIG")) for file in txtfiles]
        for file in files:
            reader = csv.DictReader(file, fieldnames=fieldnames, delimiter=";")
            for row in reader:

                # Map genre to genreid.
                try:
                    _, genreid = list(filter(lambda i: i[0].lower() == row["genre"].lower(), get_genres(db)))[0]
                except TypeError:
                    continue

                # Map language to languageid.
                try:
                    _, languageid = list(filter(lambda i: i[0].lower() == row["titlelanguage"].lower(), get_languages(db)))[0]
                except TypeError:
                    continue

                # Prepare data structure.
                tracks.append(("defaultalbums",
                               db,
                               row["albumid"],
                               int(row["discnumber"]),
                               int(row["tracknumber"]),
                               int(row["totaldiscs"]),
                               int(row["totaltracks"]),
                               int(row["origyear"]),
                               int(row["year"]),
                               row["album"],
                               genreid,
                               row["label"],
                               row["upc"],
                               row["is_bonustrack"],
                               row["is_livedisc"],
                               row["is_livetrack"],
                               row["is_bootleg"],
                               row["is_deluxe"],
                               languageid,
                               row["title"],
                               row["artistsort"],
                               row["artist"],
                               row["is_incollection"]))

    return _insert_albums(*tracks)


def get_albumheader(db: str = DATABASE, **kwargs: Union[bool, List[str], List[int]]):
    """
    Get album header matching the input primary key(s).

    :param db:
    :param kwargs:
    :return: Album detail gathered into a namedtuple.
    """
    # logger = logging.getLogger("{0}.get_albumheader".format(__name__))
    # tabsize = 3

    # -----
    # headers = list(left_justify(("\t{0}".format(item).expandtabs(tabsize) for item in ["Row ID", "Album ID", "ArtistSort", "AlbumSort", "Artist", "Album", "Cover", "Genre", "Created"])))

    # -----
    Album = NamedTuple("Album",
                       [("rowid", int),
                        ("albumid", str),
                        ("artistsort", str),
                        ("albumsort", str),
                        ("artist", str),
                        ("discs", int),
                        ("genre", str),
                        ("bootleg", bool),
                        ("incollection", bool),
                        ("language", str),
                        ("utc_created", datetime),
                        ("utc_modified", datetime),
                        ("album", str),
                        ("cover", str)])

    # -----
    albums = ((row.album_rowid,
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
              for row in _get_albums(db, **kwargs))
    albums = sorted(set(albums), key=itemgetter(1))  # type: ignore

    # -----
    for album in albums:
        row = Album._make(album)
        # logger.debug("================")
        # logger.debug("Selected record.")
        # logger.debug("================")
        # for key, value in zip(headers,
        # (row.rowid, row.albumid, row.artistsort, row.albumsort, row.artist, row.album, row.cover, row.genre, dateformat(UTC.localize(row.utc_created).astimezone(LOCAL), TEMPLATE4))):
        # logger.debug("%s: %s", key, value)
        yield row


def get_albumdetail(db: str = DATABASE, **kwargs: Union[bool, List[str], List[int]]):
    for row in _get_albums(db, **kwargs):
        yield row


def get_albumidfromartistsort(artistsort: str, *, db: str = DATABASE) -> Iterable[str]:
    """
    Get album(s) ID matching the input artistsort.

    :param artistsort: Requested artist.
    :param db: Database storing `albums` table.
    :return: Album(s) unique ID list.
    """
    for albumid in sorted(set(row.albumid for row in _get_albums(db, **dict(artistsort=[artistsort])))):
        yield albumid


def get_albumidfromalbumsort(albumsort: str, *, db: str = DATABASE) -> Iterable[str]:
    """
    Get album(s) ID matching the input albumsort.

    :param albumsort: Requested albumsort.
    :param db: Database storing `albums` table.
    :return: Album(s) unique ID list.
    """
    for albumid in sorted(set(row.albumid for row in _get_albums(db, **dict(albumsort=[albumsort])))):
        yield albumid


def get_albumidfromgenre(genre: str, *, db: str = DATABASE) -> Iterable[str]:
    """
    Get album(s) ID matching the input genre.

    :param genre: Requested genre.
    :param db: Database storing `albums` table.
    :return: Album(s) unique ID list.
    """
    for albumid in sorted(set(row.albumid for row in _get_albums(db, **dict(genre=[genre])))):
        yield albumid


def get_bootlegalbums(db: str = DATABASE) -> Iterable[str]:
    """

    :param db:
    :return:
    """
    for albumid in sorted(set(row.albumid for row in _get_albums(db, **dict(bootleg=True)))):
        yield albumid


def exist_albumid(albumid: str, *, db: str = DATABASE) -> bool:
    return albumid in set(row.albumid for row in _get_albums(db))


def get_playeddiscs(db: str = DATABASE):
    """

    :param db:
    :return:
    """
    Disc = NamedTuple("Disc", [("artistsort", str),
                               ("albumsort", str),
                               ("discid", int),
                               ("genre", str),
                               ("is_bootleg", bool),
                               ("is_live", bool),
                               ("in_collection", bool),
                               ("language", str),
                               ("utc_created", datetime),
                               ("utc_played", datetime),
                               ("played", int)])
    discs = set((row.artistsort, row.albumsort, row.discid, row.genre, row.is_bootleg, row.is_live_disc, row.in_collection, row.language, row.utc_created, row.utc_played, row.played) for row in
                filter(lambda row: row.played > 0, _get_albums(db)))
    for disc in (Disc._make(row) for row in discs):
        yield disc


def get_playeddisccount(albumid: str, discid: int, *, db: str = DATABASE) -> Tuple[int, Optional[datetime]]:
    """

    :param albumid:
    :param discid:
    :param db:
    :return:
    """
    played, utc_played = 0, None  # type: int, Optional[datetime]
    with DatabaseConnection(db) as conn:
        curs = conn.execute("SELECT played, utc_played FROM playeddiscs WHERE albumid=? AND discid=?", (albumid, discid))
        with suppress(TypeError):
            played, utc_played = curs.fetchone()
    return played, utc_played


def update_playeddisccount(albumid: str, discid: int, *, db: str = DATABASE) -> int:
    """

    :param albumid:
    :param discid:
    :param db:
    :return:
    """
    played = 0  # type: int
    with ExitStack() as stack:
        conn = stack.enter_context(DatabaseConnection(db))
        stack.enter_context(conn)
        curs = conn.execute("SELECT played FROM playeddiscs WHERE albumid=? AND discid=?", (albumid, discid))
        with suppress(TypeError):
            (played,) = curs.fetchone()
        played += 1
        conn.execute("UPDATE playeddiscs SET utc_played=?, played=? WHERE albumid=? AND discid=?", (datetime.utcnow(), played, albumid, discid))
        changes = conn.total_changes  # type: int
    return changes


def get_disc(db: str = DATABASE, albumid: Optional[str] = None, discid: Optional[int] = None):
    """
    Get disc detail matching primary keys.

    :param db: Database storing `discs` table.
    :param albumid: album primary key. Optional.
    :param discid: disc primary key. Optional.
    :return: Yield a tuple composed of ROWID, album unique ID, disc unique ID and track unique ID.
    """
    sql, where, orderby, args = "SELECT rowid, albumid, discid, tracks FROM discs ", "", "", ()  # type: str, str, str, Tuple[Union[str, int], ...]
    Disc = NamedTuple("Disc",
                      [("rowid", int),
                       ("albumid", str),
                       ("discid", int),
                       ("tracks", int)])

    # 1. Get one album.
    if albumid:
        where = "{0}albumid=? AND ".format(where)
        orderby = "discid"
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
    with DatabaseConnection(db) as conn:
        for row in (Disc._make(row) for row in conn.execute(statement, args)):
            yield row


def get_track(db: str = DATABASE, albumid: Optional[str] = None, discid: Optional[int] = None, trackid: Optional[int] = None):
    """
    Get track(s) detail matching both the input unique album ID, the disc unique ID and the track unique ID.

    :param db: Database storing `discs` table.
    :param albumid: Requested album unique ID. Optional.
    :param discid: Requested disc unique ID. Optional.
    :param trackid: Requested track unique ID. Optional.
    :return: Yield a tuple composed of ROWID, album unique ID, disc unique ID, track unique ID and title.
    """
    Track = NamedTuple("Track",
                       [("rowid", int),
                        ("albumid", str),
                        ("discid", int),
                        ("trackid", int),
                        ("title", str)])
    args, where, orderby, sql = (), "", "", "SELECT rowid, albumid, discid, trackid, title FROM tracks "  # type: Tuple[Union[str, int], ...], str, str, str

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
    with DatabaseConnection(db) as conn:
        for row in (Track._make(row) for row in conn.execute(statement, args)):
            yield row


def defaultalbums(db: str = DATABASE):
    """
    Select `defaultalbums` table content.
    Datetime objects are directly converted to strings using `TEMPLATE4` as template.

    :param db: database storing `defaultalbums`.
    :return:
    """
    Album = NamedTuple("Album",
                       [("album_rowid", int),
                        ("albumid", str),
                        ("artistsort", str),
                        ("albumsort", str),
                        ("artist", str),
                        ("discs", int),
                        ("discid", int),
                        ("tracks", int),
                        ("origyear", int),
                        ("year", int),
                        ("album", str),
                        ("genre", str),
                        ("label", str),
                        ("upc", str),
                        ("is_bootleg", bool),
                        ("is_disc_live", bool),
                        ("track", int),
                        ("title", str),
                        ("is_track_live", bool),
                        ("is_track_bonus", bool),
                        ("created_date", datetime),
                        ("ripped_date", datetime),
                        ("ripped_year", int),
                        ("ripped_month", int),
                        ("played_date", datetime),
                        ("played_year", int),
                        ("played_month", int),
                        ("played", int),
                        ("support", str)])
    with DatabaseConnection(db) as conn:
        for row in (Album._make(row) for row in conn.execute("SELECT * FROM defaultalbums_vw ORDER BY rowid")):
            yield row


def bootlegalbums(db: str = DATABASE):
    """
    Select `bootlegalbums` table content.
    Datetime objects are directly converted to strings using `TEMPLATE4` as template.

    :param db: database storing `bootlegalbums`.
    :return:
    """
    Album = NamedTuple("Album",
                       [("album_rowid", int),
                        ("albumid", str),
                        ("artistsort", str),
                        ("albumsort", str),
                        ("artist", str),
                        ("discs", int),
                        ("discid", int),
                        ("tracks", int),
                        ("album", str),
                        ("genre", str),
                        ("is_bootleg", bool),
                        ("is_disc_live", bool),
                        ("track", int),
                        ("title", str),
                        ("is_track_live", bool),
                        ("is_track_bonus", bool),
                        ("bootlegtrack_year", int),
                        ("bootlegtrack_month", int),
                        ("bootlegtrack_date", str),
                        ("bootlegtrack_city", str),
                        ("bootlegtrack_tour", str),
                        ("bootlegtrack_country", str),
                        ("created_date", datetime),
                        ("ripped_date", datetime),
                        ("ripped_year", int),
                        ("ripped_month", int),
                        ("played_date", datetime),
                        ("played_year", int),
                        ("played_month", int),
                        ("played", int),
                        ("support", str),
                        ("bootleg_countryid", int),
                        ("bootlegtrack_countryid", int)])
    with DatabaseConnection(db) as conn:
        for row in (Album._make(row) for row in conn.execute("SELECT * FROM bootlegalbums_vw ORDER BY rowid")):
            yield row


def delete_album(albumid: str, *, db: str = DATABASE) -> Tuple[str, int, int, int, int, int, int, int, int, int]:
    """
    Delete a digital album.

    :param albumid: album unique ID.
    :param db: database storing tables.
    :return: Tuple composed of deleted album unique ID, `albums` total change(s), `discs` total change(s) and `tracks` total change(s).
    """
    albumid, bonuses_count, tracks_count, rippeddiscs_count, playeddiscs_count, bootlegdiscs_count, discs_count, defaultalbums_count, bootlegalbums_count, albums_count = _delete_album(albumid, db=db)
    return albumid, bonuses_count, tracks_count, rippeddiscs_count, playeddiscs_count, bootlegdiscs_count, discs_count, defaultalbums_count, bootlegalbums_count, albums_count


def delete_album_fromuid(uid: int, *, db: str = DATABASE) -> Tuple[Optional[str], int, int, int, int, int, int, int, int, int]:
    """
    Delete a digital album.

    :param uid: album unique row ID.
    :param db: database storing tables.
    :return: Tuple composed of deleted album unique ID, `albums` total change(s), `discs` total change(s) and `tracks` total change(s).
    """
    albumid: Optional[str] = None
    with DatabaseConnection(db) as conn:
        curs = conn.execute("SELECT albumid FROM albums WHERE rowid=?", (uid,))
        with suppress(TypeError):
            (albumid,) = curs.fetchone()
    if albumid:
        albumid, bonuses_count, tracks_count, rippeddiscs_count, playeddiscs_count, bootlegdiscs_count, discs_count, defaultalbums_count, bootlegalbums_count, albums_count = _delete_album(albumid, db=db)
        return albumid, bonuses_count, tracks_count, rippeddiscs_count, playeddiscs_count, bootlegdiscs_count, discs_count, defaultalbums_count, bootlegalbums_count, albums_count
    return albumid, 0, 0, 0, 0, 0, 0, 0, 0, 0


def aggregate_albums_by_artistsort(db: str = DATABASE, artistsort: Optional[str] = None) -> Iterable[Tuple[str, int]]:
    k_artistsort: List[str] = []
    if artistsort is not None:
        k_artistsort = [artistsort]
    c = Counter(artistsort for artistsort, _ in set((row.artistsort, row.albumsort) for row in _get_albums(db, artistsort=k_artistsort)))
    for k, v in c.items():
        yield k, v  # type: ignore


def aggregate_albums_by_genre(db: str = DATABASE, genre: Optional[str] = None) -> Iterable[Tuple[str, int]]:
    k_genre: List[str] = []
    if genre is not None:
        k_genre = [genre]
    c = Counter(genre for genre, _, _ in set((row.genre, row.artistsort, row.albumsort) for row in _get_albums(db, genre=k_genre)))
    for k, v in c.items():
        yield k, v  # type: ignore


def update_albums(*keys: str, db: str = DATABASE, **kwargs: Any) -> int:
    """
    :param keys:
    :param db:
    :param kwargs:
    :return:
    """
    changes: int = 0
    try:
        changes = _update_album("albums", *keys, db=db, **kwargs)
    except ValueError:
        raise
    return changes


def update_defaultalbums(*keys: str, db: str = DATABASE, **kwargs: Any) -> int:
    """
    :param keys:
    :param db:
    :param kwargs:
    :return:
    """
    changes: int = 0
    try:
        changes = _update_album("defaultalbums", *keys, db=db, **kwargs)
    except ValueError:
        raise
    return changes


def update_bootlegalbums(*keys: str, db: str = DATABASE, **kwargs: Any) -> int:
    """
    :param keys:
    :param db:
    :param kwargs:
    :return:
    """
    changes: int = 0
    try:
        changes = _update_album("bootlegalbums", *keys, db=db, **kwargs)
    except ValueError:
        raise
    return changes


def update_rippeddiscs(*keys: str, db: str = DATABASE, **kwargs: Any) -> int:
    """
    :param keys:
    :param db:
    :param kwargs:
    :return:
    """
    changes: int = 0
    try:
        changes = _update_disc("rippeddiscs", *keys, db=db, **kwargs)
    except ValueError:
        raise
    return changes


def update_playeddiscs(*keys: str, db: str = DATABASE, **kwargs: Any) -> int:
    """
    :param keys:
    :param db:
    :param kwargs:
    :return:
    """
    changes: int = 0
    try:
        changes = _update_disc("playeddiscs", *keys, db=db, **kwargs)
    except ValueError:
        raise
    return changes


def update_tracks(*keys: str, db: str = DATABASE, **kwargs: Any) -> int:
    """
    :param keys:
    :param db:
    :param kwargs:
    :return:
    """
    changes: int = 0
    try:
        changes = _update_track("tracks", *keys, db=db, **kwargs)
    except ValueError:
        raise
    return changes


# ============================
# CherryPy specific functions.
# ============================
def get_artists(db: str = DATABASE):
    """

    :param db:
    :return:
    """
    Artist = NamedTuple("Artist",
                        [("artistsort", str),
                         ("artist", str)])
    with DatabaseConnection(db) as conn:
        for artist in (Artist._make(row) for row in conn.execute("SELECT DISTINCT alb.artistsort, art.artist FROM albums alb JOIN artists art ON alb.artistsort=art.artistsort ORDER BY alb.artistsort")):
            yield artist


def get_genres(db: str = DATABASE) -> Iterable[Tuple[str, int]]:
    """

    :param db:
    :return:
    """
    with DatabaseConnection(db) as conn:
        for genre in ((row["genre"], row["genreid"]) for row in conn.execute("SELECT genre, genreid FROM genres ORDER BY genreid")):
            yield genre


def get_languages(db: str = DATABASE) -> Iterable[Tuple[str, int]]:
    """

    :param db:
    :return:
    """
    with DatabaseConnection(db) as conn:
        for language in ((row["language"], row["languageid"]) for row in conn.execute("SELECT language, languageid FROM languages ORDER BY languageid")):
            yield language


def get_supports(db: str = DATABASE) -> Iterable[Tuple[str, int]]:
    """

    :param db:
    :return:
    """
    with DatabaseConnection(db) as conn:
        for support in ((row["support"], row["supportid"]) for row in conn.execute("SELECT support, supportid FROM supports ORDER BY supportid")):
            yield support


def get_countries(db: str = DATABASE) -> Iterable[Tuple[str, int]]:
    """

    :param db:
    :return:
    """
    with DatabaseConnection(db) as conn:
        for country in ((row["country"], row["countryid"]) for row in conn.execute("SELECT country, countryid FROM countries ORDER BY countryid")):
            yield country


def get_providers(db: str = DATABASE) -> Iterable[Tuple[str, int]]:
    """

    :param db:
    :return:
    """
    with DatabaseConnection(db) as conn:
        for provider in ((row["provider"], row["providerid"]) for row in conn.execute("SELECT provider, providerid FROM providers ORDER BY providerid")):
            yield provider


# =======================================================
# These interfaces mustn't be used from external scripts.
# =======================================================
def _insert_albums(*iterables) -> int:
    """
    Insert digital album(s) into the digital audio base.
    Albums are taken from JSON file-object(s).

    :param files: file-object(s) where the albums are taken from.
    :return: database total changes.
    """

    # -----
    logger = logging.getLogger("{0}.insert_album".format(__name__))

    # -----
    with open(os.path.join(get_dirname(os.path.abspath(__file__)), "Resources", "setup.yml"), encoding="UTF_8") as stream:
        config = yaml.load(stream)
    _statements = config["statements"]
    _selectors = config["selectors"]
    _tables = config["tables"]

    # -----
    iterables = iter(iterables)  # type: ignore
    total_changes: int = 0
    for profile, group in groupby(sorted(sorted(iterables, key=itemgetter(1)), key=itemgetter(0)), key=itemgetter(0)):
        primary_group = starmap(toboolean, list(filter(FUNCTIONS[profile], group)))
        for database, secondary_group in groupby(primary_group, key=itemgetter(1)):
            with ExitStack() as stack:
                conn = stack.enter_context(DatabaseConnection(database))
                stack.enter_context(conn)
                tracks = list(map(merge, product(_tables[profile], secondary_group)))
                statements = _statements.get(profile, _statements["default"])
                logger.debug(profile)
                logger.debug(statements)

                # Shared tables.
                for track in tracks:
                    table = track[0]
                    logger.debug(table)
                    logger.debug(track)
                    with suppress(sqlite3.IntegrityError):
                        conn.execute(statements.get(table, _statements["default"][table]), tuple(compress(track, _selectors[profile][table])))

                # "rippeddiscs" table.
                table = "rippeddiscs"
                for track in filter(lambda i: i[0].lower() == "discs", filter(lambda i: i[5] == 1, tracks)):
                    logger.debug(track)
                    with suppress(sqlite3.IntegrityError):
                        conn.execute(statements.get(table, _statements["default"][table]), tuple(compress(track, _selectors[profile][table])))

                # "bonuses" table.
                table = "bonuses"
                for track in filter(lambda i: i[8].bool, filter(lambda i: i[1].lower() == "bootlegalbums", tracks)):
                    with suppress(sqlite3.IntegrityError):
                        conn.execute(statements.get(table, _statements["default"][table]), tuple(compress(track, _selectors[profile][table])))

                # "bootlegdiscs" table.
                table = "bootlegdiscs"
                for track in filter(lambda i: i[27] is not None, filter(lambda i: i[1].lower() == "bootlegalbums", tracks)):
                    with suppress(sqlite3.IntegrityError):
                        conn.execute(statements.get(table, _statements["default"][table]), tuple(compress(track, _selectors[profile][table])))

                total_changes += conn.total_changes
                logger.debug(total_changes)

    return total_changes


def _get_albums(db: str, **kwargs):
    """
    Get digital audio albums detail.

    :param db: Database storing digital audio tables.
    :return: Digital audio albums detail sorted by album ID, disc ID, track ID.
    """
    logger = logging.getLogger("{0}._get_albums".format(__name__))
    boolean_to_integer: Mapping[bool, int] = {False: 0, True: 1}
    where, args = "", ()  # type: str, Tuple[Union[bool, int, str], ...]

    #  1. Initializations.
    Track = namedtuple("Track",
                       "album_rowid "
                       "track_rowid "
                       "albumid "
                       "albumsort "
                       "discs "
                       "deluxe "
                       "bootleg "
                       "incollection "
                       "language "
                       "discid "
                       "tracks "
                       "live_disc "
                       "trackid "
                       "title "
                       "live "
                       "bonus "
                       "artistsort "
                       "artist "
                       "origyear "
                       "year "
                       "album "
                       "label "
                       "genre "
                       "upc "
                       "utc_created "
                       "utc_modified "
                       "utc_played "
                       "played")

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

    # 3.a. Subset by `albumid`.
    albumid: List[str] = kwargs.get("albumid", [])
    if albumid:
        where = "{0}(".format(where)
        for item in albumid:
            where = "{0}albumid=? OR ".format(where)
            args += ("{0}".format(item),)
        where = "{0}) AND ".format(where[:-4])

    # 3.b. Subset by `artistsort`.
    artistsort: List[str] = kwargs.get("artistsort", [])
    if artistsort:
        where = "{0}(".format(where)
        for item in artistsort:
            where = "{0}lower(artistsort)=? OR ".format(where)
            args += ("{0}".format(item.lower()),)
        where = "{0}) AND ".format(where[:-4])

    # 3.c. Subset by `albumsort`.
    albumsort: List[str] = kwargs.get("albumsort", [])
    if albumsort:
        where = "{0}(".format(where)
        for item in albumsort:
            where = "{0}albumsort=? OR ".format(where)
            args += ("{0}".format(item),)
        where = "{0}) AND ".format(where[:-4])

    # 3.d. Subset by `genre`.
    genre: List[str] = kwargs.get("genre", [])
    if genre:
        where = "{0}(".format(where)
        for item in genre:
            where = "{0}lower(genre)=? OR ".format(where)
            args += (item.lower(),)
        where = "{0}) AND ".format(where[:-4])

    # 3.e. Subset by `year`.
    year: List[int] = kwargs.get("year", [])
    if year:
        where = "{0}(".format(where)
        for item in year:  # type: ignore
            where = "{0}year=? OR ".format(where)
            args += (item,)
        where = "{0}) AND ".format(where[:-4])

    # 3.f. Subset by `origyear`.
    year = kwargs.get("origyear", [])
    if year:
        where = "{0}(".format(where)
        for item in year:  # type: ignore
            where = "{0}origyear=? OR ".format(where)
            args += (item,)
        where = "{0}) AND ".format(where[:-4])

    # 3.g. Subset by `live`.
    live: Optional[bool] = kwargs.get("live", None)
    if live is not None:
        where = "{0}is_live_track=? AND ".format(where)
        args += (boolean_to_integer[live],)

    # 3.h. Subset by `bootleg`.
    bootleg: Optional[bool] = kwargs.get("bootleg", None)
    if bootleg is not None:
        where = "{0}is_bootleg=? AND ".format(where)
        args += (boolean_to_integer[bootleg],)

    # 4. ORDER BY clause.
    # logger.debug(kwargs.get("orderby"))
    # orderby = "ORDER BY albumid, discid, trackid"  # type: str
    # mylist = list(filter(None, map(REX.sub, repeat(translate_orderfield), kwargs.get("orderby", ["albumid", "discid", "trackid"]))))
    # if mylist:
    #     orderby = "ORDER BY {0}".format(", ".join(mylist))

    # 5. Build SQL statement.
    sql = select  # type: str
    if where:
        sql = f"{select} WHERE {where[:-5]}"
    logger.debug(sql)
    logger.debug(args)

    #  6. Run SQL statement.
    with DatabaseConnection(db) as conn:
        for row in (Track._make(row) for row in conn.execute(sql, args)):
            yield row


def _update_album(table: str, *keys: str, db: str = DATABASE, **kwargs: Any) -> int:
    """
    :param table:
    :param keys:
    :param db:
    :param kwargs:
    :return:
    """
    in_logger = logging.getLogger("{0}._update_album".format(__name__))
    fields = {"albums": ["artistsort", "discs", "genre"],
              "defaultalbums": ["album", "label", "upc", "origyear", "year"],
              "bootlegalbums": ["bootleg_date", "bootleg_city", "bootleg_tour", "bootleg_countryid"]}
    kwargs = {key: value for key, value in kwargs.items() if key.lower() in fields[table]}
    if kwargs:
        try:
            kwargs = _check_arguments(db=db, **kwargs)
        except ValueError as err:
            in_logger.exception(err)
            raise
        else:
            _set, args = set_setclause(**kwargs)  # type: str, Tuple[Any, ...]
            _where, argw = set_whereclause_album(*keys)  # type: str, Tuple[str, ...]
            arguments = args + argw  # type: Tuple[Any, ...]
            return run_statement(f"UPDATE {table.lower()} SET {_set} WHERE {_where}", *arguments, db=db)
    return 0


def _update_disc(table: str, *keys: str, db: str = DATABASE, **kwargs: Any) -> int:
    """
    :param table:
    :param keys:
    :param db:
    :param kwargs:
    :return:
    """
    in_logger = logging.getLogger("{0}._update_disc".format(__name__))
    fields = {"rippeddiscs": ["utc_ripped"]}
    kwargs = {key: value for key, value in kwargs.items() if key.lower() in fields[table]}
    if kwargs:
        try:
            kwargs = _check_arguments(db=db, **kwargs)
        except ValueError as err:
            in_logger.exception(err)
            raise
        else:
            _set, args = set_setclause(**kwargs)  # type: str, Tuple[Any, ...]
            _where, argw = set_whereclause_disc(*keys)  # type: Optional[str], Optional[Tuple[Any, ...]]
            if all([_where is not None, argw is not None]):
                arguments = args + argw  # type: Tuple[Any, ...]
                return run_statement(f"UPDATE {table.lower()} SET {_set} WHERE {_where}", *arguments, db=db)
    return 0


def _update_track(table: str, *keys: str, db: str = DATABASE, **kwargs: Any) -> int:
    """
    :param table:
    :param keys:
    :param db:
    :param kwargs:
    :return:
    """
    in_logger = logging.getLogger("{0}._update_track".format(__name__))
    fields = {"tracks": ["utc_ripped"]}
    kwargs = {key: value for key, value in kwargs.items() if key.lower() in fields[table]}
    if kwargs:
        try:
            kwargs = _check_arguments(db=db, **kwargs)
        except ValueError as err:
            in_logger.exception(err)
            raise
        else:
            _set, args = set_setclause(**kwargs)  # type: str, Tuple[Any, ...]
            _where, argw = set_whereclause_track(*keys)  # type: Optional[str], Optional[Tuple[Any, ...]]
            if all([_where is not None, argw is not None]):
                arguments = args + argw  # type: Tuple[Any, ...]
                return run_statement(f"UPDATE {table.lower()} SET {_set} WHERE {_where}", *arguments, db=db)
    return 0


def _check_arguments(db: str = DATABASE, **kwargs: Any) -> Mapping[str, Any]:
    """

    :param db:
    :param kwargs:
    :return:
    """
    if "genre" in kwargs:
        genre = kwargs["genre"]  # type: str
        genres = list(get_genres(db))  # type: List[Tuple[str, int]]
        if genre.lower() not in (item[0].lower() for item in genres):
            raise ValueError(f'"{genre}" is not defined as genre.')
        _, genreid = next(iter(filter(lambda i: i[0].lower() == genre.lower(), genres)))
        del kwargs["genre"]
        kwargs["genreid"] = genreid

    return kwargs


def _delete_album(albumid: str, *, db: str = DATABASE) -> Tuple[str, int, int, int, int, int, int, int, int, int]:
    """
    Delete a digital album.

    :param albumid: album unique ID.
    :param db: database storing tables.
    :return: Tuple composed of deleted album unique ID, `albums` total change(s), `discs` total change(s) and `tracks` total change(s).
    """

    # 1. Define logger.
    logger = logging.getLogger("{0}._delete_album".format(__name__))

    # 2. Initialize variables.
    bonuses_count, tracks_count, bootlegdiscs_count, playeddiscs_count, rippeddiscs_count, discs_count, bootlegalbums_count, defaultalbums_count, albums_count = 0, 0, 0, 0, 0, 0, 0, 0, 0

    # 3. Connect to database.
    with ExitStack() as stack:
        conn = stack.enter_context(DatabaseConnection(db))
        stack.enter_context(conn)

        # 3a. Is the album a default album or a bootleg album?
        is_bootleg: Optional[bool] = None
        curs = conn.execute("SELECT is_bootleg FROM albums_vw WHERE albumid=?", (albumid,))
        with suppress(TypeError):
            (is_bootleg,) = curs.fetchone()

        # 3b. Update tables.
        if is_bootleg is not None:

            try:

                # BONUSES table.
                conn.execute("DELETE FROM bonuses WHERE albumid=?", (albumid,))
                bonuses_count = conn.total_changes
                count = conn.total_changes  # type: int

                # TRACKS table.
                conn.execute("DELETE FROM tracks WHERE albumid=?", (albumid,))
                tracks_count = conn.total_changes - count
                count = conn.total_changes

                # RIPPEDDISCS table.
                conn.execute("DELETE FROM rippeddiscs WHERE albumid=?", (albumid,))
                rippeddiscs_count = conn.total_changes - count
                count = conn.total_changes

                # PLAYEDDISCS table.
                conn.execute("DELETE FROM playeddiscs WHERE albumid=?", (albumid,))
                playeddiscs_count = conn.total_changes - count
                count = conn.total_changes

                # BOOTLEGDISCS table.
                if is_bootleg:
                    conn.execute("DELETE FROM bootlegdiscs WHERE albumid=?", (albumid,))
                    bootlegdiscs_count = conn.total_changes - count
                    count = conn.total_changes

                # DISCS table.
                conn.execute("DELETE FROM discs WHERE albumid=?", (albumid,))
                discs_count = conn.total_changes - count
                count = conn.total_changes

                # DEFAULTALBUMS table.
                if not is_bootleg:
                    conn.execute("DELETE FROM defaultalbums WHERE albumid=?", (albumid,))
                    defaultalbums_count = conn.total_changes - count
                    count = conn.total_changes

                # BOOTLEGALBUMS table.
                if is_bootleg:
                    conn.execute("DELETE FROM bootlegalbums WHERE albumid=?", (albumid,))
                    bootlegalbums_count = conn.total_changes - count
                    count = conn.total_changes

                # ALBUMS table.
                conn.execute("DELETE FROM albums WHERE rowid=?", (albumid,))
                albums_count = conn.total_changes - count

            except sqlite3.IntegrityError as err:
                logger.exception(err)
                stack.pop_all()
                stack.callback(close_database, conn)

            finally:
                logger.info("ALBUMID            : %s.", albumid)
                logger.info("BONUSES table      : %s record(s) deleted.", "{0:>3d}".format(bonuses_count))
                logger.info("TRACKS table       : %s record(s) deleted.", "{0:>3d}".format(tracks_count))
                logger.info("RIPPEDDISCS table  : %s record(s) deleted.", "{0:>3d}".format(rippeddiscs_count))
                logger.info("PLAYEDDISCS table  : %s record(s) deleted.", "{0:>3d}".format(playeddiscs_count))
                logger.info("BOOTLEGDISCS table : %s record(s) deleted.", "{0:>3d}".format(bootlegdiscs_count))
                logger.info("DISCS table        : %s record(s) deleted.", "{0:>3d}".format(discs_count))
                logger.info("DEFAULTALBUMS table: %s record(s) deleted.", "{0:>3d}".format(defaultalbums_count))
                logger.info("BOOTLEGALBUMS table: %s record(s) deleted.", "{0:>3d}".format(bootlegalbums_count))
                logger.info("ALBUMS table       : %s record(s) deleted.", "{0:>3d}".format(albums_count))

    # 4. Return total changes.
    return albumid, bonuses_count, tracks_count, rippeddiscs_count, playeddiscs_count, bootlegdiscs_count, discs_count, defaultalbums_count, bootlegalbums_count, albums_count
