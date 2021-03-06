# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import datetime
import os
from collections import OrderedDict
from functools import partial
from itertools import groupby, islice
from operator import attrgetter, eq, itemgetter
from pathlib import Path
from string import Template
from typing import Any, Iterable, Mapping, Optional, Sequence, Set, Tuple

import cherrypy

from .Tables.Albums.shared import get_albumheader
from .Tables.PlayedDiscs.shared import get_playeddiscs
from .Tables.RippedDiscs.shared import get_rippeddiscs
from .decorators import attrgetter_
# from .Tables.Albums.shared import get_albumheader, get_track, getartist, getlastplayeddate, updatelastplayeddate
# from .Views.RippedDiscs.shared import deletelog as deleterippedcd, getmonths, insertfromargs, selectlog, selectlogs, updatelog, valid_year
# from .Tables.RippedDiscs.shared import validyear
from .shared import DATABASE, LOCAL, TEMPLATE4, TemplatingEnvironment, UTC, eq_string_, format_date, localize_date, normalize, normalize2

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent


# =====================
# Jinja2 local filters.
# =====================
def _getalbumid(artist, albumsort):
    """

    :param artist:
    :param albumsort:
    :return:
    """
    return Template(r"$a.$b.$c").substitute(a=artist[0].upper(), b=artist, c=albumsort)


def _getcover(artist, albumsort):
    """

    :param artist:
    :param albumsort:
    :return:
    """
    return Template(r"albumart/$a/$b/$c/iPod-Front.jpg").substitute(a=artist[0].upper(), b=artist, c=albumsort)


def _getvalue(dictionary, key):
    """

    :param dictionary:
    :param key:
    :return:
    """
    return dictionary.get(key, key)


def _gettimestamp(dt):
    """

    :param dt:
    :return:
    """
    return int(dt.timestamp())


# ================
# Local functions.
# ================
# def _compress(selectors, iterable):
#     return tuple(compress(iterable, selectors))


# ========
# Classes.
# ========
class DigitalAudioCollection(object):
    # Constants.
    PERIODS = {"0": "Today",
               "1": "Yesterday",
               "2": "That week",
               "3": "Two weeks ago",
               "4": "Three weeks ago",
               "5": "Four weeks ago and older"}
    SCRIPTS = {"view1": ["frameworks/jquery.js",
                         "scripts/functions.js",
                         "scripts/view1.js",
                         "scripts/shared.js"],
               "view2": ["frameworks/jquery.js",
                         "scripts/functions.js",
                         "scripts/view2.js",
                         "scripts/shared.js"]}
    SHEETS = {"view1": ["stylesheets/shared.css",
                        "stylesheets/view1.css"],
              "view2": ["stylesheets/shared.css",
                        "stylesheets/view2.css"]}
    SORT_SEQUENCE = {"digitalalbums": [("albumid", False), ("month_created", True)],
                     "rippeddiscs": [("albumid", False), ("ripped", True)],
                     "playeddiscs": [("albumid", False), ("played", True)],
                     "default": [("albumid", False), ("artistsort", False)]}

    # Templating configuration.
    TEMPLATES = {"digitalalbumsview": "T01",
                 "rippeddiscsview": "T01",
                 "playeddiscsview": "T01",
                 "rippeddiscsviewbyartist": "T02",
                 "rippeddiscsviewbygenre": "T02",
                 "rippeddiscsviewbymonth": "T02",
                 "rippeddiscsviewbyyear": "T02",
                 "getdigitalalbums": "T03"}
    TEMPLATE = TemplatingEnvironment(_MYPARENT.parent / "AudioCD" / "AudioCollection")
    TEMPLATE.set_environment(globalvars={"local": LOCAL,
                                         "utc": UTC,
                                         "utcnow": datetime.datetime.utcnow()},
                             filters={"normalize": normalize,
                                      "normalize2": normalize2,
                                      "getalbumid": _getalbumid,
                                      "getcover": _getcover,
                                      "getvalue": _getvalue,
                                      "localize": localize_date,
                                      "readable": partial(format_date, template=TEMPLATE4),
                                      "readmonth": partial(format_date, template="$Y$m"),
                                      "timestamp": _gettimestamp})

    # TEMPLATE.set_template(**TEMPLATES)

    def __init__(self, db=DATABASE):

        # Initializations.
        self._database = None
        # self._artistsort_mapping = None
        # self._artists_mapping = None
        # self._genres_mapping = None
        # self._months = None
        self._rippeddiscs = None
        self._playeddiscs = None
        # self._rippedcdlog = None
        # self._audiofiles = None
        # self._digitalartists = None
        self._digitalalbums = None
        # self._digitalalbums_mapping = None
        # self._lastplayedalbums = None

        # Setters.
        self.database = db
        # self.artistsort_mapping = db
        # self.artists_mapping = db
        # self.genres_mapping = db
        # self.months = db
        self.rippeddiscs = db
        self.playeddiscs = db
        # self.audiofiles = [["APE", "FLAC", "MP3", "M4A", "OGG"], MUSIC, ["recycle", "\$recycle"]]
        # self.digitalartists = db
        self.digitalalbums = db
        # self.digitalalbums_mapping = db
        # self.lastplayedalbums = db

    @cherrypy.expose
    def shutdown(self):
        cherrypy.engine.exit()

    # -------------------------------------------
    # Getter and setter for "database" attribute.
    # -------------------------------------------
    @property
    def database(self):
        return self._database

    @database.setter
    def database(self, arg):
        self._database = arg

    # ------------------------------------------------
    # Getter and setter for "digitalalbums" attribute.
    # ------------------------------------------------
    @property
    def digitalalbums(self):
        return self._digitalalbums

    @digitalalbums.setter
    def digitalalbums(self, arg: str) -> None:
        self._digitalalbums = list(get_albumheader(db=arg))  # type: Sequence[Any]

    # ----------------------------------------------
    # Getter and setter for "rippeddiscs" attribute.
    # ----------------------------------------------
    @property
    def rippeddiscs(self):
        return self._rippeddiscs

    @rippeddiscs.setter
    def rippeddiscs(self, arg: str) -> None:
        self._rippeddiscs = list(get_rippeddiscs(db=arg))  # type: Sequence[Any]

    # ----------------------------------------------
    # Getter and setter for "playedddiscs" attribute.
    # ----------------------------------------------
    @property
    def playeddiscs(self):
        return self._playeddiscs

    @playeddiscs.setter
    def playeddiscs(self, arg: str) -> None:
        self._playeddiscs = list(get_playeddiscs(db=arg))  # type: Sequence[Any]

    # -----------------------------------------------------
    # Getter and setter for "artistsort_mapping" attribute.
    # -----------------------------------------------------
    # @property
    # def artistsort_mapping(self):
    #     return self._artistsort_mapping
    #
    # @artistsort_mapping.setter
    # def artistsort_mapping(self, arg):
    #     # self._artistsort_mapping = dict([(item.artistsort, item.artist) for item in selectlogs(arg) if item.artistsort])
    #     self._artistsort_mapping = {}

    # --------------------------------------------------
    # Getter and setter for "artists_mapping" attribute.
    # --------------------------------------------------
    # @property
    # def artists_mapping(self):
    #     return self._artists_mapping
    #
    # @artists_mapping.setter
    # def artists_mapping(self, arg):
    #     # self._artists_mapping = dict([(item.artist, item.artistsort) for item in selectlogs(arg) if item.artistsort])
    #     self._artists_mapping = {}

    # -------------------------------------------------
    # Getter and setter for "genres_mapping" attribute.
    # -------------------------------------------------
    # @property
    # def genres_mapping(self):
    #     return self._genres_mapping
    #
    # @genres_mapping.setter
    # def genres_mapping(self, arg):
    #     # self._genres_mapping = dict([(normalize(item.genre), item.genre) for item in selectlogs(arg) if item.genre])
    #     self._genres_mapping = {}

    # -------------------------------------------------
    # Getter and setter for "digitalartists" attribute.
    # -------------------------------------------------
    # @property
    # def digitalartists(self):
    #     return self._digitalartists
    #
    # @digitalartists.setter
    # def digitalartists(self, arg):
    #     self._digitalartists = dict(set((item.artistid, item.artist) for item in getartist(arg)))

    # --------------------------------------------------------
    # Getter and setter for "digitalalbums_mapping" attribute.
    # --------------------------------------------------------
    # @property
    # def digitalalbums_mapping(self):
    #     return self._digitalalbums_mapping
    #
    # @digitalalbums_mapping.setter
    # def digitalalbums_mapping(self, arg):
    #     # reflist = [(row.albumid, row.album, row.artist, row.year) for row in get_albumheader(db=arg)]
    #     # self._digitalalbums_mapping = {albumid: (album, artist, year) for albumid, album, artist, year in reflist}
    #     self._digitalalbums_mapping = {}

    # ---------------------------------------------------
    # Getter and setter for "lastplayedalbums" attribute.
    # ---------------------------------------------------
    # @property
    # def lastplayedalbums(self):
    #     return self._lastplayedalbums
    #
    # @lastplayedalbums.setter
    # def lastplayedalbums(self, arg):
    #     self._lastplayedalbums = list(filter(lambda i: i.played > 0, getlastplayeddate(db=arg)))

    # ---------------------------------------------
    # Getter and setter for "audiofiles" attribute.
    # ---------------------------------------------
    # @property
    # def audiofiles(self):
    #     return self._audiofiles
    #
    # @audiofiles.setter
    # def audiofiles(self, arg):
    #     extensions, folder, excluded = arg
    #     audiofiles = ((os.path.normpath(fil), format_date(LOCAL.localize(datetime.datetime.fromtimestamp(os.path.getctime(fil)))), os.path.splitext(fil)[1][1:])
    #                   for fil in filesinfolder(*extensions,
    #                                            folder=folder,
    #                                            excluded=excluded)
    #                   if all([i[0] for i in map(self.checkfile, repeat(os.path.normpath(fil)), [self.grab_artistfirstletter, self.grab_artist, self.grab_year, self.grab_month])]))
    #
    #     #  1. Décorer "checkfile" à l'aide de "checkfile_fromtuple" pour pouvoir traiter le premier élément d'un tuple ("checkfile" doit reçevoir en effet une chaîne de caractères en qualité
    #     #     de premier paramètre).
    #     #     "checkfile_fromtuple" retourne la chaîne de caractères extraite par l'expression régulière enveloppée dans la fonction reçue en qualité de deuxième paramètre.
    #     checkfile = self.checkfile_fromtuple(self.checkfile)
    #
    #     #  2. Définir des fonctions ne pouvant reçevoir qu'un tuple. Elles pourront ainsi être utilisées comme clé pour le tri des fichiers audio.
    #     grab_month = partial(checkfile, rex_func=self.grab_month)
    #     grab_year = partial(checkfile, rex_func=self.grab_year)
    #     grab_artist = partial(checkfile, rex_func=self.grab_artist)
    #     grab_artistfirstletter = partial(checkfile, rex_func=self.grab_artistfirstletter)
    #
    #     #  3. Trier les fichiers audio par lettre, artiste, année, mois et extension.
    #     self._audiofiles = sorted(sorted(sorted(sorted(sorted(audiofiles, key=itemgetter(2)),
    #                                                    key=grab_month),
    #                                             key=grab_year),
    #                                      key=grab_artist),
    #                               key=grab_artistfirstletter)

    # -----------------------------------------
    # Getter and setter for "months" attribute.
    # -----------------------------------------
    # @property
    # def months(self):
    #     return self._months
    #
    # @months.setter
    # def months(self, arg):
    #     # self._months = list(getmonths(db=arg))
    #     self._months = []

    def get_page(self, collection: Iterable[Any], **kwargs) -> Any:
        """

        :param collection:
        :param kwargs:
        :return:
        """
        return self.TEMPLATE.get_template(kwargs.get("template")).render(content=iter(collection), **kwargs)

    @classmethod
    def get_collection(cls, collection: Sequence[Any], *sort_sequence: Tuple[str, bool], **kwargs) -> Tuple[Sequence[Any], Sequence[Tuple[str, str, str]]]:
        """

        :param collection:
        :param sort_sequence:
        :param kwargs:
        :return:
        """
        mappping = {"default": (" selected", "", ""),
                    "artists": ("", " selected", ""),
                    "months": ("", "", " selected")}
        covers = kwargs.get("covers")
        key = kwargs.get("key")
        start = kwargs.get("start")
        view = kwargs.get("view")
        collection = cls.sort_collection(collection, *sort_sequence)
        if view.lower() == "default":
            beg = int(start)
            end = int(start) + int(covers)
            collection = list(collection)[beg:end]
        elif view.lower() in ["artists", "months"]:
            for attr, _ in sort_sequence:
                key = attr
            collection = [(key, list(group)) for key, group in groupby(collection, key=attrgetter(key))]
        return collection, list(zip(("default", "artists", "months"), ("Default", "Artists", "Months"), mappping[view]))

    @staticmethod
    def sort_collection(collection: Sequence[Any], *sequence: Tuple[str, bool]) -> Iterable[Any]:
        for attr, reverse in sequence:
            collection = sorted(collection, key=attrgetter(attr), reverse=reverse)
        return iter(collection)

    # ------------------
    # Refresh functions.
    # ------------------
    @cherrypy.expose
    def refreshdigitalalbums(self):
        self.digitalalbums = self.database

    @cherrypy.expose
    def refreshrippeddiscs(self):
        self.rippeddiscs = self.database

    @cherrypy.expose
    def refreshplayeddiscs(self):
        self.playeddiscs = self.database

    # --------------------
    # Digital albums page.
    # --------------------
    @cherrypy.expose
    def digitalalbumsview(self, view="default", coversperpage="32", start="0", artistsort=None) -> Any:
        """
        Render digital audio albums covers into a tiles view.

        :param view: Requested covers view (default, grouped by artist or grouped by month).
        :param coversperpage: Number of displayed covers per page.
        :param start: Number of the first displayed cover.
        :param artistsort: Reduce rendered albums to a single artist albums.
        :return: HTML template rendered with CherryPy.
        """

        # Get collection.
        kwargs = {"covers": coversperpage,
                  "key": "artistsort",
                  "start": start,
                  "view": view}
        sort_sequence = self.SORT_SEQUENCE.get("digitalalbums", self.SORT_SEQUENCE["default"])  # type: Sequence[Tuple[str, bool]]
        if view.lower() == "artists":
            sort_sequence = [("month_created", True), ("artistsort", False)]
        collection, views = self.get_collection(self.digitalalbums, *sort_sequence, **kwargs)  # type: Sequence[Any], Sequence[Tuple[str, str, str]]
        if artistsort is not None:
            collection = list(filter(attrgetter_("artistsort")(partial(eq, artistsort)), collection))

        # Get HTML page and return it to the browser.
        albums = iter(self.digitalalbums)
        if artistsort is not None:
            albums = filter(attrgetter_("artistsort")(partial(eq, artistsort)), albums)
        mapping = set((album.month_created, format_date(LOCAL.localize(album.utc_created), template="$month $Y")) for album in albums)  # type: Set[Tuple[int, str]]
        kwargs = {"body": "view1",
                  "mapping": dict(mapping),
                  "page": "digitalalbumsview",
                  "scripts": self.SCRIPTS.get("view1"),
                  "sheets": self.SHEETS.get("view1"),
                  "template": self.TEMPLATES["digitalalbumsview"],
                  "title": "digital albums",
                  "view": view,
                  "views": views}
        return self.get_page(iter(collection), **kwargs)

    # ------------------
    # Ripped discs page.
    # ------------------
    @cherrypy.expose
    def rippeddiscsview(self, view="default", coversperpage="32", start="0", artistsort=None) -> Any:
        """
        Render ripped discs covers into a tiles view.

        :param view: Requested covers view (default, grouped by artist or grouped by month).
        :param coversperpage: Number of displayed covers per page.
        :param start: Number of the first displayed cover.
        :param artistsort: Reduce rendered discs to a single artist discs.
        :return: HTML template rendered with CherryPy.
        """

        # Get collection.
        kwargs = {"covers": coversperpage,
                  "key": "artistsort",
                  "start": start,
                  "view": view}
        sort_sequence = self.SORT_SEQUENCE.get("rippeddiscs", self.SORT_SEQUENCE["default"])  # type: Sequence[Tuple[str, bool]]
        if view.lower() == "artists":
            sort_sequence = [("ripped_year_month", True), ("artistsort", False)]
        collection, views = self.get_collection(self.rippeddiscs, *sort_sequence, **kwargs)  # type: Sequence, Sequence[Tuple[str, str, str]]
        if artistsort is not None:
            collection = list(filter(attrgetter_("artistsort")(partial(eq, artistsort)), collection))

        # Get HTML page and return it to the browser.
        discs = iter(self.rippeddiscs)
        if artistsort is not None:
            discs = filter(attrgetter_("artistsort")(partial(eq, artistsort)), discs)
        mapping = set((disc.ripped_year_month, format_date(LOCAL.localize(disc.ripped), template="$month $Y")) for disc in discs)  # type: Set[Tuple[int, str]]
        kwargs = {"body": "view1",
                  "mapping": dict(mapping),
                  "page": "rippeddiscsview",
                  "scripts": self.SCRIPTS.get("view1"),
                  "sheets": self.SHEETS.get("view1"),
                  "template": self.TEMPLATES["rippeddiscsview"],
                  "title": "ripped discs",
                  "view": view,
                  "views": views}
        return self.get_page(iter(collection), **kwargs)

    # ------------------
    # Played discs page.
    # ------------------
    @cherrypy.expose
    def playeddiscsview(self, view="default", coversperpage="32", start="0", artistsort=None) -> Any:
        """
        Render played discs covers into a tiles view.

        :param view: Requested covers view (default, grouped by artist or grouped by month).
        :param coversperpage: Number of displayed covers per page.
        :param start: Number of the first displayed cover.
        :param artistsort: Reduce rendered discs to a single artist discs.
        :return: HTML template rendered with CherryPy.
        """

        # Get collection.
        kwargs = {"covers": coversperpage,
                  "key": "artistsort",
                  "start": start,
                  "view": view}
        sort_sequence = self.SORT_SEQUENCE.get("playeddiscs", self.SORT_SEQUENCE["default"])  # type: Sequence[Tuple[str, bool]]
        if view.lower() == "artists":
            sort_sequence = [("played_year_month", True), ("artistsort", False)]
        collection, views = self.get_collection(self.playeddiscs, *sort_sequence, **kwargs)  # type: Sequence, Sequence[Tuple[str, str, str]]
        if artistsort is not None:
            collection = list(filter(attrgetter_("artistsort")(partial(eq, artistsort)), collection))

        # Get HTML page and return it to the browser.
        discs = iter(self.playeddiscs)
        if artistsort is not None:
            discs = filter(attrgetter_("artistsort")(partial(eq, artistsort)), discs)
        mapping = set((disc.played_year_month, format_date(LOCAL.localize(disc.played), template="$month $Y")) for disc in discs)  # type: Set[Tuple[int, str]]
        kwargs = {"body": "view1",
                  "mapping": dict(mapping),
                  "page": "playeddiscsview",
                  "scripts": self.SCRIPTS.get("view1"),
                  "sheets": self.SHEETS.get("view1"),
                  "template": self.TEMPLATES["playeddiscsview"],
                  "title": "played discs",
                  "view": view,
                  "views": views}
        return self.get_page(iter(collection), **kwargs)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getcovers(self, collection: str, coversperpage: str = "32", start: str = "0"):
        """
        Get more digital audio albums covers from AJAX request.

        :param collection:
        :param coversperpage: Number of displayed covers per page.
        :param start: Number of the first displayed cover.
        :return: JSON object enumerating retrieved covers into an HTML structure.
        """
        mapping = {"digitalalbums": self.digitalalbums, "playeddiscs": self.playeddiscs, "rippeddiscs": self.rippeddiscs}
        beg = int(start)
        end = int(start) + int(coversperpage)
        return {"covers": self.TEMPLATE.get_template(self.TEMPLATES["getdigitalalbums"]).render(content=islice(self.sort_collection(mapping[collection], *self.SORT_SEQUENCE[collection]), beg, end))}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def gettotalitems(self, collection: str) -> Mapping[str, int]:
        """
        Get total items from collection using an AJAX request.

        :return: JSON object storing retrieved total.
        """
        mapping = {"digitalalbums": self.digitalalbums, "playeddiscs": self.playeddiscs, "rippeddiscs": self.rippeddiscs}
        return {"covers": len(mapping[collection])}

    # ------------------------------
    # Ripped discs grouped by month.
    # ------------------------------
    @cherrypy.expose
    def rippeddiscsviewbymonth(self, month: Optional[str] = None) -> Any:
        """
        Render ripped audio discs grouped by ripping month.

        :param month: Requested ripping month.
        :return: HTML template rendered with CherryPy.
        """
        mapping = set((disc.ripped_year_month, format_date(LOCAL.localize(disc.ripped), template="$month $Y")) for disc in self.rippeddiscs)  # type: Set[Tuple[int, str]]
        collection = list(self.sort_collection(self.rippeddiscs, *[("artistsort", False), ("ripped", True), ("ripped_year_month", True)]))  # type: Sequence[Any]
        if month is not None:
            collection = list(filter(attrgetter_("ripped_year_month")(partial(eq, int(month))), collection))
        kwargs = {"body": "view2",
                  "bold": month,
                  "browser": OrderedDict(sorted(mapping, key=itemgetter(0), reverse=True)),
                  "link": ("month", "month"),
                  "scripts": self.SCRIPTS.get("view2"),
                  "sheets": self.SHEETS.get("view2"),
                  "template": self.TEMPLATES["rippeddiscsviewbymonth"],
                  "title": "ripped discs",
                  "view": "months",
                  "views": []}
        return self.get_page(iter((key, list(group)) for key, group in groupby(collection, key=attrgetter("ripped_year_month"))), **kwargs)

    # -----------------------------
    # Ripped discs grouped by year.
    # -----------------------------
    @cherrypy.expose
    def rippeddiscsviewbyyear(self, year: Optional[str] = None) -> Any:
        """
        Render ripped audio discs grouped by ripping year.

        :param year: Requested ripping year.
        :return: HTML template rendered with CherryPy.
        """
        mapping = set((disc.ripped_year, format_date(LOCAL.localize(disc.ripped), template="$Y")) for disc in self.rippeddiscs)  # type: Set[Tuple[int, str]]
        collection = list(self.sort_collection(self.rippeddiscs, *[("artistsort", False), ("ripped", True), ("ripped_year", True)]))  # type: Sequence[Any]
        if year is not None:
            collection = list(filter(attrgetter_("ripped_year")(partial(eq, int(year))), collection))
        kwargs = {"body": "view2",
                  "bold": year,
                  "browser": OrderedDict(sorted(mapping, key=itemgetter(0), reverse=True)),
                  "link": ("year", "year"),
                  "scripts": self.SCRIPTS.get("view2"),
                  "sheets": self.SHEETS.get("view2"),
                  "template": self.TEMPLATES["rippeddiscsviewbyyear"],
                  "title": "ripped discs",
                  "view": "years",
                  "views": []}
        return self.get_page(iter((key, list(group)) for key, group in groupby(collection, key=attrgetter("ripped_year"))), **kwargs)

    # -------------------------------
    # Ripped discs grouped by artist.
    # -------------------------------
    @cherrypy.expose
    def rippeddiscsviewbyartist(self, artistsort: Optional[str] = None) -> Any:
        """
        Render ripped audio discs grouped by artist.

        :param artistsort: Requested artist.
        :return: HTML template rendered with CherryPy.
        """
        mapping = set((disc.artistsort, disc.artist) for disc in self.rippeddiscs)  # type: Set[Tuple[str, str]]
        collection = list(self.sort_collection(self.rippeddiscs, *[("ripped", True), ("artistsort", False)]))  # type: Sequence[Any]
        if artistsort is not None:
            collection = list(filter(attrgetter_("artistsort")(partial(eq_string_, artistsort, sensitive=True)), collection))
        kwargs = {"body": "view2",
                  "bold": artistsort,
                  "browser": OrderedDict(sorted(mapping, key=itemgetter(0), reverse=True)),
                  "link": ("artist", "artistsort"),
                  "scripts": self.SCRIPTS.get("view2"),
                  "sheets": self.SHEETS.get("view2"),
                  "template": self.TEMPLATES["rippeddiscsviewbyartist"],
                  "title": "ripped discs",
                  "view": "artists",
                  "views": []}
        return self.get_page(iter((key, list(group)) for key, group in groupby(collection, key=attrgetter("artistsort"))), **kwargs)

    # ----------------------------
    # Ripped CDs grouped by genre.
    # ----------------------------
    @cherrypy.expose
    def rippeddiscsviewbygenre(self, genre: Optional[str] = None) -> Any:
        """
        Render ripped audio discs grouped by artist.

        :param genre: Requested artist.
        :return: HTML template rendered with CherryPy.
        """
        mapping = set((disc.genre, disc.genre) for disc in self.rippeddiscs)  # type: Set[Tuple[str, str]]
        collection = list(self.sort_collection(self.rippeddiscs, *[("ripped", True), ("genre", False)]))  # type: Sequence[Any]
        if genre is not None:
            collection = list(filter(attrgetter_("genre")(partial(eq_string_, genre, sensitive=False)), collection))
        kwargs = {"body": "view2",
                  "bold": genre,
                  "browser": OrderedDict(sorted(mapping, key=itemgetter(0), reverse=True)),
                  "link": ("genre", "genre"),
                  "scripts": self.SCRIPTS.get("view2"),
                  "sheets": self.SHEETS.get("view2"),
                  "template": self.TEMPLATES["rippeddiscsviewbygenre"],
                  "title": "ripped discs",
                  "view": "genres",
                  "views": []}
        return self.get_page(iter((key, list(group)) for key, group in groupby(collection, key=attrgetter("genre"))), **kwargs)

    # --------------------
    # Ripped artists view.
    # --------------------
    # @cherrypy.expose
    # def rippedartistsview(self):
    #     """
    #     Render ripped artists into a cloud view.
    #
    #     :return: HTML template rendered with CherryPy.
    #     """
    #     rippedcd = sorted(sorted(self.rippedcd, key=itemgetter(2), reverse=True), key=itemgetter(0), reverse=True)
    #     return self.TEMPLATE.rippedartistsview.render(menu=self.TEMPLATE.menu.render(months=self.months),
    #                                                   current=format_date(UTC.localize(datetime.datetime.utcnow()).astimezone(LOCAL), template="$Y$m"),
    #                                                   content=[(key, self.getclass(len(list(group)))) for key, group in groupby_(sorted(tup[3].artist for tup in rippedcd))])

    # ----------------------
    # Ripped CDs statistics.
    # ----------------------
    # @cherrypy.expose
    # def rippedcdstatistics(self, view="year"):
    #     """
    #     Render statistics about ripped audio CDs.
    #
    #     :param view: Requested view (artist, genre, month or year).
    #     :return: HTML template rendered with CherryPy.
    #     """
    #     content, detail, firstnt, secondnt = None, None, collections.namedtuple("firstnt", "href id keys count"), collections.namedtuple("secondnt", "view tableid header detail")
    #
    #     # 1. Total by year in descending order.
    #     if view == "year":
    #         detail = [firstnt._make(("rippedcdviewby{0}?{0}={1}".format(view.lower(), k[0]),
    #                                  k[0],
    #                                  k,
    #                                  len(list(g)))) for k, g in groupby_(sorted([(format_date(item[2], template="$Y"),
    #                                                                              format_date(item[2], template="$Y")) for item in self.rippedcd], key=itemgetter(0), reverse=True))]
    #         content = secondnt._make((view, "table1", (view, "count"), detail))
    #
    #     # 2. Total by month in descending order.
    #     elif view == "month":
    #         detail = [firstnt._make(("rippedcdviewby{0}?{0}={1}".format(view.lower(), k[0]),
    #                                  k[0],
    #                                  k,
    #                                  len(list(g)))) for k, g in groupby_(sorted([(format_date(item[2], template="$Y$m"),
    #                                                                              format_date(item[2], template="$month $Y")) for item in self.rippedcd], key=itemgetter(0), reverse=True))]
    #         content = secondnt._make((view, "table2", (view, "count"), detail))
    #
    #     # 3. Total by artist in ascending order.
    #     elif view == "artist":
    #         detail = [firstnt._make(("rippedcdviewby{0}?{0}={1}".format(view.lower(), self.artistsort_mapping.get(k[0], k[0])),
    #                                  k[0],
    #                                  k,
    #                                  len(list(g)))) for k, g in groupby_(sorted([(item[3].artistsort,
    #                                                                              item[3].artistsort) for item in self.rippedcd if item[3].artistsort], key=itemgetter(0)))]
    #         content = secondnt._make((view, "table3", (view, "count"), detail))
    #
    #     # 4. Total by genre in ascending order.
    #     elif view == "genre":
    #         detail = [firstnt._make(("rippedcdviewby{0}?{0}={1}".format(view.lower(), k[0]),
    #                                  k[0],
    #                                  k,
    #                                  len(list(g)))) for k, g in groupby_(sorted([(item[3].genre, item[3].genre) for item in self.rippedcd], key=itemgetter(0)))]
    #         content = secondnt._make((view, "table3", (view, "count"), detail))
    #
    #     # 5. Return HTML page.
    #     return self.TEMPLATE.rippedcdstatistics.render(body="rippedcdstatistics",
    #                                                    menu=self.TEMPLATE.menu.render(months=self.months),
    #                                                    stylesheets=["stylesheets/shared.css"],
    #                                                    content={"content": content,
    #                                                             "scripts": ["frameworks/jquery.js",
    #                                                                         "frameworks/tablesorter.js",
    #                                                                         "scripts/rippedcdstatistics.js",
    #                                                                         "scripts/common.js"]})

    # -----------------------
    # Ripped CDs maintenance.
    # -----------------------

    # 1. Display ripped CDs logs.
    # @cherrypy.expose
    # def rippedcdlogs(self, page="1"):
    #     """
    #     Render ripped audio CDs sorted by ascending row ID.
    #
    #     :param page: Requested page.
    #     :return: HTML template rendered by CherryPy.
    #     """
    #     firstnt = collections.namedtuple("firstnt", "logs scripts")
    #     rippedcd = sorted(self.rippedcd, key=lambda i: i[3].rowid)
    #     pages = list(enumerate(zip_longest(*[iter([(item[3], item[2]) for item in rippedcd])] * 8), start=1))
    #     return self.TEMPLATE.rippedcdlogs.render(body="rippedcdlogs",
    #                                              menu=self.TEMPLATE.menu.render(months=self.months),
    #                                              stylesheets=["stylesheets/shared.css",
    #                                                           "stylesheets/rippedcdlogs.css"],
    #                                              maintitle="Ripped Audio CDs",
    #                                              content=firstnt._make((list(filter(lambda i: i[0] == int(page), pages)), ["frameworks/jquery.js", "scripts/rippedcdlogs.js", "scripts/common.js"])),
    #                                              pages_cfg=self.pages_configuration_1(seq=pages, pag=page))

    # 2. Create/Update ripped CD log.
    # @cherrypy.expose
    # @cherrypy.tools.json_out()
    # def rippedcdlog(self, mode="create", rowid=None):
    #     """
    #     Render ripped audio CD tags for maintenance (delete or update).
    #
    #     :param mode: Maintenance mode.
    #     :param rowid: Ripped audio CD row ID.
    #     :return: Dialog box to run requested maintenance mode or to fix an incorrect tag.
    #     """
    # pass

    # Create log.
    # if mode == "create":
    #     return {"dialog": self.TEMPLATE.rippedcdlog.render(mode="create", genres=[(k, v, v.lower() == "rock") for k, v in self.genres_mapping.items()])}

    # Update log.
    # elif mode == "update" and rowid:
    #     if int(rowid) > 0:
    #         rippedcdlog = list(selectlog(int(rowid), db=self.database))[0]
    #         return {"dialog": self.TEMPLATE.rippedcdlog.render(mode=mode, content=rippedcdlog, genres=[(k, v, v.lower() == rippedcdlog.genre.lower()) for k, v in self.genres_mapping.items()])}

    # 3. Check ripped CD log.
    # @cherrypy.expose
    # @cherrypy.tools.json_out()
    # def checkrippedcdlog(self, action, **tags):
    #
    #     template = {"dialog": self.TEMPLATE.dialogbox2.render(box={"head": "Delete log", "body": "Would you like to delete the selected log?"})}
    #     if action.lower() in ["create", "update"]:
    #         template = {"dialog": self.TEMPLATE.dialogbox2.render(box={"head": "Update log", "body": "Would you like to update the selected log?"})}
    #         albumsort_rex1 = re.compile(r"^[12]\.({0})({1})({2})\.\d$".format(DFTYEARREGEX, DFTMONTHREGEX, DFTDAYREGEX))
    #         albumsort_rex2 = re.compile(r"^[12]\.({0})0000\.\d$".format(DFTYEARREGEX))
    #         albumsort_rex3 = re.compile(r"^[12]\.({0})[\d.]+$".format(DFTYEARREGEX))
    #         year_rex = re.compile(r"^(?:{0})$".format(DFTYEARREGEX))
    #         upc_rex = re.compile(UPCREGEX)
    #         while True:
    #
    #             #  A.1. Check albumsort.
    #             if not any([albumsort_rex1.match(tags["albumsort"]), albumsort_rex2.match(tags["albumsort"])]):
    #                 template = {"dialog": self.TEMPLATE.dialogbox1.render(box={"head": "An error has been detected", "body": "{0} is not a correct Albumsort tag.".format(tags["albumsort"])})}
    #                 break
    #
    #             # A.2. Check year.
    #             if not year_rex.match(tags["year"]):
    #                 template = {"dialog": self.TEMPLATE.dialogbox1.render(box={"head": "An error has been detected", "body": "{0} is not a correct Year tag.".format(tags["year"])})}
    #                 break
    #
    #             # A.3. Check coherence between albumsort and year.
    #             match = albumsort_rex3.match(tags["albumsort"])
    #             if match.group(1) != tags["year"]:
    #                 template = {"dialog": self.TEMPLATE.dialogbox1.render(box={"head": "An error has been detected", "body": "Albumsort and Year are not coherent."})}
    #                 break
    #
    #             # A.4. Check UPC.
    #             if not upc_rex.match(tags["upc"]):
    #                 template = {"dialog": self.TEMPLATE.dialogbox1.render(box={"head": "An error has been detected", "body": "{0} is not a correct UPC tag.".format(tags["upc"])})}
    #                 break
    #
    #             # A.5. Check ripping Unix epoch time.
    #             if not re.match(r"^\d{10}$", tags["ripped"]):
    #                 template = {"dialog": self.TEMPLATE.dialogbox1.render(box={"head": "An error has been detected", "body": "{0} is not a correct Unix epoch time.".format(tags["ripped"])})}
    #                 break
    #             try:
    #                 validyear(format_date(LOCAL.localize(datetime.datetime.fromtimestamp(int(tags["ripped"]))), template="$Y"))
    #             except ValueError:
    #                 template = {"dialog": self.TEMPLATE.dialogbox1.render(box={"head": "An error has been detected", "body": "{0} is not a correct Unix epoch time.".format(tags["ripped"])})}
    #                 break
    #
    #             # A.6. Create log.
    #             if action.lower() == "create":
    #                 template = {"dialog": self.TEMPLATE.dialogbox2.render(box={"head": "Create log", "body": "Would you like to create the log?"})}
    #                 break
    #
    #             break

    # return template

    # 4. Store ripped CD log.
    # @cherrypy.expose
    # @cherrypy.tools.json_out()
    # def storerippedcdlog(self, action, rowid=None, **tags):
    #
    #     #  A. Update log.
    #     if action.lower() == "update":
    #         new_tags = dict(tags)
    #         new_tags["genre"] = self.genres_mapping[tags["genre"]]
    #         new_tags["year"] = int(tags["year"])
    #         return {"dialog": self.TEMPLATE.dialogbox1.render(box={"head": "Update log", "body": "{0:>2d} record(s) successfully updated.".format(updatelog(int(rowid), db=self.database,
    #         **new_tags))})}
    #
    #     # B. Delete log.
    #     if action.lower() == "delete":
    #         return {"dialog": self.TEMPLATE.dialogbox1.render(box={"head": "Delete log", "body": "{0:>2d} record(s) successfully deleted.".format(deleterippedcd(int(rowid), db=self.database))})}
    #
    #     # C. Create log.
    #     if action.lower() == "create":
    #         new_tags = dict(tags)
    #         new_tags["genre"] = self.genres_mapping[tags["genre"]]
    #         new_tags["year"] = int(tags["year"])
    #         return {"dialog": self.TEMPLATE.dialogbox1.render(box={"head": "Create log", "body": "{0:>2d} record(s) successfully created.".format(insertfromargs(db=self.database, **new_tags))})}

    # @cherrypy.expose
    # @cherrypy.tools.json_out()
    # def getdialogbox(self, head, body, template="TEMPLATE.dialogbox2"):
    #     templates = {"TEMPLATE.dialogbox1": self.TEMPLATE.dialogbox1, "TEMPLATE.dialogbox2": self.TEMPLATE.dialogbox2}
    #     return {"dialog": templates[template].render(box={"head": head, "body": body})}

    # @cherrypy.expose
    # def rippedcdlogsreport(self, output, outfile=None):
    #     outputs = list(output)
    #     if isinstance(output, str):
    #         outputs = list((output,))
    #     for out in outputs:
    #         if out.lower() == "json":
    #             if not outfile:
    #                 outfile = self.JSONOUTFILE
    #             self.jsonreport(self.rippedcd, outfile)
    # elif o.lower() == "xml":
    #     toto1(self.XMLOUTFILE)
    # elif o.lower() == "log":
    #     toto2()

    # ------------------------------------------------------
    # Display digital audio tracks by both artist and album.
    # ------------------------------------------------------
    # @cherrypy.expose
    # def digitalaudiotracksbyartist(self, artistid=None, prevpage=None):
    #
    #     #  1. Get digital albums list.
    #     reflist = self.digitalalbums
    #     if artistid:
    #         reflist = list(filter(lambda i: i[1][2:-13].lower() == artistid.lower(), self.digitalalbums))
    #     reflist = sorted([item[1] for item in reflist])
    #
    #     #  2. Return HTML page.
    #     return self.TEMPLATE.digitalaudiotracksbyartist.render(menu=self.TEMPLATE.menu.render(months=self.months),
    #                                                            current=format_date(UTC.localize(datetime.datetime.utcnow()).astimezone(LOCAL), template="$Y$m"),
    #                                                            content=self.gettracks(*reflist, artists=self.digitalartists, db=self.database, **self.digitalalbums_mapping),
    #                                                            previous_page=prevpage)

    # --------------------------------------
    # Display digital audio tracks by album.
    # --------------------------------------
    # @cherrypy.expose
    # def digitalaudiotracksbyalbum(self, albumid, prevpage=None):
    #     return self.TEMPLATE.digitalaudiotracksbyalbum.render(menu=self.TEMPLATE.menu.render(months=self.months),
    #                                                           current=format_date(UTC.localize(datetime.datetime.utcnow()).astimezone(LOCAL), template="$Y$m"),
    #                                                           content=self.gettracks(albumid, artists=self.digitalartists, db=self.database, **self.digitalalbums_mapping),
    #                                                           previous_page=prevpage)

    # -----------------------------
    # Display digital audio albums.
    # -----------------------------
    # @cherrypy.expose
    # def digitalalbums_view(self, page="1"):
    #     """
    #     Render digital audio albums collection.
    #
    #     :param page: Requested page.
    #     :return: HTML template rendered by CherryPy.
    #     """
    #
    #     # Available albums in digital audio base.
    #     digitalalbums = sorted([(tup[0].rowid, tup[0].albumid, tup[0].artist, tup[0].year, tup[0].album) for tup in self.digitalalbums], key=itemgetter(1))
    #
    #     # Pages configuration.
    #     pages = list(enumerate(zip_longest(*[iter(digitalalbums)] * 30), start=1))
    #
    #     # Return HTML page.
    #     return self.TEMPLATE.digitalalbums_view.render(body="digitalalbums",
    #                                                    menu=self.TEMPLATE.menu.render(months=self.months),
    #                                                    stylesheets=["stylesheets/shared.css",
    #                                                                 "stylesheets/digitalalbums.css"],
    #                                                    content={"albums": list(filter(lambda i: i[0] == int(page), pages)),
    #                                                             "page_cfg": self.pages_configuration_1(seq=pages, pag=page),
    #                                                             "page_cur": page,
    #                                                             "scripts": ["frameworks/jquery.js",
    #                                                                         "scripts/digitalalbums.js",
    #                                                                         "scripts/common.js"]})

    # ------------------------------------
    # Display played digital audio albums.
    # ------------------------------------
    # @cherrypy.expose
    # def digitalalbums_playedview(self):
    #     """
    #     Render recently played digital audio albums ordered by descending timestamp.
    #
    #     :return: HTML template rendered by CherryPy.
    #     """
    #
    #     album = collections.namedtuple("album", "period lastplayed ripped artistsort albumsort artist year album genre")
    #
    #     # Last played audio CDs list.
    #     lastplayedalbums = filter(lambda i: self.getplayedperiod(UTC.localize(i.utc_played).astimezone(LOCAL))[0], self.lastplayedalbums)
    #     lastplayedalbums = [(self.getplayedperiod(UTC.localize(album.utc_played).astimezone(LOCAL))[1],
    #                          format_date(UTC.localize(album.utc_played).astimezone(LOCAL), template="$day $d $month $Y"),
    #                          UTC.localize(album.utc_played).astimezone(LOCAL),
    #                          album.albumid[2:-13],
    #                          album.albumid[-12:],
    #                          album.artist,
    #                          album.year,
    #                          album.album,
    #                          album.genre) for album in lastplayedalbums]
    #     lastplayedalbums = [album._make(i) for i in lastplayedalbums]
    #     lastplayedalbums = sorted(sorted([(i[0], i[1], i[2], i) for i in lastplayedalbums], key=itemgetter(2), reverse=True), key=itemgetter(0))

    # Return HTML page.
    # return self.TEMPLATE.digitalalbums_playedview.render(menu=self.TEMPLATE.menu.render(months=getmonths(db=self._database)),
    #                                                      current=dateformat(UTC.localize(datetime.datetime.utcnow()).astimezone(LOCAL), "$Y$m"),
    #                                                      maintitle="Played Audio CDs",
    #                                                      id="refresh-2",
    #                                                      content=[(key, list(group)) for key, group in groupby_(lastplayedalbums, key=lambda i: (i[0], self.PERIODS[i[0]]))])

    # @cherrypy.expose
    # @cherrypy.tools.json_out()
    # def get_digitalalbums_playedcount(self, albumid):
    #     return {"count": list(get_albumheader(self.database, albumid))[0].count}

    # -----------------------------------------------
    # Display played digital audio albums statistics.
    # -----------------------------------------------
    # @cherrypy.expose
    # def digitalalbums_playedstatistics(self):
    #     """
    #     Render statistics about recently played digital audio albums.
    #
    #     :return: HTML template rendered with CherryPy.
    #     """
    #     return self.TEMPLATE.digitalalbums_playedstatistics.render(body="digitalalbumsstatistics",
    #                                                                menu=self.TEMPLATE.menu.render(months=self.months),
    #                                                                stylesheets=["stylesheets/shared.css",
    #                                                                             "stylesheets/digitalalbumsstatistics.css"],
    #                                                                content={"content": self.lastplayedalbums,
    #                                                                         "scripts": ["frameworks/jquery.js",
    #                                                                                     "frameworks/tablesorter.js",
    #                                                                                     "scripts/digitalalbumsstatistics.js",
    #                                                                                     "scripts/common.js"]})

    # ----------------------------------------
    # Update digital audio albums played date.
    # ----------------------------------------
    # @cherrypy.expose
    # @cherrypy.tools.json_in(content_type="application/x-www-form-urlencoded")
    # def update_digitalalbums_playeddate(self):
    #     """
    #     Update played date from AJAX request.
    #
    #     :return: None.
    #     """
    #
    #     #  1. Get input data.
    #     data = cherrypy.request.json
    #
    #     #  2. Log selected record(s) unique ID.
    #     logger = logging.getLogger("{0}.updatelastplayeddate".format(__name__))
    #     for row in data["rows"]:
    #         logger.debug(row)
    #
    #     # 3. Update matching record(s).
    #     results = updatelastplayeddate(*list(map(int, data["rows"])), db=data.get("database", self.database))
    #
    #     #  4. Log results.
    #     logger.debug(results)

    # ----------------------------
    # Display digital audio files.
    # ----------------------------
    # @cherrypy.expose
    # def digitalaudiofiles(self, start="1", linesperpage="1000", **filters):
    #
    #     #  1. Get files list.
    #     data = self.getaudiofiles("digitalaudiofiles", self.audiofiles, **filters)
    #     files = [(index, fil, created) for index, (fil, created) in enumerate([(item[0], item[1]) for item in data["files"]], 1)]
    #
    #     #  2. Set dropdown lists.
    #
    #     #  2.a. Letters.
    #     letters = data["letters"]
    #     letters.insert(0, ("all", "All"))
    #     letters = [(a, b, a == filters.get("letter", "all")) for a, b in letters]
    #     letters = self.TEMPLATE.dropdownlist.render(name="letter", values=letters, select=True)
    #
    #     #  2.b. Artists.
    #     artists = data["artists"]
    #     artists.insert(0, ("all", "All"))
    #     artists = [(a, b, a == filters.get("artist", "all")) for a, b in artists]
    #     artists = self.TEMPLATE.dropdownlist.render(name="artist", values=artists, select=True)
    #
    #     #  2.c. Extensions.
    #     extensions = data["extensions"]
    #     extensions.insert(0, ("all", "All"))
    #     extensions = [(a, b, a == filters.get("extension", "all")) for a, b in extensions]
    #     extensions = self.TEMPLATE.dropdownlist.render(name="extension", values=extensions, select=True)
    #
    #     #  3. Return HTML page.
    #     return self.TEMPLATE.digitalaudiofiles.render(menu=self.TEMPLATE.menu.render(months=self.months),
    #                                                   current=format_date(UTC.localize(datetime.datetime.utcnow()).astimezone(LOCAL), template="$Y$m"),
    #                                                   content={"letters": letters,
    #                                                            "artists": artists,
    #                                                            "extensions": extensions,
    #                                                            "files": self.subset(int(start), int(linesperpage), files),
    #                                                            "pages": list(enumerate(accumulate(self.pages_configuration_2(len(files), int(linesperpage))), 1)),
    #                                                            "linesperpage": [(a, int(a) == int(linesperpage)) for a in self.LINESPERPAGE]})
    #
    # @cherrypy.expose
    # @cherrypy.tools.json_out()
    # def get_digitalaudiofiles(self, **idata):
    #
    #     #  1. Get input data.
    #     start = int(idata.get("start", "1"))
    #     linesperpage = int(idata.get("linesperpage", "1000"))
    #
    #     #  2. Get files list.
    #     odata = self.getaudiofiles("getmoredigitalaudiofiles",
    #                                self.audiofiles,
    #                                letter=idata.get("letter", "all"),
    #                                artist=idata.get("artist", "all"),
    #                                extension=idata.get("extension", "all"))
    #     files = [(index, fil, created) for index, (fil, created) in enumerate([(item[0], item[1]) for item in odata["files"]], 1)]
    #
    #     #  3. Return files
    #     return {"files": self.subset(start, linesperpage, files)}
    #
    # @cherrypy.expose
    # @cherrypy.tools.json_out()
    # def getartists(self, letter="all"):
    #
    #     odata = self.getaudiofiles("getartists", self.audiofiles, letter=letter)
    #     artists = odata["artists"]
    #     artists.insert(0, ("all", "All"))
    #     extensions = odata["extensions"]
    #     extensions.insert(0, ("all", "All"))
    #     return {"artists": self.TEMPLATE.dropdownlist.render(name="artist", values=[(a, b, a == "all") for a, b in artists], select=False),
    #             "extensions": self.TEMPLATE.dropdownlist.render(name="extension", values=[(a, b, a == "all") for a, b in extensions], select=False)}
    #
    # @cherrypy.expose
    # @cherrypy.tools.json_out()
    # def getextensions(self, artist="all"):
    #
    #     odata = self.getaudiofiles("getextensions", self.audiofiles, artist=artist)
    #     extensions = odata["extensions"]
    #     extensions.insert(0, ("all", "All"))
    #     return {"extensions": self.TEMPLATE.dropdownlist.render(name="extension", values=[(a, b, a == "all") for a, b in extensions], select=False)}
    #
    # # --------------
    # # Class methods.
    # # --------------
    # @classmethod
    # def getaudiofiles(cls, origin, collection, **filters):
    #
    #     mapping = {"all": None}
    #
    #     #  0.a. Décorer "checkfile" à l'aide de "checkfile_fromtuple" pour pouvoir traiter le premier élément d'un tuple ("checkfile" doit reçevoir en effet une chaîne de caractères
    #     #       en qualité de premier paramètre).
    #     #       "checkfile_fromtuple" retourne la chaîne de caractères extraite par l'expression régulière enveloppée dans la fonction reçue en qualité de deuxième paramètre.
    #     checkfile = cls.checkfile_fromtuple(cls.checkfile)
    #
    #     #  0.b. Définir des fonctions ne pouvant reçevoir qu'un tuple. Elles pourront ainsi être utilisées comme clé pour les tris et les regroupements.
    #     grab_artistfirstletter = partial(checkfile, rex_func=cls.grab_artistfirstletter)
    #     grab_artist = partial(checkfile, rex_func=cls.grab_artist)
    #
    #     #  1. Set global files list sorted by letter, artist, extension and file.
    #     olist = collection
    #
    #     #  2. Set available letters list, available artists list and available extensions list.
    #     letters = sorted([(letter.lower(), letter.upper()) for letter in set([letter for letter, group in groupby_(olist, key=grab_artistfirstletter)])], key=itemgetter(1))
    #     artists = sorted([(artist.replace(" ", "_"), artist) for artist in set([artist for artist, group in groupby_(olist, key=grab_artist)])], key=itemgetter(1))
    #     extensions = sorted([(extension.lower(), extension.upper()) for extension in set([extension for extension, group in groupby_(olist, key=itemgetter(2))])], key=itemgetter(1))
    #
    #     #  3. Get input filters.
    #
    #     #  3.a. Letter.
    #     let = filters.get("letter", "all")
    #     let = mapping.get(let, let)
    #
    #     #  3.b. Artist.
    #     art = filters.get("artist", "all")
    #     art = mapping.get(art, art)
    #
    #     #  3.c. Extension.
    #     ext = filters.get("extension", "all")
    #     ext = mapping.get(ext, ext)
    #
    #     #  4. Apply input filters.
    #     if let:
    #         olist = list(chain.from_iterable([list(group) for letter, group in groupby_(olist, key=grab_artistfirstletter) if letter.lower() == let.lower()]))
    #         artists = sorted([(artist.replace(" ", "_"), artist) for artist in set([artist for artist, group in groupby_(olist, key=grab_artist)])], key=itemgetter(1))
    #         extensions = sorted([(extension.lower(), extension.upper()) for extension in set([extension for extension, group in groupby_(olist, key=itemgetter(2))])], key=itemgetter(1))
    #     if art:
    #         olist = list(chain.from_iterable([list(group) for artist, group in groupby_(olist, key=grab_artist) if artist.replace(" ", "_").lower() == art.lower()]))
    #         extensions = sorted([(extension.lower(), extension.upper()) for extension in set([extension for extension, group in groupby_(olist, key=itemgetter(2))])], key=itemgetter(1))
    #     if ext:
    #         olist = list(chain.from_iterable([list(group) for extension, group in groupby_(olist, key=itemgetter(2)) if extension.lower() == ext.lower()]))
    #
    #     # 5. Return files list.
    #     if origin == "digitalaudiofiles":
    #         return {"files": olist, "letters": letters, "artists": artists, "extensions": extensions}
    #     if origin == "getmoredigitalaudiofiles":
    #         return {"files": olist}
    #     if origin == "getartists":
    #         return {"artists": artists, "extensions": extensions}
    #     if origin == "getextensions":
    #         return {"extensions": extensions}
    #
    # # ---------------
    # # Static methods.
    # # ---------------
    # @staticmethod
    # def grab_artistfirstletter(stg):
    #     match = re.search(r"^[^\\]+\\([a-z])\\", stg, re.IGNORECASE)
    #     if match:
    #         return True, match.group(1)
    #     return False, None
    #
    # @staticmethod
    # def grab_artist(stg):
    #     match = re.search(r"^(?:[^\\]+\\){2}([^\\]+)\\", stg)
    #     if match:
    #         return True, match.group(1)
    #     return False, None
    #
    # @staticmethod
    # def grab_year(stg):
    #     match = re.search(r"^(?:[^\\]+\\){{3}}(?:[12]\\)?({0})\b".format(DFTYEARREGEX), stg)
    #     if match:
    #         return True, match.group(1)
    #     return False, None
    #
    # @staticmethod
    # def grab_month(stg):
    #     match = re.search(r"\b({0})\b.\b({1})\b(?:[^\\]+\\)".format(DFTMONTHREGEX, DFTDAYREGEX), stg)
    #     if match:
    #         return True, "{0}{1}".format(match.group(1), match.group(2))
    #     return True, "0000"
    #
    # @staticmethod
    # def checkfile(stg, rex_func):
    #     return rex_func(stg)
    #
    # @staticmethod
    # def checkfile_fromtuple(func):
    #
    #     def wrapper(tup, rex_func):
    #         return func(tup[0], rex_func)[1]
    #
    #     return wrapper
    #
    # @staticmethod
    # def gettracks(*albumid, db, artists, **kwargs):
    #
    #     #  1. Get digital albums list.
    #     reflist = chain.from_iterable([[(row.albumid,
    #                                      row.discid,
    #                                      row.trackid,
    #                                      row.title) for row in genobj if row] for genobj in map(get_track, repeat(db), albumid)])
    #
    #     #  2. Sort digital albums by "artistsort", "albumid", "discid", "trackid".
    #     reflist = sorted(sorted(sorted(sorted(reflist, key=itemgetter(2)), key=itemgetter(1)), key=lambda i: i[0]), key=lambda i: i[0][2:-13])
    #
    #     #  3. Group digital albums by "artistsort", "albumid", "discid", "trackid".
    #     return [(
    #         (artistsort, artists.get(artistsort, artistsort)),
    #         [(
    #             (albumid, kwargs[albumid]),
    #             [(
    #                 discid,
    #                 [(
    #                     trackid,
    #                     list(sssubgroup)
    #                 ) for trackid, sssubgroup in groupby_(list(ssubgroup), key=lambda i: i[2])]
    #             ) for discid, ssubgroup in groupby_(list(subgroup), key=lambda i: i[1])]
    #         ) for albumid, subgroup in groupby_(list(group), key=lambda i: i[0])]
    #     ) for artistsort, group in groupby_(reflist, key=lambda i: i[0][2:-13])]
    #
    # @staticmethod
    # def getclass(count):
    #     htmlclass = None
    #     if count > 0:
    #         htmlclass = "c0"
    #     if count > 1:
    #         htmlclass = "c1"
    #     if count > 2:
    #         htmlclass = "c2"
    #     if count > 4:
    #         htmlclass = "c3"
    #     if count > 6:
    #         htmlclass = "c4"
    #     if count > 9:
    #         htmlclass = "c5"
    #     if count > 14:
    #         htmlclass = "c6"
    #     if count > 19:
    #         htmlclass = "c7"
    #     return htmlclass
    #
    # @staticmethod
    # def getplayedperiod(dtobj):
    #
    #     oneday = datetime.date.today() - datetime.timedelta(days=1)
    #     sevendays = datetime.date.today() - datetime.timedelta(days=7)
    #     fourteendays = datetime.date.today() - datetime.timedelta(days=14)
    #     twentyonedays = datetime.date.today() - datetime.timedelta(days=21)
    #     ninetydays = datetime.date.today() - datetime.timedelta(days=90)
    #     status = False, None
    #
    #     # CD played on day D.
    #     if dtobj.date() == datetime.date.today():
    #         status = True, "0"
    #
    #     # CD played on day D-1.
    #     if dtobj.date() == oneday:
    #         status = True, "1"
    #
    #     # CD played between day D-7 and day D-2.
    #     if dtobj.date() < oneday:
    #         status = True, "2"
    #
    #     # CD played between day D-14 and day D-8.
    #     if dtobj.date() < sevendays:
    #         status = True, "3"
    #
    #     # CD played between day D-21 and day D-15.
    #     if dtobj.date() < fourteendays:
    #         status = True, "4"
    #
    #     # CD played between day D-90 and day D-22.
    #     if dtobj.date() < twentyonedays:
    #         status = True, "5"
    #
    #     # Last played period older than day D-90.
    #     if dtobj.date() < ninetydays:
    #         status = False, None
    #
    #     # Return played period.
    #     return status
    #
    # @staticmethod
    # def pages_configuration_1(seq, pag):
    #     previouspage, nextpage = False, False
    #     if len(seq) > 1:
    #         if int(pag) > 1:
    #             previouspage = True
    #         if int(pag) < len(seq):
    #             nextpage = True
    #     return {"pages": list(range(1, len(seq) + 1)),
    #             "currentpage": int(pag),
    #             "previous": previouspage,
    #             "next": nextpage}
    #
    # @staticmethod
    # def pages_configuration_2(lines, linesperpage):
    #     pages = int(lines / linesperpage)
    #     if lines % linesperpage > 0:
    #         pages += 1
    #     pages = [linesperpage] * (pages - 1)
    #     pages.insert(0, 1)
    #     if len(pages) > 1:
    #         return pages
    #     return []
    #
    # @staticmethod
    # def subset(start, linesperpage, items):
    #     beg = start - 1
    #     if beg >= len(items):
    #         return []
    #     end = start + linesperpage - 1
    #     if end > len(items):
    #         return items[beg:]
    #     return items[beg:end]
    #
    # @staticmethod
    # def jsonreport(collection, outfile):
    #     keys = ["RIPPED", "ARTISTSORT", "ALBUMSORT", "ARTIST", "YEAR", "ALBUM", "GENRE", "BARCODE", "APPLICATION"]
    #     reflist = sorted([item[3] for item in collection], key=lambda i: i.rowid)
    #     reflist = [(item.rowid,
    #                 dict(zip(keys, (format_date(LOCAL.localize(item.ripped)),
    #                                 item.artistsort,
    #                                 item.albumsort,
    #                                 item.artist,
    #                                 item.year,
    #                                 item.album,
    #                                 item.upc,
    #                                 item.genre,
    #                                 item.application)))) for item in reflist]
    #     if reflist:
    #         with open(outfile, mode=WRITE, encoding=UTF8) as fp:
    #             json.dump([now(),
    #                        format_date(UTC.localize(datetime.datetime.utcnow()).astimezone(timezone("US/Eastern"))),
    #                        format_date(UTC.localize(datetime.datetime.utcnow()).astimezone(timezone("US/Pacific"))),
    #                        dict(reflist)], fp, indent=4, sort_keys=True, ensure_ascii=False)

    # A.6. Update log.
    # if action.lower() == "update":
    #
    #     #  A.6.a. New tags.
    #     new_tags = dict(tags)
    #     new_tags["genre"] = self.genres_mapping[tags["genre"]]
    #     new_tags["ripped"] = int(new_tags["ripped"])
    #     new_tags = sorted(new_tags.items(), key=itemgetter(0))
    #
    #     #  A.6.b. Current tags.
    #     cur_tags = sorted(self.rippedcdlog.items(), key=itemgetter(0))
    #
    #     #  A.6.c. Differences between new tags and current tags.
    #     differences = set(new_tags) - set(cur_tags)
    #     logger.debug("new tags    : {0}".format(new_tags))
    #     logger.debug("current tags: {0}".format(cur_tags))
    #     logger.debug("differences : {0}".format(list(differences)))
    #
    #     #  A.6.d. Update log if some differences have been found.
    #     if not differences:
    #         return {"dialog": self.TEMPLATE.dialogbox1.render(box={"head": "Update record", "body": "Any tag hasn't been changed. Can\'t update log."})}
    #     return {"dialog": self.TEMPLATE.dialogbox2.render(box={"head": "Update record", "body": "Would you like to update the selected log?"})}

    # return {"dialog": self.TEMPLATE.dialogbox2.render(box={"head": "Update log", "body": "Would you like to update the selected log?"})}
