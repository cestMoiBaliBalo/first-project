# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import locale
import logging.config
import os
from datetime import datetime
from functools import partial
from itertools import compress, groupby
from operator import itemgetter
from typing import Set, Tuple

import yaml

from Applications.Tables.XReferences.shared import get_database_albums, get_drive_albums, insert_albums, remove_albums
from Applications.shared import LOCAL, UTF8, WRITE, get_dirname

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# -----
def compress_(selectors, data):
    for item in compress(data, selectors):
        yield item


# -----
locale.setlocale(locale.LC_ALL, "")

# -----
SELECTORS = [0, 0, 0, 0, 0, 0, 1, 1]
GROUP_SELECTORS = [1, 1, 0, 0, 1, 0, 0, 0]

# -----
with open(os.path.join(get_dirname(os.path.abspath(__file__), level=3), "Resources", "logging.yml"), encoding=UTF8) as fp:
    logging.config.dictConfig(yaml.load(fp, Loader=yaml.FullLoader))
logger = logging.getLogger("MyPythonProject.Tasks.XReferences.main")

# -----
dt_beg = LOCAL.localize(datetime.now())

# -----
albums_drive = set(get_drive_albums())  # type: Set[Tuple[str, str, str, str, str, bool, str, str]]
albums_database = set(get_database_albums())  # type: Set[Tuple[str, str, str, str, str, bool, str, str]]

# -----
inserted, removed = "  0", "  0"  # type: str, str

# -----
# Were some albums/tracks inserted into the local audio drive?
new_albums = albums_drive.difference(albums_database)  # type: Set[Tuple[str, str, str, str, str, bool, str, str]]
if new_albums:
    collection = sorted(sorted(sorted(sorted(sorted(new_albums, key=itemgetter(6)), key=itemgetter(7)), key=itemgetter(4)), key=itemgetter(1)), key=itemgetter(0))
    for key, group in groupby(collection, key=partial(compress_, GROUP_SELECTORS)):
        artistid, albumid, album = key
        header = "{0:{fil}<100}".format("Album inserted into the local audio drive ", fil="=")
        logger.info("# %s #", header)
        logger.info("ArtistID: %s", artistid)
        logger.info("AlbumID : %s", albumid)
        logger.info("Album   : %s", album)
        for file, extension in map(partial(compress_, SELECTORS), group):
            logger.info("\tFile     : %s".expandtabs(4), file)
            logger.info("\tExtension: %s".expandtabs(4), extension)
    inserted = "{0:>3d}".format(insert_albums(*new_albums))

# -----
# Were some albums/tracks removed from the local audio drive?
removed_albums = albums_database.difference(albums_drive)  # type: Set[Tuple[str, str, str, str, str, bool, str, str]]
if removed_albums:
    collection = sorted(sorted(sorted(sorted(sorted(removed_albums, key=itemgetter(6)), key=itemgetter(7)), key=itemgetter(4)), key=itemgetter(1)), key=itemgetter(0))
    for key, group in groupby(collection, key=partial(compress_, GROUP_SELECTORS)):
        artistid, albumid, album = key
        header = "{0:{fil}<100}".format("Album removed from the local audio drive ", fil="=")
        logger.info("# %s #", header)
        logger.info("ArtistID: %s", artistid)
        logger.info("AlbumID : %s", albumid)
        logger.info("Album   : %s", album)
        for file, extension in map(partial(compress_, SELECTORS), group):
            logger.info("\tFile     : %s".expandtabs(4), file)
            logger.info("\tExtension: %s".expandtabs(4), extension)
    removed = "{0:>3d}".format(remove_albums(*removed_albums))

# -----
dt_end = LOCAL.localize(datetime.now())
elapsed = dt_end - dt_beg
with open(os.path.join(os.path.expandvars("%TEMP%"), "tempfile.txt"), mode=WRITE, encoding=UTF8) as stream:
    stream.write(f"{int(elapsed.total_seconds())}|{inserted}|{removed}\n")

# -----
logger.info("Inserted records: %s", inserted)
logger.info("Removed records : %s", removed)
