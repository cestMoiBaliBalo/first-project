# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import json
import logging
import os
import re
from collections import namedtuple
from collections.abc import MutableMapping
from contextlib import ContextDecorator, ExitStack, suppress
from datetime import datetime
from functools import partial
from itertools import compress, groupby
from operator import itemgetter
from pathlib import PureWindowsPath
from string import Template
from typing import Any, Callable, Dict, IO, Iterable, List, Mapping, NamedTuple, Optional, Sequence, Tuple, Union

import ftputil.error
import mutagen.flac
import mutagen.monkeysaudio
import mutagen.mp3
import yaml
from dateutil import parser
from jinja2 import Environment, FileSystemLoader
from mutagen import File, MutagenError
from mutagen.apev2 import APETextValue
from mutagen.easyid3 import EasyID3
from pytz import timezone
from sortedcontainers import SortedDict

from .. import shared
from ..Tables.Albums.shared import get_countries, get_genres, get_languages, get_providers
from ..callables import exclude_allbutlosslessaudiofiles

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# ========
# Classes.
# ========
class AudioCDTags(MutableMapping):
    logger = logging.getLogger("{0}.AudioCDTags".format(__name__))
    track_pattern = re.compile(r"^(\d{1,2})/(\d{1,2})")

    def __init__(self):
        self.logger.debug("AudioCDTags.__init__")
        self._encoder = None
        self._totaltracks_key = None
        self._totaldiscs_key = None
        self._otags = dict()

    def __getitem__(self, item):
        return self._otags[item]

    def __setitem__(self, key, value):
        self._otags[key] = value

    def __delitem__(self, key):
        del self._otags[key]

    def __len__(self):
        return len(self._otags)

    def __iter__(self):
        return iter(self._otags)

    @property
    def album(self):
        return self._otags["album"]

    @property
    def albumartist(self):
        return self._otags["albumartist"]

    @property
    def albumid(self):
        return "{0}.{1}.{2}".format(self._otags["artistsort"][0], self._otags["artistsort"], self._otags["albumsort"][:-3])

    @property
    def albumsort(self):
        return self._otags["albumsort"]

    @property
    def albumsortcount(self):
        return self._otags["albumsortcount"]

    @property
    def artist(self):
        return self._otags["artist"]

    @property
    def artistsort(self):
        return self._otags["artistsort"]

    @property
    def artistsort_letter(self):
        return self._otags["artistsort"][0]

    @property
    def bonustrack(self):
        return self._otags.get("bonustrack", "N")

    @property
    def bootleg(self):
        return self._otags.get("bootleg", "N")

    @property
    def bootlegalbum_city(self):
        return self._otags.get("bootlegalbumcity")

    @property
    def bootlegalbum_country(self):
        return self._otags.get("bootlegalbumcountry")

    @property
    def bootlegalbum_date(self):
        return self._otags.get("bootlegalbumday")

    @property
    def bootlegalbum_day(self):
        day = None
        with suppress(TypeError):
            day = self._otags.get("bootlegalbumday")[-2:]
        return day

    @property
    def bootlegalbum_month(self):
        month = None
        with suppress(TypeError):
            month = self._otags.get("bootlegalbumday")[5:-3]
        return month

    @property
    def bootlegalbum_provider(self):
        return self._otags.get("bootlegalbumprovider")

    @property
    def bootlegalbum_title(self):
        return self._otags.get("bootlegalbumtitle")

    @property
    def bootlegalbum_tour(self):
        return self._otags.get("bootlegalbumtour")

    @property
    def bootlegalbum_year(self):
        year = None
        with suppress(TypeError):
            year = self._otags.get("bootlegalbumday")[:4]
        return year

    @property
    def bootlegdisc_reference(self):
        return self._otags.get("bootlegdiscreference")

    @property
    def bootlegtrack_city(self):
        return self._otags.get("bootlegtrackcity")

    @property
    def bootlegtrack_country(self):
        return self._otags.get("bootlegtrackcountry")

    @property
    def bootlegtrack_date(self):
        return self._otags.get("bootlegtrackday")

    @property
    def bootlegtrack_day(self):
        return self._otags.get("bootlegtrackday")[-2:]

    @property
    def bootlegtrack_month(self):
        return self._otags.get("bootlegtrackday")[5:-3]

    @property
    def bootlegtrack_year(self):
        return self._otags.get("bootlegtrackday")[:4]

    @property
    def bootlegtrack_tour(self):
        return self._otags.get("bootlegtracktour")

    @property
    def deluxe(self):
        return self._otags.get("deluxe", "N")

    @property
    def discnumber(self):
        return self._otags["disc"]

    @property
    def foldersortcount(self):
        return self._otags.get("foldersortcount", "N")

    @property
    def genre(self):
        return self._otags["genre"]

    @property
    def incollection(self):
        return self._otags["incollection"]

    @property
    def interface(self):
        return SortedDict(**self._otags)

    @property
    def label(self):
        return self._otags["label"]

    @property
    def livedisc(self):
        return self._otags.get("livedisc", "N")

    @property
    def livetrack(self):
        return self._otags.get("livetrack", "N")

    @property
    def mediaprovider(self):
        return self._otags.get("mediaprovider")

    @property
    def origyear(self):
        return self._otags.get("origyear")

    @property
    def titlesort(self):
        return self._otags["titlesort"]

    @property
    def totaldiscs(self):
        return self._otags[self._totaldiscs_key]

    @property
    def totaltracks(self):
        return self._otags[self._totaltracks_key]

    @property
    def tracknumber(self):
        return self._otags["track"]

    @property
    def title(self):
        return self._otags["title"]

    @property
    def tracklanguage(self):
        return self._otags["titlelanguage"]

    @property
    def upc(self):
        return self._otags.get("upc")

    @property
    def year(self):
        return self._otags["year"]

    @classmethod
    def fromfile(cls, fil):
        regex, mapping = re.compile(DFTPATTERN, re.IGNORECASE), {}
        for line in filcontents(fil):
            _match = regex.match(line)
            if _match:
                mapping[_match.group(1).rstrip().lower()] = _match.group(2)
        return cls(**SortedDict(**mapping))

    @staticmethod
    def checktags(member, container):
        return container.get(member, "False")

    @staticmethod
    def deserialize(fil, enc=shared.UTF8):
        with open(fil, encoding=enc) as fr:
            for structure in json.load(fr):
                yield structure

    @staticmethod
    def splitfield(fld, rex):
        match = rex.match(fld)
        if match:
            return match.group(1, 2)
        return ()


class CommonAudioCDTags(AudioCDTags):
    logger = logging.getLogger("{0}.CommonAudioCDTags".format(__name__))
    __tags = {"albumartist": False,
              "albumartistsort": False,
              "artist": True,
              "artistsort": True,
              "bootleg": True,
              "disc": True,
              "encoder": True,
              "genre": False,
              "incollection": True,
              "livedisc": True,
              "livetrack": True,
              "profile": False,
              "rating": False,
              "source": False,
              "style": False,
              "title": False,
              "tracklanguage": False,
              "track": True,
              "_albumart_1_front album cover": False}

    def __init__(self, **kwargs):
        self.logger.debug("CommonAudioCDTags.__init__")
        super(CommonAudioCDTags, self).__init__()

        # ----- Check mandatory input tags.
        checked, exception = self.__validatetags(**kwargs)
        if not checked:
            raise ValueError(exception)

        # ----- Encoder dependent attributes.
        Encoder = namedtuple("Encoder", "name code folder extension")
        self._totaltracks_key = MAPPING.get(kwargs["encoder"], MAPPING["default"])["totaltracks"]
        self._totaldiscs_key = MAPPING.get(kwargs["encoder"], MAPPING["default"])["totaldiscs"]

        # ----- Attributes taken from the input tags.
        filter_keys = shared.getitem_(index=0)(shared.partial_(sorted(self.__tags))(contains_))
        self._otags = dict(filter(filter_keys, sorted(kwargs.items())))

        # ----- Set encodedby.
        self.logger.debug("Set encodedby.")
        self._otags["encodedby"] = "{0} on {1}".format(shared.get_rippingapplication(), shared.format_date(datetime.now(tz=timezone(shared.DFTTIMEZONE))))

        # ----- Set taggingtime.
        self.logger.debug("Set taggingtime.")
        self._otags["taggingtime"] = shared.format_date(datetime.now(tz=timezone(shared.DFTTIMEZONE)))

        # ----- Set encodingtime.
        self.logger.debug("Set encodingtime.")
        self._otags["encodingtime"] = int(datetime.now(tz=timezone(shared.DFTTIMEZONE)).timestamp())

        # ----- Set encodingyear.
        self.logger.debug("Set encodingyear.")
        self._otags["encodingyear"] = datetime.now(tz=timezone(shared.DFTTIMEZONE)).strftime("%Y")

        # ----- Set encoder attributes.
        self.logger.debug("Set encoder attributes.")
        for encoder in self.deserialize(ENCODERS):  # "encoder" est un dictionnaire.
            if sorted(encoder) == sorted(ENC_KEYS):
                if kwargs["encoder"] == encoder["name"]:
                    self._otags["encoder"] = kwargs["encoder"]
                    self._encoder = Encoder(encoder["name"], encoder["code"], encoder["folder"], encoder["extension"])
                    self.logger.debug("Used encoder.")
                    self.logger.debug("Name\t\t: %s".expandtabs(3), self._encoder.name)
                    self.logger.debug("Code\t\t: %s".expandtabs(3), self._encoder.code)
                    self.logger.debug("Folder\t: %s".expandtabs(3), self._encoder.folder)
                    self.logger.debug("Extension: %s".expandtabs(3), self._encoder.extension)
                    break

        # ----- Both update track and set total tracks.
        self.logger.debug("Set track.")
        self._otags["track"], self._otags[self._totaltracks_key] = self.splitfield(kwargs["track"], self.track_pattern)

        # ----- Both update disc and set total discs.
        self.logger.debug("Set disc.")
        self._otags["disc"], self._otags[self._totaldiscs_key] = self.splitfield(kwargs["disc"], self.track_pattern)

        # ----- Update genre.
        self.logger.debug("Update genre.")
        for artist, genre in self.deserialize(GENRES):
            if kwargs["artist"].lower() == artist.lower():
                self._otags["genre"] = genre
                break

        # ----- Update titlelanguage.
        self.logger.debug("Update titlelanguage.")
        self._otags["titlelanguage"] = self._otags.get("tracklanguage", "English")
        for artist, language in self.deserialize(LANGUAGES):
            if kwargs["artist"].lower() == artist.lower():
                self._otags["titlelanguage"] = language
                break

        # ----- Update title.
        self.logger.debug("Update title.")
        self._otags["title"] = shared.TitleCaseConverter().convert(self._otags["title"])

    def __validatetags(self, **kwargs):
        checktags = partial(self.checktags, container=self.__tags)
        for item in filter(checktags, self.__tags.keys()):
            self.logger.debug("CommonAudioCDTags: %s.", item)
            if item not in kwargs:
                return False, "{0} isn\'t available.".format(item)
        if not self.track_pattern.match(kwargs["track"]):
            return False, "track doesn\'t respect the expected pattern."
        if not self.track_pattern.match(kwargs["disc"]):
            return False, "disc doesn\'t respect the expected pattern."
        if kwargs["encoder"] not in [encoder.get("name") for encoder in self.deserialize(ENCODERS)]:
            return False, '"{0}" as encoder isn\'t recognized.'.format(kwargs["encoder"])
        return True, ""


class DefaultAudioCDTags(CommonAudioCDTags):
    logger = logging.getLogger("{0}.DefaultAudioCDTags".format(__name__))
    __tags = {"album": True,
              "albumsortcount": True,
              "foldersortcount": False,
              "bonustrack": False,
              "deluxe": False,
              "label": True,
              "origyear": False,
              "upc": True,
              "year": True}

    def __init__(self, **kwargs):
        self.logger.debug("DefaultAudioCDTags.__init__")
        super(DefaultAudioCDTags, self).__init__(**kwargs)

        # ----- Check mandatory input tags.
        checked, exception = self.__validatetags(**kwargs)
        if not checked:
            raise ValueError(exception)

        # ----- Update tags.
        filter_keys = shared.getitem_(index=0)(shared.partial_(sorted(self.__tags))(contains_))
        self._otags.update(dict(filter(filter_keys, sorted(kwargs.items()))))

        # ----- Set origyear.
        self.logger.debug("Set origyear.")
        self._otags["origyear"] = self._otags.get("origyear", self._otags["year"])

        # ----- Set albumsort.
        self.logger.debug("Set albumsort.")
        self._otags["albumsort"] = "1.{year}0000.{uid}.{enc}".format(year=self._otags["origyear"], uid=self._otags["albumsortcount"], enc=self._encoder.code)
        self._otags["albumsortyear"] = self._otags["albumsort"][2:6]

        # ----- Set titlesort.
        self.logger.debug("Set titlesort.")
        self._otags["titlesort"] = "D{disc}.T{track}.{bonustrack}{livetrack}{bootleg}".format(disc=self._otags["disc"],
                                                                                              track=self._otags["track"].zfill(2),
                                                                                              bonustrack=self._otags.get("bonustrack", "N"),
                                                                                              livetrack=self._otags["livetrack"],
                                                                                              bootleg=self._otags["bootleg"])

        # ----- Update album.
        self.logger.debug("Update album.")
        self._otags["album"] = shared.TitleCaseConverter().convert(self._otags["album"])

        # ----- Log new tags.
        self.logger.debug("Build tags.")
        self.logger.debug("\talbum    : %s".expandtabs(4), self._otags["album"])
        self.logger.debug("\talbumsort: %s".expandtabs(4), self._otags["albumsort"])
        self.logger.debug("\ttitlesort: %s".expandtabs(4), self._otags["titlesort"])
        self.logger.debug("\torigyear : %s".expandtabs(4), self._otags["origyear"])

    def __validatetags(self, **kwargs):
        checktags = partial(self.checktags, container=self.__tags)
        for item in filter(checktags, self.__tags.keys()):
            self.logger.debug("DefaultAudioCDTags: %s.", item)
            if item not in kwargs:
                return False, "{0} isn\'t available.".format(item)
        return True, ""


class BootlegAudioCDTags(CommonAudioCDTags):
    logger = logging.getLogger("{0}.BootlegAudioCDTags".format(__name__))
    REX1 = re.compile(r"\W+")
    REX2 = re.compile(r", ([A-Z][a-z]+)$")
    DFTCOUNTRY = "United States"
    __tags = {"bootlegtracktour": False,
              "bootlegtrackyear": False,
              "bootlegtrackcity": False,
              "bootlegalbumtour": True,
              "bootlegalbumyear": True,
              "bootlegalbumcity": True,
              "albumsortcount": True,
              "bootlegalbumprovider": False,
              "bootlegalbumtitle": False,
              "bootlegdiscreference": False,
              "bonustrack": True}

    def __init__(self, **kwargs):
        super(BootlegAudioCDTags, self).__init__(**kwargs)

        # ----- Check mandatory input tags.
        checked, exception = self.__validatetags(**kwargs)
        if not checked:
            raise ValueError(exception)

        # ----- Update tags.
        filter_keys = shared.getitem_(index=0)(shared.partial_(sorted(self.__tags))(contains_))
        self._otags.update(dict(filter(filter_keys, sorted(kwargs.items()))))

        # ----- Set bootleg date.
        self._otags["dottedbootlegalbumyear"] = self.REX1.sub(".", self._otags["bootlegalbumyear"])
        self._otags["dashedbootlegalbumyear"] = self.REX1.sub("-", self._otags["bootlegalbumyear"])

        # ----- Set bootlegalbumday.
        day = parser.parse(self.REX1.sub("-", self._otags["bootlegalbumyear"]), default=datetime.utcnow())
        self._otags["bootlegalbumday"] = day.date().isoformat()

        # ----- Set bootlegtrackday.
        day = parser.parse(self.REX1.sub("-", self._otags.get("bootlegtrackyear", self._otags["bootlegalbumyear"])), default=datetime.utcnow())
        self._otags["bootlegtrackday"] = day.date().isoformat()

        # ----- Set bootlegtrackyear.
        self.logger.debug("Update bootlegtrackyear.")
        self._otags["bootlegtrackyear"] = self.REX1.sub("-", self._otags.get("bootlegtrackyear", self._otags["bootlegalbumyear"]))
        self.logger.debug(self._otags["bootlegtrackyear"])

        # ----- Set bootlegtrackcity.
        bootlegtrackcity = self._otags.get("bootlegtrackcity", self._otags["bootlegalbumcity"])
        self._otags["bootlegtrackcity"] = bootlegtrackcity
        self.logger.debug(self._otags["bootlegtrackcity"])

        # ----- Set bootlegtrackcountry.
        self.logger.debug("Set bootlegtrackcountry.")
        self._otags["bootlegtrackcountry"] = self.DFTCOUNTRY
        match = self.REX2.search(bootlegtrackcity)
        if match:
            self._otags["bootlegtrackcountry"] = match.group(1)
        self.logger.debug(self._otags["bootlegtrackcountry"])

        # ----- Set bootlegalbumcountry.
        self.logger.debug("Set bootlegalbumcountry.")
        self._otags["bootlegalbumcountry"] = self.DFTCOUNTRY
        match = self.REX2.search(self._otags["bootlegalbumcity"])
        if match:
            self._otags["bootlegalbumcountry"] = match.group(1)
        self.logger.debug(self._otags["bootlegalbumcountry"])

        # ----- Set bootlegtracktour.
        self.logger.debug("Set bootlegtracktour.")
        self._otags["bootlegtracktour"] = self._otags.get("bootlegtracktour", self._otags["bootlegalbumtour"])
        self.logger.debug(self._otags["bootlegtracktour"])

        # ----- Set year.
        self.logger.debug("Set year.")
        self._otags["year"] = self._otags["bootlegalbumyear"][:4]

        # ----- Set albumsort.
        self.logger.debug("Set albumsort.")
        self._otags["albumsort"] = "2.{date}.{uid}.{enc}".format(date=self.REX1.sub("", self._otags["bootlegalbumyear"]),
                                                                 uid=self._otags["albumsortcount"],
                                                                 enc=self._encoder.code)
        self.logger.debug(self._otags["albumsort"])

        # ----- Set titlesort.
        self.logger.debug("Set titlesort.")
        self._otags["titlesort"] = "D{disc}.T{track}.{bonustrack}{livetrack}{bootleg}".format(disc=self._otags["disc"],
                                                                                              track=self._otags["track"].zfill(2),
                                                                                              bonustrack=self._otags["bonustrack"],
                                                                                              livetrack=self._otags["livetrack"],
                                                                                              bootleg=self._otags["bootleg"])

    def __validatetags(self, **kwargs):
        checktags = partial(self.checktags, container=self.__tags)
        for item in filter(checktags, self.__tags.keys()):
            self.logger.debug("BootlegAudioCDTags: %s.", item)
            if item not in kwargs:
                return False, "{0} isn\'t available.".format(item)
        return True, ""


class TagsModifier(AudioCDTags):
    logger = logging.getLogger("{0}.TagsModifier".format(__name__))

    def __init__(self, obj):
        super(TagsModifier, self).__init__()
        for name, value in vars(obj).items():
            setattr(self, name, value)


class ChangeAlbum(TagsModifier):
    def __init__(self, obj, template):
        super(ChangeAlbum, self).__init__(obj)
        self._otags["album"] = Template(template).substitute(self._otags)


class ChangeAlbumArtist(TagsModifier):
    def __init__(self, obj, albumartist):
        super(ChangeAlbumArtist, self).__init__(obj)
        self._otags["albumartist"] = albumartist


class ChangeEncodedBy(TagsModifier):
    def __init__(self, obj):
        super(ChangeEncodedBy, self).__init__(obj)
        self._otags["encodedby"] = "{0} on {1} from nugs.net bootleg Audio CD".format(shared.get_rippingapplication(), shared.format_date(datetime.now(tz=timezone(shared.DFTTIMEZONE))))


class ChangeMediaProvider(TagsModifier):
    def __init__(self, obj, default="nugs.net"):
        super(ChangeMediaProvider, self).__init__(obj)
        self._otags["mediaprovider"] = self._otags.get("bootlegalbumprovider", default)


class ChangeTotalTracks(TagsModifier):
    def __init__(self, obj, totaltracks):
        super(ChangeTotalTracks, self).__init__(obj)
        self._otags[self._totaltracks_key] = totaltracks


class ChangeTrack(TagsModifier):
    def __init__(self, obj, offset):
        super(ChangeTrack, self).__init__(obj)
        self._otags["track"] = str(int(self.tracknumber) + offset)


class RippedDisc(ContextDecorator):
    _environment = Environment(loader=FileSystemLoader(os.path.join(shared.get_dirname(os.path.abspath(__file__), level=3), "AudioCD", "Templates")), trim_blocks=True, lstrip_blocks=True)
    _outputtags = _environment.get_template("Tags")
    _tabs = 4
    _in_logger = logging.getLogger(f"{__name__}.RippedDisc")

    def __init__(self, rippingprofile, file, encoder, *decoratingprofiles):
        self._audiotracktags = None
        self._decorators = None
        self._encoder = None
        self._profile = None
        self._intags = None
        self._tags = None
        self.decorators = decoratingprofiles
        self.encoder = encoder
        self.profile = rippingprofile
        self.tags = file

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, arg):
        arg = arg.lower()
        if arg not in PROFILES:
            raise ValueError('"{0}" isn\'t allowed.'.format(arg))
        self._profile = arg

    @property
    def encoder(self):
        return self._encoder

    @encoder.setter
    def encoder(self, arg):
        self._encoder = arg

    @property
    def decorators(self):
        return self._decorators

    @decorators.setter
    def decorators(self, arg):
        self._decorators = arg

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, arg):
        self._tags = arg

    @property
    def intags(self):
        return self._intags

    @property
    def audiotrack(self):
        return self._audiotracktags

    @staticmethod
    def get_tags(fil):
        """

        :param fil:
        :return:
        """
        intags, offset, totaltracks = [], "0", "0"
        for line in filcontents(fil):
            match = re.match(DFTPATTERN, line)
            if match:
                intags.append((match.group(1), match.group(2)))
                if match.group(1).lower() == "offset":
                    offset = match.group(2)
                elif match.group(1).lower() == "totaltracks":
                    totaltracks = match.group(2)
        return intags, offset, totaltracks

    @staticmethod
    def alter_tags(audiotrack, *decorators, **kwargs):
        """

        :param audiotrack:
        :param decorators: 
        :return: 
        """
        in_logger = logging.getLogger(f"{__name__}.RippedDisc.alter_tags")
        offset, totaltracks = kwargs.get("offset", 0), kwargs.get("totaltracks", "0")
        for decorator in decorators:
            in_logger.debug('Tags altered according to decorating profile "%s".', decorator)

            # Change `album`.
            if decorator.lower() == "dftupdalbum":
                audiotrack = changealbum(audiotrack, "$albumsortyear.$albumsortcount - $album")
            elif decorator.lower() == "altupdalbum":
                audiotrack = changealbum(audiotrack, "$albumsortyear (Self Titled)")

            # Change `tracknumber`.
            elif decorator.lower() == "updtrack" and offset:
                audiotrack = changetrack(audiotrack, offset)

            # Change `totaltracks`.
            elif decorator.lower() == "updtotaltracks" and int(totaltracks):
                audiotrack = changetotaltracks(audiotrack, totaltracks)

            # Changes requested by `nugs` decorating profile.
            elif decorator.lower() == "nugs":
                if audiotrack.artist.lower() == "pearl jam":
                    audiotrack = changemediaprovider(changeencodedby(changealbum(audiotrack, "Live: $dashedbootlegalbumyear - $bootlegalbumcity")))
                elif audiotrack.artist.lower() == "bruce springsteen":
                    audiotrack = changemediaprovider(changealbumartist(changeencodedby(changealbum(audiotrack, "$bootlegalbumtour - $dottedbootlegalbumyear - [$bootlegalbumcity]")),
                                                                       "Bruce Springsteen And The E Street Band"))

            # Changes requested by `sbootlegs` decorating profile.
            elif decorator.lower() == "sbootlegs":
                audiotrack = changealbum(changealbumartist(audiotrack, "Bruce Springsteen And The E Street Band"), "$bootlegalbumtour - $dottedbootlegalbumyear - [$bootlegalbumcity]")

        return audiotrack

    def __enter__(self):

        # --> 1. Start logging.
        self._in_logger.info('START "%s".', os.path.basename(__file__))
        self._in_logger.info('"%s" used as ripping profile.', self._profile)
        for decorator in self._decorators:
            self._in_logger.info('"%s" used as decorating profile.', decorator)
        self._in_logger.info('"%s" used as encoder.', self._encoder)

        # --> 2. Log input file.
        self._in_logger.debug("Input file.")
        self._in_logger.debug('\t"%s"'.expandtabs(self._tabs), self._tags.name)

        # --> 3. Log input tags.
        self._tags.seek(0)
        self._intags, offset, totaltracks = self.get_tags(self._tags)
        keys, values = list(zip(*self._intags))
        self._in_logger.debug("Input tags.")
        for key, value in sorted(zip(*[list(shared.left_justify(keys)), values]), key=itemgetter(0)):
            self._in_logger.debug("\t%s: %s".expandtabs(self._tabs), key, value)
        offset = int(offset)

        # --> 4. Append encoder code.
        if "encoder" not in (key.lower() for key in keys):
            self._tags.seek(0, 2)
            self._tags.write(f"Encoder={self._encoder}")

        # --> 5. Create AudioCDTags instance.
        self._tags.seek(0)
        self._audiotracktags = PROFILES[self._profile].isinstancedfrom(self._tags)  # l'attribut "_audiotracktags" est une instance de type "AudioCDTags".

        # --> 6. Log instance attributes.
        keys, values = list(zip(*self._audiotracktags.interface.items()))
        self._in_logger.debug("Here are the key/value pairs stored by the `AudioCDTags` instance.")
        for key, value in zip(shared.left_justify(keys), values):
            self._in_logger.debug("\t%s: %s".expandtabs(5), key, value)

        # --> 7. Change instance attributes.
        self._audiotracktags = self.alter_tags(self._audiotracktags, *self._decorators, offset=offset, totaltracks=totaltracks)

        # --> 8. Return RippedDisc instance.
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        filter_keys = shared.getitem_(index=0)(shared.partial_(PROFILES[self._profile].exclusions)(contains_not_))
        outtags = dict(filter(filter_keys, sorted(self._audiotracktags.items())))

        # --> 1. Log output tags.
        self._in_logger.debug("Output tags.")
        keys, values = list(zip(*list(outtags.items())))
        for key, value in sorted(zip(*[list(shared.left_justify(keys)), values]), key=itemgetter(0)):
            self._in_logger.debug("\t%s: %s".expandtabs(self._tabs), key, value)

        # --> 2. Log output file.
        self._in_logger.debug("Output file.")
        self._in_logger.debug("\t%s".expandtabs(self._tabs), self._tags.name)

        # --> 3. Store tags.
        self._in_logger.debug("Write output tags to output file.")
        self._tags.seek(0)
        self._tags.truncate()
        self._tags.write(self._outputtags.render(tags=outtags))

        # --> 4. Stop logging.
        self._in_logger.info('END "%s".', os.path.basename(__file__))


# ================================
# Audio tags processing functions.
# ================================
def upsert_audiotags(profile: str, source: IO, encoder: str, *decorators: str, **kwargs: Any) -> int:
    """

    :param profile:
    :param source:
    :param encoder:
    :param decorators:
    :param kwargs:
    :return:
    """
    in_logger = logging.getLogger("{0}.upsert_audiotags".format(__name__))
    in_mapping = {"albums": albums, "bootlegs": bootlegs}
    stack = ExitStack()
    value = 0  # type: int
    in_logger.debug(profile)
    in_logger.debug(source.name)
    try:
        track = stack.enter_context(RippedDisc(profile, source, encoder, *decorators))
    except ValueError as err:
        in_logger.debug(err)
        value = 100
    else:
        with stack:

            for k, v in in_mapping.items():
                if kwargs.get(k, False):
                    dump_audiotags_tojson(track.audiotrack, v, database=kwargs.get("database", shared.DATABASE), jsonfile=kwargs.get("jsonfile"), encoding=kwargs.get("encoding", shared.UTF8))

            if all([kwargs.get("save"), kwargs.get("root")]):
                path = os.path.join(kwargs["root"], get_tagsfile(track.audiotrack))
                os.makedirs(path, exist_ok=True)

                # -----
                json_file = os.path.join(path, "input_tags.json")
                collection = list(load_sequence_fromjson(json_file))
                collection.append(dict(track.intags))
                dump_sequence_tojson(json_file, *collection)
                dump_sequence_toyaml(os.path.join(path, "input_tags.yml"), *collection)

                # -----
                json_file = os.path.join(path, "output_tags.json")
                collection = list(load_sequence_fromjson(json_file))
                collection.append(dict(**track.audiotrack))
                dump_sequence_tojson(json_file, *collection)
                dump_sequence_toyaml(os.path.join(path, "output_tags.yml"), *collection)

            if kwargs.get("sample", False):
                save_audiotags_sample(profile, **dict(track.intags))

    return value


def get_tagsfile(obj):
    """

    :param obj:
    :return:
    """
    in_logger = logging.getLogger("{0}.get_tagsfile".format(__name__))
    tags = {}

    # -----
    for key in ["albumsortcount",
                "foldersortcount",
                "artistsort_letter",
                "artistsort",
                "origyear",
                "album",
                "discnumber",
                "bootlegalbum_year",
                "bootlegalbum_month",
                "bootlegalbum_day",
                "bootlegalbum_city",
                "bootlegalbum_country"]:
        with suppress(AttributeError):
            tags[key] = getattr(obj, key)
    in_logger.debug(tags)

    # -----
    with open(os.path.join(shared.get_dirname(os.path.abspath(__file__), level=1), "Resources", "Templates.yml"), encoding=shared.UTF8) as stream:
        templates = yaml.load(stream)
    in_logger.debug(templates)

    # Load templates respective to "bootleg" value.
    template = templates.get(obj.bootleg, templates["N"])

    # Load templates respective to "artistsort" value.
    template = template.get(obj.artistsort, template["default"])

    # Load templates respective to "foldersortcount" value.
    template = template.get(obj.foldersortcount, templates["N"])

    # Load template respective to "totaldiscs" value.
    template = template.get(str(obj.totaldiscs), template["9"])

    # Return tags file dirname.
    return Template(template).substitute(tags)


def changealbum(obj, template):
    return ChangeAlbum(obj, template)


def changealbumartist(obj, albumartist):
    return ChangeAlbumArtist(obj, albumartist)


def changeencodedby(obj):
    return ChangeEncodedBy(obj)


def changemediaprovider(obj):
    return ChangeMediaProvider(obj)


def changetotaltracks(obj, totaltracks):
    return ChangeTotalTracks(obj, totaltracks)


def changetrack(obj, offset):
    return ChangeTrack(obj, offset)


def filcontents(fil):
    in_logger = logging.getLogger("{0}.filcontents".format(__name__))
    for line in fil:
        line = line.rstrip("\n")
        if line.startswith("#"):
            continue
        if not line:
            continue
        in_logger.debug(line)
        yield line


def album(track):
    try:
        totaldiscs = int(track.totaldiscs)
    except ValueError:
        return track.album
    if totaldiscs > 1:
        return "{o.album} ({o.discnumber}/{o.totaldiscs})".format(o=track)
    return track.album


def albums(track: DefaultAudioCDTags, *, fil: Optional[str] = None, encoding: str = shared.UTF8, db: str = shared.DATABASE) -> Iterable[Tuple[str, Tuple[Any, ...]]]:
    logger = logging.getLogger("{0}.albums".format(__name__))
    iterable = []  # type: List[Sequence[Union[int, str]]]
    genres = dict(get_genres(db))
    languages = dict(get_languages(db))
    if not fil:
        fil = os.path.join(os.path.expandvars("%TEMP%"), "tags.json")

    # Load existing sequences.
    with suppress(FileNotFoundError):
        with open(fil, encoding=encoding) as fr:
            iterable = json.load(fr)

    # Convert list(s) to tuple(s) for using `set` container.
    iterable = list(map(tuple, iterable))

    # Remove duplicate sequences.
    iterable.append(("defaultalbums",
                     db,
                     track.albumid,
                     int(track.discnumber),
                     int(track.tracknumber),
                     int(track.totaldiscs),
                     int(track.totaltracks),
                     int(track.origyear),
                     int(track.year),
                     track.album,
                     genres[track.genre],
                     track.label,
                     track.upc,
                     track.bonustrack,
                     track.livedisc,
                     track.livetrack,
                     track.bootleg,
                     track.deluxe,
                     languages[track.tracklanguage],
                     track.title,
                     track.artistsort,
                     track.artist,
                     track.incollection
                     ))
    iterable = list(set(iterable))
    for track in sorted(sorted(iterable, key=itemgetter(1)), key=itemgetter(0)):
        yield fil, track


def bootlegs(track: BootlegAudioCDTags, *, fil: Optional[str] = None, encoding: str = shared.UTF8, db: str = shared.DATABASE) -> Iterable[Tuple[str, Tuple[Any, ...]]]:
    logger = logging.getLogger("{0}.bootlegs".format(__name__))
    iterable = []  # type: List[Sequence[Union[int, str]]]
    genres = dict(get_genres(db))
    languages = dict(get_languages(db))
    countries = dict(get_countries(db))
    providers = dict(get_providers(db))
    if not fil:
        fil = os.path.join(os.path.expandvars("%TEMP%"), "tags.json")

    # Log `track` privates attributes.
    logger.debug('Here are the private key/value pairs stored into the `BootlegAudioCDTags` instance.')
    keys, values = list(zip(*track.interface.items()))
    for key, value in zip(shared.left_justify(keys), values):
        logger.debug("\t%s: %s".expandtabs(5), key, value)

    # Log `track` public attributes.
    logger.debug("Here are the public attributes stored into the `BootlegAudioCDTags` instance.")
    keys = shared.left_justify(["albumid",
                                "artistsort",
                                "artist",
                                "genre",
                                "bootleg",
                                "discnumber",
                                "livedisc",
                                "tracknumber",
                                "livetrack",
                                "bonustrack",
                                "totaldiscs",
                                "totaltracks",
                                "title",
                                "bootlegalbum_day",
                                "bootlegalbum_city",
                                "bootlegalbum_country",
                                "bootlegalbum_tour",
                                "bootlegtrack_day",
                                "bootlegtrack_city",
                                "bootlegtrack_country",
                                "bootlegtrack_tour",
                                "bootlegalbum_provider",
                                "bootlegdisc_reference",
                                "bootlegalbum_title"])
    values = [track.albumid,
              track.artistsort,
              track.artist,
              track.genre,
              track.bootleg,
              int(track.discnumber),
              track.livedisc,
              int(track.tracknumber),
              track.livetrack,
              track.bonustrack,
              int(track.totaldiscs),
              int(track.totaltracks),
              track.title,
              track.bootlegalbum_date,
              track.bootlegalbum_city,
              countries[track.bootlegalbum_country],
              track.bootlegalbum_tour,
              track.bootlegalbum_tour,
              track.bootlegtrack_date,
              track.bootlegtrack_city,
              countries[track.bootlegtrack_country],
              providers[track.bootlegalbum_provider],
              track.bootlegdisc_reference,
              track.bootlegalbum_title]
    for key, value in zip(keys, values):
        logger.debug("\t%s: %s".expandtabs(5), key, value)

    # Load existing sequences.
    with suppress(FileNotFoundError):
        with open(fil, encoding=encoding) as fr:
            iterable = json.load(fr)

    # Convert list(s) to tuple(s) for using `set` container.
    iterable = list(map(tuple, iterable))

    # Remove duplicate sequences.
    iterable.append(("bootlegalbums",
                     db,
                     track.albumid,
                     int(track.discnumber),
                     int(track.tracknumber),
                     int(track.totaldiscs),
                     int(track.totaltracks),
                     track.bonustrack,
                     track.livedisc,
                     track.livetrack,
                     track.bootleg,
                     genres[track.genre],
                     track.title,
                     languages[track.tracklanguage],
                     track.bootlegalbum_date,
                     track.bootlegalbum_city,
                     countries[track.bootlegalbum_country],
                     track.bootlegalbum_tour,
                     track.bootlegtrack_date,
                     track.bootlegtrack_city,
                     countries[track.bootlegtrack_country],
                     track.bootlegtrack_tour,
                     track.artistsort,
                     track.artist,
                     track.incollection,
                     providers[track.bootlegalbum_provider],
                     track.bootlegdisc_reference,
                     track.bootlegalbum_title
                     ))
    iterable = list(set(iterable))
    for track in sorted(sorted(sorted(iterable, key=itemgetter(2)), key=itemgetter(1)), key=itemgetter(0)):
        yield fil, track


def dump_audiotags_tojson(obj: AudioCDTags,
                          func: Callable[[AudioCDTags, Optional[str], str], Iterable[Tuple[str, Tuple[Any, ...]]]],
                          *,
                          database: str = shared.DATABASE,
                          jsonfile: Optional[str] = None,
                          encoding: str = shared.UTF8):
    """

    :param obj:
    :param func:
    :param database:
    :param jsonfile:
    :param encoding:
    :return:
    """
    for fil, sequences in groupby(func(obj, fil=jsonfile, db=database, encoding=encoding), key=itemgetter(0)):
        dump_sequence_tojson(fil, *list(sequence for _, sequence in sequences), encoding=encoding)


def save_audiotags_sample(profile: str, *, samples: str = None, **kwargs: Any) -> None:
    """

    :param profile:
    :param samples:
    :param kwargs:
    :return:
    """
    mapping = {}  # type: Dict[str, Mapping[str, Any]]
    if not samples:
        samples = os.path.join(shared.get_dirname(os.path.abspath(__file__), level=3), "Applications", "Tests", "Resources", "resource1.json")
    mapping = dict(load_mapping_fromjson(samples))
    if profile not in mapping:
        mapping[profile] = dict(**kwargs)
        dump_mapping_tojson(samples, **mapping)


# ================
# Other functions.
# ================
def contains_(a, b) -> bool:
    return shared.contains_(a, b)


def contains_not_(a, b) -> bool:
    return not shared.contains_(a, b)


def xreferences(track: Sequence[Union[bool, str]], *, fil: Optional[str] = None, encoding: str = shared.UTF8) -> None:
    _collection = []  # type: List[Sequence[Union[bool, str]]]
    if not fil:
        fil = os.path.join(os.path.expandvars("%TEMP%"), "xreferences.json")

    # Load existing references.
    with suppress(FileNotFoundError):
        with open(fil, encoding=encoding) as fr:
            _collection = json.load(fr)

    # Convert list(s) to tuple(s) for using `set` container.
    _collection = list(map(tuple, _collection))

    # Remove duplicate references.
    _collection.append(track)
    _collection = list(set(_collection))

    # Store references.
    with open(fil, mode=shared.WRITE, encoding=encoding) as fw:
        json.dump(sorted(sorted(sorted(_collection, key=itemgetter(6)), key=itemgetter(1)), key=itemgetter(0)), fw, indent=4, sort_keys=True, ensure_ascii=False)


def get_xreferences(track: Union[PureWindowsPath, str]) -> Tuple[bool, Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], bool, Optional[str], Optional[str]]]:
    """
    return artistid, albumid, artist_path, album_path, album, is_bootleg, track basename and track extension.

    :param track:
    :return:
    """
    mapping = {"1": False, "2": True}  # type: Mapping[str, bool]
    found = False  # type: bool
    group1 = (None, None)  # type: Tuple[Optional[str], ...]
    group2 = (None, None)  # type: Tuple[Optional[str], ...]
    group3 = None  # type: Optional[str]
    group4 = False  # type: bool
    group5 = (None, None)  # type: Tuple[Optional[str], ...]

    # Files with the following extensions are only matched.
    lookextensions = shared.CustomTemplate(shared.LOOKEXTENSIONS).substitute(extensions="|".join(shared.EXTENSIONS["music"]))

    # Artist group: name's first letter must match content of the 3rd capturing group.
    artist = shared.CustomTemplate(shared.ARTIST).substitute(letter="\\3")

    # File group: 4-character year must match content of the 6th capturing group.
    # File group: encoder 1-character code must match content of the 9th capturing group.
    # File group: both 2-character month and day are set to "00".
    file = shared.CustomTemplate(shared.FILE).substitute(year="\\6", month="00", day="00", encoder="\\9")

    # Create regular expression object.
    regex = re.compile(f"^{shared.LOOKDEFAULTALBUM}{lookextensions}(({shared.DRIVE}\\\\{shared.LETTER}\\\\{artist})\\\\{shared.FOLDER}{shared.DEFAULTALBUM})\\\\{shared.DISC}{shared.COMPRESSION}\\\\{file}$")

    # Extract capturing groups content if match is positive.
    match = regex.match(os.fspath(track))
    if match:
        found = True
        group1 = tuple(match.group(4, 11))
        group2 = (match.group(2),) + (match.group(1),)
        group3 = match.group(8)
        group4 = mapping.get(match.group(12), False)
        group5 = tuple(match.group(10, 13))
    return found, group1 + group2 + (group3,) + (group4,) + group5


def getmetadata(audiofil: str) -> Any:
    """
    Get metada from an audio file.
    FLAC, Monkey's Audio or MP3 (with ID3 tags) are only processed.
    :param audiofil: characters string representing an audio file.
    :return: 4-attribute named tuple:
                - "file". Both dirname and basename of the audio file.
                - "found". Boolean value depending on whether metadata have been found or not.
                - "tags". Dictionary enumerating each metadata found.
                - "object". Audio file object.
    """
    tags, Result = {}, NamedTuple("Result", [("file", str), ("found", bool), ("tags", Mapping[str, Any]), ("object", Optional[Any])])
    logger = logging.getLogger("{0}.getmetadata".format(__name__))
    logger.debug(audiofil)

    # Guess "audiofil" type.
    try:
        audioobj = File(audiofil, easy=True)
    except (MutagenError, mutagen.flac.FLACNoHeaderError, TypeError, ZeroDivisionError) as err:
        logger.exception(err)
        return Result._make((audiofil, False, {}, None))

    # Is "audiofil" a valid audio file?
    if not audioobj:
        return Result._make((audiofil, False, {}, None))

    # Is "audiofil" type FLAC, Monkey's Audio or MP3 (with ID3 tags)?
    if any([isinstance(audioobj, mutagen.flac.FLAC), isinstance(audioobj, mutagen.monkeysaudio.MonkeysAudio), isinstance(audioobj, mutagen.mp3.MP3)]):

        # --> FLAC.
        try:
            assert isinstance(audioobj, mutagen.flac.FLAC) is True
        except AssertionError:
            pass
        else:
            tags = dict((k.lower(), v) for k, v in audioobj.tags)

        # --> Monkey's audio.
        try:
            assert isinstance(audioobj, mutagen.monkeysaudio.MonkeysAudio) is True
        except AssertionError:
            pass
        else:
            tags = {k.lower(): str(v) for k, v in audioobj.tags.items() if isinstance(v, APETextValue)}

        # --> MP3 (with ID3 tags).
        try:
            assert isinstance(audioobj, mutagen.mp3.MP3) is True
        except AssertionError:
            pass
        else:

            # Map user-defined text frame key.
            for key in ["incollection", "titlelanguage", "totaltracks", "totaldiscs", "upc", "encoder"]:
                description, cycle = key, 0
                while True:
                    EasyID3.RegisterTXXXKey(key, description)
                    if key.lower() in (item.lower() for item in audioobj.tags):
                        break
                    cycle += 1
                    if cycle > 1:
                        break
                    description = key.upper()

            # Map normalized text frame key.
            for key, description in [("artistsort", "TSOP"), ("albumartistsort", "TSO2"), ("albumsort", "TSOA"), ("mediatype", "TMED"), ("encodingtime", "TDEN"), ("label", "TPUB")]:
                EasyID3.RegisterTextKey(key, description)

            # Aggregate ID3 frames.
            tags = {k.lower(): v[0] for k, v in audioobj.tags.items()}

    # Have "audiofil" metadata been retrieved?
    if not tags:
        return Result._make((audiofil, False, {}, None))
    return Result._make((audiofil, True, tags, audioobj))


def get_audiofiles(folder):
    """
    Return a generator object yielding both FLAC and Monkey's Audio files stored in "folder" having extension enumerated in "extensions".
    :param folder: folder to walk through.
    :return: generator object.
    """
    for audiofil, audioobj, tags in ((result.file, result.object, result.tags) for result in map(getmetadata, shared.find_files(folder, excluded=exclude_allbutlosslessaudiofiles)) if result.found):
        yield audiofil, audioobj, tags


def upload_audiofiles(server, user, password, *files, test=False):
    """
    Upload audio file(s) to a remote directory on the NAS server.
    :param server: IP address of the NAS server.
    :param user: user for creating connection to the server.
    :param password: password for creating connection to the server.
    :param files: list of audio files.
    :param test:
    :return: None.
    """
    keys = shared.left_justify(["Source file to upload", "Source file name", "Target directory", "Artistsort", "Albumsort", "Album"])
    uploaded, selectors = [], []

    # --> Logging.
    logger = logging.getLogger("{0}.upload_audiofile".format(__name__))

    # --> Check existing files.
    # if not any(map(os.path.exists, files)):
    #     logger.debug("No eligible file found.")
    #     return uploaded

    # --> Initializations.
    refdirectory = "/music"
    collection = [(item.file, item.tags) for item in [getmetadata(file) for file in compress(files, map(os.path.exists, files))] if item.found]
    for file, tags in collection:
        if all(["artistsort" in tags, "albumsort" in tags, "album" in tags]):
            selectors.append(True)
        else:
            selectors.append(False)
    for file, tags in compress(collection, [not selector for selector in selectors]):
        logger.debug("%s is rejected.", file)

    # --> Copy local audio collection to remote directory.
    stack1 = ExitStack()
    try:
        ftp = stack1.enter_context(ftputil.FTPHost(server, user, password))
    except ftputil.error.FTPOSError as err:
        logger.exception(err)
    else:
        with stack1:
            ftp.chdir(refdirectory)
            for file, tags in compress(collection, selectors):
                wdir = ftp.path.join(refdirectory, "/".join(os.path.splitdrive(os.path.dirname(file))[1][1:].split("\\")))
                values = [file, os.path.basename(file), wdir, tags["artistsort"], tags["albumsort"], tags["album"]]
                for key, value in zip(keys, values):
                    logger.debug("%s: %s", key, value)
                if not test:
                    stack2 = ExitStack()
                    while True:
                        try:
                            stack2.enter_context(shared.AlternativeChangeRemoteCurrentDirectory(ftp, wdir))
                        except ftputil.error.PermanentError:
                            ftp.makedirs(wdir)
                        else:
                            break
                    with stack2:
                        ftp.upload(file, os.path.basename(file))
                        uploaded.append(file)
                    logger.debug("Restored current directory\t: {0}".format(ftp.getcwd()).expandtabs(3))
    for file in uploaded:
        yield file


def load_mapping_fromjson(jsonfile: str, encoding: str = shared.UTF8) -> Iterable[Any]:
    """

    :param jsonfile:
    :param encoding:
    :return:
    """
    mapping = {}  # type: Dict[str, Any]
    with suppress(FileNotFoundError):
        with open(jsonfile, encoding=encoding) as fr:
            mapping = json.load(fr)
    for item in mapping.items():
        yield item


def load_sequence_fromjson(jsonfile: str, encoding: str = shared.UTF8) -> Iterable[Any]:
    """

    :param jsonfile:
    :param encoding:
    :return:
    """
    sequence = []  # type: List[Any]
    with suppress(FileNotFoundError):
        with open(jsonfile, encoding=encoding) as fr:
            sequence = json.load(fr)
    for item in sequence:
        yield item


def dump_mapping_tojson(jsonfile: str, encoding: str = shared.UTF8, **collection: Any) -> None:
    """

    :param jsonfile:
    :param encoding:
    :param collection:
    :return:
    """
    _dump_tojson(jsonfile, collection, encoding)


def dump_sequence_tojson(jsonfile: str, *collection: Any, encoding: str = shared.UTF8) -> None:
    """

    :param jsonfile:
    :param collection:
    :param encoding:
    :return:
    """
    _dump_tojson(jsonfile, collection, encoding)


def dump_sequence_toyaml(yamlfile: str, *collection: Any, encoding: str = shared.UTF8) -> None:
    """

    :param yamlfile:
    :param collection:
    :param encoding:
    :return:
    """
    _dump_toyaml(yamlfile, collection, encoding)


# ===================
# Private interfaces.
# ===================
def _dump_tojson(jsonfile: str, collection: Any, encoding: str) -> None:
    with open(jsonfile, mode="w", encoding=encoding) as stream:
        json.dump(collection, stream, indent=4, ensure_ascii=False, sort_keys=True)


def _dump_toyaml(yamlfile: str, collection: Any, encoding: str) -> None:
    with open(yamlfile, mode="w", encoding=encoding) as stream:
        yaml.dump(collection, stream, default_flow_style=False, indent=2)


# ================
# Initializations.
# ================
Profile = namedtuple("profile", "exclusions isinstancedfrom")

# ==========
# Constants.
# ==========
DFTPATTERN = r"^(?:\ufeff)?(?!#)(?:z_)?([^=]+)=(?!\s)(.+)$"
GENRES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources", "Genres.json")
LANGUAGES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources", "Languages.json")
ENCODERS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources", "Encoders.json")
ENC_KEYS = ["name",
            "code",
            "folder",
            "extension"]
PROFILES = {"default": Profile(["albumsortcount",
                                "foldersortcount",
                                "albumsortyear",
                                "bonustrack",
                                "bootleg",
                                "deluxe",
                                "livedisc",
                                "livetrack",
                                "tracklanguage"], DefaultAudioCDTags.fromfile),
            "bootleg": Profile(["albumsortcount",
                                "albumsortyear",
                                "bonustrack",
                                "bootleg",
                                "bootlegalbumcity",
                                "bootlegalbumcountry",
                                "bootlegalbumday",
                                "bootlegalbumprovider",
                                "bootlegalbumtour",
                                "bootlegalbumyear",
                                "bootlegtrackday",
                                "dashedbootlegalbumyear",
                                "dottedbootlegalbumyear",
                                "livedisc",
                                "livetrack",
                                "tracklanguage"], BootlegAudioCDTags.fromfile)
            }
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources", "Mapping.json"), encoding="UTF_8") as fp:
    MAPPING = json.load(fp)
