# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import sqlite3
from contextlib import ExitStack, suppress

from .shared import DatabaseConnection
from ..shared import GENRES

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"


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
            conn.execute("DROP TABLE IF EXISTS bootlegs")
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
            conn.execute("DROP TABLE IF EXISTS defaultalbums")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS bootlegalbums")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS bootlegdiscs")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP TABLE IF EXISTS rippinglog")
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
        conn.execute(
                "CREATE TABLE IF NOT EXISTS genres (genreid INTEGER PRIMARY KEY ASC AUTOINCREMENT, genre TEXT NOT NULL)")
        conn.executemany(
                "INSERT INTO genres (genre) VALUES (?)", [(i,) for i in GENRES])
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS genres_idx ON genres (genre ASC)")

        # --> Languages.
        conn.execute(
                "CREATE TABLE IF NOT EXISTS languages (languageid INTEGER PRIMARY KEY ASC AUTOINCREMENT, language TEXT NOT NULL)")
        conn.executemany(
                "INSERT INTO languages (language) VALUES (?)", [("English",), ("French",)])
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS languages_idx ON languages (language ASC)")

        # --> Supports.
        conn.execute(
                "CREATE TABLE IF NOT EXISTS supports (supportid INTEGER PRIMARY KEY ASC AUTOINCREMENT, support TEXT NOT NULL)")
        conn.executemany(
                "INSERT INTO supports (support) VALUES (?)", [("AudioCD",), ("Digital",)])
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS supports_idx ON supports (support ASC)")

        # --> Countries.
        conn.execute(
                "CREATE TABLE IF NOT EXISTS countries (countryid INTEGER PRIMARY KEY ASC AUTOINCREMENT, country TEXT NOT NULL)")
        conn.executemany(
                "INSERT INTO countries (country) VALUES (?)", [("England",), ("France",), ("Germany",), ("Italy",), ("Sweden",), ("United States",)])
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS countries_idx ON countries (country ASC)")

        # --> Providers.
        conn.execute(
                "CREATE TABLE IF NOT EXISTS providers (providerid INTEGER PRIMARY KEY ASC AUTOINCREMENT, provider TEXT NOT NULL)")
        conn.executemany(
                "INSERT INTO providers (provider) VALUES (?)", [("nugs.net",), ("Crystal Cat Records",), ("Doberman",), ("The Godfatherecords",)])
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS providers_idx ON providers (provider ASC)")

        # --> Applications.
        conn.execute(
                "CREATE TABLE IF NOT EXISTS applications (applicationid INTEGER PRIMARY KEY ASC AUTOINCREMENT, application TEXT NOT NULL)")
        conn.executemany(
                "INSERT INTO applications (application) VALUES (?)", [("dBpoweramp 15.1",), ("dBpoweramp 16.5",)])
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS applications_idx ON applications (application ASC)")

        # --> Artists.
        conn.execute(
                "CREATE TABLE IF NOT EXISTS artists (artistsort TEXT NOT NULL PRIMARY KEY ASC, artist TEXT NOT NULL)")

        # --> Albums.
        conn.execute(
                "CREATE TABLE IF NOT EXISTS albums ("
                "albumid TEXT NOT NULL PRIMARY KEY ASC, "
                "artistsort TEXT NOT NULL REFERENCES artists (artistsort), "
                "discs INTEGER NOT NULL DEFAULT 1, "
                "genreid INTEGER REFERENCES genres (genreid) DEFAULT 1, "
                "supportid INTEGER REFERENCES supports (supportid) DEFAULT 1, "
                "languageid INTEGER REFERENCES languages (languageid) DEFAULT 1, "
                "in_collection BOOLEAN NOT NULL DEFAULT 1, "
                "is_bootleg BOOLEAN NOT NULL DEFAULT 0, "
                "is_deluxe BOOLEAN NOT NULL DEFAULT 0, "
                "is_deleted BOOLEAN NOT NULL DEFAULT 0, "
                "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                "utc_modified TIMESTAMP DEFAULT NULL)")

        # --> Discs.
        conn.execute(
                "CREATE TABLE IF NOT EXISTS discs ("
                "albumid TEXT NOT NULL, "
                "discid INTEGER NOT NULL, "
                "tracks INTEGER NOT NULL DEFAULT 10, "
                "is_live BOOLEAN NOT NULL DEFAULT 0, "
                "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                "utc_modified TIMESTAMP DEFAULT NULL, "
                "FOREIGN KEY (albumid) REFERENCES albums (albumid))")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS discs_idx ON discs (albumid ASC, discid ASC)")

        # --> Tracks.
        conn.execute(
                "CREATE TABLE IF NOT EXISTS tracks ("
                "albumid TEXT NOT NULL, "
                "discid INTEGER NOT NULL, "
                "trackid INTEGER NOT NULL, "
                "title TEXT NOT NULL, "
                "is_live BOOLEAN NOT NULL DEFAULT 0, "
                "is_bonus BOOLEAN NOT NULL DEFAULT 0, "
                "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                "utc_modified TIMESTAMP DEFAULT NULL, "
                "FOREIGN KEY (albumid, discid) REFERENCES discs (albumid, discid))")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS tracks_idx ON tracks (albumid ASC, discid ASC, trackid ASC)")

        # --> Rippeddiscs.
        conn.execute(
                "CREATE TABLE IF NOT EXISTS rippeddiscs ("
                "albumid TEXT NOT NULL, "
                "discid INTEGER NOT NULL, "
                "applicationid INTEGER REFERENCES applications (applicationid) DEFAULT 1, "
                "utc_ripped TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                "utc_modified TIMESTAMP DEFAULT NULL, "
                "FOREIGN KEY (albumid, discid) REFERENCES discs (albumid, discid))")

        # --> Playeddiscs.
        conn.execute(
                "CREATE TABLE IF NOT EXISTS playeddiscs ("
                "albumid TEXT NOT NULL, "
                "discid INTEGER NOT NULL, "
                "utc_played TIMESTAMP DEFAULT NULL DEFAULT (DATETIME('now')), "
                "played INTEGER NOT NULL DEFAULT 0, "
                "utc_created TIMESTAMP NOT NULL, "
                "utc_modified TIMESTAMP DEFAULT NULL, "
                "FOREIGN KEY (albumid, discid) REFERENCES discs (albumid, discid))")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS playeddiscs_idx ON playeddiscs (albumid ASC, discid ASC)")

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
        conn.execute(
                "CREATE TABLE IF NOT EXISTS bootlegalbums ("
                "albumid TEXT PRIMARY KEY ASC, "
                "bootleg_date DATE NOT NULL, "
                "bootleg_city TEXT NOT NULL, "
                "bootleg_tour TEXT NOT NULL, "
                "bootleg_countryid INTEGER REFERENCES countries (countryid), "
                "bootleg_providerid INTEGER REFERENCES providers (providerid), "
                "bootleg_name TEXT DEFAULT NULL, "
                "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                "utc_modified TIMESTAMP DEFAULT NULL, "
                "FOREIGN KEY (albumid) REFERENCES albums (albumid))")

        # --> Bootlegdiscs.
        conn.execute(
                "CREATE TABLE IF NOT EXISTS bootlegdiscs ("
                "albumid TEXT NOT NULL, "
                "discid INTEGER NOT NULL, "
                "disc_reference TEXT DEFAULT NULL, "
                "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                "utc_modified TIMESTAMP DEFAULT NULL, "
                "FOREIGN KEY (albumid, discid) REFERENCES discs (albumid, discid))")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS bootlegdiscs_idx ON bootlegdiscs (albumid ASC, discid ASC)")

        # --> Bonus.
        conn.execute(
                "CREATE TABLE IF NOT EXISTS bonuses ("
                "albumid TEXT NOT NULL, "
                "discid INTEGER NOT NULL, "
                "trackid INTEGER NOT NULL, "
                "bootleg_date DATE NOT NULL, "
                "bootleg_city TEXT NOT NULL, "
                "bootleg_tour TEXT NOT NULL, "
                "bootleg_countryid TEXT REFERENCES countries (countryid), "
                "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                "utc_modified TIMESTAMP DEFAULT NULL, "
                "FOREIGN KEY (albumid, discid, trackid) REFERENCES tracks (albumid, discid, trackid))")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS bonuses_idx ON bonuses (albumid ASC, discid ASC, trackid ASC)")

    with ExitStack() as stack:
        conn = stack.enter_context(DatabaseConnection(db))
        stack.enter_context(conn)
        conn.execute(
                "CREATE VIEW IF NOT EXISTS tracks_vw AS "
                "SELECT "
                "b.rowid AS album_rowid, "
                "t.rowid AS track_rowid, "
                "a.albumid AS albumid, "
                "substr(a.albumid, 3, length(a.albumid) - 15) AS artistsort, "
                "substr(a.albumid, length(a.albumid) - 11) AS albumsort, "
                "d.discid AS discid, "
                "t.trackid AS trackid, "
                "t.title AS title, "
                "d.tracks AS tracks, "
                "r.utc_ripped AS utc_ripped, "
                "p.utc_played AS utc_played, "
                "p.played AS played, "
                "a.origyear AS origyear, "
                "a.year AS year, "
                "e.artist AS artist, "
                "a.album AS album, "
                "b.discs AS discs, "
                "g.genre AS genre, "
                "a.label AS label, "
                "a.upc AS upc, "
                "b.is_bootleg AS is_bootleg, "
                "b.in_collection AS in_collection, "
                "d.is_live AS is_live_disc, "
                "t.is_live AS is_live_track, "
                "b.is_deluxe AS is_deluxe, "
                "t.is_bonus AS is_bonus, "
                "l.language AS language, "
                "NULL AS bootleg_date, "
                "NULL AS bootleg_city, "
                "NULL AS bootleg_country, "
                "NULL AS bootleg_tour, "
                "b.utc_created AS utc_created, "
                "b.utc_modified AS utc_modified "
                "FROM defaultalbums a "
                "JOIN albums b ON a.albumid = b.albumid "
                "JOIN discs d ON a.albumid = d.albumid "
                "JOIN tracks t ON t.albumid = b.albumid AND t.discid = d.discid "
                "LEFT JOIN playeddiscs p ON p.albumid = b.albumid AND p.discid = d.discid "
                "LEFT JOIN rippeddiscs r ON r.albumid = a.albumid AND r.discid = d.discid "
                "JOIN genres g ON b.genreid = g.genreid "
                "JOIN languages l ON b.languageid = l.languageid "
                "JOIN supports s ON b.supportid = s.supportid "
                "JOIN artists e ON e.artistsort = substr(a.albumid, 3, length(a.albumid) - 15) "
                "UNION "
                "SELECT "
                "b.rowid AS album_rowid, "
                "t.rowid AS track_rowid, "
                "boot.albumid AS albumid, "
                "substr(boot.albumid, 3, length(boot.albumid) - 15) AS artistsort, "
                "substr(boot.albumid, length(boot.albumid) - 11) AS albumsort, "
                "d.discid AS discid, "
                "t.trackid AS trackid, "
                "t.title AS title, "
                "d.tracks AS tracks, "
                "r.utc_ripped AS utc_ripped, "
                "p.utc_played AS utc_played, "
                "p.played AS played, "
                "NULL AS origyear, "
                "NULL AS year, "
                "e.artist AS artist, "
                "CASE boot.bootleg_countryid "
                "WHEN 6 "
                "THEN boot.bootleg_tour || ' - ' || strftime('%d/%m/%Y', boot.bootleg_date) || ' - [' || boot.bootleg_city || ']' "
                "ELSE boot.bootleg_tour || ' - ' || strftime('%d/%m/%Y', boot.bootleg_date) || ' - [' || boot.bootleg_city || ', ' || cou.country || ']' "
                "END AS album, "
                "b.discs AS discs, "
                "g.genre AS genre, "
                "NULL AS label, "
                "NULL AS upc, "
                "b.is_bootleg AS is_bootleg, "
                "b.in_collection AS in_collection, "
                "d.is_live AS is_live_disc, "
                "t.is_live AS is_live_track, "
                "b.is_deluxe AS is_deluxe, "
                "t.is_bonus AS is_bonus, "
                "l.language AS language, "
                "boot.bootleg_date AS bootleg_date, "
                "boot.bootleg_city AS bootleg_city, "
                "cou.country AS bootleg_country, "
                "boot.bootleg_tour AS bootleg_tour, "
                "b.utc_created AS utc_created, "
                "b.utc_modified AS utc_modified "
                "FROM bootlegalbums boot "
                "JOIN albums b ON boot.albumid = b.albumid "
                "JOIN discs d ON boot.albumid = d.albumid "
                "JOIN tracks t ON t.albumid = b.albumid AND t.discid = d.discid "
                "LEFT JOIN playeddiscs p ON p.albumid = b.albumid AND p.discid = d.discid "
                "LEFT JOIN rippeddiscs r ON r.albumid = boot.albumid AND r.discid = d.discid "
                "JOIN genres g ON b.genreid = g.genreid "
                "JOIN languages l ON b.languageid = l.languageid "
                "JOIN supports s ON b.supportid = s.supportid "
                "JOIN countries cou ON boot.bootleg_countryid = cou.countryid "
                "JOIN artists e ON e.artistsort = substr(boot.albumid, 3, length(boot.albumid) - 15)"
        )

    return db
