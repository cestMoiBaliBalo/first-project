# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import re
from collections.abc import MutableMapping
from contextlib import suppress
from datetime import datetime

from pytz import timezone
from sortedcontainers import SortedDict  # type: ignore

from Applications.AudioCD.shared import DFTPATTERN, filcontents
from Applications.shared import DFTTIMEZONE, TEMPLATE3, UTF16, format_date, valid_albumsort

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# ==========
# Constants.
# ==========
# REGEX = re.compile(r"^(\d\.\d{2}\.)(.+)\.[a-z0-9]{3,4}$", re.IGNORECASE)


# ==========
# Pattern 1.
# ==========
# Pattern used by `AudioCD/Convert.py` from dBpoweramp Audio CD ripping application.
# 1. Used for renaming an audio file from the track title.
# 2. Used for renaming an audio file from a subset taken from the file name.
# class FileNameDecorator():
#     def __init__(self, obj):
#         self.name, self.found, self.tags, self.extension = obj.name, obj.found, obj.tags, obj.extension
#
#
# class RightTrim(FileNameDecorator):
#     def __init__(self, obj, length=30):
#         super(RightTrim, self).__init__(obj)
#         if self.found:
#             self.name = self.name[:length]
#
#
# class RenameWithTitle(FileNameDecorator):
#     def __init__(self, obj):
#         super(RenameWithTitle, self).__init__(obj)
#         if self.found:
#             _name = self.tags["title"]
#             for char in ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]:
#                 _name = _name.replace(char, "_")
#             self.name = _name


# ==========
# Pattern 2.
# ==========
# Pattern used by `AudioCD/Converter/Convert.py` from dBpoweramp Batch Converter.
# Used for processing audio tags.
class AudioTagsInterface(MutableMapping):
    def __init__(self, **kwargs):
        self._tags = dict(kwargs)

    def __setitem__(self, key, value):
        self._tags[key] = value

    def __getitem__(self, item):
        return self._tags[item]

    def __delitem__(self, key):
        del self._tags[key]

    def __len__(self):
        return len(self._tags)

    def __iter__(self):
        return iter(self._tags)

    @classmethod
    def fromfile(cls, fil, enc=UTF16):
        regex, mapping = re.compile(DFTPATTERN, re.IGNORECASE), {}
        with open(fil, encoding=enc) as fr:
            for line in filcontents(fr):
                match = regex.match(line)
                if match:
                    mapping[match.group(1).rstrip().lower()] = match.group(2)
        return cls(**mapping)


class AudioTags(AudioTagsInterface):
    def __init__(self, **kwargs):
        super(AudioTags, self).__init__(**kwargs)
        self._tags = SortedDict(self._tags)


class TagsDecorator(AudioTagsInterface):
    def __init__(self, obj):
        super(TagsDecorator, self).__init__(**dict(obj.items()))
        self._tags = SortedDict(self._tags)


class DefaultTags(TagsDecorator):
    def __init__(self, obj):
        super(DefaultTags, self).__init__(obj)
        self._tags["encodingtime"] = int(datetime.now(tz=timezone(DFTTIMEZONE)).timestamp())
        self._tags["encodingyear"] = datetime.now(tz=timezone(DFTTIMEZONE)).strftime("%Y")
        self._tags["taggingtime"] = format_date(datetime.now(tz=timezone(DFTTIMEZONE)), template=TEMPLATE3)
        for tag in ["copyright", "description", "mediaprovider", "profile", "purchasedate"]:
            with suppress(KeyError):
                del self._tags[tag]


class EncodedFromFLACFile(TagsDecorator):
    def __init__(self, obj):
        super(EncodedFromFLACFile, self).__init__(obj)
        self._tags["encodedby"] = "dBpoweramp Batch Converter on {0} from original FLAC file".format(format_date(datetime.now(tz=timezone(DFTTIMEZONE)), template=TEMPLATE3))


class EncodedFromNugsFLACFile(TagsDecorator):
    def __init__(self, obj):
        super(EncodedFromNugsFLACFile, self).__init__(obj)
        self._tags["encodedby"] = "dBpoweramp Batch Converter on {0} from original nugs.net FLAC file".format(format_date(datetime.now(tz=timezone(DFTTIMEZONE)), template=TEMPLATE3))


class EncodedFromNugsDSDFile(TagsDecorator):
    def __init__(self, obj):
        super(EncodedFromNugsDSDFile, self).__init__(obj)
        self._tags["encodedby"] = "dBpoweramp Batch Converter on {0} from original nugs.net DSD file".format(format_date(datetime.now(tz=timezone(DFTTIMEZONE)), template=TEMPLATE3))


class AlbumSort(TagsDecorator):
    CODECS = {"FDK": "02",
              "LAME": "01"}

    def __init__(self, obj, codec):
        super(AlbumSort, self).__init__(obj)
        albumsort = self._tags.get("albumsort")
        if albumsort:
            try:
                albumsort = valid_albumsort(albumsort[:-3])
            except ValueError:
                pass
            else:
                self._tags["albumsort"] = "{0}.{1}".format(albumsort, self.CODECS[codec.upper()])
