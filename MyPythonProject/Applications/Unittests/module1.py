# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import itertools
import json
import os
import sys
import unittest
from collections.abc import MutableSequence
from datetime import datetime
from functools import partial
from operator import eq, gt, lt

from pytz import timezone

from Applications.Tables.Albums.shared import get_genres
from Applications.shared import DATABASE, TitleCaseConverter, UTF8, contains_, eq_integer, eq_string, get_readabledate, get_rippingapplication, getitem_, partial_

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# ========
# Classes.
# ========
class Test01(unittest.TestCase):
    def setUp(self):
        self.ref = [1, 2, 3, 4, 5, 6, 7, 8]

    def test_t01(self):
        self.assertTrue(all([lt(x, 50) for x in self.ref]))

    def test_t02(self):
        self.assertFalse(all([gt(x, 50) for x in self.ref]))

    def test_t03(self):
        self.assertTrue(any([gt(x, 5) for x in self.ref]))

    def test_t04(self):
        self.assertTrue(any([eq(x, 5) for x in self.ref]))

    def test_t05(self):
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

    def test_t01(self):
        self.assertListEqual(self.obj.sequence, ["2.19841102.13", "2.19990822.13", "2.20000823.13", "2.20021014.13", "2.20160120.13", "2.20160125.13", "2.20160201.13", "1.20160422.02", "1.20160422.13",
                                                 "2.20160422.13", "2.20160422.15", "1.20160625.13", "2.20170101.13"])

    def test_t02(self):
        self.assertListEqual(list(self.obj), ["1984", "1999", "2000", "2002", "2016", "2016", "2016", "2016", "2016", "2016", "2016", "2016", "2017"])

    def test_t03(self):
        sentinel = "2016"
        self.assertListEqual(list(iter(partial(self.obj, sentinel), sentinel)), ["1984", "1999", "2000", "2002"])

    def test_t04(self):
        sentinel = "2018"
        self.assertListEqual(list(iter(partial(self.obj, sentinel), sentinel)), ["1984", "1999", "2000", "2002", "2016", "2016", "2016", "2016", "2016", "2016", "2016", "2016", "2017"])

    def test_t05(self):
        sentinel = "2017"
        self.assertListEqual(sorted(set(iter(partial(self.obj, sentinel), sentinel))), ["1984", "1999", "2000", "2002", "2016"])


class Test03(unittest.TestCase):
    def setUp(self):
        self.x = ["2016_00001", "2016_00002", "2016_00003", "2016_00101", "2015_00456"]

    def test_t01(self):
        self.assertEqual(int(max(self.x).split("_")[1]), 101)

    def test_t02(self):
        self.assertEqual(int(max([i.split("_")[1] for i in self.x])), 456)

    def test_t03(self):
        def myfunc1(s):
            return int(s.split("_")[1])

        self.assertListEqual(sorted(self.x, key=myfunc1), ["2016_00001", "2016_00002", "2016_00003", "2016_00101", "2015_00456"])

    def test_t04(self):
        self.assertListEqual(sorted(sorted(self.x, key=lambda i: int(i.split("_")[1])), key=lambda i: int(i.split("_")[0])), ["2015_00456", "2016_00001", "2016_00002", "2016_00003", "2016_00101"])


# class Test05(unittest.TestCase):
#     def test_t01(self):
#         self.assertEqual(validmonth("Janvier 2017"), 201701)
#
#     def test_t02(self):
#         self.assertEqual(validmonth("2017 01"), 201701)
#
#     def test_t03(self):
#         self.assertEqual(validmonth("Février 2017"), 201702)
#
#     def test_t04(self):
#         self.assertEqual(validmonth("2017 02"), 201702)
#
#     def test_t05(self):
#         self.assertEqual(validmonth("2017-02"), 201702)


class TestTitleCaseConverter(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources", "titles.json"), encoding=UTF8) as stream:
            self.titles = json.load(stream)

    def test_t01(self):
        for title in self.titles:
            title_in, title_out = title
            with self.subTest(title=title_in):
                self.assertEqual(title_out, TitleCaseConverter().convert(title_in))


@unittest.skip
class TestGetReadableDate(unittest.TestCase):

    def setUp(self):
        self.readable_date = "Jeudi 08 Novembre 2018 13:48:51 CET (UTC+0100)"

    def test_t01(self):
        self.assertEqual(get_readabledate(datetime(2018, 11, 8, 13, 48, 51), tz=timezone("Europe/Paris")), self.readable_date)

    def test_t02(self):
        self.assertEqual(get_readabledate(datetime(2018, 11, 8, 12, 48, 51), tz=timezone("UTC")), self.readable_date)


class TestGetRippingApplication(unittest.TestCase):
    """

    """

    def test_t01(self):
        self.assertEqual(get_rippingapplication(), "dBpoweramp 16.5")

    def test_t02(self):
        self.assertEqual(get_rippingapplication(timestamp=1541702820), "dBpoweramp 15.1")

    def test_t03(self):
        self.assertEqual(get_rippingapplication(timestamp=1547146020), "dBpoweramp 15.1")

    def test_t04(self):
        self.assertEqual(get_rippingapplication(timestamp=1357843620), "dBpoweramp 14.1")

    def test_t05(self):
        self.assertEqual(get_rippingapplication(timestamp=1548976600), "dBpoweramp 15.1")

    def test_t06(self):
        self.assertEqual(get_rippingapplication(timestamp=1554026400), "dBpoweramp 16.5")


class TestDecorator01(unittest.TestCase):
    """

    """

    def setUp(self):
        self.iterable = ["Alternative Rock", "Black Metal", "Hard Rock", "Rock"]

    def test_t01(self):
        decorated_function = getitem_()(partial_("alternative rock")(eq_string))
        self.assertTrue(decorated_function(self.iterable))

    def test_t02(self):
        decorated_function = getitem_(index=1)(partial_("black metal")(eq_string))
        self.assertTrue(decorated_function(self.iterable))

    def test_t03(self):
        decorated_function = getitem_(index=1)(partial_("Black Metal", sensitive=True)(eq_string))
        self.assertTrue(decorated_function(self.iterable))

    def test_t04(self):
        decorated_function = getitem_(index=1)(partial_("black metal", sensitive=True)(eq_string))
        self.assertFalse(decorated_function(self.iterable))

    def test_t05(self):
        decorated_function = getitem_(index=2)(partial_("black metal")(eq_string))
        self.assertFalse(decorated_function(self.iterable))


class TestDecorator02(unittest.TestCase):
    """

    """

    def setUp(self):
        self.iterable = [(1, "first string"), (2, "second string"), (3, "third string")]

    def test_t01(self):
        decorated_function = getitem_()(partial_(3)(eq_integer))
        self.assertListEqual(list(filter(decorated_function, self.iterable)), [(3, "third string")])

    def test_t02(self):
        decorated_function = getitem_()(partial_(2)(eq_integer))
        self.assertListEqual(list(filter(decorated_function, self.iterable)), [(2, "second string")])


class TestDecorator03(unittest.TestCase):
    """

    """

    def setUp(self):
        self.iterable = [("console", "AA"), ("database", "BB"), ("debug", "CC"), ("foo", "DD"), ("bar", "EE")]

    def test_t01(self):
        decorated_function = getitem_()(partial_(["console", "database", "debug"])(contains_))
        self.assertListEqual(list(itertools.filterfalse(decorated_function, self.iterable)), [("foo", "DD"), ("bar", "EE")])

    def test_t02(self):
        decorated_function = getitem_()(partial_(["console", "database", "debug"])(contains_))
        self.assertListEqual(list(filter(decorated_function, self.iterable)), [("console", "AA"), ("database", "BB"), ("debug", "CC")])

    @unittest.skip
    def test_t03(self):
        decorated_function = getitem_()(partial_(["console", "database", "debug"])(contains_))
        self.assertListEqual(list(itertools.filterfalse(decorated_function, self.iterable)), [("console", "AA"), ("database", "BB"), ("debug", "CC")])


@unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
class TestDecorator04(unittest.TestCase):
    """

    """

    def test_t01(self):
        _, genreid1 = list(filter(lambda i: i[0].lower() == "hard rock", get_genres(DATABASE)))[0]
        _, genreid2 = next(filter(getitem_()(partial_("hard rock")(eq_string)), get_genres(DATABASE)))
        self.assertEqual(genreid1, genreid2)

    def test_t02(self):
        _, genreid1 = list(filter(lambda i: i[0].lower() == "hard rock", get_genres(DATABASE)))[0]
        _, genreid2 = next(filter(getitem_()(partial_("rock")(eq_string)), get_genres(DATABASE)))
        self.assertNotEqual(genreid1, genreid2)
