# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import os
from contextlib import suppress
from itertools import chain, islice
from operator import itemgetter
from pathlib import Path
from typing import Any, Mapping

from mutagen import File  # type: ignore
from mutagen.apev2 import APEv2  # type: ignore
from mutagen.flac import VCommentDict  # type: ignore
from mutagen.id3 import ID3  # type: ignore
from mutagen.mp4 import MP4FreeForm, MP4Tags  # type: ignore

from Applications.shared import Files, partitioner

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent


# ===================
# Decorators factory.
# ===================
def isinstance_(obj):
    """
    Undocumented.
    """

    def outer_wrapper(func):
        def inner_wrapper(arg):
            return isinstance(func(arg), obj)

        return inner_wrapper

    return outer_wrapper


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
    MAPPING = {"mediatype": "source",
               "publisher": "label",
               "totaltracks": "tracktotal",
               "totaldiscs": "disctotal",
               "track": "tracknumber",
               "year": "date"}

    def __init__(self, path):
        self._tag = None
        super(APEv2Tag, self).__init__(path)
        if isinstance(self._tag, APEv2):
            self._collection = {self.MAPPING.get(key.lower(), key.lower()): value.value for key, value in self._tag.items()}


class ID3v2Tag(AudioMetaData):
    """
    Undocumented.
    """
    MAPPING = {"albumartist": ("TPE2", None),
               "albumartistsort": ("TSO2", None),
               "artist": ("TPE1", None),
               "artistsort": ("TSOP", None),
               "albumsort": ("TSOA", None),
               "titlesort": ("TSOT", None),
               "album": ("TALB", None),
               "genre": ("TCON", None),
               "discnumber": ("TPOS", None),
               "disctotal": ("TXXX:totaldiscs", "TXXX:TOTALDISCS"),
               "tracknumber": ("TRCK", None),
               "tracktotal": ("TXXX:totaltracks", "TXXX:TOTALTRACKS"),
               "title": ("TIT2", None),
               "titlelanguage": ("TXXX:titlelanguage", "TXXX:TITLELANGUAGE"),
               "source": ("TMED", None),
               "origyear": ("TDOR", None),
               "date": ("TDRC", None),
               "label": ("TPUB", None),
               "upc": ("TXXX:upc", "TXXX:UPC"),
               "incollection": ("TXXX:incollection", "TXXX:INCOLLECTION"),
               "encodedby": ("TENC", None),
               "encodingtime": ("TXXX:encodingtime", "TXXX:ENCODINGTIME"),
               "encodingyear": ("TXXX:encodingyear", "TXXX:ENCODINGYEAR"),
               "taggingtime": ("TXXX:taggingtime", "TXXX:TAGGINGTIME")}

    def __init__(self, path: Path):
        self._tag = None
        super(ID3v2Tag, self).__init__(path)
        if isinstance(self._tag, ID3):
            for dst, src in self.MAPPING.items():
                self._collection[dst] = self._get_frame(*src)

    def _get_frame(self, *frames):
        frame_id, fallback_id = frames
        (frame,) = self._tag.getall(frame_id) or [None]  # type: Any
        if frame is None and fallback_id is not None:
            (frame,) = self._tag.getall(fallback_id) or [None]  # type: Any
        if frame is not None:
            if frame.text:
                text = frame.text[0]
                if not isinstance(text, str):
                    text = text.text
                return text
        return None


class MP4Tag(AudioMetaData):
    """
    Undocumented.
    """
    MAPPING = {"\u00A9alb": "album",
               "\u00A9day": "date",
               "\u00A9gen": "genre",
               "\u00A9nam": "title",
               "\u00A9ART": "artist",
               "aArt": "albumartist",
               "disk": "discnumber",
               "soaa": "albumartistsort",
               "soar": "artistsort",
               "soal": "albumsort",
               "sonm": "titlesort",
               "trkn": "tracknumber",
               "----:com.apple.iTunes:INCOLLECTION": "incollection",
               "----:com.apple.iTunes:LABEL": "label",
               "----:com.apple.iTunes:ORIGYEAR": "origyear",
               "----:com.apple.iTunes:SOURCE": "source",
               "----:com.apple.iTunes:TITLELANGUAGE": "titlelanguage"}

    def __init__(self, path: Path):
        self._tag = None
        super(MP4Tag, self).__init__(path)
        if isinstance(self._tag, MP4Tags):
            tag = list(self._tag.items())  # type: Any

            # Split between list objects and boolean objects.
            list_, bool_ = partitioner(tag, predicate=isinstance_(list)(itemgetter(1)))  # type: Any, Any
            list_ = iter((k, *islice(chain(v), 1)) for k, v in list_)

            # Split between MP4FreeForm objects and string objects.
            freeform_, str_ = partitioner(list_, predicate=isinstance_(MP4FreeForm)(itemgetter(1)))  # type: Any, Any
            freeform_ = iter((k, v.decode("UTF_8")) for k, v in freeform_)

            # Gather metadata.
            collection = dict(chain(bool_, freeform_, str_))  # type: Mapping[str, Any]

            # Map metadata.
            for src, dst in self.MAPPING.items():
                self._collection[dst] = collection.get(src)
            with suppress(TypeError):
                self._collection["discnumber"], self._collection["disctotal"] = map(str, self._collection["discnumber"])
            with suppress(TypeError):
                self._collection["tracknumber"], self._collection["tracktotal"] = map(str, self._collection["tracknumber"])


class VorbisComment(AudioMetaData):
    """
    Undocumented.
    """

    def __init__(self, path):
        self._tag = None
        super(VorbisComment, self).__init__(path)
        if isinstance(self._tag, VCommentDict):
            self._collection = {key.lower(): value for key, value in self._tag}
