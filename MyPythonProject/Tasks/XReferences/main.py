# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import locale
import logging.config
import os
import sys
from datetime import datetime
from itertools import compress, groupby
from operator import itemgetter
from typing import Set, Tuple

import yaml

from Applications.Tables.XReferences.shared import get_database_albums, get_drive_albums, insert_albums, remove_albums
from Applications.shared import LOCAL, get_dirname

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# -----
locale.setlocale(locale.LC_ALL, ("french", "fr_FR.ISO8859-1"))

# -----
with open(os.path.join(get_dirname(os.path.abspath(__file__), level=3), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))
logger = logging.getLogger("MyPythonProject.Tasks.XReferences.main")

# -----
dt_beg = LOCAL.localize(datetime.now())

# -----
albums_drive = set(get_drive_albums())  # type: Set[Tuple[str, str, str, str, str, bool, str, str]]
albums_database = set(get_database_albums())  # type: Set[Tuple[str, str, str, str, str, bool, str, str]]

# -----
changes = 0  # type: int

# -----
inserted = 0  # type: int
removed = 0  # type: int

# -----
# Were some albums/tracks inserted into the local audio drive?
new_albums = albums_drive.difference(albums_database)  # type: Set[Tuple[str, str, str, str, str, bool, str, str]]
if new_albums:
    collection = sorted(sorted(sorted(sorted(sorted(new_albums, key=itemgetter(6)), key=itemgetter(7)), key=itemgetter(4)), key=itemgetter(1)), key=itemgetter(0))
    for key, group in groupby(collection, key=lambda i: tuple(compress(i, [1, 1, 0, 0, 1, 0, 0, 0]))):
        artistid, albumid, album = key
        logger.info("# Album inserted into the local audio drive ================================================== #")
        logger.info("ArtistID : %s", artistid)
        logger.info("AlbumID  : %s", albumid)
        logger.info("Album    : %s", album)
        for file, extension in map(lambda i: compress(i, [0, 0, 0, 0, 0, 0, 1, 1]), group):
            logger.info("\tFile     : %s".expandtabs(4), file)
            logger.info("\tExtension: %s".expandtabs(4), extension)
    changes += insert_albums(*new_albums)
    inserted = changes

# -----
# Were some albums/tracks removed from the local audio drive?
removed_albums = albums_database.difference(albums_drive)  # type: Set[Tuple[str, str, str, str, str, bool, str, str]]
if removed_albums:
    collection = sorted(sorted(sorted(sorted(sorted(removed_albums, key=itemgetter(6)), key=itemgetter(7)), key=itemgetter(4)), key=itemgetter(1)), key=itemgetter(0))
    for key, group in groupby(collection, key=lambda i: tuple(compress(i, [1, 1, 0, 0, 1, 0, 0, 0]))):
        artistid, albumid, album = key
        logger.info("# Album removed from the local audio drive ================================================== #")
        logger.info("ArtistID : %s", artistid)
        logger.info("AlbumID  : %s", albumid)
        logger.info("Album    : %s", album)
        for file, extension in map(lambda i: compress(i, [0, 0, 0, 0, 0, 0, 1, 1]), group):
            logger.info("\tFile     : %s".expandtabs(4), file)
            logger.info("\tExtension: %s".expandtabs(4), extension)
    changes += remove_albums(*removed_albums)
    removed = changes

# -----
dt_end = LOCAL.localize(datetime.now())
elapsed = dt_end - dt_beg
with open(os.path.join(os.path.expandvars("%TEMP%"), "tempfile.txt"), mode="w", encoding="ISO-8859-1") as stream:
    stream.write(f"{int(elapsed.total_seconds())}|{inserted}|{removed}\n")

# -----
logger.info(changes)
sys.exit(changes)
