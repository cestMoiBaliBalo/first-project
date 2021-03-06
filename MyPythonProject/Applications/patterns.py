# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import csv
import re
from contextlib import suppress
from datetime import datetime
from functools import partial
from itertools import filterfalse
from operator import itemgetter
from typing import Any, Iterator, MutableMapping, Optional, Tuple

from pytz import timezone

from Applications import callables, decorators
from Applications.shared import DFTTIMEZONE, TEMPLATE3, UTF16, eq_string_, format_date, valid_albumsort

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# ===============
# Global classes.
# ===============
class CustomDialect(csv.Dialect):
    delimiter = "="
    escapechar = "`"
    doublequote = False
    quoting = csv.QUOTE_NONE
    lineterminator = "\r\n"


# ===================
# Pattern decorators.
# ===================
class AudioMetadata(MutableMapping):
    """
    Undocumented.
    """
    REGEX = re.compile(r"^(?:z_)?(.+)$", re.IGNORECASE)

    def __init__(self, **kwargs):
        self._tags = dict(kwargs)  # type: MutableMapping[str, str]

    def __delitem__(self, key) -> None:
        del self._tags[key]

    def __getitem__(self, item) -> str:
        return self._tags[item]

    def __iter__(self) -> Iterator[Tuple[str, str]]:
        for key, value in self._tags.items():
            yield key, value

    def __len__(self) -> int:
        return len(self._tags)

    def __repr__(self) -> str:
        if not self:
            return "%s()" % (self.__class__.__name__,)
        return "%s(%r)" % (self.__class__.__name__, sorted(self, key=itemgetter(0)))

    def __setitem__(self, key, value) -> None:
        self._tags[key] = value

    def get(self, key: str) -> Optional[str]:
        return self._tags.get(key)

    @classmethod
    def fromfile(cls, fil: str, enc: str = UTF16):
        with open(fil, encoding=enc) as stream:
            tags = csv.reader(stream, dialect=CustomDialect())  # type: Any
            tags = filterfalse(decorators.itemgetter_(0)(partial(eq_string_, "encoder+")), tags)
            tags = [(decorators.rstrip_(decorators.lower_(callables.group_(1)(cls.REGEX.match)))(key), value) for key, value in tags]
            return cls(**dict(tags))


class MetaDataDecorator(AudioMetadata):
    """
    Undocumented.
    """

    def __init__(self, metadata):
        super(MetaDataDecorator, self).__init__(**dict(iter(metadata)))


class RemoveMetaData(MetaDataDecorator):
    """
    Undocumented.
    """

    def __init__(self, metadata):
        super(RemoveMetaData, self).__init__(metadata)
        self["encodingtime"] = int(datetime.now(tz=timezone(DFTTIMEZONE)).timestamp())
        self["encodingyear"] = datetime.now(tz=timezone(DFTTIMEZONE)).strftime("%Y")
        self["taggingtime"] = format_date(datetime.now(tz=timezone(DFTTIMEZONE)), template=TEMPLATE3)
        for tag in ["copyright", "description", "mediaprovider", "profile", "purchasedate"]:
            with suppress(KeyError):
                del self[tag]


class EncodedFromFLACFile(MetaDataDecorator):
    """
    Undocumented.
    """

    def __init__(self, metadata):
        super(EncodedFromFLACFile, self).__init__(metadata)
        self["encodedby"] = "dBpoweramp Batch Converter on {0} from original FLAC file".format(format_date(datetime.now(tz=timezone(DFTTIMEZONE)), template=TEMPLATE3))


class EncodedFromHDtracksFLACFile(MetaDataDecorator):
    """
    Undocumented.
    """

    def __init__(self, metadata):
        super(EncodedFromHDtracksFLACFile, self).__init__(metadata)
        self["encodedby"] = "dBpoweramp Batch Converter on {0} from original HDtracks.com FLAC file".format(format_date(datetime.now(tz=timezone(DFTTIMEZONE)), template=TEMPLATE3))


class EncodedFromNugsFLACFile(MetaDataDecorator):
    """
    Undocumented.
    """

    def __init__(self, metadata):
        super(EncodedFromNugsFLACFile, self).__init__(metadata)
        self["encodedby"] = "dBpoweramp Batch Converter on {0} from original nugs.net FLAC file".format(format_date(datetime.now(tz=timezone(DFTTIMEZONE)), template=TEMPLATE3))


class EncodedFromNugsDSDFile(MetaDataDecorator):
    """
    Undocumented.
    """

    def __init__(self, metadata):
        super(EncodedFromNugsDSDFile, self).__init__(metadata)
        self["encodedby"] = "dBpoweramp Batch Converter on {0} from original nugs.net DSD file".format(format_date(datetime.now(tz=timezone(DFTTIMEZONE)), template=TEMPLATE3))


class AlbumSort(MetaDataDecorator):
    """
    Undocumented.
    """
    CODECS = {"FDK": "02", "LAME": "01"}

    def __init__(self, metadata, codec):
        super(AlbumSort, self).__init__(metadata)
        albumsort = self.get("albumsort")
        if albumsort:
            try:
                albumsort = valid_albumsort(albumsort[:-3])
            except ValueError:
                pass
            else:
                self["albumsort"] = "{0}.{1}".format(albumsort, self.CODECS[codec.upper()])


class TrackNumber(MetaDataDecorator):
    """
    Undocumented.
    """
    PATTERN = re.compile(r"^(\d{1,2})/(\d{1,2})$")
    MAPPING = {"DFT": "tracktotal", "LAME": "totaltracks"}

    def __init__(self, metadata, codec):
        super(TrackNumber, self).__init__(metadata)
        track = self.get("track")
        if track:
            match = self.PATTERN.match(track)
            if match:
                self["track"] = match.group(1)
                self[self.MAPPING.get(codec.upper(), self.MAPPING["DFT"])] = match.group(2)


class DiscNumber(MetaDataDecorator):
    """
    Undocumented.
    """
    PATTERN = re.compile(r"^(\d{1,2})/(\d{1,2})$")
    MAPPING = {"DFT": "disctotal", "LAME": "totaldiscs"}

    def __init__(self, metadata, codec):
        super(DiscNumber, self).__init__(metadata)
        disc = self.get("disc")
        if disc:
            match = self.PATTERN.match(disc)
            if match:
                self["disc"] = match.group(1)
                self[self.MAPPING.get(codec.upper(), self.MAPPING["DFT"])] = match.group(2)
