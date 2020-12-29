# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import csv
import json
import logging
import os
import re
from collections.abc import MutableMapping
from contextlib import ContextDecorator, ExitStack, suppress
from datetime import datetime
from functools import partial
from itertools import chain, filterfalse, groupby, islice
from operator import contains, is_, itemgetter
from pathlib import Path
from string import Template
from typing import Any, Dict, Iterable, List, Mapping, NamedTuple, Optional, Sequence, Tuple

import yaml
from dateutil import parser

from .. import callables
from .. import decorators
from .. import shared
from ..Tables.Albums.shared import get_countries, get_genres, get_languages, get_providers

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent

# ====================
# Regular expressions.
# ====================
REGEX = re.compile(r"^(?:z_)?(.+)$", re.IGNORECASE)


# ========
# Classes.
# ========
class CustomDialect(csv.Dialect):
    delimiter = "="
    escapechar = "`"
    doublequote = False
    quoting = csv.QUOTE_NONE
    lineterminator = "\r\n"


class TrackTags(MutableMapping):
    """
    Master class dealing with the audio tags produced by the ripping application.
    Must not be instantiated directly!
    Used to define the interfaces required to interact with audio tags.
    """
    __logger = logging.getLogger("{0}.TrackTags".format(__name__))
    _track_pattern = re.compile(r"^(\d{1,2})/(\d{1,2})")
    _Encoder = NamedTuple("Encoder", [("name", str),
                                      ("code", str),
                                      ("folder", str),
                                      ("extension", str)])

    def __init__(self):
        self._bootlegalbum_date = None
        self._bootlegalbum_isodate = None
        self._encoder = None
        self._otags = {}
        self._sequence = None
        self._step = 0
        self._totaltracks_key = None
        self._totaldiscs_key = None

    def get(self, key):
        return self._otags.get(key)

    def items(self):
        return self._otags.items()

    def keys(self):
        return self._otags.keys()

    def values(self):
        return self._otags.values()

    def __getitem__(self, item):
        return self._otags[item]

    def __setitem__(self, key, value):
        self._otags[key] = value

    def __delitem__(self, key):
        del self._otags[key]

    def __len__(self):
        return len(self._otags)

    def __iter__(self):
        for key, value in self._otags.items():
            yield key, value

    def __repr__(self):
        if not self:
            return "%s()" % (self.__class__.__name__,)
        return "%s(%r)" % (self.__class__.__name__, sorted(self, key=itemgetter(0)))

    def __str__(self):
        return f'{self._otags["artistsort"][0]}.{self._otags["artistsort"]}.{self._otags["albumsort"]}.{self._otags["titlesort"]} - {self._otags["album"]} - track {self._otags["track"]}'

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
    def bootlegdisc(self):
        return self._otags.get("bootleg", "N")

    @property
    def bootlegalbum_city(self):
        return self._otags.get("bootlegalbumcity")

    @property
    def bootlegalbum_country(self):
        return self._otags.get("bootlegalbumcountry")

    @property
    def bootlegalbum_date(self):
        return self._bootlegalbum_isodate

    @property
    def bootlegalbum_day(self):
        day = None
        with suppress(TypeError):
            day = self._bootlegalbum_isodate[-2:]
        return day

    @property
    def bootlegalbum_month(self):
        month = None
        with suppress(TypeError):
            month = self._bootlegalbum_isodate[5:-3]
        return month

    @property
    def bootlegalbum_publisher(self):
        return self._otags.get("bootlegpublisher")

    @property
    def bootlegalbum_title(self):
        return self._otags.get("bootlegtitle")

    @property
    def bootlegalbum_tour(self):
        return self._otags.get("bootlegalbumtour")

    @property
    def bootlegalbum_year(self):
        year = None
        with suppress(TypeError):
            year = self._bootlegalbum_isodate[:4]
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
        return self._otags.get("bootlegtrackyear")

    @property
    def bootlegtrack_day(self):
        trackdate = self._otags.get("bootlegtrackyear")
        if trackdate is not None:
            return trackdate[-2:]
        return None

    @property
    def bootlegtrack_month(self):
        trackdate = self._otags.get("bootlegtrackyear")
        if trackdate is not None:
            return trackdate[5:-3]
        return None

    @property
    def bootlegtrack_tour(self):
        return self._otags.get("bootlegtracktour")

    @property
    def bootlegtrack_year(self):
        trackdate = self._otags.get("bootlegtrackyear")
        if trackdate is not None:
            return trackdate[:4]
        return None

    @property
    def database(self):
        return shared.ToBoolean(self._otags.get("database", "Y")).boolean_value

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
    def label(self):
        return self._otags["label"]

    @property
    def livedisc(self):
        return self._otags.get("livedisc", "N")

    @property
    def livetrack(self):
        return self._otags.get("livetrack", "N")

    @property
    def bootlegalbum_provider(self):
        return self._otags.get("mediaprovider")

    @property
    def origtrack(self):
        return self._otags.get("origtrack", self._otags["track"])

    @origtrack.deleter
    def origtrack(self):
        del self._otags["origtrack"]

    @property
    def origyear(self):
        return self._otags.get("origyear")

    @property
    def repository(self):
        try:
            return int(self._otags.get("lossless"))
        except TypeError:
            return None

    @property
    def sample(self):
        return shared.ToBoolean(self._otags.get("sample", "Y")).boolean_value

    @property
    def sequence(self):
        return self._sequence

    @property
    def step(self):
        return self._step

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

    @staticmethod
    def deserialize(fil, enc=shared.UTF8):
        with open(fil, encoding=enc) as fr:
            for item in json.load(fr):
                yield item

    @staticmethod
    def get_argument_tags(**kwargs):
        for item in chain.from_iterable(islice(zip(*kwargs.items()), 1)):
            yield item

    @staticmethod
    def get_mandatory_tags(**kwargs):
        for item in chain.from_iterable(islice(zip(*filter(decorators.itemgetter_(1)(partial(is_, True)), kwargs.items())), 1)):
            yield item


class CommonTrackTags(TrackTags):
    """
    Main class dealing with the audio tags produced by the ripping application.
    Must not be instantiated directly!
    Used to introduced the tags shared by every ripped audio CD.
    """
    __logger = logging.getLogger("{0}.CommonTrackTags".format(__name__))
    __tags = {"albumartist": False,
              "albumartistsort": False,
              "artist": True,
              "artistsort": True,
              "bootleg": True,
              "boxset": False,
              "database": False,
              "disc": True,
              "encoder": True,
              "genre": False,
              "incollection": True,
              "livedisc": True,
              "livetrack": True,
              "lossless": False,
              "offset": False,
              "profile": False,
              "rating": False,
              "sample": False,
              "source": False,
              "style": False,
              "title": False,
              "totaltracks": False,
              "track": True,
              "tracklanguage": False,
              "_albumart_1_front album cover": False}

    def __init__(self, sequence, **kwargs):
        super(CommonTrackTags, self).__init__()
        genres = kwargs.get("genres")
        languages = kwargs.get("languages")
        self._encoders = kwargs.get("encoders")
        kwargs = dict(filterfalse(decorators.itemgetter_(0)(partial(contains, ["encoders", "genres", "languages"])), kwargs.items()))

        # ----- Check mandatory input tags.
        mandatory = set(self.get_mandatory_tags(**self.__tags))
        arguments = set(self.get_argument_tags(**kwargs))
        if not mandatory < arguments:
            self.__logger.info("The following tag hasn\'t been found:")
            for item in mandatory.difference(arguments):
                self.__logger.info(f"\t{item}.".expandtabs(4))
            raise ValueError("At least one missing mandatory audio tag has been found! Please check log.")
        checked, exception = self.__validatetags(**kwargs)
        if not checked:
            raise ValueError(exception)

        # ----- _Encoder dependent attributes.
        self._totaltracks_key = MAPPING.get(kwargs["encoder"], MAPPING["default"])["totaltracks"]
        self._totaldiscs_key = MAPPING.get(kwargs["encoder"], MAPPING["default"])["totaldiscs"]

        # ----- Attributes taken from the input tags.
        filter_keys = decorators.itemgetter_(0)(partial(contains, sorted(self.__tags)))
        self._otags = dict(filter(filter_keys, sorted(kwargs.items())))

        # ----- Step.
        #       Step 1 : preserve both "albumsortcount" and "foldersortcount" into output tags for correct file naming.
        #       Step 2 : remove both "albumsortcount" and "foldersortcount" from output tags.
        self._sequence = sequence
        sequences = shared.TEMP / "sequences.json"
        self._step, tracks = 2, []
        if sequences.exists():
            tracks = list(self.deserialize(str(sequences)))
        self.__logger.debug(tracks)
        self.__logger.debug("Track is %s.", f'{kwargs["track"]}{sequence}')
        if f'{kwargs["track"]}{sequence}' not in tracks:
            self._step = 1
            tracks.append(f'{kwargs["track"]}{sequence}')
            self.__logger.debug("%s inserted into list.", f'{kwargs["track"]}{sequence}')
            with open(sequences, mode="w", encoding=shared.UTF8) as stream:
                json.dump(tracks, stream)
        self.__logger.debug("Step %s for track %s.", self._step, f'{kwargs["track"]}{sequence}')

        # ----- Set encoding timestamp.
        now = shared.UTC.localize(datetime.utcnow()).astimezone(shared.LOCAL)
        now_readable = shared.format_date(shared.UTC.localize(datetime.utcnow()).astimezone(shared.LOCAL))

        # ----- Set encodedby.
        self.__logger.debug("Set encodedby.")
        self._otags["encodedby"] = f"{shared.get_rippingapplication()[0]} on {now_readable}"

        # ----- Set taggingtime.
        self.__logger.debug("Set taggingtime.")
        self._otags["taggingtime"] = now_readable

        # ----- Set encodingtime.
        self.__logger.debug("Set encodingtime.")
        self._otags["encodingtime"] = int(now.timestamp())

        # ----- Set encodingyear.
        self.__logger.debug("Set encodingyear.")
        self._otags["encodingyear"] = now.strftime("%Y")

        # ----- Set encoder attributes.
        self.__logger.debug("Set encoder attributes.")
        encoder_attributes = self._encoders.get_encoder(kwargs["encoder"])
        self._encoder = self._Encoder(kwargs["encoder"], encoder_attributes["code"], encoder_attributes["folder"], encoder_attributes["extension"])
        self.__logger.debug("Used encoder.")
        self.__logger.debug("Name\t\t: %s".expandtabs(3), kwargs["encoder"])
        self.__logger.debug("Code\t\t: %s".expandtabs(3), self._encoder.code)
        self.__logger.debug("Folder\t: %s".expandtabs(3), self._encoder.folder)
        self.__logger.debug("Extension: %s".expandtabs(3), self._encoder.extension)
        self._otags["encoder"] = kwargs["encoder"]
        self._otags["code"] = encoder_attributes["code"]
        self._otags["folder"] = encoder_attributes["folder"]

        # ----- Set album total tracks.
        self.__logger.debug("Set albumtotaltracks.")
        self._otags["albumtotaltracks"] = self._otags.get("totaltracks", "0")

        # ----- Set both track and disc total tracks.
        self.__logger.debug("Set track.")
        self._otags["track"], self._otags[self._totaltracks_key] = split_(1, 2)(self._track_pattern.match)(kwargs["track"])
        self._otags["origtrack"], _ = split_(1, 2)(self._track_pattern.match)(kwargs["track"])

        # ----- Set both disc and album total discs.
        self.__logger.debug("Set disc.")
        self._otags["disc"], self._otags[self._totaldiscs_key] = split_(1, 2)(self._track_pattern.match)(kwargs["disc"])

        # ----- Update genre.
        if genres is not None:
            self.__logger.debug("Update genre.")
            self._otags["genre"] = genres.get_genre(kwargs["artistsort"], fallback=kwargs.get("genre", "Rock"))

        # ----- Update titlelanguage.
        if languages is not None:
            self.__logger.debug("Update titlelanguage.")
            self._otags["titlelanguage"] = languages.get_language(kwargs["artistsort"], fallback=kwargs.get("tracklanguage", "English"))

        # ----- Update title.
        self.__logger.debug("Update title.")
        self._otags["title"] = shared.TitleCaseConverter().convert(self._otags["title"])

    def __validatetags(self, **kwargs):
        if not self._track_pattern.match(kwargs["track"]):
            return False, "track doesn\'t respect the expected pattern."
        if not self._track_pattern.match(kwargs["disc"]):
            return False, "disc doesn\'t respect the expected pattern."
        if kwargs["encoder"] not in self._encoders.get_encoders():
            return False, f'\"{kwargs["encoder"]}\" as encoder isn\'t recognized.'
        return True, None

    def _setbootlegtags(self, logger):

        # -----
        REX1 = re.compile(r"\W+")
        REX2 = re.compile(r", ([A-Z][a-z]+)$")
        DFTCOUNTRY = "United States"

        # ----- Set bootlegalbum ISO date.
        bootleg_date = parser.parse(REX1.sub("-", self._otags["bootlegalbumyear"]), default=datetime.utcnow())
        self._bootlegalbum_isodate = bootleg_date.date().isoformat()
        self._bootlegalbum_date = bootleg_date.date().isoformat().replace("-", "")
        self._otags["dashed_bootlegalbum_date"] = bootleg_date.date().isoformat()
        self._otags["dotted_bootlegalbum_date"] = bootleg_date.date().isoformat().replace("-", ".")

        # ----- Set bootlegalbumcountry.
        logger.debug("Set bootlegalbumcountry.")
        self._otags["bootlegalbumcountry"] = DFTCOUNTRY
        match = REX2.search(self._otags["bootlegalbumcity"])
        if match:
            self._otags["bootlegalbumcountry"] = match.group(1)
        logger.debug(self._otags["bootlegalbumcountry"])

        # ----- Set bootlegtrackyear.
        logger.debug("Set bootlegtrackyear.")
        bootleg_date = parser.parse(REX1.sub("-", self._otags.get("bootlegtrackyear", self._otags["bootlegalbumyear"])), default=datetime.utcnow())
        self._otags["bootlegtrackyear"] = bootleg_date.date().isoformat()
        logger.debug(self._otags["bootlegtrackyear"])

        # ----- Set bootlegtrackcity.
        logger.debug("Set bootlegtrackcity.")
        bootlegtrackcity = self._otags.get("bootlegtrackcity", self._otags["bootlegalbumcity"])
        self._otags["bootlegtrackcity"] = bootlegtrackcity
        logger.debug(self._otags["bootlegtrackcity"])

        # ----- Set bootlegtrackcountry.
        logger.debug("Set bootlegtrackcountry.")
        self._otags["bootlegtrackcountry"] = DFTCOUNTRY
        match = REX2.search(bootlegtrackcity)
        if match:
            self._otags["bootlegtrackcountry"] = match.group(1)
        logger.debug(self._otags["bootlegtrackcountry"])

        # ----- Set bootlegtracktour.
        logger.debug("Set bootlegtracktour.")
        self._otags["bootlegtracktour"] = self._otags.get("bootlegtracktour", self._otags["bootlegalbumtour"])
        logger.debug(self._otags["bootlegtracktour"])

    @classmethod
    def fromfile(cls, fil, sequence, genres, languages, encoders):
        tags = csv.reader(fil, dialect=CustomDialect())  # type: Any
        tags = filterfalse(decorators.itemgetter_(0)(partial(shared.eq_string_, "encoder+")), tags)
        tags = [(decorators.rstrip_(decorators.lower_(callables.group_(1)(REGEX.match)))(key), value) for key, value in tags]
        return cls(sequence, genres=genres, languages=languages, encoders=encoders, **dict(sorted(tags, key=itemgetter(0))))


class DefaultTrackTags(CommonTrackTags):
    """
    Main class dealing with the audio tags set from a default audio CD.
    Is assumed as a default audio CD any official release (studio or live) enumerated into an artist's discography.
    """
    __logger = logging.getLogger("{0}.DefaultTrackTags".format(__name__))
    __tags = {"album": True,
              "albumsortcount": True,
              "foldersortcount": False,
              "bonustrack": False,
              "deluxe": False,
              "label": True,
              "origyear": False,
              "upc": True,
              "year": True}

    def __init__(self, sequence, **kwargs):
        super(DefaultTrackTags, self).__init__(sequence, **kwargs)
        kwargs = dict(filterfalse(decorators.itemgetter_(0)(partial(contains, ["encoders", "genres", "languages"])), kwargs.items()))

        # ----- Check mandatory input tags.
        mandatory = set(self.get_mandatory_tags(**self.__tags))
        arguments = set(self.get_argument_tags(**kwargs))
        if not mandatory < arguments:
            self.__logger.info("The following tag hasn\'t been found:")
            for item in mandatory.difference(arguments):
                self.__logger.info(f"\t{item}.".expandtabs(4))
            raise ValueError("At least one missing audio tags has been found! Please check log.")

        # ----- Update tags.
        filter_keys = decorators.itemgetter_(0)(partial(contains, sorted(self.__tags)))
        self._otags.update(dict(filter(filter_keys, sorted(kwargs.items()))))

        # ----- Set origyear.
        self.__logger.debug("Set origyear.")
        self._otags["origyear"] = self._otags.get("origyear", self._otags["year"])

        # ----- Set albumsort.
        self.__logger.debug("Set albumsort.")
        self._otags["albumsort"] = "1.{year}0000.{uid}.{enc}".format(year=self._otags["origyear"], uid=self._otags["albumsortcount"], enc=self._encoder.code)
        self._otags["albumsortyear"] = self._otags["albumsort"][2:6]

        # ----- Set titlesort.
        self.__logger.debug("Set titlesort.")
        self._otags["titlesort"] = "D{disc}.T{track}.{bonustrack}{livetrack}{bootleg}".format(disc=self._otags["disc"],
                                                                                              track=self._otags["track"].zfill(2),
                                                                                              bonustrack=self._otags.get("bonustrack", "N"),
                                                                                              livetrack=self._otags["livetrack"],
                                                                                              bootleg=self._otags["bootleg"])

        # ----- Update album.
        self.__logger.debug("Update album.")
        self._otags["album"] = shared.TitleCaseConverter().convert(self._otags["album"])

        # ----- Log new tags.
        self.__logger.debug("Build tags.")
        self.__logger.debug("\talbum    : %s".expandtabs(4), self._otags["album"])
        self.__logger.debug("\talbumsort: %s".expandtabs(4), self._otags["albumsort"])
        self.__logger.debug("\ttitlesort: %s".expandtabs(4), self._otags["titlesort"])
        self.__logger.debug("\torigyear : %s".expandtabs(4), self._otags["origyear"])

        # ----- Filter tags without any value.
        self._otags = dict(filterfalse(decorators.none_(itemgetter(1)), self._otags.items()))


class LiveTrackTags(DefaultTrackTags):
    """
    Main class dealing with the audio tags set from a default live audio CD.
    Is assumed as a default live audio CD any official live release enumerated into an artist's discography.
    Allow to set up specific tags about live performance: tour, date and city.
    Pearl Jam 2000 bootleg series audio CDs are targeted by this class as releases were legally available
    through both records shops and e-shops.
    """
    __logger = logging.getLogger("{0}.LiveTrackTags".format(__name__))
    __tags = {"bootlegalbumcity": True,
              "bootlegalbumtour": True,
              "bootlegalbumyear": True}

    def __init__(self, sequence, **kwargs):
        super(LiveTrackTags, self).__init__(sequence, **kwargs)
        kwargs = dict(filterfalse(decorators.itemgetter_(0)(partial(contains, ["encoders", "genres", "languages"])), kwargs.items()))

        # ----- Check mandatory input tags.
        mandatory = set(self.get_mandatory_tags(**self.__tags))
        arguments = set(self.get_argument_tags(**kwargs))
        if not mandatory < arguments:
            self.__logger.info("The following tag hasn\'t been found:")
            for item in mandatory.difference(arguments):
                self.__logger.info(f"\t{item}.".expandtabs(4))
            raise ValueError("At least one missing audio tags has been found! Please check log.")

        # ----- Update tags.
        filter_keys = decorators.itemgetter_(0)(partial(contains, sorted(self.__tags)))
        self._otags.update(dict(filter(filter_keys, sorted(kwargs.items()))))

        # ----- Set additional bootleg tags.
        self._setbootlegtags(self.__logger)

        # ----- Set albumsort.
        self.__logger.debug("Set albumsort.")
        self._otags["albumsort"] = "2.{date}.{uid}.{enc}".format(date=self._bootlegalbum_date,
                                                                 uid=self._otags["albumsortcount"],
                                                                 enc=self._encoder.code)
        self.__logger.debug(self._otags["albumsort"])

        # ----- Set titlesort.
        self.__logger.debug("Set titlesort.")
        self._otags["titlesort"] = "D{disc}.T{track}.{bonustrack}{livetrack}{bootleg}".format(disc=self._otags["disc"],
                                                                                              track=self._otags["track"].zfill(2),
                                                                                              bonustrack=self._otags["bonustrack"],
                                                                                              livetrack=self._otags["livetrack"],
                                                                                              bootleg=self._otags["bootleg"])

        # ----- Filter tags without any value.
        self._otags = dict(filterfalse(decorators.none_(itemgetter(1)), self._otags.items()))


class LiveBootlegTrackTags(CommonTrackTags):
    """
    Main class dealing with the audio tags set from a bootleg audio CD.
    Is assumed as a bootleg audio CD any unofficial live release not being part of an artist's discography.
    A release can be provided by a legal provider (such as nugs.net) or by an non-legal provider (such as The Godfatherecords).
    Allow to set up specific tags about live performance: tour, date and city.
    """
    __logger = logging.getLogger("{0}.LiveBootlegTrackTags".format(__name__))
    __tags = {"bootlegtrackcity": False,
              "bootlegtracktour": False,
              "bootlegtrackyear": False,
              "bootlegalbumcity": True,
              "bootlegalbumtour": True,
              "bootlegalbumyear": True,
              "bootlegdiscreference": False,
              "bootlegprovider": False,
              "bootlegpublisher": False,
              "bootlegtitle": False,
              "albumsortcount": True,
              "bonustrack": True}

    def __init__(self, sequence, **kwargs):
        super(LiveBootlegTrackTags, self).__init__(sequence, **kwargs)
        kwargs = dict(filterfalse(decorators.itemgetter_(0)(partial(contains, ["encoders", "genres", "languages"])), kwargs.items()))

        # ----- Check mandatory input tags.
        mandatory = set(self.get_mandatory_tags(**self.__tags))
        arguments = set(self.get_argument_tags(**kwargs))
        if not mandatory < arguments:
            self.__logger.info("The following tag hasn\'t been found:")
            for item in mandatory.difference(arguments):
                self.__logger.info(f"\t{item}.".expandtabs(4))
            raise ValueError("At least one missing audio tags has been found! Please check log.")

        # ----- Update tags.
        filter_keys = decorators.itemgetter_(0)(partial(contains, sorted(self.__tags)))
        self._otags.update(dict(filter(filter_keys, sorted(kwargs.items()))))

        # ----- Set additional bootleg tags.
        self._setbootlegtags(self.__logger)

        # ----- Set year.
        self.__logger.debug("Set year.")
        self._otags["year"] = self._otags["bootlegalbumyear"][:4]

        # ----- Set origyear.
        self.__logger.debug("Set origyear.")
        self._otags["origyear"] = self._otags["bootlegalbumyear"][:4]

        # ----- Set albumsort.
        self.__logger.debug("Set albumsort.")
        self._otags["albumsort"] = "2.{date}.{uid}.{enc}".format(date=self._bootlegalbum_date,
                                                                 uid=self._otags["albumsortcount"],
                                                                 enc=self._encoder.code)
        self.__logger.debug(self._otags["albumsort"])

        # ----- Set titlesort.
        self.__logger.debug("Set titlesort.")
        self._otags["titlesort"] = "D{disc}.T{track}.{bonustrack}{livetrack}{bootleg}".format(disc=self._otags["disc"],
                                                                                              track=self._otags["track"].zfill(2),
                                                                                              bonustrack=self._otags["bonustrack"],
                                                                                              livetrack=self._otags["livetrack"],
                                                                                              bootleg=self._otags["bootleg"])

        # ----- Set extra tags.
        self._otags["mediareference"] = self._otags.get("bootlegdiscreference")
        self._otags["mediaprovider"] = self._otags.get("bootlegprovider")
        self._otags["mediapublisher"] = self._otags.get("bootlegpublisher")
        self._otags["mediatitle"] = self._otags.get("bootlegtitle")

        # ----- Filter tags without any value.
        self._otags = dict(filterfalse(decorators.none_(itemgetter(1)), self._otags.items()))


class AudioGenres(object):
    _genres = {}  # type: Mapping[str, str]

    def get_genre(self, artistsort, *, fallback="Rock"):
        return self._genres.get(artistsort, fallback)


class AudioLanguages(object):
    _languages = {}  # type: Mapping[str, str]

    def get_language(self, artistsort, *, fallback="English"):
        return self._languages.get(artistsort, fallback)


class Audio_Encoders(object):
    _encoders = {"FDK v2.0.0": {"code": "02", "extension": "m4a", "folder": "0.MPEG-4 AAC"},
                 "FLAC 1.3.3 beta": {"code": "13", "extension": "flac", "folder": "1.Free Lossless Audio Codec"},
                 "Lame 3.100.0": {"code": "01", "extension": "mp3", "folder": "0.MPEG 1 Layer III"},
                 "Monkeys Audio v4.38": {"code": "12", "extension": "ape", "folder": "1.Monkey's Audio"},
                 "ogg vorbis (aoTuV SSE3)": {"code": "05", "extension": "ogg", "folder": "0.Ogg Vorbis"},
                 "SV8 mpcenc 1.30 stable": {"code": "03", "extension": "mpc", "folder": "0.Musepack"}
                 }

    def get_encoder(self, encoder):
        return self._encoders.get(encoder)

    def get_encoders(self):
        return sorted(self._encoders)


class TagsModifier(TrackTags):
    __logger = logging.getLogger("{0}.TagsModifier".format(__name__))

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
    def __init__(self, obj, provider):
        super(ChangeEncodedBy, self).__init__(obj)
        self._otags["encodedby"] = "{0} from {1} bootleg Audio CD".format(self._otags["encodedby"].rstrip(), provider)


class ChangeMediaProvider(TagsModifier):
    def __init__(self, obj):
        super(ChangeMediaProvider, self).__init__(obj)
        if self._otags.get("bootlegprovider"):
            self._otags["mediaprovider"] = self._otags["bootlegprovider"]


# class ChangeMediaTitle(TagsModifier):
#     def __init__(self, obj):
#         super(ChangeMediaTitle, self).__init__(obj)
#         if self._otags.get("bootlegtitle"):
#             self._otags["mediatitle"] = self._otags["bootlegtitle"]


# class ChangeMediaReference(TagsModifier):
#     def __init__(self, obj):
#         super(ChangeMediaReference, self).__init__(obj)
#         if self._otags.get("bootlegdiscreference"):
#             self._otags["mediareference"] = self._otags["bootlegdiscreference"]


class ChangeTotalTracks(TagsModifier):
    def __init__(self, obj):
        super(ChangeTotalTracks, self).__init__(obj)
        self._otags[self._totaltracks_key] = self._otags["albumtotaltracks"]


class ChangeTrackNumber(TagsModifier):
    def __init__(self, obj):
        super(ChangeTrackNumber, self).__init__(obj)
        self._otags["track"] = str(int(self._otags["track"]) + int(self._otags.get("offset", "0")))


class RippedTrack(ContextDecorator):
    """
    Main entry context decorator dealing with the audio tags produced by the ripping application.
    It aims at manipulating (create, change, and delete) tags by using the required class, then
    delivering updated tags to the ripping application.
    Called from `upsert_audiotags`.
    """
    _environment = shared.TemplatingEnvironment(_MYPARENT.parents[1] / "AudioCD" / "Templates")
    _logger = logging.getLogger(f"{__name__}.RippedTrack")
    _tabs = 4

    def __init__(self, rippingprofile, file, sequence, *decoratingprofiles, **kwargs):
        """

        :param rippingprofile: ripping profile. Set the class required to manipulate audio tags.
        :param file: audio tags text file. Made by the ripping application.
        :param sequence: dummy characters string.
        :param decoratingprofiles: decorating profiles. Set the functions used to alter specific audio tags.
        :param kwargs: extra keyword arguments.
        """
        self._audiotracktags = None
        self._decorators = None
        self._sequence = None
        self._profile = None
        self._intags = None
        self._tags = None
        self._encoders = kwargs.get("encoders", Audio_Encoders())
        self._genres = kwargs.get("genres", AudioGenres())
        self._languages = kwargs.get("languages", AudioLanguages())
        self.decorators = decoratingprofiles
        self.sequence = sequence
        self.profile = rippingprofile
        self.tags = file

    @property
    def audiotrack(self):
        return self._audiotracktags

    @property
    def intags(self):
        return self._intags

    @property
    def decorators(self):
        return self._decorators

    @decorators.setter
    def decorators(self, value):
        self._decorators = tuple(value)

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, value):
        value = value.lower()
        if value not in PROFILES:
            raise ValueError('"{0}" isn\'t allowed.'.format(value))
        self._profile = value

    @property
    def sequence(self):
        return self._sequence

    @sequence.setter
    def sequence(self, value):
        self._sequence = value

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, value):
        self._tags = value

    @staticmethod
    def get_tags(fil):
        """

        :param fil: plain text file depicting the audio tags. Made by the ripping application.
        :return: audio tags list where each item is a tuple composed of a key:value pair.
        """
        tags = csv.reader(fil, dialect=CustomDialect())  # type: Any
        tags = filterfalse(decorators.itemgetter_(0)(partial(shared.eq_string_, "encoder+")), tags)
        tags = {decorators.rstrip_(decorators.lower_(callables.group_(1)(REGEX.match)))(key): value for key, value in tags}
        return sorted(tags.items())

    @staticmethod
    def alter_tags(audiotrack, *profiles):
        """

        :param audiotrack: TrackTags subclass object.
        :param profiles: audio tags altering profile.
        :return:
        """
        logger = logging.getLogger(f"{__name__}.RippedTrack.alter_tags")
        for profile in profiles:
            logger.debug('Tags altered according to decorating profile "%s".', profile)

            # Change `album`.
            if profile.lower() == "default_album":
                audiotrack = changealbum(audiotrack, "$albumsortyear.$albumsortcount - $album")
            elif profile.lower() == "dft_bootleg_album":
                audiotrack = changealbum(audiotrack, "Live: $dashed_bootlegalbum_date - $bootlegalbumcity")
            elif profile.lower() == "alt_bootleg_album":
                audiotrack = changealbum(audiotrack, "$bootlegalbumtour - $dotted_bootlegalbum_date - [$bootlegalbumcity]")

            # Change `tracknumber` if an offset is provided by the ripping application.
            elif profile.lower() == "offset_track":
                audiotrack = changetracknumber(audiotrack)

            # Change `totaltracks`.
            elif profile.lower() == "change_totaltracks":
                audiotrack = changetotaltracks(audiotrack)

            # Changes requested by `nugs` decorating profile.
            elif profile.lower() == "nugs":
                if audiotrack.artist.lower() == "pearl jam":
                    audiotrack = changemediaprovider(changeencodedby(audiotrack))
                elif audiotrack.artist.lower() == "bruce springsteen":
                    audiotrack = changemediaprovider(changeencodedby(audiotrack))

        return audiotrack

    def __enter__(self):

        # --> 1. Start logging.
        self._logger.info('START "%s".', os.path.basename(__file__))
        self._logger.info('"%s" used as ripping profile.', self._profile)

        # --> 2. Log decorators.
        for decorator in self._decorators:
            self._logger.info('"%s" used as decorating profile.', decorator)

        # --> 3. Log input file.
        self._logger.debug("Input file.")
        self._logger.debug('\t"%s"'.expandtabs(self._tabs), self._tags.name)

        # --> 4. Log input tags.
        self._tags.seek(0)
        self._intags = self.get_tags(self._tags)
        self._logger.debug("Input tags.")
        for key, value in shared.pprint_mapping(*sorted(self._intags, key=itemgetter(0))):
            self._logger.debug("\t%s: %s".expandtabs(self._tabs), key, value)

        # --> 5. Create TrackTags subclass object.
        #        l'attribut "_audiotracktags" est une instance d'une sous-classe de TrackTags.
        self._tags.seek(0)
        self._audiotracktags = PROFILES[self._profile].isinstancedfrom(self._tags,
                                                                       self._sequence,
                                                                       self._genres,
                                                                       self._languages,
                                                                       self._encoders)

        # --> 6. Log instance attributes.
        self._logger.debug("Here are the key/value pairs stored by the `TrackTags` instance.")
        for key, value in shared.pprint_mapping(*sorted(self._audiotracktags, key=itemgetter(0))):
            self._logger.debug("\t%s: %s".expandtabs(5), key, value)

        # --> 7. Alter instance attributes.
        self._audiotracktags = self.alter_tags(self._audiotracktags, *self._decorators)
        if self._audiotracktags.origtrack == self._audiotracktags.tracknumber:
            del self._audiotracktags.origtrack

        # --> 8. Return RippedTrack instance.
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        # --> 1. Set output tags.
        exclusions = PROFILES[self._profile].exclusions
        if self._audiotracktags.step == 2:
            exclusions.append("albumsortcount")
            exclusions.append("foldersortcount")
            exclusions.append("code")
            exclusions.append("folder")
            exclusions.append("lossless")
            exclusions.append("origtrack")
        outtags = filterfalse(decorators.itemgetter_(0)(partial(contains, exclusions)), sorted(self._audiotracktags, key=itemgetter(0)))  # type: Any
        outtags = dict(outtags)

        # --> 2. Log output tags.
        self._logger.debug(f'Processed track is: \"{self._audiotracktags}\"')
        self._logger.debug("Output tags.")
        for key, value in shared.pprint_mapping(*sorted(outtags.items(), key=itemgetter(0))):
            self._logger.debug("\t%s: %s".expandtabs(self._tabs), key, value)

        # --> 3. Log output file.
        self._logger.debug("Output file.")
        self._logger.debug("\t%s".expandtabs(self._tabs), self._tags.name)

        # --> 4. Store tags.
        self._logger.debug("Write output tags to output file.")
        self._tags.seek(0)
        self._tags.truncate()
        self._tags.write(self._environment.get_template("Tags").render(tags=outtags))

        # --> 5. Stop logging.
        self._logger.info('END "%s".', os.path.basename(__file__))


# ================================
# Audio tags processing functions.
# ================================
def upsert_audiotags(rippingprofile, file, sequence, *decoratingprofiles, **kwargs):
    """
    Main entry function called by the ripping application to manipulate audio tags.
    Called from `grabber.py`.
    Called from `grabber_beg.cmd`.

    :param rippingprofile: ripping profile. Set the class required to manipulate audio tags.
    :param file: audio tags text file. Made by the ripping application.
    :param sequence: dummy characters string. Deprecated!
    :param decoratingprofiles: decorating profiles. Set the functions used to alter specific audio tags.
    :param kwargs: extra keyword arguments.
    :return: 2-item tuple composed of:
                    1) a return code. 0 for success. 100 for failure.
                    2) an optional TrackTags subclass object in case of success.
    """
    in_logger = logging.getLogger("{0}.upsert_audiotags".format(__name__))
    in_mapping = {"albums": albums, "bootlegs": bootlegs}
    stack = ExitStack()
    level, track = 0, None  # type: int, Optional[RippedTrack]
    in_logger.debug("Profile is  : %s", rippingprofile)
    in_logger.debug("File name is: %s", file.name)
    try:
        track = stack.enter_context(RippedTrack(rippingprofile, file, sequence, *decoratingprofiles, **kwargs))
    except ValueError as err:
        in_logger.debug(err)
        level = 100
    else:
        with stack:

            # Log input extra keyword arguments.
            for key, value in shared.pprint_mapping(*sorted(kwargs.items(), key=itemgetter(0))):  # type: ignore
                in_logger.debug("%s: %s", key, value)

            # Insert tags into the local audio database.
            if track.audiotrack.database and kwargs.get("database"):
                database = Path(kwargs["database"])
                if database.exists():
                    for key, value in in_mapping.items():
                        if kwargs.get(key, False):
                            dump_audiotags_tojson(track.audiotrack, value, database=str(database), jsonfile=kwargs.get("jsonfile"), encoding=kwargs.get("encoding", shared.UTF8))

            # Serialize tags into plain files.
            if kwargs.get("save", False):
                root = Path(kwargs.get("root"))
                if root.exists():
                    path = kwargs["root"] / Path(get_tagsfile(track.audiotrack))
                    os.makedirs(str(path), exist_ok=True)

                    # -----
                    json_file = str(path / "input_tags.json")
                    collection = list(load_sequence_fromjson(json_file))
                    collection.append(dict(track.intags))
                    dump_sequence_tojson(json_file, *collection)
                    dump_sequence_toyaml(str(path / "input_tags.yml"), *collection)

                    # -----
                    json_file = str(path / "output_tags.json")
                    collection = list(load_sequence_fromjson(json_file))
                    collection.append(dict(sorted(track.audiotrack, key=itemgetter(0))))
                    dump_sequence_tojson(json_file, *collection)
                    dump_sequence_toyaml(str(path / "output_tags.yml"), *collection)

    if level:
        return level, None
    return level, track.audiotrack


def get_tagsfile(obj):
    """

    :param obj:
    :return:
    """
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

    # -----
    with open(_MYPARENT / "Resources" / "Templates.yml", encoding=shared.UTF8) as stream:
        templates = yaml.load(stream, Loader=yaml.FullLoader)

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


def changeencodedby(obj, *, provider="nugs.net"):
    return ChangeEncodedBy(obj, provider)


def changemediaprovider(obj):
    return ChangeMediaProvider(obj)


# def changemediareference(obj):
#     return ChangeMediaReference(obj)


# def changemediatitle(obj):
#     return ChangeMediaTitle(obj)


def changetotaltracks(obj):
    return ChangeTotalTracks(obj)


def changetracknumber(obj):
    return ChangeTrackNumber(obj)


def albums(track, *, fil=None, encoding=shared.UTF8, db=shared.DATABASE):
    """
    Set the audio tags collection for further storage into the local audio database.
    Tags are appended to the collection retrieved from a JSON file.
    Duplicates are removed.

    :param track: DefaultTrackTags object.
    :param fil: JSON file full path.
    :param encoding: JSON file characters encoding.
    :param db: local database full path.
    :return: yield a tuple composed of:
                1. JSON file full path.
                2. tag value.
    """
    logger = logging.getLogger("{0}.albums".format(__name__))
    iterable = []  # type: List[Sequence[Any]]
    countries = dict(get_countries(db))  # type: Mapping[str, int]
    genres = dict(get_genres(db))  # type: Mapping[str, int]
    languages = dict(get_languages(db))  # type: Mapping[str, int]
    _fil = shared.TEMP / "tags.json"  # type:Path
    if fil:
        _fil = Path(fil)

    # Load existing sequences.
    with suppress(FileNotFoundError):
        with open(_fil, encoding=encoding) as fr:
            iterable = json.load(fr)

    # Convert list(s) to tuple(s) for using set container.
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
                     track.bootlegdisc,
                     track.deluxe,
                     languages[track.tracklanguage],
                     track.title,
                     track.artistsort,
                     track.artist,
                     track.incollection,
                     shared.get_rippingapplication()[1],
                     track.bootlegalbum_date,
                     track.bootlegalbum_city,
                     countries.get(track.bootlegalbum_country),
                     track.bootlegalbum_tour,
                     None,
                     track.repository))
    iterable = list(set(iterable))
    for item in sorted(sorted(iterable, key=itemgetter(1)), key=itemgetter(0)):
        yield str(_fil), item


def bootlegs(track, *, fil=None, encoding=shared.UTF8, db=shared.DATABASE):
    """
    Set the audio tags collection for further storage into the local audio database.
    Tags are appended to the collection retrieved from a JSON file.
    Duplicates are removed.

    :param track: LiveBootlegTrackTags object.
    :param fil: JSON file full path.
    :param encoding: JSON file characters encoding.
    :param db: local database full path.
    :return: yield a tuple composed of:
                1. JSON file full path.
                2. tag value.
    """
    logger = logging.getLogger("{0}.bootlegs".format(__name__))
    iterable = []  # type: List[Sequence[Any]]
    countries = dict(get_countries(db))  # type: Mapping[str, int]
    genres = dict(get_genres(db))  # type: Mapping[str, int]
    languages = dict(get_languages(db))  # type: Mapping[str, int]
    providers = dict(get_providers(db))  # type: Mapping[str, int]
    _fil = shared.TEMP / "tags.json"  # type: Path
    if fil:
        _fil = Path(fil)

    # Log `track` privates attributes.
    logger.debug('Here are the private key/value pairs stored into the `LiveBootlegTrackTags` instance.')
    for key, value in shared.pprint_mapping(*sorted(track, key=itemgetter(0))):
        logger.debug("\t%s: %s".expandtabs(5), key, value)

    # Log `track` public attributes.
    logger.debug("Here are the public attributes stored into the `LiveBootlegTrackTags` instance.")
    keys = ["albumid",
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
            "bootlegalbum_date",
            "bootlegalbum_city",
            "bootlegalbum_country",
            "bootlegalbum_tour",
            "bootlegtrack_date",
            "bootlegtrack_city",
            "bootlegtrack_country",
            "bootlegtrack_tour",
            "bootlegalbum_publisher",
            "bootlegalbum_title",
            "bootlegdisc_reference",
            "repository"]
    values = [track.albumid,
              track.artistsort,
              track.artist,
              track.genre,
              track.bootlegdisc,
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
              track.bootlegtrack_date,
              track.bootlegtrack_city,
              countries[track.bootlegtrack_country],
              track.bootlegalbum_tour,
              providers[track.bootlegalbum_publisher or track.bootlegalbum_provider],
              track.bootlegalbum_title,
              track.bootlegdisc_reference,
              track.repository]
    for key, value in shared.pprint_mapping(*zip(keys, values)):
        logger.debug("\t%s: %s".expandtabs(5), key, value)

    # Load existing sequences.
    with suppress(FileNotFoundError):
        with open(_fil, encoding=encoding) as fr:
            iterable = json.load(fr)

    # Convert list(s) to tuple(s) for using set container.
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
                     track.bootlegdisc,
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
                     providers[track.bootlegalbum_publisher or track.bootlegalbum_provider],
                     track.bootlegdisc_reference,
                     track.bootlegalbum_title,
                     shared.get_rippingapplication()[1],
                     track.repository))
    iterable = list(set(iterable))
    for item in sorted(sorted(sorted(iterable, key=itemgetter(2)), key=itemgetter(1)), key=itemgetter(0)):
        yield str(_fil), item


def dump_audiotags_tojson(track, kallable, *, database=shared.DATABASE, jsonfile=None, encoding=shared.UTF8):
    """
    Dump audio tags into a JSON file for further storage into the local audio database.

    :param track: TrackTags subclass object.
    :param kallable: callable object providing the tags collection.
    :param database: local database full path.
    :param jsonfile: JSON file full path.
    :param encoding: JSON file characters encoding.
    :return: None.
    """
    for fil, sequences in groupby(kallable(track, **dict(fil=jsonfile, db=database, encoding=encoding)), key=itemgetter(0)):
        dump_sequence_tojson(fil, *list(sequence for _, sequence in sequences), encoding=encoding)


def split_(*indexes):
    def outer_wrapper(func):
        def inner_wrapper(arg):
            out = ()  # type: Tuple[str, ...]
            for index in indexes:
                out += (callables.group_(index)(func)(arg),)
            return out

        return inner_wrapper

    return outer_wrapper


# ========================
# Miscellaneous functions.
# ========================
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
    for key, value in mapping.items():
        yield key, value


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


def dump_mapping_tojson(jsonfile, encoding=shared.UTF8, **collection) -> None:
    """

    :param jsonfile:
    :param encoding:
    :param collection:
    :return:
    """
    _dump_tojson(jsonfile, collection, encoding)


def dump_sequence_tojson(jsonfile, *collection, encoding=shared.UTF8) -> None:
    """

    :param jsonfile:
    :param collection:
    :param encoding:
    :return:
    """
    _dump_tojson(jsonfile, collection, encoding)


def dump_sequence_toyaml(yamlfile, *collection, encoding=shared.UTF8) -> None:
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


# ========
# Objects.
# ========
Profile = NamedTuple("Profile", [("exclusions", List[str]),
                                 ("isinstancedfrom", Any)])

# ==========
# Constants.
# ==========
PROFILES = {"default": Profile(["albumsortyear",
                                "albumtotaltracks",
                                "bonustrack",
                                "bootleg",
                                "database",
                                "deluxe",
                                "livedisc",
                                "livetrack",
                                "offset",
                                "sample",
                                "tracklanguage"], DefaultTrackTags.fromfile),
            "bootleg": Profile(["albumtotaltracks",
                                "bonustrack",
                                "bootleg",
                                "bootlegalbumcity",
                                "bootlegalbumcountry",
                                "bootlegalbumtour",
                                "bootlegalbumyear",
                                "bootlegdiscreference",
                                "bootlegprovider",
                                "bootlegpublisher",
                                "bootlegtitle",
                                "dashed_bootlegalbum_date",
                                "database",
                                "deluxe",
                                "dotted_bootlegalbum_date",
                                "livedisc",
                                "livetrack",
                                "offset",
                                "sample",
                                "tracklanguage"], LiveBootlegTrackTags.fromfile),
            "live": Profile(["albumsortyear",
                             "albumtotaltracks",
                             "bonustrack",
                             "bootleg",
                             "bootlegalbumcity",
                             "bootlegalbumcountry",
                             "bootlegalbumtour",
                             "bootlegalbumyear",
                             "dashed_bootlegalbum_date",
                             "database",
                             "deluxe",
                             "dotted_bootlegalbum_date",
                             "livedisc",
                             "livetrack",
                             "offset",
                             "sample",
                             "tracklanguage"], LiveTrackTags.fromfile)
            }
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources", "Mapping.json"), encoding="UTF_8") as fp:
    MAPPING = json.load(fp)
