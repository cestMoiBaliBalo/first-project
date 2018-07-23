# -*- coding: utf-8 -*-
import logging.config
import os
import unittest
from contextlib import ExitStack
from tempfile import TemporaryDirectory

import yaml

from ..AudioCD.shared import RippedDisc
from ..shared import UTF16, UTF8

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))

join = os.path.join


class RippedDiscTest(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tests", "tags.yml"), encoding=UTF8) as stream:
            self.config = yaml.load(stream)

    def test_01(self):
        with TemporaryDirectory() as tempdir:
            txttags = join(tempdir, "tags.txt")
            for key, value in self.config.items():
                tags, profile, decorators, albums, bootlegs, expected = value

                # -----
                with open(txttags, mode="w", encoding=UTF16) as stream:
                    for k, v in tags.items():
                        stream.write("{0}={1}\n".format(k.lower(), v))

                # -----
                with open(txttags, mode="r+", encoding=UTF16) as stream:
                    with ExitStack() as stack:
                        track = stack.enter_context(RippedDisc(profile, stream, *decorators))

                # -----
                for k, v in expected.items():
                    with self.subTest(key=k):
                        self.assertEqual(v, getattr(track.audiotrack, k, None))
