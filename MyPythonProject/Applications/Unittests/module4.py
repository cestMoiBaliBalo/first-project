# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import os
import sqlite3
import unittest
from pathlib import Path

from ..shared import TESTDATABASE

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent


@unittest.skipIf(not Path("F:/").exists(), "Unit test run on local platform only!")
class TestDatabase01A(unittest.TestCase):

    def setUp(self) -> None:
        self.conn = sqlite3.connect(TESTDATABASE)

    def tearDown(self) -> None:
        self.conn.close()

    def test01(self):
        cursor = self.conn.execute("SELECT count(*) FROM artists")
        (artists,) = cursor.fetchone()
        self.assertEqual(artists, 3)

    def test02(self):
        cursor = self.conn.execute("SELECT count(*) FROM albums")
        (albums,) = cursor.fetchone()
        self.assertEqual(albums, 4)

    def test03(self):
        cursor = self.conn.execute("SELECT count(*) FROM bootlegalbums")
        (albums,) = cursor.fetchone()
        self.assertEqual(albums, 2)

    def test04(self):
        cursor = self.conn.execute("SELECT count(*) FROM livealbums")
        (albums,) = cursor.fetchone()
        self.assertEqual(albums, 2)

    def test05(self):
        cursor = self.conn.execute("SELECT count(*) FROM digitalalbums")
        (albums,) = cursor.fetchone()
        self.assertEqual(albums, 1)

    def test06(self):
        cursor = self.conn.execute("SELECT count(*) FROM defaultalbums")
        (albums,) = cursor.fetchone()
        self.assertEqual(albums, 2)

    def test07(self):
        cursor = self.conn.execute("SELECT count(*) FROM discs")
        (discs,) = cursor.fetchone()
        self.assertEqual(discs, 5)

    def test08(self):
        cursor = self.conn.execute("SELECT count(*) FROM bootlegdiscs")
        (discs,) = cursor.fetchone()
        self.assertEqual(discs, 2)

    def test09(self):
        cursor = self.conn.execute("SELECT count(*) FROM tracks")
        (tracks,) = cursor.fetchone()
        self.assertEqual(tracks, 19)

    def test10(self):
        cursor = self.conn.execute("SELECT count(*) FROM bonuses")
        (tracks,) = cursor.fetchone()
        self.assertEqual(tracks, 0)


@unittest.skipIf(not Path("F:/").exists(), "Unit test run on local system only!")
class TestDatabase02A(unittest.TestCase):

    def setUp(self) -> None:
        self.conn = sqlite3.connect(TESTDATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.row_factory = sqlite3.Row

    def tearDown(self) -> None:
        self.conn.close()

    def test01(self):
        tracks = set(row["title"] for row in self.conn.execute("SELECT title FROM tracks"))
        self.assertSetEqual(tracks, {"Announcement",
                                     "Baba O'Riley",
                                     "Bargain",
                                     "Beautiful Day",
                                     "Elevation",
                                     "Grace",
                                     "The Ground Beneath Her Feet",
                                     "In A Little While",
                                     "Intro",
                                     "Kite",
                                     "Nebraska",
                                     "New York",
                                     "Peace On Earth",
                                     "The River",
                                     "Stuck In A Moment You Can't Get Out Of",
                                     "The Ties That Bind",
                                     "Walk On",
                                     "When I Look At The World",
                                     "Wild Honey"})

    def test02(self):
        artists = set(row["artistsort"] for row in self.conn.execute("SELECT artistsort FROM albums"))
        self.assertSetEqual(artists, {"Springsteen, Bruce", "U2", "Who, The"})

    def test03(self):
        years = set(row["origyear"] for row in self.conn.execute("SELECT origyear FROM defaultalbums"))
        self.assertSetEqual(years, {1971, 2000})

    def test04(self):
        barcodes = set(row["upc"] for row in self.conn.execute("SELECT upc FROM defaultalbums"))
        self.assertSetEqual(barcodes, {"00602507404635", "731452776020"})

    def test05(self):
        titles = set(row["title"] for row in self.conn.execute("SELECT title FROM bootlegalbums"))
        self.assertSetEqual(set(filter(None, titles)), {"A Night for the Vietnam Veterans"})

    def test06(self):
        providers = set(row["providerid"] for row in self.conn.execute("SELECT providerid FROM bootlegalbums"))
        self.assertSetEqual(set(filter(None, providers)), {1, 4})


@unittest.skipIf(Path("F:/").exists(), "Unit test run on Travis-CI system only!")
class TestDatabase01B(unittest.TestCase):

    def setUp(self) -> None:
        self.conn = sqlite3.connect(TESTDATABASE)

    def tearDown(self) -> None:
        self.conn.close()

    def test01(self):
        cursor = self.conn.execute("SELECT count(*) FROM artists")
        (artists,) = cursor.fetchone()
        self.assertEqual(artists, 2)

    def test02(self):
        cursor = self.conn.execute("SELECT count(*) FROM albums")
        (albums,) = cursor.fetchone()
        self.assertEqual(albums, 3)

    def test03(self):
        cursor = self.conn.execute("SELECT count(*) FROM bootlegalbums")
        (albums,) = cursor.fetchone()
        self.assertEqual(albums, 2)

    def test04(self):
        cursor = self.conn.execute("SELECT count(*) FROM livealbums")
        (albums,) = cursor.fetchone()
        self.assertEqual(albums, 2)

    def test05(self):
        cursor = self.conn.execute("SELECT count(*) FROM digitalalbums")
        (albums,) = cursor.fetchone()
        self.assertEqual(albums, 0)

    def test06(self):
        cursor = self.conn.execute("SELECT count(*) FROM defaultalbums")
        (albums,) = cursor.fetchone()
        self.assertEqual(albums, 1)

    def test07(self):
        cursor = self.conn.execute("SELECT count(*) FROM discs")
        (discs,) = cursor.fetchone()
        self.assertEqual(discs, 4)

    def test08(self):
        cursor = self.conn.execute("SELECT count(*) FROM bootlegdiscs")
        (discs,) = cursor.fetchone()
        self.assertEqual(discs, 2)

    def test09(self):
        cursor = self.conn.execute("SELECT count(*) FROM tracks")
        (tracks,) = cursor.fetchone()
        self.assertEqual(tracks, 7)

    def test10(self):
        cursor = self.conn.execute("SELECT count(*) FROM bonuses")
        (tracks,) = cursor.fetchone()
        self.assertEqual(tracks, 0)


@unittest.skipIf(Path("F:/").exists(), "Unit test run on Travis-CI platform only!")
class TestDatabase02B(unittest.TestCase):

    def setUp(self) -> None:
        self.conn = sqlite3.connect(TESTDATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.row_factory = sqlite3.Row

    def tearDown(self) -> None:
        self.conn.close()

    def test01(self):
        tracks = set(row["title"] for row in self.conn.execute("SELECT title FROM tracks"))
        self.assertSetEqual(tracks, {"Announcement",
                                     "Baba O'Riley",
                                     "Bargain",
                                     "Intro",
                                     "Nebraska",
                                     "The River",
                                     "The Ties That Bind"})

    def test02(self):
        artists = set(row["artistsort"] for row in self.conn.execute("SELECT artistsort FROM albums"))
        self.assertSetEqual(artists, {"Springsteen, Bruce", "Who, The"})

    def test03(self):
        years = set(row["origyear"] for row in self.conn.execute("SELECT origyear FROM defaultalbums"))
        self.assertSetEqual(years, {1971})

    def test04(self):
        barcodes = set(row["upc"] for row in self.conn.execute("SELECT upc FROM defaultalbums"))
        self.assertSetEqual(barcodes, {"731452776020"})

    def test05(self):
        titles = set(row["title"] for row in self.conn.execute("SELECT title FROM bootlegalbums"))
        self.assertSetEqual(set(filter(None, titles)), {"A Night for the Vietnam Veterans"})

    def test06(self):
        providers = set(row["providerid"] for row in self.conn.execute("SELECT providerid FROM bootlegalbums"))
        self.assertSetEqual(set(filter(None, providers)), {1, 4})
