# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import fnmatch
import os
from functools import partial
from itertools import chain, compress, groupby, repeat
from operator import contains, itemgetter
from pathlib import Path
from subprocess import run
from typing import Any, Iterable, Iterator, List, NamedTuple, Tuple, Union

from mutagen.flac import FLAC  # type: ignore

from Applications.decorators import itemgetter_

__author__ = "Xavier ROSSET"
__maintainer__ = "Xavier ROSSET"
__email__ = "xavier.python.computing@protonmail.com"
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent

# ========
# Objects.
# ========
Bootlegs = NamedTuple("Bootlegs", [("bootleg", str),
                                   ("artist", str),
                                   ("year", str),
                                   ("in_collection", str),
                                   ("provider", str)])


# ===============
# Global classes.
# ===============
class Files(object):

    def __init__(self, path: Union[Path, str], *included: str) -> None:

        """

        :param path:
        :param included:
        :return:
        """
        collection: Iterable[Any] = [[Path(root) / file for file in files] for root, _, files in os.walk(path) if files]  # [root1/file1.flac, root1/file2.flac], [root2/file1.m4a, root2/file2.m4a], ...
        extensions = tuple(included)  # type: Tuple[str, ...]

        if len(extensions) == 1:
            (extension,) = extensions
            collection = [filter(None, fnmatch.filter(group, f"*.{extension}")) for group in collection]  # [root1/file1.flac, root1/file2.flac], ...

        elif len(extensions) > 1:

            # [[root1/file1.flac, root1/file2.flac], []], [[], [root2/file1.m4a, root2/file2.m4a]], ...
            collection = [[fnmatch.filter(group, f"*.{extension}") for group in groups] for groups, extension in zip(repeat(collection, len(extensions)), extensions)]

            # [root1/file1.flac, root1/file2.flac], [root2/file1.m4a, root2/file2.m4a], ...
            collection = chain.from_iterable(collection)

        # root1/file1.flac, root1/file2.flac, root2/file1.m4a, root2/file2.m4a, ...
        self._collection = iter(chain.from_iterable(collection))  # type: Iterator[Path]

    def __iter__(self):
        return self

    def __next__(self):
        try:
            nextit = next(self._collection)
        except StopIteration:
            raise
        return nextit


class AudioFLACMetaData(object):

    def __init__(self, path: Union[Path, str]) -> None:
        """

        :param path:
        :return:
        """
        collection = []  # type: List[Any]
        files = [(file, FLAC(file)) for file in Files(path, "flac")]  # (root1/file1.flac, dict_data), (root2/file2.flac, dict_data), ...
        for file, metadata in files:

            # [(tag1, value1), (tag1, value2)], [(tag2, value)], [(tag3, value)], ...
            comments = [[(key, value) for value in values] for key, values in metadata.items()]  # type: Iterable[Any]

            # [(tag1, value1), (tag2, value), (tag3, value), ...]
            comments = list(chain.from_iterable([compress(item, [1]) for item in comments]))

            # (root1/file1.flac, [(tag1, value1), (tag2, value), (tag3, value), ...]), ...
            collection.append(tuple([file, comments]))

        self._collection = iter(collection)  # type: Iterator[Tuple[Path, List[Tuple[str, str]]]]

    def __iter__(self):
        return self

    def __next__(self):
        try:
            nextit = next(self._collection)
        except StopIteration:
            raise
        file, comments = nextit
        return file, comments


class Formatter(object):
    GAP = 8  # type: int
    SEP = "*"  # type: str

    def __init__(self, *iterables: Bootlegs) -> None:
        """

        :param iterables:
        """
        self._iterables = tuple(iterables)  # type: Tuple[Bootlegs, ...]

        # 1. Get bootlegs maximum width.
        bootlegs = [compress(item, [1, 0, 0, 0, 0]) for item in iterables]  # type: List[Iterator[str]]
        self._width_bootlegs = self.get_width(*chain.from_iterable(bootlegs))  # type: int

        # 2. Get artists maximum width.
        artists = [compress(item, [0, 1, 0, 0, 0]) for item in iterables]  # type: List[Iterator[str]]
        self._width_artists = self.get_width(*chain.from_iterable(artists))  # type: int

        # 3. Get years maximum width.
        years = [compress(item, [0, 0, 1, 0, 0]) for item in iterables]  # type: List[Iterator[str]]
        self._width_years = self.get_width(*chain.from_iterable(years))  # type: int

        # 4. Get providers maximum width.
        providers = [compress(item, [0, 0, 0, 0, 1]) for item in iterables]  # type: Iterable[Any]
        providers = filter(None, chain.from_iterable(providers))
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

    def __call__(self) -> Iterator[str]:
        """

        :return:
        """
        first = True
        for key_artist, main_group in groupby(self._iterables, key=itemgetter(1)):
            brk_artist = True
            for key_year, sub_group in groupby(main_group, key=itemgetter(2)):
                brk_year = True
                for item in sub_group:

                    # -----
                    bootleg = self.justify(item.bootleg, self._width_bootlegs + self.GAP)

                    # -----
                    provider = None
                    if item.provider:
                        provider = self.justify(item.provider, self._width_providers + self.GAP, justify=">")

                    # -----
                    detail = self.justify(item.in_collection, self._width_providers + self.GAP + 1)
                    if provider:
                        detail = f"{item.in_collection}{provider}"

                    # -----
                    if all([brk_artist, brk_year]):
                        artist = self.justify(key_artist, self._width_artists + self.GAP)
                        year = self.justify(key_year, self._width_years + self.GAP)
                        if not first:
                            yield ""
                            yield ""
                        first = False
                        yield self.delimiters
                        yield self.headers
                        yield self.delimiters
                        yield f"{artist}{year}{bootleg}{detail}"

                    # -----
                    elif any([brk_artist, brk_year]) and not brk_artist:
                        year = self.justify(key_year, self._width_years + self.GAP)
                        year = self.justify(year, self._width_artists + self._width_years + 2 * self.GAP, justify=">")
                        yield f"{year}{bootleg}{detail}"

                    # -----
                    elif not any([brk_artist, brk_year]):
                        detail = f"{bootleg}{detail}"
                        yield self.justify(detail, self._width_artists + self._width_years + self._width_bootlegs + self._width_providers + 4 * self.GAP + 1, justify=">")

                    brk_artist = False
                    brk_year = False

    @staticmethod
    def get_width(*items: str) -> int:
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


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("path", nargs="+", action=GetPath)

if __name__ == "__main__":

    arguments = parser.parse_args()
    CHUNK = 50  # type: int
    TAGS = ["album", "albumartist", "albumsort", "date", "incollection", "mediaprovider"]  # type: List[str]
    bootlegs, top = [], int(CHUNK)  # type: List[Any], int

    # Get bootlegs collection.
    print("Bootlegs list is in progress. Please wait as it could take a while.")
    for path in arguments.path:
        collection: Any = [comments for _, comments in AudioFLACMetaData(path)]
        collection = [filter(itemgetter_(0)(partial(contains, TAGS)), item) for item in collection]
        for item in collection:
            dict_data = dict(item)
            dict_data.update(incollection=dict_data.get("incollection", "N"))
            dict_data.update(mediaprovider=dict_data.get("mediaprovider"))
            bootlegs.append(tuple(dict_data[key] for key in sorted(dict_data)))  # (value1, value2, value3), ...
            bootlegs = list(set(bootlegs))

    # Format bootlegs collection.
    bootlegs = sorted(bootlegs, key=itemgetter(2))
    bootlegs = sorted(bootlegs, key=itemgetter(3))
    bootlegs = sorted(bootlegs, key=itemgetter(1))
    bootlegs = [compress(item, [1, 1, 0, 1, 1, 1]) for item in bootlegs]
    bootlegs = [Bootlegs(*item) for item in bootlegs]
    bootlegs = list(Formatter(*bootlegs)())

    # Display bootlegs collection.
    while True:
        run("CLS", shell=True)
        index = 0  # type: int
        for bootleg in bootlegs:
            if index >= top:
                print("\n\n")
                run("PAUSE", shell=True)
                top += CHUNK
                break
            index += 1
            print(bootleg)
        else:
            break
