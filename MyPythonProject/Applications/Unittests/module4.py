# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import os
import unittest
from collections import defaultdict
from contextlib import ExitStack
from tempfile import TemporaryDirectory
import sys

import yaml

from ..AudioCD.shared import RippedDisc, set_audiotags
from ..Tables.Albums.shared import insert_albums_fromjson
from ..Tables.RippedDiscs.shared import get_total_rippeddiscs
from ..Tables.tables import create_tables, drop_tables
from ..shared import DATABASE, UTF16, UTF8, copy

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

basename, join = os.path.basename, os.path.join


class RippedDiscTest(unittest.TestCase):

    def setUp(self):
        self.totallogs = get_total_rippeddiscs(DATABASE)
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources", "resource3.yml"), encoding=UTF8) as stream:
            self.config = yaml.load(stream)

    def test_t01(self):
        with TemporaryDirectory() as tempdir:
            txttags = join(tempdir, "tags.txt")
            for key, value in self.config.items():
                tags, profile, decorators, _, _, expected = value

                # -----
                with open(txttags, mode="w", encoding=UTF16) as stream:
                    for k, v in tags.items():
                        stream.write("{0}={1}\n".format(k.lower(), v))

                # -----
                with open(txttags, mode="r+", encoding=UTF16) as stream:
                    with RippedDisc(profile, stream, *decorators) as track:
                        pass

                # -----
                for k, v in expected.items():
                    with self.subTest(key=k):
                        self.assertEqual(v, getattr(track.audiotrack, k, None))

    # @unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
    def test_t02(self):
        with TemporaryDirectory() as tempdir:
            inserted, items = 0, 0
            database = copy(DATABASE, tempdir)
            txttags = join(tempdir, "tags.txt")
            jsontags = join(tempdir, "tags.json")
            for key, value in self.config.items():
                items += 1
                tags, profile, decorators, albums, bootlegs, _ = value

                # -----
                with open(txttags, mode="w", encoding=UTF16) as stream:
                    for k, v in tags.items():
                        stream.write("{0}={1}\n".format(k.lower(), v))

                # -----
                with open(txttags, mode="r+", encoding=UTF16) as stream:
                    set_audiotags(profile, stream, *decorators, db=database, db_albums=albums, db_bootlegs=bootlegs, dbjsonfile=jsontags)

            stack = ExitStack()
            try:
                stream = stack.enter_context(open(jsontags, encoding=UTF8))
            except FileNotFoundError:
                pass
            else:
                with stack:
                    insert_albums_fromjson(stream)
            self.assertEqual(self.totallogs + items, get_total_rippeddiscs(database))

    # @unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
    def test_t03(self):
        with TemporaryDirectory() as tempdir:
            inserted, items = 0, 0
            database = copy(DATABASE, tempdir)
            txttags = join(tempdir, "tags.txt")
            jsontags = join(tempdir, "tags.json")
            for key, value in self.config.items():
                items += 1
                tags, profile, decorators, albums, bootlegs, _ = value

                # -----
                with open(txttags, mode="w", encoding=UTF16) as stream:
                    for k, v in tags.items():
                        stream.write("{0}={1}\n".format(k.lower(), v))

                # -----
                with open(txttags, mode="r+", encoding=UTF16) as stream:
                    set_audiotags(profile, stream, *decorators, db=database, db_albums=albums, db_bootlegs=bootlegs, dbjsonfile=jsontags)

            stack = ExitStack()
            try:
                stream = stack.enter_context(open(jsontags, encoding=UTF8))
            except FileNotFoundError:
                pass
            else:
                with stack:
                    inserted = insert_albums_fromjson(stream)
            self.assertEqual(inserted, items)

    # @unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
    def test_t04(self):
        with TemporaryDirectory() as tempdir:
            inserted, items = 0, 0
            database = join(tempdir, "database.db")
            txttags = join(tempdir, "tags.txt")
            jsontags = join(tempdir, "tags.json")
            drop_tables(database)
            create_tables(database)
            _artists = defaultdict(int)
            _albums = defaultdict(int)
            _defaultalbums = 0
            _bootlegalbums = 0
            _discs = 0
            _rippeddiscs = 0
            _tracks = 0
            for key, value in self.config.items():
                items += 1
                tags, profile, decorators, albums, bootlegs, _ = value

                # -----
                _artists[tags["AlbumArtistSort"]] += 1
                if albums:
                    _albums[tags["Album"]] += 1
                    _defaultalbums += 1
                if bootlegs:
                    _albums[tags["BootlegAlbumYear"]] += 1
                    _bootlegalbums += 1
                _discs += 1
                _rippeddiscs += 1
                _tracks += 1

                # -----
                with open(txttags, mode="w", encoding=UTF16) as stream:
                    for k, v in tags.items():
                        stream.write("{0}={1}\n".format(k.lower(), v))

                # -----
                with open(txttags, mode="r+", encoding=UTF16) as stream:
                    set_audiotags(profile, stream, *decorators, db=database, db_albums=albums, db_bootlegs=bootlegs, dbjsonfile=jsontags)

            stack = ExitStack()
            try:
                stream = stack.enter_context(open(jsontags, encoding=UTF8))
            except FileNotFoundError:
                pass
            else:
                with stack:
                    inserted = insert_albums_fromjson(stream)
            self.assertEqual(inserted, len(_artists.keys()) + len(_albums.keys()) + _defaultalbums + _bootlegalbums + _discs + _rippeddiscs + _tracks)
