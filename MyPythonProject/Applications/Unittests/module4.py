# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import fnmatch
import logging.config
import os
import unittest
from collections import defaultdict
from contextlib import suppress
from datetime import datetime
from functools import partial
from operator import contains
from pathlib import PurePath, PureWindowsPath
from tempfile import TemporaryDirectory
from typing import Optional, Tuple

import yaml

from ..AudioCD.shared import RippedTrack, upsert_audiotags
from ..Tables.Albums.shared import insert_albums_fromjson, update_playeddisccount
from ..Tables.RippedDiscs.shared import get_total_rippeddiscs
from ..Tables.tables import DatabaseConnection, create_tables, drop_tables
from ..shared import DATABASE, LOCAL, UTC, UTF16, UTF8, copy, get_readabledate, itemgetter_, partial_

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_THATFILE = PureWindowsPath(os.path.abspath(__file__))  # type: PureWindowsPath
basename, exists, join = os.path.basename, os.path.exists, os.path.join


@itemgetter_(0)
@partial_(["debug", "database", "console"])
def not_contains1_(iterable, item: str):
    return not contains(iterable, item.lower())


@itemgetter_(0)
@partial_(["save", "root", "debug", "database", "console"])
def not_contains2_(iterable, item: str):
    return not contains(iterable, item.lower())


class Changes(object):
    logger = logging.getLogger(f"{__name__}")

    def __init__(self, db=DATABASE):
        """

        :param db:
        """
        self._artists, self._albums, self._defautlalbums, self._bootlegalbums, self._discs, self._rippeddiscs, self._bootlegdiscs, self._tracks, self._bonuses = defaultdict(int), \
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


class TestRippedTrack(unittest.TestCase):

    def setUp(self):
        with open(_THATFILE.parent / "Resources" / "resource3.yml", encoding=UTF8) as stream:
            self.test_cases = yaml.load(stream, Loader=yaml.FullLoader)
        with open(_THATFILE.parents[2] / "AudioCD" / "Resources" / "profiles.yml", encoding=UTF8) as stream:
            self.test_config = yaml.load(stream, Loader=yaml.FullLoader)

    def test_t01a(self):
        """
        Test that audio tags held by any RippedTrack instance are the expected ones.
        """
        with TemporaryDirectory() as tempdir:
            txttags = join(tempdir, "tags.txt")
            for value in self.test_cases.values():
                source, profile, decorators, _, expected = value

                # -----
                with open(txttags, mode="w", encoding=UTF16) as stream:
                    for k, v in source.items():
                        stream.write("{0}={1}\n".format(k.lower(), v))

                # -----
                with open(txttags, mode="r+", encoding=UTF16) as stream:
                    with RippedTrack(profile, stream, "C1", *decorators) as track:
                        pass

                # -----
                for k, v in expected.items():
                    with self.subTest(key=k):
                        self.assertEqual(v, getattr(track.audiotrack, k, None))

    def test_t01b(self):
        """
        Test that return value returned by `upsert_audiotags` main function is the expected one.
        """
        with TemporaryDirectory() as tempdir:
            database = copy(DATABASE, tempdir)
            txttags = join(tempdir, "tags.txt")
            jsontags = join(tempdir, "tags.json")
            for value in self.test_cases.values():
                source, profile, decorators, tags_processing, expected = value

                # -----
                with open(txttags, mode="w", encoding=UTF16) as stream:
                    for k, v in source.items():
                        stream.write("{0}={1}\n".format(k.lower(), v))

                # -----
                config = dict(filter(not_contains1_, self.test_config.get(tags_processing, {}).items()))
                with open(txttags, mode="r+", encoding=UTF16) as stream:
                    value, _ = upsert_audiotags(profile, stream, "C1", *decorators, database=database, jsonfile=jsontags, **config)

                # -----
                self.assertEqual(value, 0)

    def test_t01c(self):
        """
        Test that audio tags returned by `upsert_audiotags` main function are the expected ones.
        """
        with TemporaryDirectory() as tempdir:
            database = copy(DATABASE, tempdir)
            txttags = join(tempdir, "tags.txt")
            jsontags = join(tempdir, "tags.json")
            for value in self.test_cases.values():
                source, profile, decorators, tags_processing, expected = value

                # -----
                with open(txttags, mode="w", encoding=UTF16) as stream:
                    for k, v in source.items():
                        stream.write("{0}={1}\n".format(k.lower(), v))

                # -----
                config = dict(filter(not_contains1_, self.test_config.get(tags_processing, {}).items()))
                with open(txttags, mode="r+", encoding=UTF16) as stream:
                    _, track = upsert_audiotags(profile, stream, "C1", *decorators, database=database, jsonfile=jsontags, **config)

                # -----
                for k, v in expected.items():
                    with self.subTest(key=k):
                        self.assertEqual(v, getattr(track, k, None))

    def test_t02(self):
        """
        Test `upsert_audiotags` main function.
        Test that total ripped discs is coherent after new discs insertion.
        """
        total_rippeddiscs, rippeddiscs = get_total_rippeddiscs(DATABASE), 0
        with TemporaryDirectory() as tempdir:
            inserted, items = 0, 0
            database = copy(DATABASE, tempdir)
            txttags = join(tempdir, "tags.txt")
            jsontags = join(tempdir, "tags.json")
            for value in self.test_cases.values():
                items += 1
                source, profile, decorators, tags_processing, _ = value

                # -----
                _tags_processing = any([self.test_config.get(tags_processing, {}).get("albums", False), self.test_config.get(tags_processing, {}).get("bootlegs", False)])
                if _tags_processing:
                    if int(source["Track"].split("/")[0]) == 1:
                        rippeddiscs += 1

                # -----
                with open(txttags, mode="w", encoding=UTF16) as stream:
                    for k, v in source.items():
                        stream.write("{0}={1}\n".format(k.lower(), v))

                # -----
                config = dict(filter(not_contains1_, self.test_config.get(tags_processing, {}).items()))
                with open(txttags, mode="r+", encoding=UTF16) as stream:
                    upsert_audiotags(profile, stream, "C1", *decorators, database=database, jsonfile=jsontags, **config)

            with open(jsontags, encoding=UTF8) as stream:
                inserted = insert_albums_fromjson(stream)
            self.assertGreater(inserted, 0)
            self.assertEqual(total_rippeddiscs + rippeddiscs, get_total_rippeddiscs(database))

    def test_t03(self):
        """
        Test `upsert_audiotags` main function.
        Test that total database changes is coherent.
        Use production database duplicated into the working temporary folder.
        """

        # Run tests cases.
        with TemporaryDirectory() as tempdir:
            database = copy(DATABASE, tempdir)
            txttags = join(tempdir, "tags.txt")
            jsontags = join(tempdir, "tags.json")
            changes = Changes(db=database)
            for value in self.test_cases.values():
                source, profile, decorators, tags_processing, expected = value

                # -----
                _db_album = self.test_config.get(tags_processing, {}).get("albums", False)
                _db_bootleg = self.test_config.get(tags_processing, {}).get("bootlegs", False)
                _tags_processing = any([_db_album, _db_bootleg])
                if _tags_processing:
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
                config = dict(filter(not_contains1_, self.test_config.get(tags_processing, {}).items()))
                with open(txttags, mode="r+", encoding=UTF16) as stream:
                    upsert_audiotags(profile, stream, "C1", *decorators, database=database, jsonfile=jsontags, **config)

            inserted = 0
            with open(jsontags, encoding=UTF8) as stream:
                inserted = insert_albums_fromjson(stream)
            self.assertEqual(inserted, changes.total_changes)

    def test_t04(self):
        """
        Test `upsert_audiotags` main function.
        Test that total database changes is coherent.
        Create an empty database into the working temporary directory.
        """

        # Run tests cases.
        with TemporaryDirectory() as tempdir:
            database = join(tempdir, "database.db")
            txttags = join(tempdir, "tags.txt")
            jsontags = join(tempdir, "tags.json")
            create_tables(drop_tables(database))
            changes = Changes(db=database)
            for value in self.test_cases.values():
                source, profile, decorators, tags_processing, expected = value

                # -----
                _db_album = self.test_config.get(tags_processing, {}).get("albums", False)
                _db_bootleg = self.test_config.get(tags_processing, {}).get("bootlegs", False)
                _tags_processing = any([_db_album, _db_bootleg])
                if _tags_processing:
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
                config = dict(filter(not_contains2_, self.test_config.get(tags_processing, {}).items()))
                with open(txttags, mode="r+", encoding=UTF16) as stream:
                    upsert_audiotags(profile, stream, "C1", *decorators, database=database, jsonfile=jsontags, save=True, root=PurePath(tempdir), **config)

            inserted = 0
            with open(jsontags, encoding=UTF8) as stream:
                inserted = insert_albums_fromjson(stream)
            self.assertEqual(inserted, changes.total_changes)

    def test_t05(self):
        """
        Test `upsert_audiotags` main function.
        Test that total database changes is coherent.
        Use production database duplicated into the working temporary folder.
        """
        with TemporaryDirectory() as tempdir:
            database = copy(DATABASE, tempdir)
            txttags = join(tempdir, "tags.txt")
            jsontags = join(tempdir, "tags.json")
            changes = Changes(db=database)
            source, profile, decorators, tags_processing, expected = self.test_cases["default4"]

            # -----
            _db_album = self.test_config.get(tags_processing, {}).get("albums", False)
            _db_bootleg = self.test_config.get(tags_processing, {}).get("bootlegs", False)
            _tags_processing = any([_db_album, _db_bootleg])
            if _tags_processing:
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
            config = dict(filter(not_contains2_, self.test_config.get(tags_processing, {}).items()))
            with open(txttags, mode="r+", encoding=UTF16) as stream:
                upsert_audiotags(profile, stream, "C1", *decorators, database=database, jsonfile=jsontags, save=True, root=PurePath(tempdir), **config)

            # -----
            # inserted = 0
            with open(jsontags, encoding=UTF8) as stream:
                insert = insert_albums_fromjson(stream)
            self.assertEqual(insert, changes.total_changes)

    @unittest.skip
    def test_t06(self):
        """
        Test `upsert_audiotags` main function.
        Test that audio tags backup files are created into the right directory.
        Create an empty database into the working temporary directory.
        """
        with TemporaryDirectory() as tempdir:
            txttags = join(tempdir, "tags.txt")
            source, profile, decorators, tags_processing, _ = self.test_cases["bootleg1"]

            # -----
            with open(txttags, mode="w", encoding=UTF16) as stream:
                for k, v in source.items():
                    stream.write("{0}={1}\n".format(k.lower(), v))

            # -----
            config = dict(filter(lambda i: i[0] not in ["console", "database", "debug", "root", "save"], self.test_config.get(tags_processing, {}).items()))
            with open(txttags, mode="r+", encoding=UTF16) as stream:
                upsert_audiotags(profile, stream, *decorators, save=True, root=tempdir, **config)
            self.assertTrue(exists(join(tempdir, "S")))
            self.assertTrue(exists(join(tempdir, "S", "Springsteen, Bruce")))
            self.assertTrue(exists(join(tempdir, "S", "Springsteen, Bruce", "2")))
            self.assertTrue(exists(join(tempdir, "S", "Springsteen, Bruce", "2", "2002")))
            self.assertTrue(exists(join(tempdir, "S", "Springsteen, Bruce", "2", "2002", "10.14 - Paris, France")))
            self.assertTrue(exists(join(tempdir, "S", "Springsteen, Bruce", "2", "2002", "10.14 - Paris, France", "CD2")))

    @unittest.skip
    def test_t07(self):
        """
        Test `upsert_audiotags` main function.
        Test that audio tags backup files are created into the right directory.
        Create an empty database into the working temporary directory.
        """
        with TemporaryDirectory() as tempdir:
            txttags = join(tempdir, "tags.txt")
            source, profile, decorators, tags_processing, _ = self.test_cases["bootleg1"]

            # -----
            with open(txttags, mode="w", encoding=UTF16) as stream:
                for k, v in source.items():
                    stream.write("{0}={1}\n".format(k.lower(), v))

            # -----
            config = dict(filter(lambda i: i[0] not in ["console", "database", "debug", "root", "save"], self.test_config.get(tags_processing, {}).items()))
            with open(txttags, mode="r+", encoding=UTF16) as stream:
                upsert_audiotags(profile, stream, *decorators, save=True, root=tempdir, **config)
            self.assertTrue(exists(os.path.join(tempdir, "S", "Springsteen, Bruce", "2", "2002", "10.14 - Paris, France", "CD2", "input_tags.json")))
            self.assertTrue(exists(os.path.join(tempdir, "S", "Springsteen, Bruce", "2", "2002", "10.14 - Paris, France", "CD2", "input_tags.yml")))
            self.assertTrue(exists(os.path.join(tempdir, "S", "Springsteen, Bruce", "2", "2002", "10.14 - Paris, France", "CD2", "output_tags.json")))
            self.assertTrue(exists(os.path.join(tempdir, "S", "Springsteen, Bruce", "2", "2002", "10.14 - Paris, France", "CD2", "output_tags.yml")))
            self.assertListEqual(list(fnmatch.filter(os.listdir(os.path.join(tempdir, "S", "Springsteen, Bruce", "2", "2002", "10.14 - Paris, France", "CD2")), "*.json")),
                                 ["input_tags.json", "output_tags.json"])
            self.assertListEqual(list(fnmatch.filter(os.listdir(os.path.join(tempdir, "S", "Springsteen, Bruce", "2", "2002", "10.14 - Paris, France", "CD2")), "*.yml")),
                                 ["input_tags.yml", "output_tags.yml"])

    @unittest.skip
    def test_t08(self):
        """
        Test `upsert_audiotags` main function.
        Test that audio tags backup files are created into the right directory.
        """
        with TemporaryDirectory() as tempdir:
            txttags = join(tempdir, "tags.txt")
            source, profile, decorators, tags_processing, _ = self.test_cases["bootleg"]

            # -----
            with open(txttags, mode="w", encoding=UTF16) as stream:
                for k, v in source.items():
                    stream.write("{0}={1}\n".format(k.lower(), v))

            # -----
            config = dict(filter(lambda i: i[0] not in ["console", "database", "debug", "root", "save"], self.test_config.get(tags_processing, {}).items()))
            with open(txttags, mode="r+", encoding=UTF16) as stream:
                upsert_audiotags(profile, stream, *decorators, save=True, root=tempdir, **config)
            self.assertTrue(exists(join(tempdir, "S", "Springsteen, Bruce", "2", "1993", "06.24 - East Rutherford, NJ", "CD2", "input_tags.json")))
            self.assertTrue(exists(join(tempdir, "S", "Springsteen, Bruce", "2", "1993", "06.24 - East Rutherford, NJ", "CD2", "input_tags.yml")))
            self.assertTrue(exists(join(tempdir, "S", "Springsteen, Bruce", "2", "1993", "06.24 - East Rutherford, NJ", "CD2", "output_tags.json")))
            self.assertTrue(exists(join(tempdir, "S", "Springsteen, Bruce", "2", "1993", "06.24 - East Rutherford, NJ", "CD2", "output_tags.yml")))
            self.assertListEqual(list(fnmatch.filter(os.listdir(join(tempdir, "S", "Springsteen, Bruce", "2", "1993", "06.24 - East Rutherford, NJ", "CD2")), "*.json")),
                                 ["input_tags.json", "output_tags.json"])
            self.assertListEqual(list(fnmatch.filter(os.listdir(join(tempdir, "S", "Springsteen, Bruce", "2", "1993", "06.24 - East Rutherford, NJ", "CD2")), "*.yml")),
                                 ["input_tags.yml", "output_tags.yml"])

    @unittest.skip
    def test_t09(self):
        """
        Test `upsert_audiotags` main function.
        Test that audio tags backup files are created into the right directory.
        """
        with TemporaryDirectory() as tempdir:
            txttags = join(tempdir, "tags.txt")
            source, profile, decorators, tags_processing, _ = self.test_cases["bootleg"]

            # -----
            with open(txttags, mode="w", encoding=UTF16) as stream:
                for k, v in source.items():
                    stream.write("{0}={1}\n".format(k.lower(), v))

            # -----
            config = dict(filter(lambda i: i[0] not in ["console", "database", "debug", "root", "save"], self.test_config.get(tags_processing, {}).items()))
            with open(txttags, mode="r+", encoding=UTF16) as stream:
                upsert_audiotags(profile, stream, *decorators, save=False, root=None, **config)
            self.assertFalse(exists(join(tempdir, "S", "Springsteen, Bruce", "2", "1993", "06.24 - East Rutherford, NJ", "CD2")))
            self.assertFalse(exists(join(tempdir, "S", "Springsteen, Bruce", "2", "1993", "06.24 - East Rutherford, NJ")))
            self.assertFalse(exists(join(tempdir, "S", "Springsteen, Bruce", "2", "1993")))
            self.assertFalse(exists(join(tempdir, "S", "Springsteen, Bruce", "2")))
            self.assertFalse(exists(join(tempdir, "S", "Springsteen, Bruce")))
            self.assertFalse(exists(join(tempdir, "S")))
            self.assertTrue(exists(tempdir))

    @unittest.skip
    def test_t10(self):
        """
        Test `upsert_audiotags` main function.
        Test that audio tags backup files are created into the right directory.
        """
        with TemporaryDirectory() as tempdir:
            txttags = join(tempdir, "tags.txt")
            source, profile, decorators, tags_processing, _ = self.test_cases["bootleg"]

            # -----
            with open(txttags, mode="w", encoding=UTF16) as stream:
                for k, v in source.items():
                    stream.write("{0}={1}\n".format(k.lower(), v))

            # -----
            config = dict(filter(lambda i: i[0] not in ["console", "database", "debug", "root", "save"], self.test_config.get(tags_processing, {}).items()))
            with open(txttags, mode="r+", encoding=UTF16) as stream:
                upsert_audiotags(profile, stream, *decorators, save=True, root=None, **config)
            self.assertFalse(exists(join(tempdir, "S", "Springsteen, Bruce", "2", "1993", "06.24 - East Rutherford, NJ", "CD2")))
            self.assertFalse(exists(join(tempdir, "S", "Springsteen, Bruce", "2", "1993", "06.24 - East Rutherford, NJ")))
            self.assertFalse(exists(join(tempdir, "S", "Springsteen, Bruce", "2", "1993")))
            self.assertFalse(exists(join(tempdir, "S", "Springsteen, Bruce", "2")))
            self.assertFalse(exists(join(tempdir, "S", "Springsteen, Bruce")))
            self.assertFalse(exists(join(tempdir, "S")))
            self.assertTrue(exists(tempdir))

    @unittest.skip
    def test_t11(self):
        """
        Test `upsert_audiotags` main function.
        Test that audio tags backup files are created into the right directory.
        """
        with TemporaryDirectory() as tempdir:
            txttags = join(tempdir, "tags.txt")
            source, profile, decorators, tags_processing, _ = self.test_cases["bootleg"]

            # -----
            with open(txttags, mode="w", encoding=UTF16) as stream:
                for k, v in source.items():
                    stream.write("{0}={1}\n".format(k.lower(), v))

            # -----
            config = dict(filter(lambda i: i[0] not in ["console", "database", "debug", "root", "save"], self.test_config.get(tags_processing, {}).items()))
            with open(txttags, mode="r+", encoding=UTF16) as stream:
                upsert_audiotags(profile, stream, *decorators, save=False, root=tempdir, **config)
            self.assertFalse(exists(join(tempdir, "S", "Springsteen, Bruce", "2", "1993", "06.24 - East Rutherford, NJ", "CD2")))
            self.assertFalse(exists(join(tempdir, "S", "Springsteen, Bruce", "2", "1993", "06.24 - East Rutherford, NJ")))
            self.assertFalse(exists(join(tempdir, "S", "Springsteen, Bruce", "2", "1993")))
            self.assertFalse(exists(join(tempdir, "S", "Springsteen, Bruce", "2")))
            self.assertFalse(exists(join(tempdir, "S", "Springsteen, Bruce")))
            self.assertFalse(exists(join(tempdir, "S")))
            self.assertTrue(exists(tempdir))


class DatabaseFunctionsTest01(unittest.TestCase):
    _count = 10

    def setUp(self):
        self._played = 0  # type: int
        self._albumid, self._discid = "A.Adams, Bryan.1.19840000.1", 1  # type: str, int
        with DatabaseConnection(DATABASE) as conn:
            curs = conn.cursor()
            curs.execute("SELECT played FROM playeddiscs WHERE albumid=? AND discid=?", (self._albumid, self._discid))
            with suppress(TypeError):
                (self._played,) = curs.fetchone()
        self._datobj = datetime.now()  # type: datetime
        self._datstr = get_readabledate(LOCAL.localize(self._datobj))  # type: str

    def test_t01(self):
        with TemporaryDirectory() as tempdir:
            copy(DATABASE, tempdir)
            _, updated = update_playeddisccount(self._albumid, self._discid, db=join(tempdir, "database.db"), local_played=self._datobj)
            self.assertEqual(updated, 1)

    def test_t02(self):
        i, played = 1, 0  # type: int, int
        with TemporaryDirectory() as tempdir:
            database = join(tempdir, "database.db")
            copy(DATABASE, tempdir)
            while i <= self._count:
                update_playeddisccount(self._albumid, self._discid, db=database)
                i += 1
            with DatabaseConnection(database) as conn:
                curs = conn.cursor()
                curs.execute("SELECT played FROM playeddiscs WHERE albumid=? AND discid=?", (self._albumid, self._discid))
                with suppress(TypeError):
                    (played,) = curs.fetchone()
        self.assertEqual(played, self._played + self._count)

    def test_t03(self):
        utc_played = None  # type: Optional[datetime]
        with TemporaryDirectory() as tempdir:
            database = join(tempdir, "database.db")
            copy(DATABASE, tempdir)
            update_playeddisccount(self._albumid, self._discid, db=database, local_played=self._datobj)
            with DatabaseConnection(database) as conn:
                curs = conn.cursor()
                curs.execute("SELECT utc_played FROM playeddiscs WHERE albumid=? AND discid=?", (self._albumid, self._discid))
                with suppress(TypeError):
                    (utc_played,) = curs.fetchone()
        self.assertIsNotNone(utc_played)
        self.assertEqual(get_readabledate(UTC.localize(utc_played).astimezone(LOCAL)), self._datstr)

    def test_t04(self):
        utc_played = None  # type: Optional[datetime]
        with TemporaryDirectory() as tempdir:
            database = join(tempdir, "database.db")
            copy(DATABASE, tempdir)
            update_playeddisccount(self._albumid, self._discid, db=database, local_played=LOCAL.localize(self._datobj))
            with DatabaseConnection(database) as conn:
                curs = conn.cursor()
                curs.execute("SELECT utc_played FROM playeddiscs WHERE albumid=? AND discid=?", (self._albumid, self._discid))
                with suppress(TypeError):
                    (utc_played,) = curs.fetchone()
        self.assertIsNotNone(utc_played)
        self.assertEqual(get_readabledate(UTC.localize(utc_played).astimezone(LOCAL)), self._datstr)

    def test_t05(self):
        with TemporaryDirectory() as tempdir:
            copy(DATABASE, tempdir)
            update = partial(update_playeddisccount, db=join(tempdir, "database.db"), local_played=None)
            self.assertEqual(sum([updated for _, updated in map(update, *zip(*[(self._albumid, self._discid)] * self._count))]), self._count)

    def test_t06(self):
        played = 0  # type: int
        with DatabaseConnection(DATABASE) as conn:
            curs = conn.cursor()
            curs.execute("SELECT played FROM playeddiscs WHERE albumid=? AND discid=?", (self._albumid, self._discid))
            with suppress(TypeError):
                (played,) = curs.fetchone()
        self.assertEqual(played, self._played)


class DatabaseFunctionsTest02(unittest.TestCase):

    def setUp(self):
        with DatabaseConnection(DATABASE) as conn:
            self.args = list(conn.execute("SELECT albumid, discid FROM playeddiscs ORDER BY albumid, discid"))

    def test_t01(self):
        with TemporaryDirectory() as tempdir:
            copy(DATABASE, tempdir)
            update = partial(update_playeddisccount, db=join(tempdir, "database.db"), local_played=None)
            self.assertEqual(sum([updated for _, updated in map(update, *zip(*self.args))]), len(self.args))
