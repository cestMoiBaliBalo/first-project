# -*- coding: utf-8 -*-
import argparse
import logging.config
import os
import sqlite3
from datetime import datetime
from itertools import repeat

import yaml

from ..shared import convert_tobooleanvalue
from ...AudioCD.shared import getmetadata
from ...parsers import database_parser
from ...shared import LOCAL, TEMPLATE4, UTC, dateformat

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

if __name__ == "__main__":

    # ---------------------
    # Define logging level.
    # ---------------------
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
        logging.config.dictConfig(yaml.load(fp))
    logger = logging.getLogger("Applications.Database.AudioCD.audiostation")

    # ------------------------------
    # Define sqlite3 data converter.
    # ------------------------------
    sqlite3.register_converter("boolean", convert_tobooleanvalue)

    # --------------
    # Define parser.
    # --------------
    parser = argparse.ArgumentParser(parents=[database_parser], argument_default=argparse.SUPPRESS)
    subparser = parser.add_subparsers(dest="step")
    parser_drop = subparser.add_parser("1")
    parser_create = subparser.add_parser("2")
    parser_insert = subparser.add_parser("3")
    parser_insert.add_argument("path")
    parser_insert.add_argument("files", type=int)
    parser_select1 = subparser.add_parser("4")
    parser_select2 = subparser.add_parser("5")
    arguments = parser.parse_args()
    pairs = vars(arguments)
    for key in sorted(pairs):
        logger.debug("{0}: {1}".format(key, pairs[key]))

    # -----------
    # DROP table.
    # -----------
    if int(arguments.step) == 1:
        conn = sqlite3.connect(arguments.db)
        with conn:
            conn.execute("DROP TABLE IF EXISTS audiostation")
        conn.close()

    # -------------
    # CREATE table.
    # -------------
    elif int(arguments.step) == 2:
        conn = sqlite3.connect(arguments.db)
        with conn:
            conn.execute("CREATE TABLE IF NOT EXISTS audiostation (file TEXT NOT NULL, status BOOLEAN NOT NULL DEFAULT 0, utc_created TIMESTAMP NOT NULL, utc_uploaded TIMESTAMP DEFAULT NULL)")
        conn.close()

    # ---------------
    # INSERT records.
    # ---------------
    elif int(arguments.step) == 3:
        changes = 0
        file, extension = os.path.splitext(arguments.path)
        if arguments.files:
            files = zip(["{0}{1:>02d}{2}".format(file[:-2], i, extension) for i in range(1, arguments.files + 1)], repeat(datetime.utcnow()))
            conn = sqlite3.connect(arguments.db)
            try:
                with conn:
                    conn.executemany("INSERT INTO audiostation (file, utc_created) VALUES (?, ?)", files)
            except sqlite3.OperationalError:
                pass
            finally:
                changes = conn.total_changes
                conn.close()
        print(" {0:>2d} files inserted.".format(changes))

    # ---------------
    # SELECT records.
    # ---------------
    elif int(arguments.step) == 4:
        conn = sqlite3.connect(arguments.db, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        for row in conn.execute("SELECT rowid, file, status, utc_created, utc_uploaded FROM audiostation ORDER BY file, utc_created"):
            print("\n\n# ROWID: {0:>4d} ========== #\n".format(row["rowid"]))
            print("Tracks\t: {0}".format(row["file"]).expandtabs(4))
            print("Created\t: {0}".format(dateformat(UTC.localize(row["utc_created"]).astimezone(LOCAL), TEMPLATE4)).expandtabs(4))
            if row["status"]:
                if row["utc_uploaded"]:
                    print("Uploaded: {0}".format(dateformat(UTC.localize(row["utc_uploaded"]).astimezone(LOCAL), TEMPLATE4)).expandtabs(4))
            if not row["status"]:
                print("Uploaded: not uploaded yet!")

    # ---------------
    # SELECT records.
    # ---------------
    elif int(arguments.step) == 5:
        artists = []
        conn = sqlite3.connect(arguments.db, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        for row in conn.execute("SELECT file FROM audiostation WHERE status=? ORDER BY file", (1,)):
            file = getmetadata(row["file"])
            if file.found:
                try:
                    artists.append(file.tags["artistsort"])
                except KeyError:
                    pass
        conn.close()
        for number, artist in enumerate(sorted(set(artists)), start=1):
            print("{0:>2d}. {1}".format(number, artist))
