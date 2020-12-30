# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import os
import re
from collections.abc import Sequence
from contextlib import suppress
from functools import partial
from itertools import chain, groupby, islice, starmap, tee
from operator import attrgetter, contains, itemgetter
from pathlib import Path
from typing import Any, Dict, Iterator, List, Mapping, NamedTuple, Tuple, Union

from Applications.Tables.Albums.shared import get_countries, get_genres, get_languages, get_providers, insert_discs
from Applications.decorators import contains_, eq_, itemgetter_, lower_, none_
from Applications.more_shared import APEv2Tag, VorbisComment
from Applications.parsers import database_parser
from Applications.shared import Files, GetPath, partitioner

__author__ = "Xavier ROSSET"
__maintainer__ = "Xavier ROSSET"
__email__ = "xavier.python.computing@protonmail.com"
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent


# ========
# Classes.
# ========
class Track(Sequence):
    TAGS = []  # type: List[str]
    MAPPING = {".ape": APEv2Tag, ".flac": VorbisComment, ".wv": APEv2Tag}

    def __init__(self, database: str, *paths: Path, **kwargs: Mapping[str, int]) -> None:
        """

        :param database:
        :param paths:
        :param kwargs:
        """
        collection = []  # type: Any
        self._database = database  # type: str
        self._genres = kwargs.get("genres", {"Rock": 9})  # type: Mapping[str, int]
        self._languages = kwargs.get("languages", {"English", 1})  # type: Mapping[str, int]
        self._providers = kwargs.get("providers", {})  # type: Mapping[str, int]
        for extension, group in filter(contains_(".ape", ".flac", ".wv")(lower_(itemgetter(0))), groupby(self._get_files(*paths), key=attrgetter("suffix"))):
            for file in group:
                collection.append(iter(self.MAPPING[extension](file)))
        collection = [list(filter(itemgetter_(0)(partial(contains, self.TAGS)), item)) for item in collection]
        self._collection = list(starmap(self.__update, collection))  # type: Any

    def __contains__(self, item):
        return item in self._collection

    def __getitem__(self, item):
        return self._collection[item]

    def __iter__(self):
        for item in self._collection:
            yield item

    def __len__(self):
        return len(self._collection)

    def __repr__(self):
        if not self:
            return "%s()" % (self.__class__.__name__,)
        return "%s(%r)" % (self.__class__.__name__, list(self))

    def __update(self, *items: Tuple[str, str]) -> Iterator[Tuple[str, Union[int, str]]]:
        """

        :param items:
        :return:
        """
        comments = dict(items)  # type: Dict[str, Union[int, str]]
        comments.update(albumid=f"{comments.get('artistsort', comments.get('artist'))[0]}.{comments.get('artistsort', comments.get('artist'))}.{comments.get('albumsort')[:-3]}")
        comments.update(bonus=comments.get("titlesort", "       N")[7])
        comments.update(discnumber=int(comments.get("discnumber", 0)))
        comments.update(disctotal=int(comments.get("disctotal", 0)))
        comments.update(genre=self._genres.get(comments.get("genre", "Rock")))
        comments.update(incollection=comments.get("incollection", "N"))
        comments.update(titlelanguage=self._languages.get(comments.get("titlelanguage", "English")))
        comments.update(tracknumber=int(comments.get("tracknumber", 0)))
        comments.update(tracktotal=int(comments.get("tracktotal", 0)))
        for key, value in comments.items():
            yield key, value

    @staticmethod
    def _get_files(*paths: Path) -> Iterator[Path]:
        files = chain.from_iterable(iter(Files(path)) for path in paths)  # type: Any
        files = sorted(files, key=attrgetter("stem"))
        files = sorted(files, key=attrgetter("parent"))
        files = sorted(files, key=attrgetter("suffix"))
        for file in files:
            yield file


class BootlegTrack(Track):
    REGEX1 = re.compile(r"^([^-]+)-([^-]+)- \[(([^,]+),([^]]+))]$")
    REGEX2 = re.compile(r"^(([^,]+), ([A-Z][A-Z]))$")
    LENGTH = 31
    TAGS = ["album",
            "albumartist",
            "albumsort",
            "artist",
            "artistsort",
            "bootlegtrackcity",
            "bootlegtrackcountry",
            "bootlegtracktour",
            "bootlegtrackyear",
            "date",
            "discnumber",
            "disctotal",
            "genre",
            "incollection",
            "label",
            "origalbum",
            "publisherreference",
            "title",
            "titlelanguage",
            "titlesort",
            "tracknumber",
            "tracktotal"]  # type: List[str]
    TRACKS = NamedTuple("BootlegTrack", [("album", str),
                                         ("albumartist", str),
                                         ("albumid", str),
                                         ("albumsort", str),
                                         ("artist", str),
                                         ("artistsort", str),
                                         ("bonustrack", str),
                                         ("bootlegalbum_city", str),
                                         ("bootlegalbum_country", int),
                                         ("bootlegalbum_tour", str),
                                         ("bootlegalbum_day", str),
                                         ("bootlegdisc", str),
                                         ("bootlegtrack_city", str),
                                         ("bootlegtrack_country", int),
                                         ("bootlegtrack_tour", str),
                                         ("bootlegtrack_day", str),
                                         ("year", str),
                                         ("discnumber", int),
                                         ("totaldiscs", int),
                                         ("genre", int),
                                         ("incollection", str),
                                         ("livedisc", str),
                                         ("livetrack", str),
                                         ("bootlegalbum_title", str),
                                         ("bootlegalbum_publisher", int),
                                         ("bootlegdisc_reference", str),
                                         ("title", str),
                                         ("titlelanguage", int),
                                         ("titlesort", str),
                                         ("tracknumber", int),
                                         ("totaltracks", int)])

    def __init__(self, database: str, *paths: Path, **kwargs: Mapping[str, int]) -> None:
        """

        :param database:
        :param paths:
        :param kwargs:
        """
        super(BootlegTrack, self).__init__(database, *paths, **kwargs)
        self._countries = kwargs.get("countries", {})  # type: Mapping[str, int]
        tracks = starmap(self._update, self._collection)  # type: Any

        # -----
        _ok, self._ko = partitioner(tracks, predicate=eq_(self.LENGTH)(len))  # type: Any, Any

        # -----
        tracks = sorted(set(_ok), key=itemgetter(29))
        tracks = sorted(tracks, key=itemgetter(17))
        tracks = sorted(tracks, key=itemgetter(2))
        tracks = [self.TRACKS(*track) for track in tracks]
        self._collection = list(tracks)

    def _update(self, *items: Tuple[str, Union[int, str]]) -> Tuple[Union[int, str], ...]:
        """

        :param items:
        :return:
        """
        comments = dict(items)  # type: Dict[str, Union[int, str]]

        # ----- Update specific tags or create new ones.
        comments.update(bootlegdisc="Y")
        comments.update(livedisc="Y")
        comments.update(livetrack="Y")
        comments.update(origalbum=comments.get("origalbum"))
        comments.update(publisher=comments.get("label"))
        comments.update(publisherreference=comments.get("publisherreference"))

        # ----- Remove useless keys.
        with suppress(KeyError):
            del comments["label"]

        # ----- Create `bootlegalbumXXXXX` tags from `album` tag.
        album = comments.get("album")
        if album:
            match = self.REGEX1.match(album)
            if match:
                comments.update(bootlegalbumcity=match.group(4).strip())
                comments.update(bootlegalbumcountry=match.group(5).strip())
                comments.update(bootlegalbumtour=match.group(1).strip())
                comments.update(bootlegalbumyear=match.group(2).strip().replace(".", "-"))
                match = self.REGEX2.match(match.group(3))
                if match:
                    comments.update(bootlegalbumcity=match.group(1).strip())
                    comments.update(bootlegalbumcountry="United States")

        # ----- Map character values to integer values.
        comments.update(bootlegalbumcountry=self._countries.get(comments.get("bootlegalbumcountry", "United States")))
        comments.update(bootlegtrackcountry=self._countries.get(comments.get("bootlegtrackcountry", "United States")))
        if comments.get("publisher") is not None:
            comments.update(publisher=self._providers.get(comments.get("publisher")))

        # ----- Gather values together into a tuple then remove duplicates.
        return tuple(chain(*islice(zip(*sorted(comments.items(), key=itemgetter(0))), 1, 2)))

    def __iter__(self):
        for track in self._collection:
            yield ("bootlegalbums",
                   self._database,
                   track.albumid,
                   int(track.discnumber),
                   int(track.tracknumber),
                   int(track.totaldiscs),
                   int(track.totaltracks),
                   track.bonustrack,
                   track.livedisc,
                   track.livetrack,
                   track.bootlegdisc,
                   track.genre,
                   track.title,
                   track.titlelanguage,
                   track.bootlegalbum_day,
                   track.bootlegalbum_city,
                   track.bootlegalbum_country,
                   track.bootlegalbum_tour,
                   track.bootlegtrack_day,
                   track.bootlegtrack_city,
                   track.bootlegtrack_country,
                   track.bootlegtrack_tour,
                   track.artistsort,
                   track.artist,
                   track.incollection,
                   track.bootlegalbum_publisher,
                   track.bootlegdisc_reference,
                   track.bootlegalbum_title,
                   None,
                   None)

    @property
    def exceptions(self) -> Iterator[Tuple[Any, ...]]:
        return self._ko


class DefaultTrack(Track):
    LENGTH = 25
    TAGS = ["album",
            "albumartist",
            "albumsort",
            "artist",
            "artistsort",
            "date",
            "discnumber",
            "disctotal",
            "genre",
            "incollection",
            "label",
            "mediaprovider",
            "origyear",
            "title",
            "titlelanguage",
            "titlesort",
            "tracknumber",
            "tracktotal",
            "upc"]  # type: List[str]
    TRACKS = NamedTuple("DefaultTrack", [("album", str),
                                         ("albumartist", str),
                                         ("albumid", str),
                                         ("albumsort", str),
                                         ("artist", str),
                                         ("artistsort", str),
                                         ("bonustrack", str),
                                         ("bootlegdisc", str),
                                         ("year", int),
                                         ("deluxe", str),
                                         ("discnumber", str),
                                         ("totaldiscs", str),
                                         ("genre", int),
                                         ("incollection", str),
                                         ("label", str),
                                         ("livedisc", str),
                                         ("livetrack", str),
                                         ("mediaprovider", str),
                                         ("origyear", int),
                                         ("title", str),
                                         ("titlelanguage", int),
                                         ("titlesort", str),
                                         ("tracknumber", str),
                                         ("totaltracks", str),
                                         ("upc", str)])

    def __init__(self, database: str, *paths: Path, **kwargs: Mapping[str, int]) -> None:
        """

        :param database:
        :param paths:
        :param kwargs:
        """
        super(DefaultTrack, self).__init__(database, *paths, **kwargs)
        tracks = starmap(self._update, self._collection)  # type: Any

        # -----
        _ok, self._ko = partitioner(tracks, predicate=eq_(self.LENGTH)(len))  # type: Any, Any
        _, _ok = partitioner(_ok, predicate=none_(itemgetter_(11)))

        # -----
        tracks = sorted(set(_ok), key=itemgetter(20))
        tracks = sorted(tracks, key=itemgetter(9))
        tracks = sorted(tracks, key=itemgetter(2))
        tracks = [self.TRACKS(*track) for track in tracks]
        self._collection = list(tracks)

    def _update(self, *items: Tuple[str, Union[int, str]]) -> Tuple[Union[int, str], ...]:
        """

        :param items:
        :return:
        """
        comments = dict(items)  # type: Dict[str, Union[int, str]]
        comments.update(bootlegdisc="N")
        comments.update(date=int(comments.get("date", 0)))
        comments.update(deluxe="N")
        comments.update(livedisc="N")
        comments.update(livetrack=comments.get("titlesort", "        N")[8])
        comments.update(mediaprovider=self._providers.get(comments.get("mediaprovider")))
        comments.update(origyear=int(comments.get("origyear", 0)))
        comments.update(upc=comments.get("upc", "999999999999"))

        # ----- Gather values together into a tuple then remove duplicates.
        return tuple(chain(*islice(zip(*sorted(comments.items(), key=itemgetter(0))), 1, 2)))

    def __iter__(self):
        for track in self._collection:
            yield ("defaultalbums",
                   self._database,
                   track.albumid,
                   int(track.discnumber),
                   int(track.tracknumber),
                   int(track.totaldiscs),
                   int(track.totaltracks),
                   int(track.origyear),
                   int(track.year),
                   track.album,
                   track.genre,
                   track.label,
                   track.upc,
                   track.bonustrack,
                   track.livedisc,
                   track.livetrack,
                   track.bootlegdisc,
                   track.deluxe,
                   track.titlelanguage,
                   track.title,
                   track.artistsort,
                   track.artist,
                   track.incollection,
                   None,
                   None,
                   None,
                   None,
                   None,
                   track.mediaprovider,
                   None)

    @property
    def exceptions(self) -> Iterator[Tuple[Any, ...]]:
        return self._ko


# ============
# Main script.
# ============
if __name__ == "__main__":
    import argparse
    import datetime
    import logging.config
    import pytz
    import sys

    import yaml

    from Applications.shared import TemplatingEnvironment, rjustify, stringify, UTF8, WRITE, TEMP, DFTTIMEZONE

    # ----- Classes.
    class GetClass(argparse.Action):
        MAPPING = {"bootleg": BootlegTrack, "default": DefaultTrack}

        def __init__(self, option_strings, dest, **kwargs):
            super(GetClass, self).__init__(option_strings, dest, **kwargs)

        def __call__(self, parsobj, namespace, values, option_string=None):
            setattr(namespace, self.dest, values)
            setattr(namespace, "klass", self.MAPPING.get(values))


    # ----- Arguments parser.
    parser = argparse.ArgumentParser(parents=[database_parser])
    parser.add_argument("album", choices=["bootleg", "default"], action=GetClass)
    parser.add_argument("path", nargs="+", action=GetPath)
    parser.add_argument("--skip", action="store_true")

    # ----- Load logging configuration.
    with open(_MYPARENT.parent / "Resources" / "logging.yml", encoding=UTF8) as stream:
        log_config = yaml.load(stream, Loader=yaml.FullLoader)
    logging.config.dictConfig(log_config)

    # ----- Miscellaneous objects.
    arguments = parser.parse_args()
    genres = dict(get_genres())  # type: Mapping[str, int]
    countries = dict(get_countries())  # type: Mapping[str, int]
    languages = dict(get_languages())  # type: Mapping[str, int]
    providers = dict(get_providers())  # type: Mapping[str, int]

    # ----- Templating environment.
    ENVIRONMENT = TemplatingEnvironment(_MYPARENT / "Templates")
    ENVIRONMENT.set_environment(filters={"rjustify": rjustify,
                                         "stringify": stringify})

    # ----- Get tracks collection.
    collection = arguments.klass(arguments.db, *arguments.path, countries=countries, genres=genres, languages=languages, providers=providers)  # type: Any

    # ----- Print raised exceptions.
    print(ENVIRONMENT.get_template("T02").render(collection=collection.exceptions))

    # ----- Dump tracks collection.
    coll1, coll2 = tee(collection)
    coll1 = list(coll1)
    coll1.insert(0, pytz.timezone("UTC").localize(datetime.datetime.utcnow()).astimezone(pytz.timezone(DFTTIMEZONE)).isoformat())
    with open(TEMP / "digitaldiscs.yml", mode=WRITE, encoding=UTF8) as stream:
        yaml.dump(coll1, stream)

    # ----- Insert tracks collection into database.
    if arguments.skip:
        sys.exit(0)
    sys.exit(insert_discs(*coll2))
