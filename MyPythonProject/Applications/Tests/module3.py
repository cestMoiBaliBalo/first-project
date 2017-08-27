# -*- coding: utf-8 -*-
from ..Database.DigitalAudioFiles.shared import selectalbums
import itertools
import unittest

__author__ = 'Xavier ROSSET'


class Test01(unittest.TestCase):

    def setUp(self):
        self.thatlist = list(itertools.chain.from_iterable([(row.artist, row.album, row.language, row.year) for row in selectalbums(albumid="I.INXS.1.19870000.1") if row]))

    def test_01first(self):
        self.assertEqual(len(self.thatlist), 4)

    def test_02second(self):
        artist, album, language, year = self.thatlist
        self.assertEqual(artist, "INXS")

    def test_03third(self):
        artist, album, language, year = self.thatlist
        self.assertEqual(album.lower(), "kick")

    def test_04fourth(self):
        artist, album, language, year = self.thatlist
        self.assertEqual(language.lower(), "english")

    def test_05fifth(self):
        artist, album, language, year = self.thatlist
        self.assertEqual(year, 1987)
