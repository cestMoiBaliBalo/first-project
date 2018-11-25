# -*- coding: utf-8 -*-
import argparse
import logging.config
import os
import sqlite3
from contextlib import ExitStack, suppress
from datetime import datetime

import yaml
from dateutil.parser import parse

from Applications.Tables.shared import DatabaseConnection, ToBoolean, adapt_booleanvalue, close_database, convert_tobooleanvalue
from Applications.callables import exclude_allbutaudiofiles
from Applications.parsers import database_parser
from Applications.shared import DATABASE, GENRES, LOCAL, MUSIC, TEMPLATE4, UTC, find_files, get_albums, get_artists, get_readabledate

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))
logger = logging.getLogger("database")


# ==========================
# SQLite3 custom converters.
# ==========================
def datetime_converter(bytstr):
    chrstr = bytstr.decode("ascii")
    datobj = parse(chrstr)
    with suppress(ValueError):
        datobj = UTC.localize(parse(chrstr))
    return get_readabledate(datobj.astimezone(LOCAL), template=TEMPLATE4)


# ================
# SQLite3 adapter.
# ================
sqlite3.register_adapter(ToBoolean, adapt_booleanvalue)

# ==================
# SQLite3 converter.
# ==================
sqlite3.register_converter("boolean", convert_tobooleanvalue)

# ==========
# Arguments.
# ==========
parser = argparse.ArgumentParser(parents=[database_parser])
parser.add_argument("task", type=int, nargs="+")
argument = parser.parse_args()

# ==========
# Constants.
# ==========
DATABASE_READ = DATABASE

# =========
# Mappings.
# =========
d = {False: 0, True: 1}

# ============
# Main script.
# ============
for task in argument.task:

    # DROP tables.
    if task == 1:
        conn = sqlite3.connect(argument.db)
        with conn:
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
                conn.execute("DROP TABLE IF EXISTS defaultalbums")
            with suppress(sqlite3.OperationalError):
                conn.execute("DROP TABLE IF EXISTS bootlegalbums")
            with suppress(sqlite3.OperationalError):
                conn.execute("DROP TABLE IF EXISTS bootlegdiscs")
            with suppress(sqlite3.OperationalError):
                conn.execute("DROP TABLE IF EXISTS rippinglog")
            with suppress(sqlite3.OperationalError):
                conn.execute("DROP TABLE IF EXISTS encoders")
            with suppress(sqlite3.OperationalError):
                conn.execute("DROP TABLE IF EXISTS mytable")
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
        conn.close()

    # CREATE tables.
    elif task == 2:
        conn = sqlite3.connect(argument.db)
        with conn:

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
                    "INSERT INTO applications (application) VALUES (?)", [("dBpoweramp 15.1",)])
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
                    "utc_played TIMESTAMP DEFAULT NULL, "
                    "played INTEGER NOT NULL DEFAULT 0, "
                    "utc_created TIMESTAMP NOT NULL DEFAULT (DATETIME('now')), "
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

            # --> Bonuses.
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

        conn.close()

    # CREATE main views.
    elif task == 3:
        with ExitStack() as stack:
            conn = stack.enter_context(DatabaseConnection(argument.db))
            stack.enter_context(conn)
            with suppress(sqlite3.OperationalError):
                conn.execute("DROP VIEW IF EXISTS playeddiscs_vw")
            with suppress(sqlite3.OperationalError):
                conn.execute("DROP VIEW IF EXISTS played_albums_vw")
            with suppress(sqlite3.OperationalError):
                conn.execute("DROP VIEW IF EXISTS played_albums_vw1")
            with suppress(sqlite3.OperationalError):
                conn.execute("DROP VIEW IF EXISTS played_albums_vw2")
            with suppress(sqlite3.OperationalError):
                conn.execute("DROP VIEW IF EXISTS albums_vw")
            with suppress(sqlite3.OperationalError):
                conn.execute("DROP VIEW IF EXISTS tracks_vw")
            with suppress(sqlite3.OperationalError):
                conn.execute("DROP VIEW IF EXISTS audiocdalbums")
            with suppress(sqlite3.OperationalError):
                conn.execute("DROP VIEW IF EXISTS bootlegalbums_view")
            try:
                conn.execute(
                        "CREATE VIEW IF NOT EXISTS playeddiscs_vw AS "
                        "SELECT "
                        "a.rowid AS rowid, "
                        "a.albumid AS albumid, "
                        "substr(a.albumid, 3, length(a.albumid) - 15) AS artistsort, "
                        "substr(a.albumid, length(a.albumid) - 11) AS albumsort, "
                        "e.artist AS artist, "
                        "a.discid AS discid, "
                        "c.year AS year, "
                        "c.origyear AS origyear, "
                        "c.album AS album, "
                        "d.genre AS genre, "
                        "c.label AS label, "
                        "c.upc AS upc, "
                        "a.utc_played AS utc_played, "
                        "cast(strftime('%Y', a.utc_played) AS INTEGER) AS year_played, "
                        "cast(strftime('%m', a.utc_played) AS INTEGER) AS month_played, "
                        "a.played AS played, "
                        "b.is_bootleg AS is_bootleg, "
                        "NULL AS bootleg_date, "
                        "NULL AS bootleg_city, "
                        "NULL AS bootleg_country, "
                        "NULL AS bootleg_tour "
                        "FROM playeddiscs a "
                        "JOIN albums b ON a.albumid = b.albumid "
                        "JOIN defaultalbums c ON b.albumid = c.albumid "
                        "JOIN genres d ON b.genreid = d.genreid "
                        "JOIN artists e ON e.artistsort = substr(a.albumid, 3, length(a.albumid) - 15) "
                        "UNION "
                        "SELECT "
                        "a.rowid AS rowid, "
                        "a.albumid AS albumid, "
                        "substr(a.albumid, 3, length(a.albumid) - 15) AS artistsort, "
                        "substr(a.albumid, length(a.albumid) - 11) AS albumsort, "
                        "e.artist AS artist, "
                        "a.discid AS discid, "
                        "NULL AS year, "
                        "NULL AS origyear, "
                        "CASE boot.bootleg_countryid "
                        "WHEN 6 "
                        "THEN boot.bootleg_tour || ' - ' || strftime('%d/%m/%Y', boot.bootleg_date) || ' - [' || boot.bootleg_city || ']' "
                        "ELSE boot.bootleg_tour || ' - ' || strftime('%d/%m/%Y', boot.bootleg_date) || ' - [' || boot.bootleg_city || ', ' || h.country || ']' "
                        "END AS album, "
                        "d.genre AS genre, "
                        "NULL AS label, "
                        "NULL AS upc, "
                        "a.utc_played AS utc_played, "
                        "cast(strftime('%Y', a.utc_played) AS INTEGER) AS year_played, "
                        "cast(strftime('%m', a.utc_played) AS INTEGER) AS month_played, "
                        "a.played AS played, "
                        "b.is_bootleg AS is_bootleg, "
                        "c.bootleg_date AS bootleg_date, "
                        "c.bootleg_city AS bootleg_city, "
                        "h.country AS bootleg_country, "
                        "c.bootleg_tour AS bootleg_tour "
                        "FROM playeddiscs a "
                        "JOIN albums b ON a.albumid = b.albumid "
                        "JOIN bootlegalbums c ON b.albumid = c.albumid "
                        "JOIN genres d ON b.genreid = d.genreid "
                        "JOIN countries h ON c.bootleg_countryid = h.countryid "
                        "JOIN artists e ON e.artistsort = substr(a.albumid, 3, length(a.albumid) - 15)"
                )
                conn.execute(
                        "CREATE VIEW IF NOT EXISTS albums_vw AS "
                        "SELECT "
                        "alb.rowid AS main_rowid, "
                        "dft.rowid AS secondary_rowid, "
                        "dft.albumid AS albumid, "
                        "substr(dft.albumid, 3, length(dft.albumid) - 15) AS artistsort, "
                        "substr(dft.albumid, length(dft.albumid) - 11) AS albumsort, "
                        "dis.discid AS discid, "
                        "dis.tracks AS tracks, "
                        "rip.utc_ripped AS utc_ripped, "
                        "play.utc_played AS utc_played, "
                        "play.played AS played, "
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
                        "alb.is_deluxe AS is_deluxe, "
                        "lan.language AS language, "
                        "NULL AS bootleg_date, "
                        "NULL AS bootleg_city, "
                        "NULL AS bootleg_country, "
                        "NULL AS bootleg_tour "
                        "FROM defaultalbums dft "
                        "JOIN albums alb ON dft.albumid = alb.albumid "
                        "JOIN discs dis ON dft.albumid = dis.albumid "
                        "LEFT JOIN playeddiscs play ON play.albumid = alb.albumid AND play.discid = dis.discid "
                        "LEFT JOIN rippeddiscs rip ON rip.albumid = dft.albumid AND rip.discid = dis.discid "
                        "JOIN genres gen ON alb.genreid = gen.genreid "
                        "JOIN languages lan ON alb.languageid = lan.languageid "
                        "JOIN supports sup ON alb.supportid = sup.supportid "
                        "JOIN artists art ON art.artistsort = substr(dft.albumid, 3, length(dft.albumid) - 15) "
                        "UNION "
                        "SELECT "
                        "alb.rowid AS main_rowid, "
                        "boot.rowid AS secondary_rowid, "
                        "boot.albumid AS albumid, "
                        "substr(boot.albumid, 3, length(boot.albumid) - 15) AS artistsort, "
                        "substr(boot.albumid, length(boot.albumid) - 11) AS albumsort, "
                        "dis.discid AS discid, "
                        "dis.tracks AS tracks, "
                        "rip.utc_ripped AS utc_ripped, "
                        "play.utc_played AS utc_played, "
                        "play.played AS played, "
                        "NULL AS origyear, "
                        "NULL AS year, "
                        "art.artist AS artist, "
                        "CASE boot.bootleg_countryid "
                        "WHEN 6 "
                        "THEN boot.bootleg_tour || ' - ' || strftime('%d/%m/%Y', boot.bootleg_date) || ' - [' || boot.bootleg_city || ']' "
                        "ELSE boot.bootleg_tour || ' - ' || strftime('%d/%m/%Y', boot.bootleg_date) || ' - [' || boot.bootleg_city || ', ' || cou.country || ']' "
                        "END AS album, "
                        "alb.discs AS discs, "
                        "gen.genre AS genre, "
                        "NULL AS label, "
                        "NULL AS upc, "
                        "alb.is_bootleg AS is_bootleg, "
                        "alb.in_collection AS in_collection, "
                        "dis.is_live AS is_live_disc, "
                        "alb.is_deluxe AS is_deluxe, "
                        "lan.language AS language, "
                        "boot.bootleg_date AS bootleg_date, "
                        "boot.bootleg_city AS bootleg_city, "
                        "cou.country AS bootleg_country, "
                        "boot.bootleg_tour AS bootleg_tour "
                        "FROM bootlegalbums boot "
                        "JOIN albums alb ON boot.albumid = alb.albumid "
                        "JOIN discs dis ON boot.albumid = dis.albumid "
                        "LEFT JOIN playeddiscs play ON play.albumid = alb.albumid AND play.discid = dis.discid "
                        "LEFT JOIN rippeddiscs rip ON rip.albumid = boot.albumid AND rip.discid = dis.discid "
                        "JOIN genres gen ON alb.genreid = gen.genreid "
                        "JOIN languages lan ON alb.languageid = lan.languageid "
                        "JOIN supports sup ON alb.supportid = sup.supportid "
                        "JOIN countries cou ON boot.bootleg_countryid = cou.countryid "
                        "JOIN artists art ON art.artistsort = substr(boot.albumid, 3, length(boot.albumid) - 15)"
                )
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
            except sqlite3.OperationalError as err:
                print(err)
                stack.pop_all()
                stack.callback(close_database, conn)

    # --> Display data from "rippeddiscs_vw" view.
    elif task == 12:
        sqlite3.register_converter("timestamp", datetime_converter)
        with DatabaseConnection(argument.db) as conn:
            for row in conn.execute(
                    "SELECT rowid, albumid, albumsort, discid, is_disc_live, album, genre, label, upc, application, ripped_date, is_bootleg, bootleg_date, bootleg_city, bootleg_country, bootleg_tour, support "
                    "FROM rippeddiscs_vw "
                    "ORDER BY rowid"):
                print(row["rowid"],
                      row["albumid"],
                      row["albumsort"],
                      row["discid"],
                      row["is_disc_live"],
                      row["album"],
                      row["genre"],
                      row["label"],
                      row["upc"],
                      row["application"],
                      row["ripped_date"],
                      row["is_bootleg"],
                      row["bootleg_date"],
                      row["bootleg_city"],
                      row["bootleg_country"],
                      row["bootleg_tour"],
                      row["support"])

    # --> Display data from "audiocdalbums_vw" view.
    elif task == 13:
        sqlite3.register_converter("timestamp", datetime_converter)
        with DatabaseConnection(argument.db) as conn:
            for row in conn.execute(
                    "SELECT albumid, artistsort, discid, ripped_year, ripped_month, ripped_date, played_date, played, discs, album, genre, label, upc, is_bootleg, is_deluxe, language FROM audiocdalbums_vw"):
                print(row["albumid"],
                      row["artistsort"],
                      row["discid"],
                      row["ripped_year"],
                      row["ripped_month"],
                      row["ripped_date"],
                      row["played_date"],
                      row["played"],
                      row["discs"],
                      row["album"],
                      row["genre"],
                      row["label"],
                      row["upc"],
                      row["is_bootleg"],
                      row["is_deluxe"],
                      row["language"])

    # --> Display data from "tracks_vw" view.
    # elif task == 14:
    # with DatabaseConnection(argument.db) as conn:
    # for row in conn.execute("SELECT albumid, discid, trackid, artistsort, albumsort, album, title, is_live_disc, is_live_track FROM tracks_vw ORDER BY albumid, discid, trackid"):
    # print(row["albumid"], row["discid"], row["trackid"], row["artistsort"], row["albumsort"], row["album"], row["title"], row["is_live_disc"], row["is_live_track"])

    # --> Display data from "bonuses" table.
    elif task == 15:
        with DatabaseConnection(argument.db) as conn:
            for row in conn.execute("SELECT * FROM bonuses ORDER BY rowid"):
                print(row)

    # --> Display data from "bootlegalbums_vw" view.
    elif task == 16:
        with DatabaseConnection(argument.db) as conn:
            for row in conn.execute(
                    "SELECT "
                    "albumid, "
                    "artistsort, "
                    "albumsort, "
                    "album, "
                    "discid, "
                    "track, "
                    "title, "
                    "is_disc_live, "
                    "is_track_live, "
                    "is_track_bonus, "
                    "bootlegtrack_year, "
                    "bootlegtrack_month, "
                    "bootlegtrack_date, "
                    "bootlegtrack_city, "
                    "bootlegtrack_country, "
                    "bootlegtrack_tour, "
                    "created_date, "
                    "played_date, "
                    "support "
                    "FROM bootlegalbums_vw "
                    "ORDER BY albumid, discid, track"):
                print(row["albumid"],
                      row["artistsort"],
                      row["albumsort"],
                      row["album"],
                      row["discid"],
                      row["track"],
                      row["title"],
                      row["is_disc_live"],
                      row["is_track_live"],
                      row["is_track_bonus"],
                      row["bootlegtrack_year"],
                      row["bootlegtrack_month"],
                      row["bootlegtrack_date"],
                      row["bootlegtrack_city"],
                      row["bootlegtrack_country"],
                      row["bootlegtrack_tour"],
                      row["created_date"],
                      row["played_date"],
                      row["support"])

    elif task == 21:
        with ExitStack() as stack:
            conn = stack.enter_context(DatabaseConnection(argument.db))
            stack.enter_context(conn)
            with suppress(sqlite3.OperationalError):
                conn.execute("DROP VIEW IF EXISTS defaultalbums_vw")
            try:
                conn.execute(
                        "CREATE VIEW IF NOT EXISTS defaultalbums_vw AS "
                        "SELECT "
                        "dft.rowid AS rowid, "
                        "dft.albumid AS albumid, "
                        "substr(dft.albumid, 3, length(dft.albumid) - 15) AS artistsort, "
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
                        "dis.is_live AS is_disc_live, "
                        "trk.trackid AS track, "
                        "trk.title AS title, "
                        "trk.is_live AS is_track_live, "
                        "trk.is_bonus AS is_track_bonus, "
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
                        "JOIN defaultalbums dft ON alb.albumid = dft.albumid "
                        "JOIN discs dis ON alb.albumid = dis.albumid "
                        "JOIN tracks trk ON alb.albumid = trk.albumid AND dis.discid = trk.discid "
                        "JOIN genres gen ON gen.genreid = alb.genreid "
                        "JOIN supports sup ON alb.supportid = sup.supportid "
                        "JOIN artists art ON art.artistsort = substr(alb.albumid, 3, length(alb.albumid) - 15) "
                        "LEFT JOIN rippeddiscs rip ON rip.albumid = alb.albumid AND rip.discid = dis.discid "
                        "LEFT JOIN playeddiscs pla ON pla.albumid = alb.albumid AND pla.discid = dis.discid"
                )
            except sqlite3.OperationalError as err:
                print(err)
                stack.pop_all()
                stack.callback(close_database, conn)

    elif task == 22:
        with ExitStack() as stack:
            conn = stack.enter_context(DatabaseConnection(argument.db))
            stack.enter_context(conn)
            with suppress(sqlite3.OperationalError):
                conn.execute("DROP VIEW IF EXISTS bootlegalbums_vw")
            try:
                conn.execute(
                        "CREATE VIEW IF NOT EXISTS bootlegalbums_vw AS "
                        "SELECT "
                        "boot.rowid AS rowid, "
                        "alb.albumid AS albumid, "
                        "substr(alb.albumid, 3, length(alb.albumid) - 15) AS artistsort, "
                        "substr(alb.albumid, length(alb.albumid) - 11) AS albumsort, "
                        "art.artist AS artist, "
                        "alb.discs AS discs, "
                        "dis.discid AS discid, "
                        "dis.tracks AS tracks, "
                        "CASE boot.bootleg_countryid "
                        "WHEN 6 "
                        "THEN boot.bootleg_tour || ' - ' || strftime('%d/%m/%Y', boot.bootleg_date) || ' - [' || boot.bootleg_city || ']' "
                        "ELSE boot.bootleg_tour || ' - ' || strftime('%d/%m/%Y', boot.bootleg_date) || ' - [' || boot.bootleg_city || ', ' || cou1.country || ']' "
                        "END AS album, "
                        "gen.genre AS genre, "
                        "alb.is_bootleg AS is_bootleg, "
                        "dis.is_live AS is_disc_live, "
                        "trk.trackid AS track, "
                        "trk.title AS title, "
                        "trk.is_live AS is_track_live, "
                        "trk.is_bonus AS is_track_bonus, "
                        "cast(strftime('%Y', boot.bootleg_date) AS INTEGER) AS bootlegtrack_year, "
                        "cast(strftime('%m', boot.bootleg_date) AS INTEGER) AS bootlegtrack_month, "
                        "strftime('%d/%m/%Y', ifnull(bon.bootleg_date, boot.bootleg_date)) AS bootlegtrack_date, "
                        "ifnull(bon.bootleg_city, boot.bootleg_city) AS bootlegtrack_city, "
                        "ifnull(bon.bootleg_tour, boot.bootleg_tour) AS bootlegtrack_tour, "
                        "cou2.country AS bootlegtrack_country, "
                        "boot.utc_created AS created_date, "
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
                        "sup.support AS support, "
                        "boot.bootleg_countryid, "
                        "ifnull(bon.bootleg_countryid, boot.bootleg_countryid) AS bootlegtrack_countryid "
                        "FROM albums alb "
                        "JOIN bootlegalbums boot ON boot.albumid = alb.albumid "
                        "JOIN discs dis ON alb.albumid = dis.albumid "
                        "JOIN tracks trk ON alb.albumid = trk.albumid AND dis.discid = trk.discid "
                        "JOIN genres gen ON gen.genreid = alb.genreid "
                        "JOIN supports sup ON alb.supportid = sup.supportid "
                        "JOIN countries cou1 ON boot.bootleg_countryid = cou1.countryid "
                        "JOIN countries cou2 ON bootlegtrack_countryid = cou2.countryid "
                        "JOIN artists art ON art.artistsort = substr(alb.albumid, 3, length(alb.albumid) - 15) "
                        "LEFT JOIN bonuses bon ON alb.albumid = bon.albumid AND dis.discid = bon.discid AND trk.trackid = bon.trackid "
                        "LEFT JOIN rippeddiscs rip ON rip.albumid = alb.albumid AND rip.discid = dis.discid "
                        "LEFT JOIN playeddiscs pla ON pla.albumid = alb.albumid AND pla.discid = dis.discid"
                )
            except sqlite3.OperationalError as err:
                print(err)
                stack.pop_all()
                stack.callback(close_database, conn)

    elif task == 23:
        with ExitStack() as stack:
            conn = stack.enter_context(DatabaseConnection(argument.db))
            stack.enter_context(conn)
            with suppress(sqlite3.OperationalError):
                conn.execute("DROP VIEW IF EXISTS rippeddiscs_vw")
            try:
                conn.execute(
                        "CREATE VIEW IF NOT EXISTS rippeddiscs_vw AS "
                        "SELECT "
                        "rip.rowid AS rowid, "
                        "rip.albumid AS albumid, "
                        "substr(rip.albumid, 3, length(rip.albumid) - 15) AS artistsort, "
                        "substr(rip.albumid, length(rip.albumid) - 11) AS albumsort, "
                        "art.artist AS artist, "
                        "rip.discid AS discid, "
                        "dis.tracks AS tracks, "
                        "dft.origyear AS origyear, "
                        "dft.year AS year, "
                        "dft.album AS album, "
                        "gen.genre AS genre, "
                        "dft.label AS label, "
                        "dft.upc AS upc, "
                        "alb.is_bootleg AS is_bootleg, "
                        "dis.is_live AS is_disc_live, "
                        "NULL AS bootleg_date, "
                        "NULL AS bootleg_city, "
                        "NULL AS bootleg_country, "
                        "NULL AS bootleg_tour, "
                        "app.application AS application, "
                        "rip.utc_ripped AS ripped_date, "
                        "cast(strftime('%Y', rip.utc_ripped) AS INTEGER) AS ripped_year, "
                        "cast(strftime('%m', rip.utc_ripped) AS INTEGER) AS ripped_month, "
                        "rip.utc_created AS created_date, "
                        "rip.utc_modified AS modified_date, "
                        "sup.support AS support "
                        "FROM rippeddiscs rip "
                        "JOIN albums alb ON rip.albumid = alb.albumid "
                        "JOIN defaultalbums dft ON alb.albumid = dft.albumid "
                        "JOIN discs dis ON rip.albumid = dis.albumid AND rip.discid = dis.discid "
                        "JOIN genres gen ON gen.genreid = alb.genreid "
                        "JOIN supports sup ON alb.supportid = sup.supportid "
                        "JOIN applications app ON app.applicationid = rip.applicationid "
                        "JOIN artists art ON art.artistsort = substr(rip.albumid, 3, length(rip.albumid) - 15) "
                        "UNION "
                        "SELECT "
                        "rip.rowid AS rowid, "
                        "rip.albumid AS albumid, "
                        "substr(rip.albumid, 3, length(rip.albumid) - 15) AS artistsort, "
                        "substr(rip.albumid, length(rip.albumid) - 11) AS albumsort, "
                        "art.artist AS artist, "
                        "rip.discid AS discid, "
                        "dis.tracks AS tracks, "
                        "NULL AS origyear, "
                        "NULL AS year, "
                        "CASE boot.bootleg_countryid "
                        "WHEN 6 "
                        "THEN boot.bootleg_tour || ' - ' || strftime('%d/%m/%Y', boot.bootleg_date) || ' - [' || boot.bootleg_city || ']' "
                        "ELSE boot.bootleg_tour || ' - ' || strftime('%d/%m/%Y', boot.bootleg_date) || ' - [' || boot.bootleg_city || ', ' || cou.country || ']' "
                        "END AS album, "
                        "gen.genre AS genre, "
                        "NULL AS label, "
                        "NULL AS upc, "
                        "alb.is_bootleg AS is_bootleg, "
                        "dis.is_live AS is_disc_live, "
                        "boot.bootleg_date AS bootleg_date, "
                        "boot.bootleg_city AS bootleg_city, "
                        "cou.country AS bootleg_country, "
                        "boot.bootleg_tour AS bootleg_tour, "
                        "app.application AS application, "
                        "rip.utc_ripped AS ripped_date, "
                        "cast(strftime('%Y', rip.utc_ripped) AS INTEGER) AS ripped_year, "
                        "cast(strftime('%m', rip.utc_ripped) AS INTEGER) AS ripped_month, "
                        "rip.utc_created AS created_date, "
                        "rip.utc_modified AS modified_date, "
                        "sup.support AS support "
                        "FROM rippeddiscs rip "
                        "JOIN albums alb ON rip.albumid = alb.albumid "
                        "JOIN bootlegalbums boot ON alb.albumid = boot.albumid "
                        "JOIN discs dis ON rip.albumid = dis.albumid AND rip.discid = dis.discid "
                        "JOIN genres gen ON alb.genreid = gen.genreid "
                        "JOIN supports sup ON alb.supportid = sup.supportid "
                        "JOIN applications app ON rip.applicationid = app.applicationid "
                        "JOIN countries cou ON boot.bootleg_countryid = cou.countryid "
                        "JOIN artists art ON art.artistsort = substr(rip.albumid, 3, length(rip.albumid) - 15)"
                )
            except sqlite3.OperationalError as err:
                print(err)
                stack.pop_all()
                stack.callback(close_database, conn)

    elif task == 24:
        with ExitStack() as stack:
            conn = stack.enter_context(DatabaseConnection(argument.db))
            stack.enter_context(conn)
            with suppress(sqlite3.OperationalError):
                conn.execute("DROP VIEW IF EXISTS audiocdalbums_vw")
            try:
                conn.execute(
                        "CREATE VIEW IF NOT EXISTS audiocdalbums_vw AS "
                        "SELECT "
                        "alb.rowid AS main_rowid, "
                        "dft.rowid AS secondary_rowid, "
                        "dft.albumid AS albumid, "
                        "substr(dft.albumid, 3, length(dft.albumid) - 15) AS artistsort, "
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
                        "alb.is_deluxe AS is_deluxe, "
                        "dis.is_live AS is_live_disc, "
                        "lan.language AS language, "
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
                        "play.utc_played AS played_date, "
                        "CASE "
                        "WHEN play.utc_played IS NOT NULL "
                        "THEN cast(strftime('%Y', play.utc_played) AS INTEGER) "
                        "ELSE NULL "
                        "END AS played_year, "
                        "CASE "
                        "WHEN play.utc_played IS NOT NULL "
                        "THEN cast(strftime('%m', play.utc_played) AS INTEGER) "
                        "ELSE NULL "
                        "END AS played_month, "
                        "ifnull(play.played, 0) AS played, "
                        "sup.support AS support "
                        "FROM defaultalbums dft "
                        "JOIN albums alb ON dft.albumid = alb.albumid "
                        "JOIN discs dis ON dft.albumid = dis.albumid "
                        "LEFT JOIN playeddiscs play ON play.albumid = alb.albumid AND play.discid = dis.discid "
                        "LEFT JOIN rippeddiscs rip ON rip.albumid = alb.albumid AND rip.discid = dis.discid "
                        "JOIN genres gen ON alb.genreid = gen.genreid "
                        "JOIN languages lan ON alb.languageid = lan.languageid "
                        "JOIN supports sup ON alb.supportid = sup.supportid "
                        "JOIN artists art ON art.artistsort = substr(dft.albumid, 3, length(dft.albumid) - 15) "
                        "WHERE alb.supportid = 1 "
                        "UNION "
                        "SELECT "
                        "alb.rowid AS main_rowid, "
                        "boot.rowid AS secondary_rowid, "
                        "boot.albumid AS albumid, "
                        "substr(boot.albumid, 3, length(boot.albumid) - 15) AS artistsort, "
                        "substr(boot.albumid, length(boot.albumid) - 11) AS albumsort, "
                        "art.artist AS artist, "
                        "alb.discs AS discs, "
                        "dis.discid AS discid, "
                        "dis.tracks AS tracks, "
                        "NULL AS origyear, "
                        "NULL AS year, "
                        "CASE boot.bootleg_countryid "
                        "WHEN 6 "
                        "THEN boot.bootleg_tour || ' - ' || strftime('%d/%m/%Y', boot.bootleg_date) || ' - [' || boot.bootleg_city || ']' "
                        "ELSE boot.bootleg_tour || ' - ' || strftime('%d/%m/%Y', boot.bootleg_date) || ' - [' || boot.bootleg_city || ', ' || cou.country || ']' "
                        "END AS album, "
                        "gen.genre AS genre, "
                        "NULL AS label, "
                        "NULL AS upc, "
                        "alb.is_bootleg AS is_bootleg, "
                        "dis.is_live AS is_live_disc, "
                        "alb.is_deluxe AS is_deluxe, "
                        "lan.language AS language, "
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
                        "play.utc_played AS played_date, "
                        "CASE "
                        "WHEN play.utc_played IS NOT NULL "
                        "THEN cast(strftime('%Y', play.utc_played) AS INTEGER) "
                        "ELSE NULL "
                        "END AS played_year, "
                        "CASE "
                        "WHEN play.utc_played IS NOT NULL "
                        "THEN cast(strftime('%m', play.utc_played) AS INTEGER) "
                        "ELSE NULL "
                        "END AS played_month, "
                        "ifnull(play.played, 0) AS played, "
                        "sup.support AS support "
                        "FROM bootlegalbums boot "
                        "JOIN albums alb ON boot.albumid = alb.albumid "
                        "JOIN discs dis ON boot.albumid = dis.albumid "
                        "LEFT JOIN playeddiscs play ON play.albumid = alb.albumid AND play.discid = dis.discid "
                        "LEFT JOIN rippeddiscs rip ON rip.albumid = alb.albumid AND rip.discid = dis.discid "
                        "JOIN genres gen ON alb.genreid = gen.genreid "
                        "JOIN languages lan ON alb.languageid = lan.languageid "
                        "JOIN supports sup ON alb.supportid = sup.supportid "
                        "JOIN countries cou ON boot.bootleg_countryid = cou.countryid "
                        "JOIN artists art ON art.artistsort = substr(boot.albumid, 3, length(boot.albumid) - 15) "
                        "WHERE alb.supportid = 1"
                )
            except sqlite3.OperationalError as err:
                print(err)
                stack.pop_all()
                stack.callback(close_database, conn)

    elif task == 25:
        with ExitStack() as stack:
            conn = stack.enter_context(DatabaseConnection(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Resources", "xreferences.db")))
            stack.enter_context(conn)
            conn.execute("DROP TABLE IF EXISTS files")
            conn.execute("DROP TABLE IF EXISTS albums")
            conn.execute("DROP VIEW IF EXISTS albums_vw")
            conn.execute("DROP TABLE IF EXISTS artists")
            conn.execute("CREATE TABLE IF NOT EXISTS artists (artistid TEXT NOT NULL PRIMARY KEY ASC, artist_path TEXT NOT NULL, utc_created TIMESTAMP NOT NULL)")
            conn.execute(
                    "CREATE TABLE IF NOT EXISTS albums (artistid TEXT NOT NULL, albumid TEXT NOT NULL, album_path TEXT NOT NULL, album TEXT NOT NULL, is_bootleg BOOLEAN DEFAULT 0, utc_created TIMESTAMP NOT "
                    "NULL, "
                    "FOREIGN KEY (artistid) REFERENCES artists (artistid), "
                    "PRIMARY KEY (artistid, albumid))")
            conn.execute(
                    "CREATE TABLE IF NOT EXISTS files (artistid TEXT NOT NULL, albumid TEXT NOT NULL, file TEXT NOT NULL, extension TEXT NOT NULL, utc_created TIMESTAMP NOT NULL, "
                    "FOREIGN KEY (artistid, albumid) REFERENCES albums (artistid, albumid), "
                    "PRIMARY KEY (artistid, albumid, file, extension))")
            conn.execute(
                    "CREATE VIEW IF NOT EXISTS albums_vw AS SELECT a.artistid, b.albumid, c.file, c.extension, a.artist_path, b.album_path, b.album, b.is_bootleg FROM artists a "
                    "JOIN albums b ON a.artistid=b.artistid "
                    "JOIN files c ON b.artistid=c.artistid AND b.albumid=c.albumid")

    elif task == 26:
        to_integer = {True: 1, False: 0}
        with ExitStack() as stack:
            conn = stack.enter_context(DatabaseConnection(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Resources", "xreferences.db")))
            stack.enter_context(conn)
            for artist, artist_path in get_artists(MUSIC):
                if "recycle" in artist_path.lower():
                    continue
                conn.execute("INSERT INTO artists (artistid, artist_path, utc_created) VALUES (?, ?, ?)", (artist, artist_path, datetime.utcnow()))
                print("# ----- #")
                print(artist)
                print(artist_path)
                for album, album_path, albumid, isbootleg in get_albums(artist_path):
                    conn.execute("INSERT INTO albums (artistid, album_path, albumid, album, is_bootleg, utc_created) VALUES (?, ?, ?, ?, ?, ?)",
                                 (artist, album_path, albumid, album, to_integer[isbootleg], datetime.utcnow()))
                    print("# #")
                    print(album)
                    print(album_path)
                    print(albumid)
                    print(isbootleg)
                    for file in find_files(album_path, excluded=exclude_allbutaudiofiles):
                        file, extension = os.path.splitext(file)
                        conn.execute("INSERT INTO files (artistid, albumid, file, extension, utc_created) VALUES (?, ?, ?, ?, ?)", (artist, albumid, os.path.basename(file), extension[1:], datetime.utcnow()))
                        print("# #")
                        print(os.path.basename(file))
                        print(extension[1:])
