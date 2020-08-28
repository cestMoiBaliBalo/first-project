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
class TestRippedTrack01(unittest.TestCase):

    def setUp(self):
        self._tags = {}
        with open(TEMP / "idtags_01_FLAC.txt", encoding=UTF16) as stream:
            tags = csv.reader(stream, dialect=CustomDialect())  # type: Any
            tags = sorted(tags, key=operator.itemgetter(0))
            self._tags = dict(tags)

    def test_t01(self):
        self.assertEqual(self._tags["album"], "Who's Next")
        self.assertEqual(self._tags["albumsort"], "1.19710000.1.13")
        self.assertEqual(self._tags["totaltracks"], "16")
        self.assertEqual(self._tags["track"], "1")


class TestRippedTrack02(unittest.TestCase):

    def setUp(self):
        self._tags = {}
        with open(TEMP / "idtags_01_FDK.txt", encoding=UTF16) as stream:
            tags = csv.reader(stream, dialect=CustomDialect())  # type: Any
            tags = sorted(tags, key=operator.itemgetter(0))
            self._tags = dict(tags)

    def test_t01(self):
        self.assertEqual(self._tags["album"], "Who's Next")
        self.assertEqual(self._tags["albumsort"], "1.19710000.1.02")
        self.assertEqual(self._tags["totaltracks"], "16")
        self.assertEqual(self._tags["track"], "1")


class TestRippedTrack03(unittest.TestCase):

    def setUp(self):
        self._tags = {}
        with open(TEMP / "idtags_02_FLAC.txt", encoding=UTF16) as stream:
            tags = csv.reader(stream, dialect=CustomDialect())  # type: Any
            tags = sorted(tags, key=operator.itemgetter(0))
            self._tags = dict(tags)

    def test_t01(self):
        self.assertEqual(self._tags["album"], "Who's Next")
        self.assertEqual(self._tags["albumsort"], "1.19710000.1.13")
        self.assertEqual(self._tags["totaltracks"], "16")
        self.assertEqual(self._tags["track"], "2")


class TestRippedTrack04(unittest.TestCase):

    def setUp(self):
        self._tags = {}
        with open(TEMP / "idtags_03_FLAC.txt", encoding=UTF16) as stream:
            tags = csv.reader(stream, dialect=CustomDialect())  # type: Any
            tags = sorted(tags, key=operator.itemgetter(0))
            self._tags = dict(tags)

    def test_t01(self):
        self.assertEqual(self._tags["album"], "Who's Next")
        self.assertEqual(self._tags["albumsort"], "1.19710000.1.13")
        self.assertEqual(self._tags["totaltracks"], "16")
        self.assertEqual(self._tags["track"], "3")


class TestRippedTrack05(unittest.TestCase):

    def setUp(self):
        self._tags = {}
        with open(TEMP / "idtags_04_FDK.txt", encoding=UTF16) as stream:
            tags = csv.reader(stream, dialect=CustomDialect())  # type: Any
            tags = sorted(tags, key=operator.itemgetter(0))
            self._tags = dict(tags)

    def test_t01(self):
        self.assertEqual(self._tags["album"], "1977.2 - Alive II")
        self.assertEqual(self._tags["albumsort"], "1.19770000.2.02")
        self.assertEqual(self._tags["totaltracks"], "20")
        self.assertEqual(self._tags["track"], "11")


class TestRippedTrack06(unittest.TestCase):

    def setUp(self):
        self._tags = {}
        with open(TEMP / "idtags_04_FLAC.txt", encoding=UTF16) as stream:
            tags = csv.reader(stream, dialect=CustomDialect())  # type: Any
            tags = sorted(tags, key=operator.itemgetter(0))
            self._tags = dict(tags)

    def test_t01(self):
        self.assertEqual(self._tags["album"], "1977.2 - Alive II")
        self.assertEqual(self._tags["albumsort"], "1.19770000.2.13")
        self.assertEqual(self._tags["totaltracks"], "20")
        self.assertEqual(self._tags["track"], "11")
