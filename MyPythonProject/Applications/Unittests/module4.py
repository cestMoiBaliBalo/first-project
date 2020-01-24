# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import logging.config
import os
import shutil
import sys
import unittest
from collections import defaultdict
from contextlib import suppress
from datetime import datetime
from functools import partial, wraps
from itertools import filterfalse
from operator import contains, itemgetter
from pathlib import PurePath
from tempfile import TemporaryDirectory, mkdtemp
from typing import Optional, Tuple
from unittest.mock import Mock, PropertyMock, patch

import yaml

from ..AudioCD.shared import AudioGenres, albums, dump_audiotags_tojson, get_tagsfile, upsert_audiotags
from ..Tables.Albums.shared import defaultalbums, exist_albumid, get_albumidfromgenre, insert_albums_fromjson, update_defaultalbums, update_playeddisccount
from ..Tables.RippedDiscs.shared import get_total_rippeddiscs
from ..Tables.tables import DatabaseConnection, create_tables, drop_tables
from ..decorators import itemgetter_
from ..shared import DATABASE, LOCAL, UTC, UTF16, UTF8, copy, get_readabledate

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_THATFILE = PurePath(os.path.abspath(__file__))  # type: PurePath
basename, exists, join = os.path.basename, os.path.exists, os.path.join


# ===============
# Global classes.
# ===============
class CustomAudioGenres(AudioGenres):
    _genres = {}


class Changes(object):
    logger = logging.getLogger(f"{__name__}")

    def __init__(self, db=DATABASE):
        """

        :param db:
        """
        self._artists, self._albums, self._defautlalbums, self._bootlegalbums, self._livealbums, self._discs, self._rippeddiscs, self._bootlegdiscs, self._tracks, self._bonuses = defaultdict(int), \
                                                                                                                                                                                   defaultdict(int), \
                                                                                                                                                                                   defaultdict(int), \
                                                                                                                                                                                   defaultdict(int), \
                                                                                                                                                                                   defaultdict(int), \
                                                                                                                                                                                   defaultdict(int), \
                                                                                                                                                                                   defaultdict(int), \
                                                                                                                                                                                   defaultdict(int), \
                                                                                                                                                                                   defaultdict(int), \
                                                                                                                                                                                   defaultdict(int)
        self._database = db  # type: str
        self._changes = 0  # type: int
        self._db_album = None  # type: Optional[bool]
        self._db_bootleg = None  # type: Optional[bool]
        self._bonus = None  # type: Optional[str]
        self._bootlegdisc = None  # type: Optional[str]
        self._artistid = None  # type: Optional[str]
        self._albumsort = None  # type: Optional[str]
        self._albumid = None  # type: Optional[str]
        self._discid = None  # type: Optional[int]
        self._trackid = None  # type: Optional[int]

    def estimate(self, **kwargs) -> None:
        """

        :param kwargs:
        :return:
        """
        self._db_album = kwargs.get("db_album", False)
        self._db_bootleg = kwargs.get("db_bootleg", False)
        self._bonus = kwargs.get("bonus", "N")
        self._bootlegdisc = kwargs.get("bootlegdisc")
        self._artistid = kwargs["artistsort"]
        self._albumsort = kwargs["albumsort"][:-3]
        self._albumid = f"{self._artistid[0]}.{self._artistid}.{self._albumsort}"
        self._discid = int(kwargs["discnumber"])
        self._trackid = int(kwargs["tracknumber"])
        artist, album, disc, track, bonus, bootlegdisc = self._exists(self._artistid, self._albumid, self._discid, self._trackid, db=self._database)

        # Artist.
        if not artist:
            self._artists[self._artistid] += 1

        # Album.
        if not album:
            self._albums[self._albumid] += 1
            if self._db_album:
                self._defautlalbums[self._albumid] += 1
            if self._db_bootleg:
                self._bootlegalbums[self._albumid] += 1
                self._livealbums[self._albumid] += 1

        # Disc.
        if not disc:
            self._discs[f"{self._albumid}.{self._discid}"] += 1
            if not bootlegdisc and self._bootlegdisc:
                self._bootlegdiscs[f"{self._albumid}.{self._discid}"] += 1
        if self._trackid == 1:
            self._rippeddiscs[f"{self._albumid}.{self._discid}"] += 1

        # Track.
        if not track:
            self._tracks[f"{self._albumid}.{self._discid}.{self._trackid}"] += 1
            if not bonus and self._bonus == "Y":
                self._bonuses[f"{self._albumid}.{self._discid}.{self._trackid}"] += 1

        # Total changes.
        self._changes = len(self._artists.keys()) + \
                        len(self._albums.keys()) + \
                        len(self._defautlalbums.keys()) + \
                        len(self._bootlegalbums.keys()) + \
                        len(self._livealbums.keys()) + \
                        len(self._discs.keys()) + \
                        len(self._bootlegdiscs.keys()) + \
                        len(self._rippeddiscs.keys()) + \
                        len(self._tracks.keys()) + \
                        len(self._bonuses.keys())

        # Log changes.
        self.logger.debug("artists      : %s", self._artists)
        self.logger.debug("albums       : %s", self._albums)
        self.logger.debug("defautlalbums: %s", self._defautlalbums)
        self.logger.debug("bootlegalbums: %s", self._bootlegalbums)
        self.logger.debug("livealbums   : %s", self._livealbums)
        self.logger.debug("discs        : %s", self._discs)
        self.logger.debug("bootlegdiscs : %s", self._bootlegdiscs)
        self.logger.debug("rippeddiscs  : %s", self._rippeddiscs)
        self.logger.debug("tracks       : %s", self._tracks)
        self.logger.debug("bonuses      : %s", self._bonuses)

    @staticmethod
    def _exists(artistid: str, albumid: str, discid: int, trackid: int, db: str = DATABASE) -> Tuple[bool, ...]:
        """

        :param artistid:
        :param albumid:
        :param discid:
        :param trackid:
        :param db:
        :return:
        """
        with DatabaseConnection(db) as conn:
            curs = conn.cursor()

            # artists.
            curs.execute("SELECT count(*) FROM artists WHERE artistsort=?", (artistid,))
            (artist,) = curs.fetchone()

            # albums.
            curs.execute("SELECT count(*) FROM albums WHERE albumid=?", (albumid,))
            (album,) = curs.fetchone()

            # discs.
            curs.execute("SELECT count(*) FROM discs WHERE albumid=? AND discid=?", (albumid, discid))
            (disc,) = curs.fetchone()

            # bootlegdiscs.
            curs.execute("SELECT count(*) FROM bootlegdiscs WHERE albumid=? AND discid=?", (albumid, discid))
            (bootlegdisc,) = curs.fetchone()

            # tracks.
            curs.execute("SELECT count(*) FROM tracks WHERE albumid=? AND discid=? AND trackid=?", (albumid, discid, trackid))
            (track,) = curs.fetchone()

            # bonuses.
            curs.execute("SELECT count(*) FROM bonuses WHERE albumid=? AND discid=? AND trackid=?", (albumid, discid, trackid))
            (bonus,) = curs.fetchone()

        return bool(artist), bool(album), bool(disc), bool(track), bool(bonus), bool(bootlegdisc)

    @property
    def total_changes(self) -> int:
        return self._changes


class SetUp(object):
    _encoding = UTF8

    def _decorate_callable(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self as tempdir:
                database = join(tempdir, "database.db")
                jsontags = join(tempdir, "tags.json")
                create_tables(drop_tables(database))
                with open(_THATFILE.parent / "Resources" / "resource2.yml", encoding=self._encoding) as stream:
                    collection = yaml.load(stream, Loader=yaml.FullLoader)
                for item in collection:
                    track = Mock()
                    for key, value in item.items():
                        setattr(track, key, value)
                    dump_audiotags_tojson(track, albums, database=database, jsonfile=jsontags)
                with open(jsontags, encoding=self._encoding) as stream:
                    insert_albums_fromjson(stream)
                args += (database,)
                if self.args:
                    args += self.args
                func(*args, **kwargs)

        return wrapper

    def _decorate_class(self, klass):
        for attr in dir(klass):
            if not attr.startswith("test"):
                continue
            attr_value = getattr(klass, attr)
            if not hasattr(attr_value, "__call__"):
                continue
            setattr(klass, attr, self(attr_value))
        return klass

    def __init__(self, *args, suffix=None, prefix=None, root=None):
        self.name = None
        self.suffix = suffix
        self.prefix = prefix
        self.root = root
        self.args = args

    def __enter__(self):
        self.name = mkdtemp(self.suffix, self.prefix, self.root)
        return self.name

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.name)

    def __call__(self, arg):
        if isinstance(arg, type):
            return self._decorate_class(arg)
        return self._decorate_callable(arg)


# ==============
# Tests classes.
# ==============
class TestRippedTrack(unittest.TestCase):

    def setUp(self):
        with open(_THATFILE.parent / "Resources" / "resource3.yml", encoding=UTF8) as stream:
            self.test_cases = yaml.load(stream, Loader=yaml.FullLoader)
        with open(_THATFILE.parents[2] / "AudioCD" / "Resources" / "profiles.yml", encoding=UTF8) as stream:
            self.test_config = yaml.load(stream, Loader=yaml.FullLoader)
        with open(_THATFILE.parents[2] / "Resources" / "logging.yml", encoding=UTF8) as stream:
            log_config = yaml.load(stream, Loader=yaml.FullLoader)
        logging.config.dictConfig(log_config)
        self._logger = logging.getLogger("Applications.Unittests.module4.TestRippedTrack")

    @patch("Applications.AudioCD.shared.AudioCDTags.database", new_callable=PropertyMock)
    def test_t01a(self, mock_database):
        """
        Test that value returned by `upsert_audiotags` function is the expected one.
        """
        mock_database.return_value = False
        with TemporaryDirectory() as tempdir:
            txttags = join(tempdir, "tags.txt")
            for value in self.test_cases:
                source, profile, decorators, actions, expected = value

                # -----
                with open(txttags, mode="w", encoding=UTF16) as stream:
                    for k, v in source.items():
                        stream.write("{0}={1}\n".format(k.lower(), v))

                # -----
                config = dict(filterfalse(itemgetter_()(partial(contains, ["debug", "database", "console"])), self.test_config.get(actions, {}).items()))
                with open(txttags, mode="r+", encoding=UTF16) as stream:
                    with patch("Applications.shared.TEMP", tempdir):
                        value, _ = upsert_audiotags(profile, stream, "C1", *decorators, genres=CustomAudioGenres(), **config)

                # -----
                self.assertEqual(value, 0)

    @patch("Applications.AudioCD.shared.AudioCDTags.database", new_callable=PropertyMock)
    def test_t01b(self, mock_database):
        """
        Test that audio tags returned by `upsert_audiotags` function are the expected ones.
        """
        mock_database.return_value = False
        with TemporaryDirectory() as tempdir:
            txttags = join(tempdir, "tags.txt")
            for value in self.test_cases:
                source, profile, decorators, actions, expected = value

                # -----
                with open(txttags, mode="w", encoding=UTF16) as stream:
                    for k, v in source.items():
                        stream.write("{0}={1}\n".format(k.lower(), v))

                # -----
                config = dict(filterfalse(itemgetter_()(partial(contains, ["debug", "database", "console"])), self.test_config.get(actions, {}).items()))
                with open(txttags, mode="r+", encoding=UTF16) as stream:
                    with patch("Applications.shared.TEMP", tempdir):
                        _, track = upsert_audiotags(profile, stream, "C1", *decorators, genres=CustomAudioGenres(), **config)

                # -----
                for k, v in expected.items():
                    with self.subTest(key=k):
                        self.assertEqual(v, getattr(track, k, None))

    @unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
    def test_t02(self):
        """
        Test `upsert_audiotags` function.
        Test that total ripped discs are coherent after inserting new discs.
        Use production database duplicated into the working temporary folder.
        """
        total_rippeddiscs, rippeddiscs = get_total_rippeddiscs(DATABASE), 0  # type: int, int
        with TemporaryDirectory() as tempdir:
            inserted, items = 0, 0
            database = copy(DATABASE, tempdir)
            txttags = join(tempdir, "tags.txt")
            jsontags = join(tempdir, "tags.json")
            for value in self.test_cases:
                items += 1
                source, profile, decorators, actions, _ = value

                # -----
                _actions = any([self.test_config.get(actions, {}).get("albums", False), self.test_config.get(actions, {}).get("bootlegs", False)])
                if _actions:
                    if int(source["Track"].split("/")[0]) == 1:
                        rippeddiscs += 1

                # -----
                with open(txttags, mode="w", encoding=UTF16) as stream:
                    for k, v in source.items():
                        stream.write("{0}={1}\n".format(k.lower(), v))

                # -----
                config = dict(filterfalse(itemgetter_()(partial(contains, ["debug", "database", "console"])), self.test_config.get(actions, {}).items()))
                with open(txttags, mode="r+", encoding=UTF16) as stream:
                    with patch("Applications.shared.TEMP", tempdir):
                        upsert_audiotags(profile, stream, "C1", *decorators, genres=CustomAudioGenres(), database=database, jsonfile=jsontags, **config)

            with open(jsontags, encoding=UTF8) as stream:
                inserted = insert_albums_fromjson(stream)
            self.assertGreater(inserted, 0)
            self.assertEqual(total_rippeddiscs + rippeddiscs, get_total_rippeddiscs(database))

    @unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
    def test_t03(self):
        """
        Test `upsert_audiotags` main function.
        Test that total database changes are coherent.
        Use production database duplicated into the working temporary folder.
        """
        with TemporaryDirectory() as tempdir:
            database = copy(DATABASE, tempdir)
            txttags = join(tempdir, "tags.txt")
            jsontags = join(tempdir, "tags.json")
            changes = Changes(db=database)
            for value in self.test_cases:
                source, profile, decorators, actions, expected = value

                # -----
                _db_album = self.test_config.get(actions, {}).get("albums", False)
                _db_bootleg = self.test_config.get(actions, {}).get("bootlegs", False)
                _actions = any([_db_album, _db_bootleg])
                if _actions:
                    kwargs = {k.lower(): v for k, v in source.items()}
                    kwargs.update(albumsort=expected["albumsort"],
                                  bonus=kwargs.get("bonustrack", "N"),
                                  bootlegdisc=kwargs.get("bootlegdiscreference"),
                                  db_album=_db_album,
                                  db_bootleg=_db_bootleg,
                                  discnumber=expected["discnumber"],
                                  tracknumber=expected["tracknumber"])
                    changes.estimate(**kwargs)

                # -----
                with open(txttags, mode="w", encoding=UTF16) as stream:
                    for k, v in source.items():
                        stream.write("{0}={1}\n".format(k.lower(), v))

                # -----
                config = dict(filterfalse(itemgetter_()(partial(contains, ["debug", "database", "console"])), self.test_config.get(actions, {}).items()))
                with open(txttags, mode="r+", encoding=UTF16) as stream:
                    with patch("Applications.shared.TEMP", tempdir):
                        upsert_audiotags(profile, stream, "C1", *decorators, genres=CustomAudioGenres(), database=database, jsonfile=jsontags, **config)

            inserted = 0
            with open(jsontags, encoding=UTF8) as stream:
                inserted = insert_albums_fromjson(stream)
            self._logger.debug("inserted: %s", inserted)
            self._logger.debug("expected: %s", changes.total_changes)
            self.assertEqual(inserted, changes.total_changes)

    def test_t04(self):
        """
        Test `upsert_audiotags` main function.
        Test that total database changes are coherent.
        Create an empty database into the working temporary directory.
        """
        with TemporaryDirectory() as tempdir:
            database = join(tempdir, "database.db")
            txttags = join(tempdir, "tags.txt")
            jsontags = join(tempdir, "tags.json")
            create_tables(drop_tables(database))
            changes = Changes(db=database)
            for value in self.test_cases:
                source, profile, decorators, actions, expected = value

                # -----
                _db_album = self.test_config.get(actions, {}).get("albums", False)
                _db_bootleg = self.test_config.get(actions, {}).get("bootlegs", False)
                _actions = any([_db_album, _db_bootleg])
                if _actions:
                    kwargs = {k.lower(): v for k, v in source.items()}
                    kwargs.update(albumsort=expected["albumsort"],
                                  bonus=kwargs.get("bonustrack", "N"),
                                  bootlegdisc=kwargs.get("bootlegdiscreference"),
                                  db_album=_db_album,
                                  db_bootleg=_db_bootleg,
                                  discnumber=expected["discnumber"],
                                  tracknumber=expected["tracknumber"])
                    changes.estimate(**kwargs)

                # -----
                with open(txttags, mode="w", encoding=UTF16) as stream:
                    for k, v in source.items():
                        stream.write("{0}={1}\n".format(k.lower(), v))

                # -----
                config = dict(filterfalse(itemgetter_()(partial(contains, ["debug", "database", "console"])), self.test_config.get(actions, {}).items()))
                with open(txttags, mode="r+", encoding=UTF16) as stream:
                    with patch("Applications.shared.TEMP", tempdir):
                        upsert_audiotags(profile, stream, "C1", *decorators, genres=CustomAudioGenres(), database=database, jsonfile=jsontags, **config)

            inserted = 0
            with open(jsontags, encoding=UTF8) as stream:
                inserted = insert_albums_fromjson(stream)
            self.assertEqual(inserted, changes.total_changes)


class TestGetTagsFile01(unittest.TestCase):

    def setUp(self):
        self.track = Mock()
        self.track.album = "The Album"
        self.track.albumsortcount = "1"
        self.track.artistsort = "Artist, The"
        self.track.artistsort_letter = "A"
        self.track.bootleg = "N"
        self.track.discnumber = "1"
        self.track.foldersortcount = "N"
        self.track.origyear = "2019"
        self.track.totaldiscs = "1"

    def test01(self):
        self.assertEqual(get_tagsfile(self.track), r"A\Artist, The\2019 - The Album")

    def test02(self):
        self.track.totaldiscs = "2"
        self.assertEqual(get_tagsfile(self.track), r"A\Artist, The\2019 - The Album\CD1")

    def test03(self):
        self.track.discnumber = "2"
        self.track.totaldiscs = "2"
        self.assertEqual(get_tagsfile(self.track), r"A\Artist, The\2019 - The Album\CD2")

    def test04(self):
        self.track.foldersortcount = "Y"
        self.assertEqual(get_tagsfile(self.track), r"A\Artist, The\2019.1 - The Album")

    def test05(self):
        self.track.albumsortcount = "2"
        self.track.foldersortcount = "Y"
        self.assertEqual(get_tagsfile(self.track), r"A\Artist, The\2019.2 - The Album")

    def test06(self):
        self.track.albumsortcount = "2"
        self.track.discnumber = "3"
        self.track.foldersortcount = "Y"
        self.track.totaldiscs = "3"
        self.assertEqual(get_tagsfile(self.track), r"A\Artist, The\2019.2 - The Album\CD3")


@patch("Applications.Unittests.module4.get_tagsfile", return_value="dummy string")
class TestGetTagsFile02(unittest.TestCase):

    def setUp(self):
        self.track = Mock()
        self.track.album = "The Album"
        self.track.albumsortcount = "1"
        self.track.artistsort = "Artist, The"
        self.track.artistsort_letter = "A"
        self.track.bootleg = "N"
        self.track.discnumber = "1"
        self.track.foldersortcount = "N"
        self.track.origyear = "2019"
        self.track.totaldiscs = "1"

    def test01(self, mock_get_tagsfile):
        self.assertEqual(get_tagsfile(self.track), "dummy string")
        mock_get_tagsfile.assert_called()
        mock_get_tagsfile.assert_called_once()

    def test02(self, mock_get_tagsfile):
        self.track.totaldiscs = "2"
        self.assertEqual(get_tagsfile(self.track), "dummy string")
        mock_get_tagsfile.assert_called()
        mock_get_tagsfile.assert_called_once()

    def test03(self, mock_get_tagsfile):
        self.track.discnumber = "2"
        self.track.totaldiscs = "2"
        self.assertEqual(get_tagsfile(self.track), "dummy string")
        mock_get_tagsfile.assert_called()
        mock_get_tagsfile.assert_called_once()

    def test04(self, mock_get_tagsfile):
        self.track.foldersortcount = "Y"
        self.assertEqual(get_tagsfile(self.track), "dummy string")
        mock_get_tagsfile.assert_called()
        mock_get_tagsfile.assert_called_once()

    def test05(self, mock_get_tagsfile):
        self.track.albumsortcount = "2"
        self.track.foldersortcount = "Y"
        self.assertEqual(get_tagsfile(self.track), "dummy string")
        mock_get_tagsfile.assert_called()
        mock_get_tagsfile.assert_called_once()

    def test06(self, mock_get_tagsfile):
        self.track.albumsortcount = "2"
        self.track.discnumber = "3"
        self.track.foldersortcount = "Y"
        self.track.totaldiscs = "3"
        self.assertEqual(get_tagsfile(self.track), "dummy string")
        mock_get_tagsfile.assert_called()
        mock_get_tagsfile.assert_called_once()


@SetUp("A.Artist, The.1.20190000.1", 1)
class TestDatabase01(unittest.TestCase):

    def setUp(self):
        self._count = 10  # type: int
        self._played = 0  # type: int
        self._datobj = datetime.now()  # type: datetime
        self._datstr = get_readabledate(LOCAL.localize(self._datobj))  # type: str

    def test_t01(self, database, albumid, discid):
        """
        Test `update_playeddisccount` function.
        Test that database changes are the expected ones.
        """
        _, updated = update_playeddisccount(albumid, discid, db=database, local_played=self._datobj)
        self.assertEqual(updated, 1)

    def test_t02(self, database, albumid, discid):
        """
        Test `update_playeddisccount` function.
        Test that played count is the expected one.
        """
        i, played = 1, 0  # type: int, int
        while i <= self._count:
            update_playeddisccount(albumid, discid, db=database)
            i += 1
        with DatabaseConnection(database) as conn:
            curs = conn.cursor()
            curs.execute("SELECT played FROM playeddiscs WHERE albumid=? AND discid=?", (albumid, discid))
            with suppress(TypeError):
                (played,) = curs.fetchone()
        self.assertEqual(played, self._played + self._count)

    def test_t03(self, database, albumid, discid):
        """
        Test `update_playeddisccount` function.
        Test that most recent played date is the expected one.
        Use a naive local timestamp (Europe/Paris timezone).
        """
        utc_played = None  # type: Optional[datetime]
        update_playeddisccount(albumid, discid, db=database, local_played=self._datobj)
        with DatabaseConnection(database) as conn:
            curs = conn.cursor()
            curs.execute("SELECT utc_played FROM playeddiscs WHERE albumid=? AND discid=?", (albumid, discid))
            with suppress(TypeError):
                (utc_played,) = curs.fetchone()
        self.assertIsNotNone(utc_played)
        self.assertEqual(get_readabledate(UTC.localize(utc_played).astimezone(LOCAL)), self._datstr)

    def test_t04(self, database, albumid, discid):
        """
        Test `update_playeddisccount` function.
        Test that most recent played date is the expected one.
        Use an aware local timestamp (Europe/Paris timezone).
        """
        utc_played = None  # type: Optional[datetime]
        update_playeddisccount(albumid, discid, db=database, local_played=LOCAL.localize(self._datobj))
        with DatabaseConnection(database) as conn:
            curs = conn.cursor()
            curs.execute("SELECT utc_played FROM playeddiscs WHERE albumid=? AND discid=?", (albumid, discid))
            with suppress(TypeError):
                (utc_played,) = curs.fetchone()
        self.assertIsNotNone(utc_played)
        self.assertEqual(get_readabledate(UTC.localize(utc_played).astimezone(LOCAL)), self._datstr)


@patch("Applications.Tables.Albums.shared.datetime")
@SetUp("A.Artist, The.1.20190000.1", 1)
class TestDatabase02(unittest.TestCase):

    def setUp(self):
        self._datobj = datetime(2019, 9, 19, 22)

    def test_t01(self, mock_datetime, database, albumid, discid):
        """
        Test `update_playeddisccount` function.
        Test that most recent played date is the expected one.
        """
        mock_datetime.now.return_value = self._datobj
        mock_datetime.utcnow.return_value = datetime.utcnow()
        utc_played = None  # type: Optional[datetime]
        update_playeddisccount(albumid, discid, db=database)
        with DatabaseConnection(database) as conn:
            curs = conn.cursor()
            curs.execute("SELECT utc_played FROM playeddiscs WHERE albumid=? AND discid=?", (albumid, discid))
            with suppress(TypeError):
                (utc_played,) = curs.fetchone()
        self.assertEqual(get_readabledate(UTC.localize(utc_played).astimezone(LOCAL)), get_readabledate(LOCAL.localize(self._datobj)))
        mock_datetime.now.assert_called_once()
        mock_datetime.utcnow.assert_called()
        self.assertEqual(mock_datetime.utcnow.call_count, 2)


@SetUp()
class TestDatabase03(unittest.TestCase):

    def test_t01(self, database):
        """
        Test `get_albumidfromgenre` function.
        """
        self.assertListEqual(sorted(get_albumidfromgenre("Rock", db=database)), ["A.Artist, The.1.20110000.1",
                                                                                 "A.Artist, The.1.20130000.1",
                                                                                 "A.Artist, The.1.20150000.1",
                                                                                 "A.Artist, The.1.20170000.1",
                                                                                 "A.Artist, The.1.20190000.1"])

    def test_t02(self, database):
        """
        Test `get_albumidfromgenre` function.
        """
        self.assertListEqual(sorted(get_albumidfromgenre("Alternative Rock", db=database)), ["A.Awesome Artist, The.1.20080000.1"])

    def test_t03(self, database):
        """
        Test `exist_albumid` function.
        """
        self.assertTrue(exist_albumid("A.Awesome Artist, The.1.20080000.1", db=database))

    def test_t04(self, database):
        """
        Test `exist_albumid` function.
        """
        self.assertFalse(exist_albumid("A.Awesome Artist, The.1.20080000.2", db=database))

    def test_t05(self, database):
        """
        Test `exist_albumid` function.
        """
        self.assertFalse(exist_albumid("A.Awesome Artist.1.20080000.1", db=database))

    def test_t06(self, database):
        """
        Test that total ripped discs are coherent after inserting new discs.
        """
        self.assertEqual(get_total_rippeddiscs(database), 16)

    def test_t07(self, database):
        """
        Test `defaultalbums` function.
        """
        collection = sorted(set([track.genre for track in defaultalbums(db=database)]))
        expected_collection = ["Alternative Rock", "Hard Rock", "Rock"]
        self.assertListEqual(collection, expected_collection)

    def test_t08(self, database):
        """
        Test `defaultalbums` function.
        """
        collection = sorted(set([(track.artistsort, track.genre) for track in defaultalbums(db=database)]), key=itemgetter(0))
        expected_collection = [("Artist, The", "Rock"), ("Awesome Artist, The", "Alternative Rock"), ("Other Artist, The", "Hard Rock")]
        self.assertListEqual(collection, expected_collection)

    def test_t09(self, database):
        """
        Test `update_defaultalbums` function.
        """
        self.assertEqual(update_defaultalbums(*[f"O.Other Artist, The.1.{year}0000.1" for year in range(2012, 2020, 2)], db=database, label="Island Records"), 4)

    def test_t10(self, database):
        """
        Test `defaultalbums` function.
        """
        collection = sorted(set([(track.artistsort, track.label) for track in defaultalbums(db=database)]), key=itemgetter(0))
        expected_collection = [("Artist, The", "Columbia Records"), ("Awesome Artist, The", "Columbia Records"), ("Other Artist, The", "Roadrunner Records")]
        self.assertListEqual(collection, expected_collection)

    def test_t11(self, database):
        """
        Test `update_defaultalbums` function.
        """
        self.assertEqual(update_defaultalbums(*[f"O.Other Artist, The.1.{year}0000.1" for year in range(2012, 2020, 2)], db=database, label="Island Records", upc="123456789012"), 4)
        collection = sorted(set([(track.artistsort, track.label) for track in defaultalbums(db=database)]), key=itemgetter(0))
        expected_collection = [("Artist, The", "Columbia Records"), ("Awesome Artist, The", "Columbia Records"), ("Other Artist, The", "Island Records")]
        self.assertListEqual(collection, expected_collection)

    def test_t12(self, database):
        """
        Test `update_defaultalbums` function.
        """
        update_defaultalbums(*[f"O.Other Artist, The.1.{year}0000.1" for year in range(2012, 2020, 2)], db=database, label="Island Records")
        collection = sorted(set([track.label for track in defaultalbums(db=database)]), key=itemgetter(0))
        self.assertFalse("Roadrunner Records" in collection)
        self.assertListEqual(collection, ["Columbia Records", "Island Records"])


@SetUp("A.Artist, The.1.20190000.1", 1)
class TestDatabase04(unittest.TestCase):

    def setUp(self):
        self._count, self._played = 10, 0  # type: int, int

    def test_t01(self, database, albumid, discid):
        played = 0  # type: int
        with DatabaseConnection(database) as conn:
            curs = conn.cursor()
            curs.execute("SELECT played FROM playeddiscs WHERE albumid=? AND discid=?", (albumid, discid))
            with suppress(TypeError):
                (played,) = curs.fetchone()
        self.assertEqual(played, self._played)

    def test_t02(self, database, albumid, discid):
        with DatabaseConnection(database) as conn:
            curs = conn.cursor()
            curs.execute("SELECT played FROM playeddiscs WHERE albumid=? AND discid=?", (albumid, discid))
            with suppress(TypeError):
                (self._played,) = curs.fetchone()
        update = partial(update_playeddisccount, db=database)
        self.assertEqual(sum([updated for _, updated in map(update, *zip(*[(albumid, discid)] * self._count))]), self._count)


@unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
class TestDatabase05(unittest.TestCase):

    def setUp(self):
        self._albums = []
        with DatabaseConnection(DATABASE) as conn:
            self._albums = list(conn.execute("SELECT albumid, discid FROM playeddiscs ORDER BY albumid, discid"))

    def test_t01(self):
        with TemporaryDirectory() as tempdir:
            copy(DATABASE, tempdir)
            update = partial(update_playeddisccount, db=join(tempdir, "database.db"))
            self.assertEqual(sum([updated for _, updated in map(update, *zip(*self._albums))]), len(self._albums))
