# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import re
from operator import attrgetter, itemgetter
from pathlib import Path
from typing import Mapping, Optional

from Applications.callables import filter_extensions, filterfalse_
from Applications.more_shared import ID3v2Tag, VorbisComment
from Applications.shared import DFTDAYREGEX, DFTMONTHREGEX, DFTYEARREGEX, GetPath, LOOKALBUMSORT

__author__ = "Xavier ROSSET"
__maintainer__ = "Xavier ROSSET"
__email__ = "xavier.python.computing@protonmail.com"
__status__ = "Production"


# ==============
# Local classes.
# ==============
class GetAttributes(argparse.Action):
    """
    Undocumented.
    """

    def __init__(self, option_strings, dest, **kwargs):
        super(GetAttributes, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        setattr(namespace, "parent", Path("G:/") / "Music")
        setattr(namespace, "extension", None)
        if values in ["lossless1", "lossless2"]:
            setattr(namespace, "extension", "flac")
        if values == "lossy":
            setattr(namespace, "extension", "mp3")


class AudioFileMetadata(Mapping):
    """
    Undocumented.
    """
    MAPPING = {".flac": VorbisComment, ".mp3": ID3v2Tag}
    REX1 = re.compile(r"^{3}\d\.({0}){1}{2}\.(\d)$".format(DFTYEARREGEX, DFTMONTHREGEX, DFTDAYREGEX, LOOKALBUMSORT))
    REX2 = re.compile(r"^{1}\d\.({0})0000\.(\d)$".format(DFTYEARREGEX, LOOKALBUMSORT))

    def __init__(self, path: Path) -> None:

        if not path.exists():
            raise FileNotFoundError(f"No such file or directory: '{path}'")
        klass = self.MAPPING[path.suffix]
        metadata = klass(path)
        self._collection = dict(iter(metadata))  # type: Mapping[str, str]
        self._path = metadata.path  # type: Path
        self._extension = metadata.extension  # type: str
        self._parent = self._set_parent(self.get("artistsort"), self.get("albumsort"))
        self._name = self._set_name(self.get("discnumber"), self.get("tracknumber"), self.get("title"))

    def get(self, key):
        return self._collection.get(key)

    def items(self):
        return self._collection.items()

    def keys(self):
        return self._collection.keys()

    def values(self):
        return self._collection.values()

    def __getitem__(self, item):
        return self._collection[item]

    def __iter__(self):
        for key, value in sorted(self._collection.items(), key=itemgetter(0)):
            yield key, value

    def __len__(self):
        return len(self._collection)

    def __repr__(self):
        if not self:
            return "%s()" % (self.__class__.__name__,)
        return "%s(%r)" % (self.__class__.__name__, list(self))

    @classmethod
    def _set_name(cls, disc: str, track: str, title: str) -> Optional[str]:
        if all([disc, track, title]):
            title = cls._replace(title[:30], "_", "\\", "/", ":", "*", "?", "\"", ">", "<", "|").lstrip().rstrip()
            return f"{disc}.{track.zfill(2)}.{title}"
        return None

    @staticmethod
    def _replace(arg: str, new: str, *old: str) -> str:
        for item in old:
            arg = arg.replace(item, new)
        return arg

    @staticmethod
    def _set_parent(artistsort: str, albumsort: str) -> Optional[Path]:
        if all([albumsort, artistsort]):
            return Path(f"{artistsort[:1]}") / artistsort / albumsort[:-3]
        return None

    @property
    def album(self) -> Optional[str]:
        albumsort = self.get("albumsort")
        if albumsort:
            albumsort = albumsort[:-3]
            match = self.REX1.match(albumsort)
            if match:
                return f"{match.group(1)}.{match.group(2)} - {self['album']}"
            match = self.REX2.match(albumsort)
            if match:
                return f"{match.group(1)}.{match.group(2)} - {self['album']}"
        return None

    @property
    def dst(self) -> Optional[Path]:
        if all([self._parent, self._name]):
            return self._parent / f"{self._name}{self._extension}"
        return None

    @property
    def src(self) -> Path:
        return self._path


# ============
# Main script.
# ============
if __name__ == "__main__":

    import argparse
    import locale
    import logging.config
    import os
    from shutil import copy
    from typing import Any, List

    import yaml
    from mutagen import File  # type: ignore
    from mutagen.flac import FLAC  # type: ignore

    from Applications.shared import UTF8, Files

    _ME = Path(os.path.abspath(__file__))
    _MYNAME = Path(os.path.abspath(__file__)).stem
    _MYPARENT = Path(os.path.abspath(__file__)).parent

    # Set French environment.
    locale.setlocale(locale.LC_ALL, "")

    # Load logging configuration.
    with open(_MYPARENT.parent / "Resources" / "logging.yml", encoding=UTF8) as fr:
        logging.config.dictConfig(yaml.load(fr, Loader=yaml.FullLoader))

    # Arguments parser.
    parser = argparse.ArgumentParser()
    parser.add_argument("directories", nargs="+", action=GetPath)
    parser.add_argument("repository", choices=["lossless1", "lossless2", "lossy"], action=GetAttributes)
    parser.add_argument("--test", action="store_true")
    arguments = parser.parse_args()

    # Main process.
    collection = []  # type: List[AudioFileMetadata]
    if arguments.extension:
        for directory in arguments.directories:
            for file in Files(directory, excluded=filterfalse_(filter_extensions(arguments.extension))):  # type: Any
                collection.append(AudioFileMetadata(file))
    collection = sorted(collection, key=attrgetter("dst"))

    # Copy files.
    for file in collection:
        if all([file.src, file.dst]):
            src = file.src
            dst = arguments.parent / arguments.repository.capitalize() / file.dst
            if arguments.test:
                print(f'"{src}" will be both copied and renamed to "{dst}"')
            if not arguments.test:
                os.makedirs(dst.parent, exist_ok=True)
                copy(src, dst)

    # Alter tags.
    if not arguments.test:
        track, tracks = 0, len(collection)  # type: int, int
        for file in collection:
            path = arguments.parent / arguments.repository.capitalize() / file.dst
            if path.exists():
                track += 1

                if arguments.extension == "flac":
                    flac_file = FLAC(path)
                    if file.album:
                        flac_file["album"] = file.album
                        flac_file["tracknumber"] = str(track)
                        flac_file["tracktotal"] = str(tracks)
                        flac_file.save()

                if arguments.extension == "mp3":
                    mp3_file = File(path)
                    tag = mp3_file.tags
                    if file.album:
                        tag.add("TALB", text=file.album)
                        tag.add("TRCK", text=str(track))
                        tag.add("TXXX", description="TOTALTRACKS", text=str(tracks))
                        mp3_file.save()
