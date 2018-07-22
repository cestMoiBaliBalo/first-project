# -*- coding: utf-8 -*-
import logging.config
import os
import unittest
from collections import MutableSequence
from functools import partial
from operator import eq, gt, lt

import yaml

from Interface_Tables import validmonth
from .. import shared

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))


# ========
# Classes.
# ========
class Test01(unittest.TestCase):
    def setUp(self):
        self.ref = [1, 2, 3, 4, 5, 6, 7, 8]

    def test_01first(self):
        self.assertTrue(all([lt(x, 50) for x in self.ref]))

    def test_02second(self):
        self.assertFalse(all([gt(x, 50) for x in self.ref]))

    def test_03third(self):
        self.assertTrue(any([gt(x, 5) for x in self.ref]))

    def test_04fourth(self):
        self.assertTrue(any([eq(x, 5) for x in self.ref]))

    def test_05fifth(self):
        self.assertFalse(all([eq(x, 5) for x in self.ref]))


class Test02(unittest.TestCase):
    def setUp(self):

        class ThatClass(MutableSequence):

            def __init__(self, seq):
                self._index = -1
                self._seq = sorted(sorted(sorted(seq, key=lambda i: int(i.split(".")[2])), key=lambda i: int(i.split(".")[0])), key=lambda i: int(i.split(".")[1]))

            def __getitem__(self, item):
                return self._seq[item]

            def __setitem__(self, key, value):
                self._seq[key] = value

            def __delitem__(self, key):
                del self._seq[key]

            def __len__(self):
                return len(self._seq)

            def __iter__(self):
                return self

            def __next__(self):
                self._index += 1
                if self._index >= len(self._seq):
                    raise StopIteration
                return self._seq[self._index][2:6]

            def __call__(self, arg):
                self._index += 1
                try:
                    return self._seq[self._index][2:6]
                except IndexError:
                    return arg

            def insert(self, index, value):
                self._seq.insert(index, value)

            @property
            def sequence(self):
                return self._seq

        self.obj = ThatClass(["2.20160125.13", "2.20160201.13", "2.20160120.13", "1.20160625.13", "2.20160422.13", "1.20160422.13", "2.20160422.15", "2.19841102.13", "2.19990822.13", "2.20021014.13",
                              "2.20000823.13", "2.20170101.13", "1.20160422.02"])

    def test_01first(self):
        self.assertListEqual(self.obj.sequence, ["2.19841102.13", "2.19990822.13", "2.20000823.13", "2.20021014.13", "2.20160120.13", "2.20160125.13", "2.20160201.13", "1.20160422.02", "1.20160422.13",
                                                 "2.20160422.13", "2.20160422.15", "1.20160625.13", "2.20170101.13"])

    def test_02second(self):
        self.assertListEqual(list(self.obj), ["1984", "1999", "2000", "2002", "2016", "2016", "2016", "2016", "2016", "2016", "2016", "2016", "2017"])

    def test_03third(self):
        sentinel = "2016"
        self.assertListEqual(list(iter(partial(self.obj, sentinel), sentinel)), ["1984", "1999", "2000", "2002"])

    def test_04fourth(self):
        sentinel = "2018"
        self.assertListEqual(list(iter(partial(self.obj, sentinel), sentinel)), ["1984", "1999", "2000", "2002", "2016", "2016", "2016", "2016", "2016", "2016", "2016", "2016", "2017"])

    def test_05fifth(self):
        sentinel = "2017"
        self.assertListEqual(sorted(set(iter(partial(self.obj, sentinel), sentinel))), ["1984", "1999", "2000", "2002", "2016"])


class Test03(unittest.TestCase):
    def setUp(self):
        self.x = ["2016_00001", "2016_00002", "2016_00003", "2016_00101", "2015_00456"]

    def test_01first(self):
        self.assertEqual(int(max(self.x).split("_")[1]), 101)

    def test_02second(self):
        self.assertEqual(int(max([i.split("_")[1] for i in self.x])), 456)

    def test_03third(self):
        def myfunc1(s):
            return int(s.split("_")[1])

        self.assertListEqual(sorted(self.x, key=myfunc1), ["2016_00001", "2016_00002", "2016_00003", "2016_00101", "2015_00456"])

    def test_04fourth(self):
        self.assertListEqual(sorted(sorted(self.x, key=lambda i: int(i.split("_")[1])), key=lambda i: int(i.split("_")[0])), ["2015_00456", "2016_00001", "2016_00002", "2016_00003", "2016_00101"])


@unittest.skip
class Test04(unittest.TestCase):
    def test_01first(self):
        myimg = shared.Images(r"H:\201601\201601_00001.JPG")
        self.assertEqual(myimg.originaldatetime, "22/01/2016 10:03:26 CET+0100")

    def test_02second(self):
        self.assertRaises(FileNotFoundError, shared.Images, r"H:\201701\201701_00001.JPG")

    def test_03third(self):
        self.assertRaises(OSError, shared.Images, r"C:\Users\Xavier\Documents\Music - Regex test files.xav")


class Test05(unittest.TestCase):
    def test_01first(self):
        self.assertEqual(validmonth("Janvier 2017"), 201701)

    def test_02second(self):
        self.assertEqual(validmonth("2017 01"), 201701)

    def test_03third(self):
        self.assertEqual(validmonth("Février 2017"), 201702)

    def test_04fourth(self):
        self.assertEqual(validmonth("2017 02"), 201702)

    def test_05fifth(self):
        self.assertEqual(validmonth("2017-02"), 201702)


class Test06(unittest.TestCase):
    """
    Test regular expressions.
    """

    def test_01first(self):
        self.assertRegex("1.19840000.1.13", r"^(?=1\.\d[\d.]+$)(?=[\d.]+\.13$)1\.(?:{0})0000\.\d\.13$".format(shared.DFTYEARREGEX))

    def test_02second(self):
        self.assertNotRegex("1.19840000.1.15", r"^(?=1\.\d[\d.]+$)(?=[\d.]+\.13$)1\.(?:{0})0000\.\d\.13$".format(shared.DFTYEARREGEX))

    def test_03third(self):
        self.assertNotRegex("1.19840000.1", r"^(?=1\.\d[\d.]+$)(?=[\d.]+\.13$)1\.(?:{0})0000\.\d\.13$".format(shared.DFTYEARREGEX))

    def test_04fourth(self):
        self.assertNotRegex("2.20160529.1.13", r"^(?=1\.\d[\d.]+$)(?=[\d.]+\.13$)1\.(?:{0})0000\.\d\.13$".format(shared.DFTYEARREGEX))

    def test_05fifth(self):
        self.assertNotRegex("2.99999999.1.13", r"^(?=1\.\d[\d.]+$)(?=[\d.]+\.13$)1\.(?:{0})0000\.\d\.13$".format(shared.DFTYEARREGEX))

    def test_06sixth(self):
        self.assertRegex("1994.1 - Dissident", r"^(?:{0})\.\d -\B".format(shared.DFTYEARREGEX))

    def test_07seventh(self):
        self.assertNotRegex("Dissident", r"^(?:{0})\.\d -\B".format(shared.DFTYEARREGEX))

    def test_08eighth(self):
        self.assertNotRegex("1994 - Dissident", r"^(?:{0})\.\d -\B".format(shared.DFTYEARREGEX))

    def test_09ninth(self):
        self.assertRegex("Janvier 2017", r"^\b[\w]+\b\s\b{0}$".format(shared.DFTYEARREGEX))

    def test_10Tenth(self):
        self.assertRegex("Février 2017", r"^\b[\w]+\b\s\b{0}$".format(shared.DFTYEARREGEX))
