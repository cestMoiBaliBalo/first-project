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
    all_tags: Any = [compress(file, [0, 1]) for file in bootlegs.AudioFLACTags(path)]  # ([(tag1, value1), (tag2, value), (tag3, value), ...],), ([(tag1, value1), (tag2, value), (tag3, value), ...],), ...
    for tags in chain.from_iterable(all_tags):
        if "status" not in list(chain.from_iterable([tuple(compress(item, [1, 0])) for item in tags])):
            continue
        temp_list = []  # type: Any
        for inclusion in ["album", "albumartist", "albumsort", "date", "incollection", "mediaprovider"]:
            temp_list.append(tuple(filter(itemgetter_(0)(partial(eq, inclusion)), tags)))
        temp_list = list(chain.from_iterable(temp_list))
        dict_tags = dict(temp_list)
        dict_tags.update(incollection=dict_tags.get("incollection", "N"))
        dict_tags.update(mediaprovider=dict_tags.get("mediaprovider"))
        albums.append(tuple(dict_tags[key] for key in sorted(dict_tags)))  # (value1, value2, value3), ...
        albums = list(set(albums))

# Format albums collection.
albums = sorted(albums, key=itemgetter(2))
albums = sorted(albums, key=itemgetter(3))
albums = sorted(albums, key=itemgetter(1))
albums = [compress(item, [1, 1, 0, 1, 1, 1]) for item in albums]
albums = [bootlegs.Bootlegs(*item) for item in albums]
for bootleg in bootlegs.Formatter(*albums)():
    print(bootleg)
