# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import sqlite3
from contextlib import ExitStack, suppress
from pathlib import Path, PosixPath, WindowsPath
from typing import Union

from .shared import DatabaseConnection
from ..shared import GENRES

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


def adapt_path(path: Union[PosixPath, WindowsPath]) -> str:
    return str(path)


def convert_path(byt: bytes) -> Path:
    return Path(byt.decode())


sqlite3.register_adapter(WindowsPath, adapt_path)
sqlite3.register_adapter(PosixPath, adapt_path)
sqlite3.register_converter("path", convert_path)


def drop_tables(db: str) -> str:
    """

    :param db:
    :return:
    """
    with ExitStack() as stack:
        conn = stack.enter_context(DatabaseConnection(db))
        stack.enter_context(conn)
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS artists")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS albums")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS discs")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS tracks")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS bonuses")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS rippeddiscs")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS playeddiscs")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS bootlegdiscs")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS defaultalbums")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS bootlegalbums")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS livealbums")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS digitalalbums")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS genres")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS languages")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS supports")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS providers")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS countries")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS applications")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS repositories")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS duplicates")

    return db


def create_tables(db: str) -> str:
    """

    :param db:
    :return:
    """
    with ExitStack() as stack:
        conn = stack.enter_context(DatabaseConnection(db))
        stack.enter_context(conn)

        # --> Genres.
        conn.execute("CREATE TABLE IF NOT EXISTS genres (genreid INTEGER PRIMARY KEY ASC AUTOINCREMENT, genre TEXT NOT NULL)")
        conn.executemany("INSERT INTO genres (genre) VALUES (?)", [(item,) for item in GENRES])
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS genres_idx ON genres (genre ASC)")

        # --> Languages.
        conn.execute("CREATE TABLE IF NOT EXISTS languages (languageid INTEGER PRIMARY KEY ASC AUTOINCREMENT, language TEXT NOT NULL)")
        conn.executemany("INSERT INTO languages (language) VALUES (?)", [("English",), ("French",)])
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS languages_idx ON languages (language ASC)")

        # --> Supports.
        conn.execute("CREATE TABLE IF NOT EXISTS supports (supportid INTEGER PRIMARY KEY ASC AUTOINCREMENT, support TEXT NOT NULL)")
        conn.executemany("INSERT INTO supports (support) VALUES (?)", [("CD",), ("Digital",)])
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS supports_idx ON supports (support ASC)")

        # --> Countries.
        conn.execute("CREATE TABLE IF NOT EXISTS countries (countryid INTEGER PRIMARY KEY ASC AUTOINCREMENT, country TEXT NOT NULL)")
        conn.executemany("INSERT INTO countries (country) VALUES (?)", [("Australia",), ("England",), ("France",), ("Germany",), ("Italy",), ("Norway",), ("Sweden",), ("United States",)])
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS countries_idx ON countries (country ASC)")

        # --> Providers.
        conn.execute("CREATE TABLE IF NOT EXISTS providers (providerid INTEGER PRIMARY KEY ASC AUTOINCREMENT, provider TEXT NOT NULL)")
        conn.executemany("INSERT INTO providers (provider) VALUES (?)", [("nugs.net",), ("Crystal Cat Records",), ("Doberman",), ("The Godfatherecords",), ("HDtracks.com",)])
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS providers_idx ON providers (provider ASC)")

        # --> Applications.
        conn.execute("CREATE TABLE IF NOT EXISTS applications (applicationid INTEGER PRIMARY KEY ASC AUTOINCREMENT, application TEXT NOT NULL)")
        conn.executemany("INSERT INTO applications (application) VALUES (?)", [("dBpoweramp 15.1",), ("dBpoweramp Release 16.6",)])
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS applications_idx ON applications (application ASC)")

        # --> Repositories.
        conn.execute("CREATE TABLE IF NOT EXISTS repositories (repositoryid INTEGER PRIMARY KEY ASC AUTOINCREMENT, repository PATH NOT NULL)")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS repositories_idx ON repositories (repository ASC)")
        conn.executemany("INSERT INTO repositories (repository) VALUES (?)", [(Path("G:/") / "Music" / "Lossless1",), (Path("G:/") / "Music" / "Lossless2",)])

        # --> Duplicates.
        conn.execute("CREATE TABLE IF NOT EXISTS duplicates ("
                     "albumid TEXT NOT NULL, "
                     "discid INTEGER NOT NULL, "
                     "repositoryid INTEGER REFERENCES repositories (repositoryid), "
                     "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                     "utc_modified TIMESTAMP DEFAULT NULL, "
                     "FOREIGN KEY (albumid, discid) REFERENCES discs (albumid, discid))")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS duplicates_idx ON duplicates (albumid ASC, discid ASC, repositoryid ASC)")

        # --> Artists.
        conn.execute("CREATE TABLE IF NOT EXISTS artists (artistsort TEXT NOT NULL PRIMARY KEY ASC, artist TEXT NOT NULL)")

        # --> Albums.
        conn.execute("CREATE TABLE IF NOT EXISTS albums ("
                     "albumid TEXT NOT NULL PRIMARY KEY ASC, "
                     "artistsort TEXT NOT NULL REFERENCES artists (artistsort), "
                     "discs INTEGER NOT NULL DEFAULT 1, "
                     "genreid INTEGER REFERENCES genres (genreid) DEFAULT 1, "
                     "languageid INTEGER REFERENCES languages (languageid) DEFAULT 1, "
                     "in_collection BOOLEAN NOT NULL DEFAULT 1, "
                     "is_bootleg BOOLEAN NOT NULL DEFAULT 0, "
                     "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                     "utc_modified TIMESTAMP DEFAULT NULL)")

        # --> Discs.
        conn.execute("CREATE TABLE IF NOT EXISTS discs ("
                     "albumid TEXT NOT NULL, "
                     "discid INTEGER NOT NULL, "
                     "tracks INTEGER NOT NULL DEFAULT 10, "
                     "is_live BOOLEAN NOT NULL DEFAULT 0, "
                     "is_bonus BOOLEAN NOT NULL DEFAULT 0, "
                     "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                     "utc_modified TIMESTAMP DEFAULT NULL, "
                     "FOREIGN KEY (albumid) REFERENCES albums (albumid))")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS discs_idx ON discs (albumid ASC, discid ASC)")

        # --> Tracks.
        conn.execute("CREATE TABLE IF NOT EXISTS tracks ("
                     "albumid TEXT NOT NULL, "
                     "discid INTEGER NOT NULL, "
                     "trackid INTEGER NOT NULL, "
                     "title TEXT NOT NULL, "
                     "is_live BOOLEAN NOT NULL DEFAULT 0, "
                     "is_bonus BOOLEAN NOT NULL DEFAULT 0, "
                     "supportid INTEGER REFERENCES supports (supportid) DEFAULT 1, "
                     "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                     "utc_modified TIMESTAMP DEFAULT NULL, "
                     "FOREIGN KEY (albumid, discid) REFERENCES discs (albumid, discid))")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS tracks_idx ON tracks (albumid ASC, discid ASC, trackid ASC)")

        # --> Rippeddiscs.
        conn.execute("CREATE TABLE IF NOT EXISTS rippeddiscs ("
                     "albumid TEXT NOT NULL, "
                     "discid INTEGER NOT NULL, "
                     "applicationid INTEGER REFERENCES applications (applicationid) DEFAULT 1, "
                     "utc_ripped TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                     "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                     "utc_modified TIMESTAMP DEFAULT NULL, "
                     "FOREIGN KEY (albumid, discid) REFERENCES discs (albumid, discid))")

        # --> Playeddiscs.
        conn.execute("CREATE TABLE IF NOT EXISTS playeddiscs ("
                     "albumid TEXT NOT NULL, "
                     "discid INTEGER NOT NULL, "
                     "played INTEGER NOT NULL DEFAULT 0, "
                     "utc_played TIMESTAMP DEFAULT NULL, "
                     "utc_created TIMESTAMP NOT NULL, "
                     "utc_modified TIMESTAMP DEFAULT NULL, "
                     "FOREIGN KEY (albumid, discid) REFERENCES discs (albumid, discid))")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS playeddiscs_idx ON playeddiscs (albumid ASC, discid ASC)")

        # --> Bootlegdiscs.
        conn.execute("CREATE TABLE IF NOT EXISTS bootlegdiscs ("
                     "albumid TEXT NOT NULL, "
                     "discid INTEGER NOT NULL, "
                     "bootlegid TEXT DEFAULT NULL, "
                     "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                     "utc_modified TIMESTAMP DEFAULT NULL, "
                     "FOREIGN KEY (albumid, discid) REFERENCES discs (albumid, discid))")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS bootlegdiscs_idx ON bootlegdiscs (albumid ASC, discid ASC)")

        # --> Defaultalbums.
        conn.execute(
                "CREATE TABLE IF NOT EXISTS defaultalbums ("
                "albumid TEXT PRIMARY KEY ASC, "
                "origyear INTEGER NOT NULL, "
                "year INTEGER NOT NULL, "
                "album TEXT NOT NULL, "
                "label TEXT DEFAULT NULL, "
                "upc TEXT DEFAULT NULL, "
                "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                "utc_modified TIMESTAMP DEFAULT NULL, "
                "FOREIGN KEY (albumid) REFERENCES albums (albumid))")

        # --> Bootlegalbums.
        conn.execute("CREATE TABLE IF NOT EXISTS bootlegalbums ("
                     "albumid TEXT PRIMARY KEY ASC, "
                     "providerid INTEGER REFERENCES providers (providerid), "
                     "title TEXT DEFAULT NULL, "
                     "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                     "utc_modified TIMESTAMP DEFAULT NULL, "
                     "FOREIGN KEY (albumid) REFERENCES albums (albumid))")

        # --> Livealbums.
        conn.execute("CREATE TABLE IF NOT EXISTS livealbums ("
                     "albumid TEXT PRIMARY KEY ASC, "
                     "date DATE NOT NULL, "
                     "city TEXT NOT NULL, "
                     "tour TEXT NOT NULL, "
                     "countryid INTEGER REFERENCES countries (countryid), "
                     "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                     "utc_modified TIMESTAMP DEFAULT NULL, "
                     "FOREIGN KEY (albumid) REFERENCES albums (albumid))")

        # --> Digitalalbums.
        conn.execute("CREATE TABLE IF NOT EXISTS digitalalbums ("
                     "albumid TEXT REFERENCES albums (albumid), "
                     "providerid INTEGER REFERENCES providers (providerid), "
                     "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                     "utc_modified TIMESTAMP DEFAULT NULL)")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS digitalalbums_idx ON digitalalbums (albumid ASC, providerid ASC)")

        # --> Bonuses.
        conn.execute("CREATE TABLE IF NOT EXISTS bonuses ("
                     "albumid TEXT NOT NULL, "
                     "discid INTEGER NOT NULL, "
                     "trackid INTEGER NOT NULL, "
                     "date DATE NOT NULL, "
                     "city TEXT NOT NULL, "
                     "tour TEXT NOT NULL, "
                     "countryid TEXT REFERENCES countries (countryid), "
                     "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                     "utc_modified TIMESTAMP DEFAULT NULL, "
                     "FOREIGN KEY (albumid, discid, trackid) REFERENCES tracks (albumid, discid, trackid))")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS bonuses_idx ON bonuses (albumid ASC, discid ASC, trackid ASC)")

    return db


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument("database")
    arguments = parser.parse_args()
    create_tables(drop_tables(os.path.abspath(arguments.database)))
