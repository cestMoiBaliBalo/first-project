# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import logging.config
import os
import unittest
from itertools import chain, compress

import yaml

from Applications.shared import get_albums

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))


class TestGetAlbums(unittest.TestCase):
    albums = list(get_albums(r"F:\A\Adams, Bryan"))

    def test_t01(self):
        albums = sorted(chain.from_iterable(compress(album, [1, 0, 0, 0]) for album in self.albums))
        self.assertListEqual(albums, ["Cuts Like a Knife", "Into the Fire", "Reckless", "Waking Up The Neighbours"])

    def test_t02(self):
        albums = sorted(chain.from_iterable(compress(album, [0, 1, 0, 0]) for album in self.albums))
        self.assertListEqual(albums, [r"F:\A\Adams, Bryan\1983 - Cuts Like a Knife",
                                      r"F:\A\Adams, Bryan\1984 - Reckless",
                                      r"F:\A\Adams, Bryan\1987 - Into the Fire",
                                      r"F:\A\Adams, Bryan\1991 - Waking Up The Neighbours"])
