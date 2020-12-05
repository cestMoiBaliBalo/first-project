# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import os
from operator import itemgetter
from pathlib import Path
from typing import Any, Mapping

from mutagen import File  # type: ignore
from mutagen.apev2 import APEv2  # type: ignore
from mutagen.flac import VCommentDict  # type: ignore
from mutagen.id3 import ID3  # type: ignore

from Applications.shared import Files

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent


# ==============
# Shared classes.
# ==============
class AudioMetaData(Mapping):
    """
    Undocumented.
    """

    def __init__(self, path):
        self._path = path
        self._name = path.stem
        self._extension = path.suffix
        self._collection = {}
        try:
            self._tag = File(path).tags
        except AttributeError:
            raise ValueError(f'Can\'t open "{path}". Please check whether it is an appropriate audio file.')

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
    def fromdirectory(cls, path, *, excluded=None):
        for file in Files(path, excluded=excluded):
            yield list(cls(file))

    @property
    def name(self):
        return self._name

    @property
    def extension(self):
        return self._extension

    @property
    def path(self):
        return self._path


class APEv2Tag(AudioMetaData):
    """
    Undocumented.
    """

    def __init__(self, path):
        self._tag = None
        super(APEv2Tag, self).__init__(path)
        if isinstance(self._tag, APEv2):
            self._collection = {key.lower(): value.value for key, value in self._tag.items()}


class ID3v2Tag(AudioMetaData):
    """
    Undocumented.
    """

    def __init__(self, path: Path):
        self._tag = None
        super(ID3v2Tag, self).__init__(path)
        if isinstance(self._tag, ID3):
            self._collection["artistsort"] = self._get_frame("TSOP")  # artistsort.
            self._collection["albumsort"] = self._get_frame("TSOA")  # albumsort.
            self._collection["titlesort"] = self._get_frame("TSOT")  # titlesort.
            self._collection["album"] = self._get_frame("TALB")  # album.
            self._collection["genre"] = self._get_frame("TCON")  # genre.
            self._collection["discnumber"] = self._get_frame("TPOS")  # disc number.
            self._collection["disctotal"] = self._get_frame("TXXX:TOTALDISCS")  # total discs.
            self._collection["tracknumber"] = self._get_frame("TRCK")  # track number.
            self._collection["tracktotal"] = self._get_frame("TXXX:TOTALTRACKS")  # total tracks.
            self._collection["title"] = self._get_frame("TIT2")  # track title.
            self._collection["titlelanguage"] = self._get_frame("TXXX:TITLELANGUAGE")  # title language.
            self._collection["source"] = self._get_frame("TMED")  # source.
            self._collection["origyear"] = self._get_frame("TDOR")  # original release year.
            self._collection["date"] = self._get_frame("TDRC")  # release year.
            self._collection["label"] = self._get_frame("TPUB")  # label.
            self._collection["upc"] = self._get_frame("TXXX:UPC")  # UPC.
            self._collection["incollection"] = self._get_frame("TXXX:INCOLLECTION")  # in collection.
            self._collection["encodedby"] = self._get_frame("TENC")  # encoded by.
            self._collection["encodingtime"] = self._get_frame("TXXX:encodingtime")  # encoding time.
            self._collection["encodingyear"] = self._get_frame("TXXX:encodingyear")  # encoding year.
            self._collection["taggingtime"] = self._get_frame("TXXX:taggingtime")  # tagging time.

    def _get_frame(self, frame_id):
        (frame,) = self._tag.getall(frame_id) or [None]  # type: Any
        if frame is not None:
            return frame.text[0]
        return None


class VorbisComment(AudioMetaData):
    """
    Undocumented.
    """

    def __init__(self, path):
        self._tag = None
        super(VorbisComment, self).__init__(path)
        if isinstance(self._tag, VCommentDict):
            self._collection = {key.lower(): value for key, value in self._tag}
