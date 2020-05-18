# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import fnmatch
import os
from collections import namedtuple
from functools import partial
from itertools import chain, compress, filterfalse, groupby, tee
from operator import eq, itemgetter
from pathlib import Path
from typing import Any, Iterator, Mapping, Optional, Tuple, Union

from mutagen.flac import FLAC

from Applications.decorators import itemgetter_

__author__ = "Xavier ROSSET"
__maintainer__ = "Xavier ROSSET"
__email__ = "xavier.python.computing@protonmail.com"
__status__ = "Development"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent


# ==============
# Local classes.
# ==============
class Formatter(object):
    GAP = 8  # type: int
    SEP = "*"  # type: str

    def __init__(self, *iterables: Tuple[str, ...]) -> None:
        """

        :param iterables:
        """
        self._iterables = tuple(iterables)  # type: Tuple[Tuple[str, ...]]

        # 1. Get bootlegs maximum width.
        bootlegs = chain(*tuple(compress(item, [1, 0, 0, 0, 0]) for item in iterables))  # type: Iterator[str]
        self._width_bootlegs = self.get_width(*bootlegs)  # type: int

        # 2. Get artists maximum width.
        artists = chain(*tuple(compress(item, [0, 1, 0, 0, 0]) for item in iterables))  # type: Iterator[str]
        self._width_artists = self.get_width(*artists)  # type: int

        # 3. Get years maximum width.
        years = chain(*tuple(compress(item, [0, 0, 1, 0, 0]) for item in iterables))  # type: Iterator[str]
        self._width_years = self.get_width(*years)  # type: int

        # 4. Get providers maximum width.
        providers = chain(*tuple(compress(item, [0, 0, 0, 0, 1]) for item in iterables))  # type: Iterator[str]
        providers = filter(None, providers)
        self._width_providers = self.get_width(*providers)  # type: int

        # 5. Set headers delimiters.

        # --> Artists.
        header_artist = self.justify(self.SEP * self._width_artists, self._width_artists + self.GAP)  # type: str

        # --> Years.
        header_year = self.justify(self.SEP * self._width_years, self._width_years + self.GAP)  # type: str

        # --> Bootlegs.
        header_bootleg = self.justify(self.SEP * self._width_bootlegs, self._width_bootlegs + self.GAP + 1)  # type: str

        # --> Providers.
        self._width_providers = max([self._width_providers, len("PROVIDER")])
        header_provider = self.justify(self.SEP * self._width_providers, self._width_providers + self.GAP, justify=">")  # type: str

        # 6. Set headers titles.

        # --> Artists.
        title_artist = self.justify("ARTIST", self._width_artists + self.GAP)  # type: str

        # --> Years.
        title_year = self.justify("YEAR", self._width_years + self.GAP)  # type: str

        # --> Bootlegs.
        title_bootleg = self.justify("BOOTLEG", self._width_bootlegs + self.GAP + 1)  # type: str

        # --> Providers.
        title_provider = self.justify("PROVIDER", self._width_providers + self.GAP, justify=">")  # type: str

        # 7. Set headers instance members.
        self.delimiters = f"{header_artist}{header_year}{header_bootleg}{header_provider}"  # type: str
        self.headers = f"{title_artist}{title_year}{title_bootleg}{title_provider}"  # type: str

    def __call__(self):
        """

        :return:
        """
        for key_artist, group in groupby(self._iterables, key=itemgetter(1)):
            artist = True
            for key_year, sub_group in groupby(group, key=itemgetter(2)):
                year = True
                for item in sub_group:
                    bootleg = self.justify(item.bootleg, self._width_bootlegs + self.GAP)
                    provider = None
                    if item.provider:
                        provider = self.justify(item.provider, self._width_providers + self.GAP, justify=">")
                    detail = self.justify(item.in_collection, self._width_providers + self.GAP + 1)
                    if provider:
                        detail = f"{item.in_collection}{provider}"

                    if all([artist, year]):
                        artist = self.justify(key_artist, self._width_artists + self.GAP)
                        year = self.justify(key_year, self._width_years + self.GAP)
                        yield ""
                        yield ""
                        yield self.delimiters
                        yield self.headers
                        yield self.delimiters
                        yield f"{artist}{year}{bootleg}{detail}"

                    elif any([artist, year]) and not artist:
                        year = self.justify(key_year, self._width_years + self.GAP)
                        year = self.justify(year, self._width_artists + self._width_years + 2 * self.GAP, justify=">")
                        yield f"{year}{bootleg}{detail}"

                    elif not any([artist, year]):
                        detail = f"{bootleg}{detail}"
                        yield self.justify(detail, self._width_artists + self._width_years + self._width_bootlegs + self._width_providers + 4 * self.GAP + 1, justify=">")

                    artist = False
                    year = False

    @staticmethod
    def get_width(*items: Optional[str]) -> int:
        """

        :param items:
        :return:
        """
        if items:
            return max(map(len, items))
        return 0

    @staticmethod
    def justify(item: str, width: int, *, justify: str = "<") -> str:
        """

        :param item:
        :param width:
        :param justify:
        :return:
        """
        return "{0:{justify}{width}}".format(item, width=width, justify=justify)


class GetPath(argparse.Action):
    """

    """

    def __init__(self, option_strings, dest, **kwargs):
        super(GetPath, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, list(map(Path, values)))


# ================
# Local functions.
# ================
def get_audiotags(path: Union[Path, str]) -> Iterator[Tuple[str, Mapping[str, str]]]:
    """

    :param path:
    :return:
    """
    collection: Any = [[Path(root) / file for file in files] for root, _, files in os.walk(path) if files]  # [file1.flac, file2.flac, file3.flac], [file4.flac, file5.flac, file6.flac], [file1.jpg], ...
    collection = [fnmatch.filter(files, "*.flac") for files in collection]  # [file1.flac, file2.flac, file3.flac], [file4.flac, file5.flac, file6.flac], [], ...
    collection = filter(None, collection)  # [file1.flac, file2.flac, file3.flac], [file4.flac, file5.flac, file6.flac], ...
    collection = chain(*collection)  # file1.flac, file2.flac, file3.flac, file4.flac, file5.flac, file6.flac, ...
    collection = [(file, FLAC(file)) for file in collection]  # (file1.flac, tags), (file2.flac, tags), ...
    for file, tags in collection:
        data = [[(tag, value) for value in values] for tag, values in tags.items()]  # [(tag1, value)], [(tag2, value)], ...
        data = chain(*data)  # (tag1, value), (tag2, value), ...
        yield file, dict(sorted(data, key=itemgetter(0)))


# ==========
# Constants.
# ==========
EXCLUDED = ["accurateripdiscid",
            "accurateripresult",
            "albumartistsort",
            "artist",
            "artistsort",
            "bootlegtrackcity",
            "bootlegtrackcountry",
            "bootlegtracktour",
            "bootlegtrackyear",
            "boxset",
            "copyright",
            "description",
            "discnumber",
            "disctotal",
            "encodedby",
            "encoder",
            "encodingyear",
            "encodingtime",
            "freedb",
            "genre",
            "itunnorm",
            "itunsmpb",
            "label",
            "organization",
            "origalbum",
            "origyear",
            "profile",
            "publisherreference",
            "purchasedate",
            "replaygain_album_gain",
            "replaygain_album_peak",
            "source",
            "status",
            "taggingtime",
            "title",
            "titlelanguage",
            "titlesort",
            "tracknumber",
            "tracktotal"]

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("path", nargs="+", action=GetPath)
arguments = parser.parse_args()

# ============
# Main script.
# ============
Bootlegs = namedtuple("Bootlegs", ["bootleg", "artist", "year", "in_collection", "provider"])

# Get bootlegs collection.
master_collection = []  # type: Any
for path in arguments.path:

    # ----- Get audio tags collection.
    collection = []  # type: Any
    audio_tags = [tuple(compress(item, [0, 1])) for item in get_audiotags(path)]
    audio_tags = chain(*audio_tags)  # {"album": ..., "albumartist": ..., ...}, {"album": ..., "albumartist": ..., ...}, ...
    for tag in audio_tags:
        tag.update(incollection=tag.get("incollection", "N"))
        tag.update(mediaprovider=tag.get("mediaprovider"))
        collection.append(tag)
    audio_tags = [item.items() for item in collection]  # dict_items([("album", ...), ("albumartist", ...), ...]), dict_items([("album", ...), ("albumartist", ...), ...]), ...

    # ---- Remove excluded audio tags.
    collection = []
    for item in audio_tags:
        for tag in EXCLUDED:
            item = tuple(filterfalse(itemgetter_(0)(partial(eq, tag)), item))
        item = tuple(sorted(item, key=itemgetter(0)))
        collection.append(item)

    # ----- Remove duplicates audio tags.
    collection = [[tuple(compress(sub_item, [0, 1])) for sub_item in item] for item in collection]  # [(album,), (albumartist,), ...], [(album,), (albumartist,), ...], ...
    collection = [tuple(chain(*item)) for item in collection]  # (album, albumartist, ...), (album, albumartist, ...), ...
    collection = set(collection)

    # ----- Set audio tags master collection.
    master_collection.append(collection)

# Format bootlegs collection.
master_collection = chain(*master_collection)
master_collection = sorted(master_collection, key=itemgetter(2))
master_collection = sorted(master_collection, key=itemgetter(3))
master_collection = sorted(master_collection, key=itemgetter(1))
master_collection = [tuple(compress(item, [1, 1, 0, 1, 1, 1])) for item in master_collection]
master_collection = [Bootlegs(*item) for item in master_collection]
for bootleg in Formatter(*master_collection)():
    print(bootleg)
