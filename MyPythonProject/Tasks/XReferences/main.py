# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import locale
import logging.config
import os
from datetime import datetime
from functools import partial
from itertools import compress, groupby
from operator import itemgetter
from typing import Any, Iterator, List, Sequence, Set, Tuple

import yaml

from Applications.Tables.XReferences.shared import get_database_albums, get_drive_albums, insert_albums, remove_albums
from Applications.shared import LOCAL, UTF8, WRITE, get_dirname

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# -----
def compress_(selectors: List[int], data: Sequence[Any]) -> Tuple[Any]:
    """
    
    :param selectors: 
    :param data: 
    :return: 
    """
    return tuple(compress(data, selectors))


def sorted_(iterable: Iterator[Any], *indexes: int) -> Iterator[Any]:
    """
    
    :param iterable: 
    :param indexes: 
    :return: 
    """
    _iterable = list(iterable)
    for index in indexes:
        _iterable = sorted(_iterable, key=itemgetter(index))
    return iter(_iterable)


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
inserted, removed = "  0", "  0"  # type: str, str

# -----
albums_drive = set(get_drive_albums())  # type: Set[Tuple[str, str, str, str, str, bool, str, str]]
albums_database = set(get_database_albums())  # type: Set[Tuple[str, str, str, str, str, bool, str, str]]

# -----
# Were some albums/tracks inserted into the local audio drive?
inserted_albums = albums_drive.difference(albums_database)  # type: Set[Tuple[str, str, str, str, str, bool, str, str]]
if inserted_albums:
    header = "{0:{filler}<100}".format("Album inserted into the local audio drive ", filler="=")
    collection = list(sorted_(iter(inserted_albums), 6, 7, 4, 1, 0))
    for key, group in groupby(collection, key=partial(compress_, GROUP_SELECTORS)):
        artistid, albumid, album = key
        logger.info("# %s #", header)
        logger.info("Artist ID: %s", artistid)
        logger.info("Album ID : %s", albumid)
        logger.info("Album    : %s", album)
        first = True
        for file, extension in map(partial(compress_, SELECTORS), group):
            _msg = f"           {file}.{extension}"
            if first:
                first = False
                _msg = f"Files    : {file}.{extension}"
            logger.info(_msg)
    inserted = "{0:>3d}".format(insert_albums(*inserted_albums))

# -----
# Were some albums/tracks removed from the local audio drive?
removed_albums = albums_database.difference(albums_drive)  # type: Set[Tuple[str, str, str, str, str, bool, str, str]]
if removed_albums:
    header = "{0:{filler}<100}".format("Album removed from the local audio drive ", filler="=")
    collection = list(sorted_(iter(inserted_albums), 6, 7, 4, 1, 0))
    for key, group in groupby(collection, key=partial(compress_, GROUP_SELECTORS)):
        artistid, albumid, album = key
        logger.info("# %s #", header)
        logger.info("Artist ID: %s", artistid)
        logger.info("Album ID : %s", albumid)
        logger.info("Album    : %s", album)
        first = True
        for file, extension in map(partial(compress_, SELECTORS), group):
            _msg = f"           {file}.{extension}"
            if first:
                first = False
                _msg = f"Files    : {file}.{extension}"
            logger.info(_msg)
    removed = "{0:>3d}".format(remove_albums(*removed_albums))

# -----
dt_end = LOCAL.localize(datetime.now())
elapsed = dt_end - dt_beg
with open(os.path.join(os.path.expandvars("%TEMP%"), "xreferences.txt"), mode=WRITE, encoding=UTF8) as stream:
    stream.write(f"{int(elapsed.total_seconds())}|{inserted.strip()}|{removed.strip()}\n")

# -----
logger.info("Inserted records: %s", inserted)
logger.info("Removed records : %s", removed)
