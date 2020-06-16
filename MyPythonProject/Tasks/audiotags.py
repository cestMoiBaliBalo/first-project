# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import os
from functools import partial
from itertools import chain, compress
from operator import eq, itemgetter
from pathlib import Path
from typing import Any

import bootlegs

from Applications.decorators import itemgetter_

__author__ = "Xavier ROSSET"
__maintainer__ = "Xavier ROSSET"
__email__ = "xavier.python.computing@protonmail.com"
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent

albums = []  # type: Any
arguments = bootlegs.parser.parse_args()

# Get albums collection.
for path in arguments.path:
    for tags in [tags for _, tags in bootlegs.AudioFLACMetaData(path)]:
        if "status" not in chain.from_iterable([compress(item, [1, 0]) for item in tags]):
            continue
        comments = []  # type: Any
        for inclusion in ["album", "albumartist", "albumsort", "date", "incollection", "mediaprovider"]:
            comments.append(filter(itemgetter_(0)(partial(eq, inclusion)), tags))
        dict_data = dict(chain.from_iterable(comments))
        dict_data.update(incollection=dict_data.get("incollection", "N"))
        dict_data.update(mediaprovider=dict_data.get("mediaprovider"))
        albums.append(tuple(dict_data[key] for key in sorted(dict_data)))  # (value1, value2, value3), ...
        albums = list(set(albums))

# Format albums collection.
albums = sorted(albums, key=itemgetter(2))
albums = sorted(albums, key=itemgetter(3))
albums = sorted(albums, key=itemgetter(1))
albums = [compress(item, [1, 1, 0, 1, 1, 1]) for item in albums]
albums = [bootlegs.Bootlegs(*item) for item in albums]
for bootleg in bootlegs.Formatter(*albums)():
    print(bootleg)
