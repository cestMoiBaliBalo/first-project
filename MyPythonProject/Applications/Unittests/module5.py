# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import csv
import operator
import os
import unittest
from pathlib import Path
from typing import Any

from ..shared import TEMP, UTF16

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent


# ===============
# Global classes.
# ===============
class CustomDialect(csv.Dialect):
    delimiter = "="
    escapechar = "`"
    doublequote = False
    quoting = csv.QUOTE_NONE
    lineterminator = "\r\n"


# ==============
# Tests classes.
# ==============
class TestGrabbedTrack01(unittest.TestCase):

    def setUp(self):
        self._tags = {}
        with open(TEMP / "default_idtags_01_FLAC.txt", encoding=UTF16) as stream:
            tags = csv.reader(stream, dialect=CustomDialect())  # type: Any
            tags = sorted(tags, key=operator.itemgetter(0))
            self._tags = dict(tags)

    def test_t01(self):
        self.assertEqual(self._tags["album"], "Who's Next")
        self.assertEqual(self._tags["albumsort"], "1.19710000.1.13")
        self.assertEqual(self._tags["disc"], "1")
        self.assertEqual(self._tags["track"], "1")
        self.assertEqual(self._tags["totaltracks"], "16")

    def test_t02(self):
        self.assertNotIn("albumsortcount", self._tags)
        self.assertNotIn("foldersortcount", self._tags)
        self.assertNotIn("database", self._tags)
        self.assertNotIn("lossless", self._tags)


class TestGrabbedTrack02(unittest.TestCase):

    def setUp(self):
        self._tags = {}
        with open(TEMP / "default_idtags_01_FDK.txt", encoding=UTF16) as stream:
            tags = csv.reader(stream, dialect=CustomDialect())  # type: Any
            tags = sorted(tags, key=operator.itemgetter(0))
            self._tags = dict(tags)

    def test_t01(self):
        self.assertEqual(self._tags["album"], "Who's Next")
        self.assertEqual(self._tags["albumsort"], "1.19710000.1.02")
        self.assertEqual(self._tags["disc"], "1")
        self.assertEqual(self._tags["track"], "1")
        self.assertEqual(self._tags["totaltracks"], "16")

    def test_t02(self):
        self.assertNotIn("albumsortcount", self._tags)
        self.assertNotIn("foldersortcount", self._tags)
        self.assertNotIn("database", self._tags)
        self.assertNotIn("lossless", self._tags)


class TestGrabbedTrack03(unittest.TestCase):

    def setUp(self):
        self._tags = {}
        with open(TEMP / "default_idtags_02_FLAC.txt", encoding=UTF16) as stream:
            tags = csv.reader(stream, dialect=CustomDialect())  # type: Any
            tags = sorted(tags, key=operator.itemgetter(0))
            self._tags = dict(tags)

    def test_t01(self):
        self.assertEqual(self._tags["album"], "Who's Next")
        self.assertEqual(self._tags["albumsort"], "1.19710000.1.13")
        self.assertEqual(self._tags["disc"], "1")
        self.assertEqual(self._tags["track"], "2")
        self.assertEqual(self._tags["totaltracks"], "16")

    def test_t02(self):
        self.assertNotIn("albumsortcount", self._tags)
        self.assertNotIn("foldersortcount", self._tags)
        self.assertNotIn("database", self._tags)
        self.assertNotIn("lossless", self._tags)


class TestGrabbedTrack04(unittest.TestCase):

    def setUp(self):
        self._tags = {}
        with open(TEMP / "default_idtags_03_FLAC.txt", encoding=UTF16) as stream:
            tags = csv.reader(stream, dialect=CustomDialect())  # type: Any
            tags = sorted(tags, key=operator.itemgetter(0))
            self._tags = dict(tags)

    def test_t01(self):
        self.assertEqual(self._tags["album"], "Who's Next")
        self.assertEqual(self._tags["albumsort"], "1.19710000.1.13")
        self.assertEqual(self._tags["disc"], "1")
        self.assertEqual(self._tags["track"], "3")
        self.assertEqual(self._tags["totaltracks"], "16")

    def test_t02(self):
        self.assertNotIn("albumsortcount", self._tags)
        self.assertNotIn("foldersortcount", self._tags)
        self.assertNotIn("database", self._tags)
        self.assertNotIn("lossless", self._tags)


class TestGrabbedTrack05(unittest.TestCase):

    def setUp(self):
        self._tags = {}
        with open(TEMP / "default_idtags_04_FDK.txt", encoding=UTF16) as stream:
            tags = csv.reader(stream, dialect=CustomDialect())  # type: Any
            tags = sorted(tags, key=operator.itemgetter(0))
            self._tags = dict(tags)

    def test_t01(self):
        self.assertEqual(self._tags["album"], "Alive II")
        self.assertEqual(self._tags["albumsort"], "1.19770000.2.02")
        self.assertEqual(self._tags["disc"], "2")
        self.assertEqual(self._tags["track"], "1")
        self.assertEqual(self._tags["totaltracks"], "10")

    def test_t02(self):
        self.assertNotIn("albumsortcount", self._tags)
        self.assertNotIn("foldersortcount", self._tags)
        self.assertNotIn("database", self._tags)
        self.assertNotIn("lossless", self._tags)


class TestGrabbedTrack06(unittest.TestCase):

    def setUp(self):
        self._tags = {}
        with open(TEMP / "default_idtags_04_FLAC.txt", encoding=UTF16) as stream:
            tags = csv.reader(stream, dialect=CustomDialect())  # type: Any
            tags = sorted(tags, key=operator.itemgetter(0))
            self._tags = dict(tags)

    def test_t01(self):
        self.assertEqual(self._tags["album"], "1977.2 - Alive II")
        self.assertEqual(self._tags["albumsort"], "1.19770000.2.13")
        self.assertEqual(self._tags["disc"], "2")
        self.assertEqual(self._tags["track"], "1")
        self.assertEqual(self._tags["totaltracks"], "10")

    def test_t02(self):
        self.assertNotIn("albumsortcount", self._tags)
        self.assertNotIn("foldersortcount", self._tags)
        self.assertNotIn("database", self._tags)
        self.assertNotIn("lossless", self._tags)


class TestGrabbedTrack07(unittest.TestCase):

    def setUp(self):
        self._tags = {}
        with open(TEMP / "sbootleg1_idtags_03_FLAC.txt", encoding=UTF16) as stream:
            tags = csv.reader(stream, dialect=CustomDialect())  # type: Any
            tags = sorted(tags, key=operator.itemgetter(0))
            self._tags = dict(tags)

    def test_t01(self):
        self.assertEqual(self._tags["album"], "The River Tour - 1981.08.20 - [Los Angeles, CA]")
        self.assertEqual(self._tags["albumsort"], "2.19810820.1.13")
        self.assertEqual(self._tags["disc"], "2")
        self.assertEqual(self._tags["totaldiscs"], "3")
        self.assertEqual(self._tags["track"], "23")
        self.assertEqual(self._tags["totaltracks"], "42")

    def test_t02(self):
        self.assertEqual(self._tags["bootlegtrackcity"], "Los Angeles, CA")
        self.assertEqual(self._tags["bootlegtrackcountry"], "United States")
        self.assertEqual(self._tags["bootlegtracktour"], "The River Tour")
        self.assertEqual(self._tags["bootlegtrackyear"], "1981-08-20")
        self.assertEqual(self._tags["mediapublisher"], "The Godfatherecords")
        self.assertEqual(self._tags["mediareference"], "G.R. 256")
        self.assertEqual(self._tags["mediatitle"], "A Night for the Vietnam Veterans")

    def test_t03(self):
        self.assertNotIn("bootlegalbumprovider", self._tags)
        self.assertNotIn("bootlegalbumtitle", self._tags)
        self.assertNotIn("albumsortcount", self._tags)
        self.assertNotIn("database", self._tags)
        self.assertNotIn("lossless", self._tags)
        self.assertNotIn("offset", self._tags)


class TestGrabbedTrack08(unittest.TestCase):

    def setUp(self):
        self._tags = {}
        with open(TEMP / "sbootleg1_idtags_04_FLAC.txt", encoding=UTF16) as stream:
            tags = csv.reader(stream, dialect=CustomDialect())  # type: Any
            tags = sorted(tags, key=operator.itemgetter(0))
            self._tags = dict(tags)

    def test_t01(self):
        self.assertEqual(self._tags["album"], "The River Tour - 1981.08.20 - [Los Angeles, CA]")
        self.assertEqual(self._tags["albumsort"], "2.19810820.1.13")
        self.assertEqual(self._tags["disc"], "1")
        self.assertEqual(self._tags["totaldiscs"], "3")
        self.assertEqual(self._tags["track"], "13")
        self.assertEqual(self._tags["totaltracks"], "42")

    def test_t02(self):
        self.assertEqual(self._tags["bootlegtrackcity"], "Los Angeles, CA")
        self.assertEqual(self._tags["bootlegtrackcountry"], "United States")
        self.assertEqual(self._tags["bootlegtracktour"], "The River Tour")
        self.assertEqual(self._tags["bootlegtrackyear"], "1981-08-20")
        self.assertEqual(self._tags["mediapublisher"], "The Godfatherecords")
        self.assertEqual(self._tags["mediareference"], "G.R. 256")
        self.assertEqual(self._tags["mediatitle"], "A Night for the Vietnam Veterans")

    def test_t03(self):
        self.assertNotIn("bootlegalbumprovider", self._tags)
        self.assertNotIn("bootlegalbumtitle", self._tags)
        self.assertNotIn("albumsortcount", self._tags)
        self.assertNotIn("database", self._tags)
        self.assertNotIn("lossless", self._tags)
        self.assertNotIn("offset", self._tags)


class TestGrabbedTrack09(unittest.TestCase):

    def setUp(self):
        self._tags = {}
        with open(TEMP / "sbootleg1_idtags_01_FLAC.txt", encoding=UTF16) as stream:
            tags = csv.reader(stream, dialect=CustomDialect())  # type: Any
            tags = sorted(tags, key=operator.itemgetter(0))
            self._tags = dict(tags)

    def test_t01(self):
        self.assertEqual(self._tags["album"], "The River Tour - 1981.08.20 - [Los Angeles, CA]")
        self.assertEqual(self._tags["albumsort"], "2.19810820.1.13")
        self.assertEqual(self._tags["disc"], "1")
        self.assertEqual(self._tags["totaldiscs"], "3")
        self.assertEqual(self._tags["track"], "1")
        self.assertEqual(self._tags["totaltracks"], "19")

    def test_t02(self):
        self.assertEqual(self._tags["bootlegtrackcity"], "Los Angeles, CA")
        self.assertEqual(self._tags["bootlegtrackcountry"], "United States")
        self.assertEqual(self._tags["bootlegtracktour"], "The River Tour")
        self.assertEqual(self._tags["bootlegtrackyear"], "1981-08-20")
        self.assertEqual(self._tags["mediapublisher"], "The Godfatherecords")
        self.assertEqual(self._tags["mediareference"], "G.R. 256")
        self.assertEqual(self._tags["mediatitle"], "A Night for the Vietnam Veterans")

    def test_t03(self):
        self.assertNotIn("bootlegalbumprovider", self._tags)
        self.assertNotIn("bootlegalbumtitle", self._tags)
        self.assertNotIn("albumsortcount", self._tags)
        self.assertNotIn("database", self._tags)
        self.assertNotIn("lossless", self._tags)
        self.assertNotIn("offset", self._tags)


class TestGrabbedTrack10(unittest.TestCase):

    def setUp(self):
        self._tags = {}
        with open(TEMP / "sbootleg1_idtags_05_FLAC.txt", encoding=UTF16) as stream:
            tags = csv.reader(stream, dialect=CustomDialect())  # type: Any
            tags = sorted(tags, key=operator.itemgetter(0))
            self._tags = dict(tags)

    def test_t01(self):
        self.assertEqual(self._tags["album"], "The River Tour - 1981.08.20 - [Los Angeles, CA]")
        self.assertEqual(self._tags["albumsort"], "2.19810820.1.13")
        self.assertEqual(self._tags["disc"], "2")
        self.assertEqual(self._tags["totaldiscs"], "3")
        self.assertEqual(self._tags["track"], "4")
        self.assertEqual(self._tags["totaltracks"], "11")

    def test_t02(self):
        self.assertEqual(self._tags["bootlegtrackcity"], "Los Angeles, CA")
        self.assertEqual(self._tags["bootlegtrackcountry"], "United States")
        self.assertEqual(self._tags["bootlegtracktour"], "The River Tour")
        self.assertEqual(self._tags["bootlegtrackyear"], "1981-08-20")
        self.assertEqual(self._tags["mediapublisher"], "The Godfatherecords")
        self.assertEqual(self._tags["mediareference"], "G.R. 256")
        self.assertEqual(self._tags["mediatitle"], "A Night for the Vietnam Veterans")

    def test_t03(self):
        self.assertNotIn("bootlegalbumprovider", self._tags)
        self.assertNotIn("bootlegalbumtitle", self._tags)
        self.assertNotIn("albumsortcount", self._tags)
        self.assertNotIn("database", self._tags)
        self.assertNotIn("lossless", self._tags)
        self.assertNotIn("offset", self._tags)


class TestGrabbedTrack11(unittest.TestCase):

    def setUp(self):
        self._tags = {}
        with open(TEMP / "sbootleg1_idtags_01_FDK.txt", encoding=UTF16) as stream:
            tags = csv.reader(stream, dialect=CustomDialect())  # type: Any
            tags = sorted(tags, key=operator.itemgetter(0))
            self._tags = dict(tags)

    def test_t01(self):
        self.assertEqual(self._tags["album"], "The River Tour - 1981.08.20 - [Los Angeles, CA]")
        self.assertEqual(self._tags["albumsort"], "2.19810820.1.02")
        self.assertEqual(self._tags["disc"], "1")
        self.assertEqual(self._tags["totaldiscs"], "3")
        self.assertEqual(self._tags["track"], "1")
        self.assertEqual(self._tags["totaltracks"], "19")

    def test_t02(self):
        self.assertEqual(self._tags["bootlegtrackcity"], "Los Angeles, CA")
        self.assertEqual(self._tags["bootlegtrackcountry"], "United States")
        self.assertEqual(self._tags["bootlegtracktour"], "The River Tour")
        self.assertEqual(self._tags["bootlegtrackyear"], "1981-08-20")
        self.assertEqual(self._tags["mediapublisher"], "The Godfatherecords")
        self.assertEqual(self._tags["mediareference"], "G.R. 256")
        self.assertEqual(self._tags["mediatitle"], "A Night for the Vietnam Veterans")

    def test_t03(self):
        self.assertNotIn("bootlegalbumprovider", self._tags)
        self.assertNotIn("bootlegalbumtitle", self._tags)
        self.assertNotIn("albumsortcount", self._tags)
        self.assertNotIn("database", self._tags)
        self.assertNotIn("lossless", self._tags)
        self.assertNotIn("offset", self._tags)


class TestConvertedTrack01(unittest.TestCase):

    def setUp(self):
        self._tags = {}
        with open(TEMP / "converter_idtags_01.txt", encoding=UTF16) as stream:
            tags = csv.reader(stream, dialect=CustomDialect())  # type: Any
            tags = sorted(tags, key=operator.itemgetter(0))
            self._tags = dict(tags)

    def test_t01(self):
        self.assertEqual(self._tags["albumsort"], "1.20200000.1.02")
        self.assertEqual(self._tags["source"], "Perfect (Lossless) [flac]")


class TestConvertedTrack02(unittest.TestCase):

    def setUp(self):
        self._tags = {}
        with open(TEMP / "converter_idtags_03.txt", encoding=UTF16) as stream:
            tags = csv.reader(stream, dialect=CustomDialect())  # type: Any
            tags = sorted(tags, key=operator.itemgetter(0))
            self._tags = dict(tags)

    def test_t01(self):
        self.assertEqual(self._tags["albumsort"], "1.20200000.1.01")
        self.assertEqual(self._tags["source"], "Perfect (Lossless) [flac]")
