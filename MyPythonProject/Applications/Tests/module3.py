# -*- coding: utf-8 -*-
import logging.config
import os
import unittest
from contextlib import ExitStack
from tempfile import TemporaryDirectory

import yaml

from Main import get_tags
from ..AudioCD.shared import RippedDisc
from ..Tables.Albums.shared import insertfromfile
from ..Tables.RippedDiscs.shared import get_totallogs
from ..shared import DATABASE, UTF16, UTF8, copy

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))

basename, join = os.path.basename, os.path.join


class RippedDiscTest(unittest.TestCase):

    def setUp(self):
        self.totallogs = get_totallogs(DATABASE)
        with open(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tests", "tags.yml"), encoding=UTF8) as stream:
            self.config = yaml.load(stream)

    def test_01first(self):
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

    def test_02second(self):
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
                    get_tags(profile, stream, *decorators, db=database, db_albums=albums, db_bootlegs=bootlegs, dbjsonfile=jsontags)

            stack = ExitStack()
            try:
                stream = stack.enter_context(open(jsontags, encoding=UTF8))
            except FileNotFoundError:
                pass
            else:
                with stack:
                    insertfromfile(stream)
            self.assertEqual(self.totallogs + items, get_totallogs(database))

    def test_03third(self):
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
                    get_tags(profile, stream, *decorators, db=database, db_albums=albums, db_bootlegs=bootlegs, dbjsonfile=jsontags)

            stack = ExitStack()
            try:
                stream = stack.enter_context(open(jsontags, encoding=UTF8))
            except FileNotFoundError:
                pass
            else:
                with stack:
                    inserted = insertfromfile(stream)
            self.assertEqual(inserted, items)
