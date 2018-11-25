# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import json
import logging
import os
import sqlite3
from contextlib import ExitStack, suppress
from datetime import datetime
from itertools import chain, repeat, tee
from typing import IO, Iterable, Mapping, Optional, Sequence, Tuple, Union

from Applications import shared
from Applications.Tables.shared import DatabaseConnection, close_database
from Applications.callables import exclude_allbutaudiofiles

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# ==================
# Public interfaces.
# ==================
def get_drive_albums() -> Iterable[Tuple[str, str, str, str, str, bool, str, str]]:
    """

    :return:
    """
    for artistid, albumid, artist_path, album_path, album, is_bootleg, file, extension in _get_albums():
        yield artistid, albumid, artist_path, album_path, album, is_bootleg, file, extension


def get_database_albums() -> Iterable[Tuple[str, str, str, str, str, bool, str, str]]:
    """

    :return:
    """
    with ExitStack() as _stack:
        conn = _stack.enter_context(DatabaseConnection(os.path.expandvars("%_XREFERENCES%")))
        for artistid, albumid, artist_path, album_path, album, is_bootleg, file, extension in ((row["artistid"],
                                                                                                row["albumid"],
                                                                                                row["artist_path"],
                                                                                                row["album_path"],
                                                                                                row["album"],
                                                                                                row["is_bootleg"],
                                                                                                row["file"],
                                                                                                row["extension"]) for row in
                                                                                               conn.execute(
                                                                                                       "SELECT artistid, albumid, artist_path, album_path, album, is_bootleg, file, extension FROM albums_vw "
                                                                                                       "ORDER BY artistid, albumid, extension, file")):
            yield artistid, albumid, artist_path, album_path, album, is_bootleg, file, extension


def insert_albums(*collection: Sequence[Union[bool, str]]) -> int:
    """

    :param collection:
    :return:
    """
    return _insert_albums(*collection, logobj=logging.getLogger(f"{__name__}.insert_albums"))


def insert_albums_fromjson(*jsonfiles: IO) -> int:
    """

    :param jsonfiles:
    :return:
    """
    return _insert_albums(*chain.from_iterable(json.load(file) for file in jsonfiles), logobj=logging.getLogger(f"{__name__}.insert_albums_fromjson"))


def remove_albums(*collection: Sequence[Union[bool, str]]) -> int:
    """

    :param collection:
    :return:
    """
    return _remove_albums(*collection, logobj=logging.getLogger(f"{__name__}.remove_albums"))


def get_artists(*extensions: str) -> Iterable[Tuple[str, str]]:
    """

    :param extensions:
    :return:
    """
    select = "SELECT DISTINCT artistid, artist_path FROM albums_vw "  # type: str
    where = None  # type: Optional[str]
    args = ()  # type: Tuple[str, ...]
    if extensions:
        placeholders = ", ".join(["?"] * len(extensions))  # type: str
        where = f"WHERE extension IN ({placeholders}) "
        args += tuple(extension.lower() for extension in extensions)
    orderby = "ORDER BY artistid"  # type: str
    statement = f"{select}"  # type: str
    if where:
        statement = f"{statement}{where}"
    statement = f"{statement}{orderby}"
    with ExitStack() as stack:
        conn = stack.enter_context(DatabaseConnection(os.path.join(shared.get_dirname(os.path.abspath(__file__), level=4), "Resources", "xreferences.db")))
        for row in conn.execute(statement, args):
            yield row["artistid"], row["artist_path"]


def get_albums(artist: str, *extensions: str) -> Iterable[Tuple[str, str, str, str, str]]:
    """

    :param artist:
    :param extensions:
    :return:
    """
    select = "SELECT DISTINCT artistid, albumid, artist_path, album, album_path FROM albums_vw "  # type: str
    where = "WHERE artistid=? AND "  # type: str
    args = (artist,)  # type: Tuple[str, ...]
    if extensions:
        placeholders = ", ".join(["?"] * len(extensions))  # type: str
        where = f"{where}extension IN ({placeholders}) AND "
        args += tuple(extension.lower() for extension in extensions)
    orderby = "ORDER BY albumid"  # type: str
    statement = f"{select}{where[:-5]} {orderby}"  # type: str
    with ExitStack() as stack:
        conn = stack.enter_context(DatabaseConnection(os.path.join(shared.get_dirname(os.path.abspath(__file__), level=4), "Resources", "xreferences.db")))
        for row in conn.execute(statement, args):
            yield row["artistid"], row["albumid"], row["artist_path"], row["album"], row["album_path"]


# ===================
# Private interfaces.
# ===================
def _filter_albums(arg: Tuple[str, str, str, str, str, bool]) -> bool:
    return "recycle" not in arg[2].lower()


def _get_albums() -> Iterable[Tuple[str, str, str, str, str, bool, str, str]]:
    """

    """
    logger = logging.getLogger(f"{__name__}.get_albums")

    # `_albums` below is an iter object.
    # Every yielded item is a 6-item tuple describing an album.
    _albums = chain.from_iterable(filter(_filter_albums, [(artistid,
                                                           albumid,
                                                           artist_path,
                                                           album_path,
                                                           album,
                                                           is_bootleg) for album, album_path, albumid, is_bootleg in shared.get_albums(artist_path)]) for artistid, artist_path in shared.get_artists())
    _albums_it1, _albums_it2, _albums_it3 = tee(_albums, 3)
    logger.debug(" # LOCAL DRIVE ALBUMS ================================================== #")
    for _item in _albums_it1:
        logger.debug(_item)

    # `_files` below is a generator object.
    # Every yielded item is a sequence composed of N 2-item tuples describing the audio files associated with an album.
    # Every tuple is composed of the file basename and the file extension.
    _files = ([(os.path.basename(os.path.splitext(file)[0]), os.path.splitext(file)[1][1:]) for file in shared.find_files(_item[3], excluded=exclude_allbutaudiofiles)] for _item in _albums_it2)
    _files_it1, _files_it2 = tee(_files)
    logger.debug("# LOCAL DRIVE FILES ================================================== #")
    for _item in _files_it1:  # type: ignore
        logger.debug(_item)

    first = True
    # `_collection` below is a generator object.
    # Every yielded item is a zip object.
    # Every zip object yields a 2-items tuple:
    #     - The first item is a tuple describing an album.
    #     - The second item is a tuple describing an audio file associated with the album.
    _collection = (zip(repeat(album), files) for album, files in zip(_albums_it3, _files_it2))
    for _zipobj in _collection:
        for _item in _zipobj:  # type: ignore
            artistid, albumid, artist_path, album_path, album, is_bootleg, file, extension = chain.from_iterable(_item)
            if first:
                first = False
                logger.debug("# LOCAL DRIVE COLLECTION ================================================== #")
            logger.debug(_item)
            yield artistid, albumid, artist_path, album_path, album, is_bootleg, file, extension


def _insert_albums(*collection: Sequence[Union[bool, str]], logobj=None) -> int:
    """

    :param collection:
    :param logobj:
    :return:
    """
    to_integer = {True: 1, False: 0}  # type: Mapping[bool, int]
    with ExitStack() as _stack:
        _conn = _stack.enter_context(DatabaseConnection(os.path.expandvars("%_XREFERENCES%")))
        _stack.enter_context(_conn)
        _collection = iter(collection)
        _total_changes = 0  # type: int
        for artistid, albumid, artist_path, album_path, album, is_bootleg, file, extension in _collection:

            # Insert artist.
            with suppress(sqlite3.IntegrityError):
                _conn.execute("INSERT INTO artists (artistid, artist_path, utc_created) VALUES (?, ?, ?)", (artistid, artist_path, datetime.utcnow()))
            _artists_changes = _conn.total_changes - _total_changes
            if logobj:
                logobj.info("{0:>3d} artist(s) inserted.".format(_artists_changes))

            # Insert album.
            with suppress(sqlite3.IntegrityError):
                _conn.execute("INSERT INTO albums (artistid, albumid, album_path, album, is_bootleg, utc_created) VALUES (?, ?, ?, ?, ?, ?)",
                              (artistid, albumid, album_path, album, to_integer[is_bootleg], datetime.utcnow()))
            _albums_changes = _conn.total_changes - _total_changes - _artists_changes
            if logobj:
                logobj.info("{0:>3d} album(s) inserted.".format(_albums_changes))

            # Insert file.
            _conn.execute("INSERT INTO files (artistid, albumid, file, extension, utc_created) VALUES (?, ?, ?, ?, ?)", (artistid, albumid, file, extension, datetime.utcnow()))
            _files_changes = _conn.total_changes - _total_changes - _albums_changes - _artists_changes
            _total_changes = _conn.total_changes
            if logobj:
                logobj.info("{0:>3d} file(s) inserted.".format(_files_changes))

        _changes = _conn.total_changes  # type: int
        if not _changes:
            _stack.pop_all()
            _stack.callback(close_database, _conn)
    return _changes


def _remove_albums(*collection: Sequence[Union[bool, str]], logobj=None) -> int:
    """

    :param collection:
    :param logobj:
    :return:
    """
    with ExitStack() as _stack:
        _conn = _stack.enter_context(DatabaseConnection(os.path.expandvars("%_XREFERENCES%")))
        _stack.enter_context(_conn)
        _collection = iter(collection)
        for artistid, albumid, _, _, _, _, _, _ in _collection:
            # Delete file(s).
            _conn.execute("DELETE FROM files WHERE artistid=? AND albumid=?", (artistid, albumid))
            _files_changes = _conn.total_changes
            if logobj:
                logobj.info("{0:>3d} file(s) removed.".format(_files_changes))

            # Delete album(s).
            with suppress(sqlite3.IntegrityError):
                _conn.execute("DELETE FROM albums WHERE artistid=? AND albumid=?", (artistid, albumid))
            _albums_changes = _conn.total_changes - _files_changes
            if logobj:
                logobj.info("{0:>3d} album(s) removed.".format(_albums_changes))

            # Delete artist.
            with suppress(sqlite3.IntegrityError):
                _conn.execute("DELETE FROM artists WHERE artistid=?", (artistid,))
            _artists_changes = _conn.total_changes - _albums_changes - _files_changes
            if logobj:
                logobj.info("{0:>3d} artist(s) removed.".format(_artists_changes))

        _changes = _conn.total_changes  # type: int
        if not _changes:
            _stack.pop_all()
            _stack.callback(close_database, _conn)
    return _changes
