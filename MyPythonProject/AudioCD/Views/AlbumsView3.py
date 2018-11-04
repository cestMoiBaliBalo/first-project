# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import logging.config
import os
import sys
from itertools import groupby
from operator import itemgetter
from subprocess import run
from typing import List, Tuple

import jinja2
import yaml

from Applications.Tables.Albums.shared import get_albumdetail
from Applications.parsers import subset_parser
from Applications.shared import DATABASE, LOCAL, TemplatingEnvironment, UTC, UTF8, rjustify

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding=UTF8) as fp:
    logging.config.dictConfig(yaml.load(fp))

# =======
# Parser.
# =======
arguments = vars(subset_parser.parse_args())


# ================
# Local functions.
# ================
def sort_iterable(item: int, *iterable: Tuple[str, str, bool, str, str, str, str, int, int, bool, str, bool], reverse: bool = False) \
        -> List[Tuple[str, str, bool, str, str, str, str, int, int, bool, str, bool]]:
    return sorted(iterable, key=itemgetter(item), reverse=reverse)


# =========
# Template.
# =========
TEMPLATE = TemplatingEnvironment(loader=jinja2.FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "AudioCD", "Views")))
TEMPLATE.set_environment(globalvars={},
                         filters={"rjustify": rjustify})

# ===============
# Main algorithm.
# ===============

# Get albums collection.
collection = list((row.artistsort,
                   row.artist,
                   row.bootleg,
                   row.albumsort,
                   row.album,
                   row.genre,
                   UTC.localize(row.utc_created).astimezone(LOCAL).strftime("%d/%m/%Y %H:%M:%S %Z (UTC%z)"),
                   row.discid,
                   row.trackid,
                   row.incollection,
                   row.title,
                   row.live
                   ) for row in get_albumdetail(db=arguments.get("db", DATABASE), artistsort=arguments.get("artistsort", []), albumsort=arguments.get("albumsort", [])))

# Sort collection by track ID.
collection = sort_iterable(8, *collection)

# Sort collection by discID.
collection = sort_iterable(7, *collection)

# Sort collection by creation date.
collection = sort_iterable(6, *collection)

# Sort collection by genre.
collection = sort_iterable(5, *collection)

# Sort collection by album.
collection = sort_iterable(4, *collection)

# Sort collection by albumsort.
collection = sort_iterable(3, *collection)

# Sort collection by bootleg indicator.
collection = sort_iterable(2, *collection)

# Sort collection by artist.
collection = sort_iterable(1, *collection)

# Sort collection by artistsort.
collection = sort_iterable(0, *collection)

# Group collection content.
collection = ((artistsort,  # type: ignore
               artist,
               [(bootleg,
                 [(albumsort,
                   album,
                   utc_created,
                   genre,
                   [(discid,
                     [(trackid,
                       list(group4)) for trackid, group4 in groupby(group3, key=itemgetter(8))])
                    for discid, group3 in groupby(group2, key=itemgetter(7))])
                  for (albumsort, album, utc_created, genre), group2 in groupby(group1, key=lambda i: (i[3], i[4], i[5], i[6]))])
                for bootleg, group1 in groupby(group, key=itemgetter(2))])
              for (artistsort, artist), group in groupby(collection, key=lambda i: (i[0], i[1])))

# Edit albums.
run("CLS", shell=True)
print(TEMPLATE.environment.get_template("T01").render(content=collection))

# Exit algorithm.
sys.exit(0)
