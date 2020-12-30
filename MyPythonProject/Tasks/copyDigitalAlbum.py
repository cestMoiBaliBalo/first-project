# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import re
import sys
from operator import attrgetter, itemgetter
from pathlib import Path
from typing import Mapping, Optional

from Applications.callables import filter_extensions, filterfalse_
from Applications.more_shared import ID3v2Tag, VorbisComment
from Applications.shared import DFTDAYREGEX, DFTMONTHREGEX, DFTYEARREGEX, GetPath

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
        setattr(namespace, self.dest, values.capitalize())
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
    ALBUMSORT = re.compile(r"^([12]\.{0}\d{{4}}\.\d)\.[01]\d$".format(DFTYEARREGEX))
    MAPPING = {".flac": VorbisComment, ".mp3": ID3v2Tag}
    REX1 = re.compile(r"^[12]\.({0}){1}{2}\.(\d)\.[01]\d$".format(DFTYEARREGEX, DFTMONTHREGEX, DFTDAYREGEX))
    REX2 = re.compile(r"^[12]\.({0})0000\.(\d)\.[01]\d$".format(DFTYEARREGEX))

    def __init__(self, path: Path) -> None:

        if not path.exists():
            raise FileNotFoundError(f"No such file or directory: '{path}'")
        klass = self.MAPPING[path.suffix.lower()]
        self._collection = dict(iter(klass(path)))  # type: Mapping[str, str]
        self._path = path  # type: Path
        self._suffix = path.suffix  # type: str
        self._artistsort = self.get("artistsort")  # type: Optional[str]
        self._albumsort = self.get("albumsort")  # type: Optional[str]
        self._albumsort_short = self._get_albumsort_short()
        self._album = self.get("album")  # type: Optional[str]
        self._parent1 = self._set_parent1()  # type: Optional[Path]
        self._parent2 = self._set_parent2()  # type: Optional[Path]
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

    def _set_parent1(self) -> Optional[Path]:
        if all([self._artistsort, self._albumsort]):
            match = self.ALBUMSORT.match(self._albumsort)
            if match:
                return Path(self._artistsort[:1]) / self._artistsort / match.group(1)
        return None

    def _set_parent2(self) -> Optional[Path]:
        if all([self._artistsort, self._albumsort_short, self._album]):
            return Path(self._artistsort[:1]) / self._artistsort / f"{self._albumsort_short} - {self._album}"
        return None

    def _get_albumsort_short(self) -> Optional[str]:
        if self._albumsort:
            match = self.REX1.match(self._albumsort)
            if match:
                return f"{match.group(1)}.{match.group(2)}"
            match = self.REX2.match(self._albumsort)
            if match:
                return f"{match.group(1)}.{match.group(2)}"
        return None

    @classmethod
    def _set_name(cls, disc: str, track: str, title: str) -> Optional[str]:
        if all([disc, track, title]):
            title = cls._replace(title.rstrip()[:30], "_", "\\", "/", ":", "*", "?", "\"", ">", "<", "|")
            return f"{disc}.{track.zfill(2)}.{title}"
        return None

    @staticmethod
    def _replace(arg: str, new: str, *old: str) -> str:
        for item in old:
            arg = arg.replace(item, new)
        return arg

    @property
    def album(self) -> Optional[str]:
        if all([self._albumsort_short, self._album]):
            return f"{self._albumsort_short} - {self._album}"
        return None

    @property
    def dst(self) -> Optional[Path]:
        mapping = {".flac": self._parent1, ".mp3": self._parent2}
        if all([mapping.get(self._suffix.lower()), self._name]):
            return mapping.get(self._suffix.lower()) / f"{self._name}{self._suffix}"
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
    from contextlib import suppress
    from shutil import copy
    from typing import Any, List

    import yaml
    from mutagen import File, MutagenError  # type: ignore
    from mutagen.id3 import TALB, TRCK, TXXX  # type: ignore

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

    # -------------
    # Main process.
    # -------------
    collection = []  # type: List[AudioFileMetadata]
    if arguments.extension:
        for directory in arguments.directories:
            for file in Files(directory, excluded=filterfalse_(filter_extensions(arguments.extension))):  # type: Any
                collection.append(AudioFileMetadata(file))
    collection = sorted(collection, key=attrgetter("dst"))

    # -----------
    # Copy files.
    # -----------
    count, index = 0, 0  # type: int, int
    for file in collection:
        if all([file.src, file.dst]):
            index += 1
            src = file.src
            dst = arguments.parent / arguments.repository.capitalize() / file.dst
            print(f'{index:>2d}. Copy and rename "{src}" to "{dst}".')
            if not arguments.test:
                os.makedirs(dst.parent, exist_ok=True)
                copy(src, dst)
                count += 1

    # ---------------
    # Alter metadata.
    # ---------------
    if not arguments.test:
        track, tracks = 0, len(collection)  # type: int, int
        for file in collection:
            if file.album:
                path = arguments.parent / arguments.repository.capitalize() / file.dst
                if path.exists():
                    audio_file = File(path)
                    tag = audio_file.tags
                    track += 1

                    if arguments.extension == "flac":
                        tag["album"] = file.album
                        tag["tracknumber"] = str(track)
                        tag["tracktotal"] = str(tracks)
                        with suppress(MutagenError):
                            audio_file.save()

                    elif arguments.extension == "mp3":
                        tag.add(TALB(text=file.album))
                        tag.add(TRCK(text=str(track)))
                        tag.add(TXXX(description="TOTALTRACKS", text=str(tracks)))
                        with suppress(MutagenError):
                            audio_file.save()

    sys.exit(count)
