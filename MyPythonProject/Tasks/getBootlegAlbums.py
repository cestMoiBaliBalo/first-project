# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import os
import re
from collections import deque
from functools import partial
from itertools import chain, compress, groupby, islice, starmap
from operator import attrgetter, contains, itemgetter
from pathlib import Path
from subprocess import run
from typing import Any, Iterator, List, NamedTuple, Optional, Tuple

from Applications.decorators import cvtint_, itemgetter_, lstrip_, substr_
from Applications.shared import Files, GetPath, VorbisComment, grouper

__author__ = "Xavier ROSSET"
__maintainer__ = "Xavier ROSSET"
__email__ = "xavier.python.computing@protonmail.com"
__status__ = "Development"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent


# ===============
# Global classes.
# ===============
class Formatter(object):
    """
    Undocumented.
    """
    GAP = 4  # type: int
    REX = re.compile("\\S")
    SEP = "*"  # type: str

    def __init__(self, *iterables: Tuple[str, ...]) -> None:
        self._collection = []  # type: List[Tuple[str, ...]]
        bootlegs, artists, years, flags, providers = list(zip(*iterables))  # type: Tuple[str, ...], Tuple[str, ...], Tuple[str, ...], Tuple[str, ...], Tuple[str, ...]

        # 1. Get bootlegs maximum width.
        self._width_bootlegs = max([self._get_width(*bootlegs), len("BOOTLEG")])  # type: int

        # 2. Get artists maximum width.
        self._width_artists = max([self._get_width(*artists), len("ARTIST")])  # type: int

        # 3. Get years maximum width.
        self._width_years = max([self._get_width(*years), len("YEAR")])  # type: int

        # 4. Get flags maximum width.
        self._width_flags = max([self._get_width(*flags), len("COLLECTION")])  # type: int

        # 5. Get providers maximum width.
        self._width_providers = max([self._get_width(*map(self._rstrip, filter(None, providers))), len("PROVIDER")])  # type: int

        # 6. Process collection.
        #       i. Replace null values by empty strings.
        #      ii. Justify items.
        #     iii. Group items by artist, then by year.
        collection = self._group(*self._align(*starmap(self._replace, iterables)))  # type: Any
        for group in grouper(CHUNK, *collection):
            group = list(filter(None, group))
            group.extend(self._set_headers())
            group = deque(group)
            group.rotate(3)
            self._collection.extend(group)

    def __iter__(self) -> Iterator[Tuple[str, ...]]:
        for item in self._collection:
            yield item

    def __len__(self) -> int:
        return len(self._collection)

    def _align(self, *iterables: Tuple[str, ...]) -> Iterator[Tuple[str, ...]]:
        """
        Undocumented.
        """
        bootlegs, artists, years, flags, providers = list(zip(*iterables))  # type: Any, Any, Any, Any, Any
        artists = [self._justify(item, self._width_artists) for item in artists]
        years = [self._justify(item, self._width_years + self.GAP, justify=">") for item in years]
        bootlegs = [self._justify(self._justify(item, self._width_bootlegs), self._width_bootlegs + self.GAP, justify=">") for item in bootlegs]
        flags = [self._justify(item, self._width_flags + self.GAP, justify=">") for item in flags]
        providers = [self._justify(self._justify(item, self._width_providers), self._width_providers + self.GAP, justify=">") for item in providers]
        for item in zip(bootlegs, artists, years, flags, providers):
            yield item

    def _group(self, *iterables: Tuple[str, ...]) -> Iterator[Tuple[str, ...]]:
        """
        Undocumented.
        """
        _output = []  # type: List[Tuple[str, ...]]
        _iterables = sorted(iterables, key=itemgetter(0))  # type: List[Tuple[str, ...]]
        _iterables = sorted(_iterables, key=cvtint_()(substr_(4)(lstrip_(itemgetter(2)))))
        _iterables = sorted(_iterables, key=itemgetter(1))
        for _, group1 in groupby(_iterables, key=itemgetter(1)):
            for _, group2 in groupby(group1, key=itemgetter(2)):
                first = True
                for bootleg, artist, year, flag, provider in group2:
                    if not first:
                        artist = (re.sub(self.REX, " ", artist))
                        year = (re.sub(self.REX, " ", year))
                    first = False
                    _output.append((bootleg, artist, year, flag, provider))
        for item in _output:
            yield item

    def _set_headers(self):
        artists = self.SEP * self._width_artists  # type: str
        years = self._justify(self.SEP * self._width_years, self._width_years + self.GAP, justify=">")  # type: str
        bootlegs = self._justify(self.SEP * self._width_bootlegs, self._width_bootlegs + self.GAP, justify=">")  # type: str
        flags = self._justify(self.SEP * self._width_flags, self._width_flags + self.GAP, justify=">")  # type: str
        providers = self._justify(self.SEP * self._width_providers, self._width_providers + self.GAP, justify=">")  # type: str
        yield bootlegs, artists, years, flags, providers
        yield self._justify(self._justify("BOOTLEG", self._width_bootlegs), self._width_bootlegs + self.GAP, justify=">"), \
              self._justify("ARTIST", self._width_artists), \
              self._justify(self._justify("YEAR", self._width_years), self._width_years + self.GAP, justify=">"), \
              self._justify(self._justify("COLLECTION", self._width_flags), self._width_flags + self.GAP, justify=">"), \
              self._justify(self._justify("PROVIDER", self._width_providers), self._width_providers + self.GAP, justify=">")
        yield bootlegs, artists, years, flags, providers

    @staticmethod
    def _get_width(*items: str) -> int:
        """
        Undocumented.
        """
        if items:
            return max(map(len, items))
        return 0

    @staticmethod
    def _justify(item: str, width: int, *, justify: str = "<") -> str:
        """
        Undocumented.
        """
        return "{0:{justify}{width}}".format(item, width=width, justify=justify)

    @staticmethod
    def _replace(*iterable: str) -> Tuple[str, ...]:
        """
        Undocumented.
        """
        output = ()  # type: Tuple[str, ...]
        for item in iterable:
            _item = (item,)  # type: Tuple[str]
            if item is None:
                _item = (" ",)
            output += _item
        return output

    @staticmethod
    def _rstrip(arg: str) -> str:
        """
        Undocumented.
        """
        return arg.rstrip()


# ===============
# Global objects.
# ===============
Album = NamedTuple("Bootleg", [("bootleg", str),
                               ("artist", str),
                               ("year", str),
                               ("in_collection", str),
                               ("provider", str)])

# =================
# Argument parsers.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("path", nargs="+", action=GetPath)

# ============
# Main script.
# ============

# Initializations.
CHUNK = 60  # type: int
TAGS = ["album", "albumartist", "albumsort", "date", "incollection", "mediaprovider"]  # type: List[str]
files, comments = [], []  # type: List[Path], List[List[Tuple[str, Optional[str]]]]

# Parse arguments.
arguments = parser.parse_args()

# Get audio files collection.
for path in arguments.path:
    paths = sorted(Files(path, "flac"), key=attrgetter("name"))
    paths = sorted(paths, key=attrgetter("parent"))
    for _, group in groupby(paths, key=attrgetter("parent")):
        files.extend(islice(group, 1))

# Get Vorbis comments.
for file in files:
    tags = dict(list(VorbisComment(file)))  # type: Any
    tags.update(incollection=tags.get("incollection", "N"))
    tags.update(mediaprovider=tags.get("mediaprovider"))
    comments.append(list(tags.items()))

# Process Vorbis comments.
tags = [list(filter(itemgetter_(0)(partial(contains, TAGS)), comment)) for comment in comments]
tags = [sorted(item, key=itemgetter(0)) for item in tags]
tags = [[tuple(compress(tag, [0, 1])) for tag in item] for item in tags]
tags = [tuple(chain(*item)) for item in tags]
tags = set(tags)
tags = [tuple(compress(item, [1, 1, 0, 1, 1, 1])) for item in tags]
tags = [Album(*item) for item in Formatter(*tags)]

# Display Vorbis comments.
collection = list(grouper(CHUNK + 3, *tags))  # type: List[List[Album]]
page, pages = 0, len(collection)  # type: int, int
for group in collection:
    run("CLS", shell=True)
    for item in filter(None, group):
        print(f"{item.artist}{item.year}{item.bootleg}{item.in_collection}{item.provider}")
    page += 1
    print(f"\n\nPage {page}/{pages}")
    run("PAUSE", shell=True)
run("CLS", shell=True)
