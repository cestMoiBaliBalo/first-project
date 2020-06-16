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
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP VIEW IF EXISTS defaultalbums_vw")
        with suppress(sqlite3.OperationalError):
            conn.execute("DROP VIEW IF EXISTS tracks_vw")
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
                "INSERT INTO supports (support) VALUES (?)", [("CD",), ("Digital",)])
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS supports_idx ON supports (support ASC)")

        # --> Countries.
        conn.execute(
                "CREATE TABLE IF NOT EXISTS countries (countryid INTEGER PRIMARY KEY ASC AUTOINCREMENT, country TEXT NOT NULL)")
        conn.executemany(
                "INSERT INTO countries (country) VALUES (?)", [("Australia",), ("England",), ("France",), ("Germany",), ("Italy",), ("Norway",), ("Sweden",), ("United States",)])
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
                "INSERT INTO applications (application) VALUES (?)", [("dBpoweramp 15.1",), ("dBpoweramp Release 16.6",)])
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS applications_idx ON applications (application ASC)")

        # --> Repositories.
        conn.execute("CREATE TABLE IF NOT EXISTS repositories (repositoryid INTEGER PRIMARY KEY ASC AUTOINCREMENT, repository PATH NOT NULL)")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS repositories_idx ON repositories (repository ASC)")
        conn.executemany("INSERT INTO repositories (repository) VALUES (?)", [(Path("G:/") / "Music" / "Lossless1",), (Path("G:/") / "Music" / "Lossless2",)])

        # --> Duplicates.
        conn.execute(
                "CREATE TABLE IF NOT EXISTS duplicates ("
                "albumid TEXT NOT NULL, "
                "discid INTEGER NOT NULL, "
                "repositoryid INTEGER REFERENCES repositories (repositoryid), "
                "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                "utc_modified TIMESTAMP DEFAULT NULL, "
                "FOREIGN KEY (albumid, discid) REFERENCES discs (albumid, discid))")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS duplicates_idx ON duplicates (albumid ASC, discid ASC, repositoryid ASC)")

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
                "utc_played TIMESTAMP DEFAULT NULL, "
                "played INTEGER NOT NULL DEFAULT 0, "
                "utc_created TIMESTAMP NOT NULL, "
                "utc_modified TIMESTAMP DEFAULT NULL, "
                "FOREIGN KEY (albumid, discid) REFERENCES discs (albumid, discid))")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS playeddiscs_idx ON playeddiscs (albumid ASC, discid ASC)")

        # --> Bootlegdiscs.
        conn.execute(
                "CREATE TABLE IF NOT EXISTS bootlegdiscs ("
                "albumid TEXT NOT NULL, "
                "discid INTEGER NOT NULL, "
                "referenceid TEXT DEFAULT NULL, "
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
        conn.execute(
                "CREATE TABLE IF NOT EXISTS bootlegalbums ("
                "albumid TEXT PRIMARY KEY ASC, "
                "providerid INTEGER REFERENCES providers (providerid), "
                "title TEXT DEFAULT NULL, "
                "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                "utc_modified TIMESTAMP DEFAULT NULL, "
                "FOREIGN KEY (albumid) REFERENCES albums (albumid))")

        # --> Livealbums.
        conn.execute(
                "CREATE TABLE IF NOT EXISTS livealbums ("
                "albumid TEXT PRIMARY KEY ASC, "
                "date DATE NOT NULL, "
                "city TEXT NOT NULL, "
                "tour TEXT NOT NULL, "
                "countryid INTEGER REFERENCES countries (countryid), "
                "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                "utc_modified TIMESTAMP DEFAULT NULL, "
                "FOREIGN KEY (albumid) REFERENCES albums (albumid))")

        # --> Digitalalbums.
        conn.execute(
                "CREATE TABLE IF NOT EXISTS digitalalbums ("
                "albumid TEXT REFERENCES albums (albumid), "
                "providerid INTEGER REFERENCES providers (providerid), "
                "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
                "utc_modified TIMESTAMP DEFAULT NULL)")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS digitalalbums_idx ON digitalalbums (albumid ASC, providerid ASC)")

        # --> Bonuses.
        conn.execute(
                "CREATE TABLE IF NOT EXISTS bonuses ("
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

    with ExitStack() as stack:
        conn = stack.enter_context(DatabaseConnection(db))
        stack.enter_context(conn)
        conn.execute(
                "CREATE VIEW IF NOT EXISTS tracks_vw AS "
                "SELECT "
                "dft.rowid AS defaultalbum_rowid, "
                "alb.rowid AS album_rowid, "
                "tra.rowid AS track_rowid, "
                "dft.albumid AS albumid, "
                "alb.artistsort AS artistsort, "
                "substr(dft.albumid, length(dft.albumid) - 11) AS albumsort, "
                "dis.discid AS discid, "
                "tra.trackid AS trackid, "
                "tra.title AS title, "
                "dis.tracks AS tracks, "
                "rip.utc_ripped AS utc_ripped, "
                "pla.utc_played AS utc_played, "
                "pla.played AS played, "
                "dft.origyear AS origyear, "
                "dft.year AS year, "
                "art.artist AS artist, "
                "dft.album AS album, "
                "alb.discs AS discs, "
                "gen.genre AS genre, "
                "dft.label AS label, "
                "dft.upc AS upc, "
                "alb.is_bootleg AS is_bootleg, "
                "alb.in_collection AS in_collection, "
                "dis.is_live AS is_live_disc, "
                "tra.is_live AS is_live_track, "
                "alb.is_deluxe AS is_deluxe, "
                "tra.is_bonus AS is_bonus, "
                "lan.language AS language, "
                "liv.date, "
                "liv.city, "
                "liv.country, "
                "liv.tour, "
                "alb.utc_created AS utc_created, "
                "alb.utc_modified AS utc_modified "
                "FROM defaultalbums dft "
                "INNER JOIN albums alb ON alb.albumid = dft.albumid "
                "INNER JOIN artists art ON art.artistsort = alb.artistsort "
                "INNER JOIN discs dis ON dis.albumid = dft.albumid "
                "INNER JOIN tracks tra ON tra.albumid = dft.albumid AND tra.discid = dis.discid "
                "INNER JOIN genres gen ON gen.genreid = alb.genreid "
                "INNER JOIN languages lan ON lan.languageid = alb.languageid "
                "LEFT JOIN playeddiscs pla ON pla.albumid = dft.albumid AND pla.discid = dis.discid "
                "LEFT JOIN rippeddiscs rip ON rip.albumid = dft.albumid AND rip.discid = dis.discid "
                "LEFT OUTER JOIN (SELECT a.albumid, a.date, a.city, cou.country, a.tour FROM livealbums a INNER JOIN countries cou ON a.countryid = cou.countryid) liv ON liv.albumid = dft.albumid "
                "UNION "
                "SELECT "
                "boot.rowid AS bootlegalbum_rowid, "
                "alb.rowid AS album_rowid, "
                "tra.rowid AS track_rowid, "
                "boot.albumid AS albumid, "
                "alb.artistsort AS artistsort, "
                "substr(boot.albumid, length(boot.albumid) - 11) AS albumsort, "
                "dis.discid AS discid, "
                "tra.trackid AS trackid, "
                "tra.title AS title, "
                "dis.tracks AS tracks, "
                "rip.utc_ripped AS utc_ripped, "
                "pla.utc_played AS utc_played, "
                "pla.played AS played, "
                "NULL AS origyear, "
                "NULL AS year, "
                "art.artist AS artist, "
                "CASE liv.countryid "
                "WHEN 6 "
                "THEN liv.tour || ' - ' || strftime('%d/%m/%Y', liv.date) || ' - [' || liv.city || ']' "
                "ELSE liv.tour || ' - ' || strftime('%d/%m/%Y', liv.date) || ' - [' || liv.city || ', ' || liv.country || ']' "
                "END AS album, "
                "alb.discs AS discs, "
                "gen.genre AS genre, "
                "NULL AS label, "
                "NULL AS upc, "
                "alb.is_bootleg AS is_bootleg, "
                "alb.in_collection AS in_collection, "
                "dis.is_live AS is_live_disc, "
                "tra.is_live AS is_live_track, "
                "alb.is_deluxe AS is_deluxe, "
                "tra.is_bonus AS is_bonus, "
                "lan.language AS language, "
                "liv.date, "
                "liv.city, "
                "liv.country, "
                "liv.tour, "
                "alb.utc_created AS utc_created, "
                "alb.utc_modified AS utc_modified "
                "FROM bootlegalbums boot "
                "INNER JOIN albums alb ON boot.albumid = alb.albumid "
                "INNER JOIN artists art ON art.artistsort = alb.artistsort "
                "INNER JOIN discs dis ON boot.albumid = dis.albumid "
                "INNER JOIN tracks tra ON tra.albumid = boot.albumid AND tra.discid = dis.discid "
                "INNER JOIN genres gen ON alb.genreid = gen.genreid "
                "INNER JOIN languages lan ON alb.languageid = lan.languageid "
                "LEFT JOIN playeddiscs pla ON pla.albumid = boot.albumid AND pla.discid = dis.discid "
                "LEFT JOIN rippeddiscs rip ON rip.albumid = boot.albumid AND rip.discid = dis.discid "
                "LEFT OUTER JOIN (SELECT a.albumid, a.date, a.city, a.countryid, cou.country, a.tour FROM livealbums a INNER JOIN countries cou ON a.countryid = cou.countryid) liv ON liv.albumid = boot.albumid"
        )
        conn.execute(
                "CREATE VIEW IF NOT EXISTS defaultalbums_vw AS "
                "SELECT "
                "alb.rowid AS album_rowid, "
                "dft.rowid AS rowid, "
                "dft.albumid AS albumid, "
                "alb.artistsort AS artistsort, "
                "substr(dft.albumid, length(dft.albumid) - 11) AS albumsort, "
                "art.artist AS artist, "
                "alb.discs AS discs, "
                "dis.discid AS discid, "
                "dis.tracks AS tracks, "
                "dft.origyear AS origyear, "
                "dft.year AS year, "
                "dft.album AS album, "
                "gen.genre AS genre, "
                "dft.label AS label, "
                "dft.upc AS upc, "
                "alb.is_bootleg AS is_bootleg, "
                "tra.trackid AS track, "
                "tra.title AS title, "
                "dis.is_live AS is_disc_live, "
                "tra.is_live AS is_track_live, "
                "tra.is_bonus AS is_track_bonus, "
                "dft.utc_created AS created_date, "
                "rip.utc_ripped AS ripped_date, "
                "CASE "
                "WHEN rip.utc_ripped IS NOT NULL "
                "THEN cast(strftime('%Y', rip.utc_ripped) AS INTEGER) "
                "ELSE NULL "
                "END AS ripped_year, "
                "CASE "
                "WHEN rip.utc_ripped IS NOT NULL "
                "THEN cast(strftime('%m', rip.utc_ripped) AS INTEGER) "
                "ELSE NULL "
                "END AS ripped_month, "
                "pla.utc_played AS played_date, "
                "CASE "
                "WHEN pla.utc_played IS NOT NULL "
                "THEN cast(strftime('%Y', pla.utc_played) AS INTEGER) "
                "ELSE NULL "
                "END AS played_year, "
                "CASE "
                "WHEN pla.utc_played IS NOT NULL "
                "THEN cast(strftime('%m', pla.utc_played) AS INTEGER) "
                "ELSE NULL "
                "END AS played_month, "
                "ifnull(pla.played, 0) AS played, "
                "sup.support AS support "
                "FROM albums alb "
                "INNER JOIN defaultalbums dft ON alb.albumid = dft.albumid "
                "INNER JOIN artists art ON art.artistsort = alb.artistsort "
                "INNER JOIN discs dis ON alb.albumid = dis.albumid "
                "INNER JOIN tracks tra ON alb.albumid = tra.albumid AND dis.discid = tra.discid "
                "INNER JOIN genres gen ON gen.genreid = alb.genreid "
                "INNER JOIN supports sup ON alb.supportid = sup.supportid "
                "LEFT JOIN rippeddiscs rip ON rip.albumid = alb.albumid AND rip.discid = dis.discid "
                "LEFT JOIN playeddiscs pla ON pla.albumid = alb.albumid AND pla.discid = dis.discid"
        )

    return db
