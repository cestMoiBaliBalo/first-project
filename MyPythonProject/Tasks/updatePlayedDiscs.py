# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import datetime
import itertools
import json
import locale
import os
import sys
from collections import defaultdict
from functools import partial
from itertools import compress
from operator import contains, itemgetter, le
from pathlib import Path
from typing import Any, Dict, Iterator

import pytz
from dateutil import parser
from lxml import etree  # type: ignore

from Applications.Tables.Albums.shared import get_disc, update_playeddisccount
from Applications.Tables.Tasks.shared import get_task, insert_task, update_task
from Applications.decorators import itemgetter_, map_
from Applications.parsers import database_parser
from Applications.shared import DFTTIMEZONE, GENRES, TEMP, UTF8, WRITE, valid_albumsort

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ================
# Local functions.
# ================
def get_disc_(db) -> Iterator[str]:
    for disc in get_disc(db=db):
        yield f"{disc.albumid}.{disc.discid}"


def localize_(arg: datetime.datetime) -> datetime.datetime:
    return arg.astimezone(pytz.timezone(DFTTIMEZONE))


def valid_albumsort_(arg: str) -> bool:
    try:
        valid_albumsort(arg)
    except ValueError:
        return False
    return True


# ==========
# Constants.
# ==========
DEFAULT = datetime.datetime(2018, 9, 1, 22, 0, 0)

# =================
# Arguments parser.
# =================
arguments = database_parser.parse_args()

# ==========
# Variables.
# ==========
collection, collektion = [], []  # type: Any, Any
taskid = 123456799  # type: int

# ==================
# Get last run date.
# ==================
_, utc_run = get_task(taskid, db=arguments.db)
if utc_run is None:
    insert_task(taskid, db=arguments.db, dtobj=DEFAULT)
    utc_run = DEFAULT

# ===============
# Main algorithm.
# ===============

#  1. Browse the XML tree using XPATH.
tree = etree.parse(os.path.join(os.path.expandvars("%USERPROFILE%"), "Music", "iTunes", "iTunes Music Library.xml"))
for tracks in tree.xpath("/plist/dict/dict/dict"):
    album, albumsort, artist, artistsort, disc, genre, utc_played = None, None, None, None, None, None, None
    for tags in tracks.xpath("key"):

        if tags.text.lower() == "album":
            for data in tags.xpath("following-sibling::string[1]"):
                album = data.text

        if tags.text.lower() == "artist":
            for data in tags.xpath("following-sibling::string[1]"):
                artist = data.text

        if tags.text.lower() == "disc number":
            for data in tags.xpath("following-sibling::integer[1]"):
                disc = data.text

        if tags.text.lower() == "genre":
            for data in tags.xpath("following-sibling::string[1]"):
                genre = data.text

        elif tags.text.lower() == "play date utc":
            for data in tags.xpath("following-sibling::date[1]"):
                utc_played = parser.parse(data.text)

        elif tags.text.lower() == "sort album":
            for data in tags.xpath("following-sibling::string[1]"):
                albumsort = data.text

        elif tags.text.lower() == "sort artist":
            for data in tags.xpath("following-sibling::string[1]"):
                artistsort = data.text

    if all([any([artist, artistsort]), album, albumsort, disc, genre, utc_played]):
        albumid = None
        if artist:
            albumid = f"{artist[0]}.{artist}"
        if artistsort:
            albumid = f"{artistsort[0]}.{artistsort}"
        if albumid:
            collection.append((f"{albumid}.{albumsort[:-3]}.{disc}", utc_played, genre, albumsort[:-3], album))

#  2. Sort collection by ascending artist then descending played date.
collection = sorted(sorted(collection, key=itemgetter(1), reverse=True), key=itemgetter(0))

#  3. Remove albums played prior to the last run date.
collection = filter(itemgetter_(1)(partial(le, pytz.timezone("UTC").localize(utc_run))), collection)

#  4. Remove albums without a compliant genre.
collection = filter(itemgetter_(2)(partial(contains, GENRES)), collection)

#  5. Remove albums without a compliant albumsort.
collection = filter(itemgetter_(3)(partial(valid_albumsort_)), collection)

#  6. Remove albums absent from the local audio database.
collection = filter(itemgetter_(0)(partial(contains, list(get_disc_(arguments.db)))), collection)

#  7. Map UTC datetime to local datetime.
#     update_playeddisccount assumes that datetime is local and converts therefore to UTC.
collection = map_(1)(localize_)(*collection)

#  8. Remove both genre and albumsort from the collection.
collection = [tuple(compress(item, [1, 1, 0, 0, 1])) for item in collection]

#  9. Exit if collection is empty.
if not collection:
    sys.exit(-1)

# 10. Group collection by album ID. Get only the most recent played date.
#     Album ID is composed of artistsort first letter, artistsort, albumsort and disc number.
for key, group in itertools.groupby(collection, key=itemgetter(0)):
    collektion.append(list(next(group)))

# 12. Update PLAYEDDISCS table.
results = defaultdict(int)  # type: Dict[str, int]
for albumid, played, _ in collektion:
    inserted, updated = update_playeddisccount(albumid[:-2], int(albumid[-1:]), db=arguments.db, local_played=played)  # type: int, int
    results["inserted"] += inserted
    results["updated"] += updated

# 13. Update TASKS table.
update_task(taskid, db=arguments.db)

# 14. Dump collection into an external JSON file.

#       i. Sort collection by descending played date.
collektion = sorted(collektion, key=itemgetter(1), reverse=True)

#      ii. Serialize played date.
collektion = [(albumid, album, utc_played.isoformat()) for albumid, utc_played, album in collektion]

#     iii. Insert system timestamp. Not really useful but just for fun.
collektion = [pytz.timezone("UTC").localize(datetime.datetime.utcnow()).astimezone(pytz.timezone(DFTTIMEZONE)).isoformat(), collektion]

#      iv. Dump collection.
with open(TEMP / "playeddiscs.json", mode=WRITE, encoding=UTF8) as stream:
    json.dump(collektion, stream, ensure_ascii=False, indent=4)

# 15. Exit.
sys.exit(results["inserted"] + results["updated"])
