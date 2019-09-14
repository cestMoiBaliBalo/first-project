# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import os
import re
import sys
import unittest
from functools import partial
from itertools import chain, compress, repeat
from operator import contains
from pathlib import PurePath
from typing import List, Tuple
from unittest.mock import patch

from Applications.shared import DFTYEARREGEX, MUSIC, get_albums, itemgetter_, partitioner

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# -----------------
# Functions labels.
# -----------------
join = os.path.join

# -----------------
# Global variables.
# -----------------
iterable = chain.from_iterable(os.listdir(str(MUSIC / letter)) for letter in os.listdir(str(MUSIC)) if re.match(r"^[A-Z]$", letter))
specifics, generics = partitioner(iterable, predicate=partial(contains, ["Bad English", "Fleetwood Mac", "Iron Maiden", "Kiss", "Metallica", "Pearl Jam", "Springsteen, Bruce", "U2"]))
generics = list((artist[0], artist) for artist in generics)  # Generic artists.
specifics = list(filter(itemgetter_(1)(partial(contains, ["Kiss", "Metallica", "Pearl Jam", "Springsteen, Bruce"])), [(artist[0], artist) for artist in specifics]))  # Specific artists.


# --------------
# Tests classes.
# --------------
@unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
class TestGetAlbums01(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.artists = generics  # type: List[Tuple[str, str]]

    def test_t01(self):
        for letter, artist in self.artists:
            directory = MUSIC / letter / artist  # type: PurePath
            reference = os.listdir(str(directory))  # type: List[str]
            with self.subTest(artist=artist):
                albums = sorted(chain.from_iterable(compress(album, [1, 0, 0, 0]) for album in list(get_albums(directory))))  # type: List[str]
                self.assertListEqual(albums, sorted(map(lambda i: i.split("-", maxsplit=1)[-1].strip(), reference)))


@unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
class TestGetAlbums02(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.artists = generics  # type: List[Tuple[str, str]]

    def test_t02(self):
        for letter, artist in self.artists:
            directory = MUSIC / letter / artist  # type: PurePath
            reference = os.listdir(str(directory))  # type: List[str]
            with self.subTest(artist=artist):
                paths = sorted(chain.from_iterable(compress(album, [0, 1, 0, 0]) for album in list(get_albums(directory))))  # type: List[str]
                self.assertListEqual(paths, sorted(map(join, repeat(str(directory)), reference)))


@unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
class TestGetAlbums03(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.artists = specifics  # type: List[Tuple[str, str]]

    def test_t01(self):
        for letter, artist in self.artists:
            # ----
            first_directory = MUSIC / letter / artist / "1"  # type: PurePath
            self.reference = list(map(lambda i: i.split("-", maxsplit=1)[-1].strip(), os.listdir(str(first_directory))))  # type: List[str]

            # -----
            second_directory = MUSIC / letter / artist / "2"  # type: PurePath
            self.reference.extend(chain.from_iterable([os.listdir(str(second_directory / year)) for year in os.listdir(str(second_directory)) if re.match(f"^{DFTYEARREGEX}$", year)]))

            # -----
            with self.subTest(artist=artist):
                albums = chain.from_iterable(compress(album, [1, 0, 0, 0]) for album in list(get_albums(MUSIC / letter / artist)))  # type: List[str]
                self.assertListEqual(sorted(albums), sorted(self.reference))
