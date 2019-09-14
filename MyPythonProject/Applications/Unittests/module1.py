# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import itertools
import json
import locale
import os
import sys
import unittest
from collections.abc import MutableSequence
from datetime import datetime
from functools import partial
from operator import contains, eq, gt, lt
from unittest.mock import patch

from Applications.Tables.Albums import shared
from Applications.shared import DATABASE, TitleCaseConverter, ToBoolean, UTF8, eq_string, get_rippingapplication, int_, itemgetter2_, itemgetter_, now, partial_

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# ==========
# Functions.
# ==========
def split_(char: str, strg: str):
    return strg.split(char)


@int_
@itemgetter_(0, 2)
@partial_(".")
def split1_(char: str, strg: str):
    return strg.split(char)


@int_
@itemgetter_(0, 1)
@partial_(".")
def split2_(char: str, strg: str):
    return strg.split(char)


@partial_(".")
def split3_(char: str, strg: str):
    return strg.split(char)


@int_
@itemgetter_(1, 2)
@partial_(".")
def split4_(char: str, strg: str):
    return strg.split(char)


@int_
@itemgetter_(1, 1)
@partial_(".")
def split5_(char: str, strg: str):
    return strg.split(char)


@int_
@itemgetter_(1, 0)
@partial_(".")
def split6_(char: str, strg: str):
    return strg.split(char)


# ==============
# Tests classes.
# ==============
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
                self._seq = sorted(sorted(sorted(seq, key=int_(itemgetter2_(2)(partial(split_, ".")))), key=itemgetter2_()(partial(split_, "."))), key=itemgetter2_(1)(partial(split_, ".")))

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
        self.iterable = ["2016_00001", "2016_00002", "2016_00003", "2016_00101", "2015_00456"]

    def test_t01(self):
        self.assertEqual(int(max(self.iterable).split("_")[1]), 101)

    def test_t02(self):
        self.assertEqual(int_(itemgetter2_(1)(partial(split_, "_")))(max(self.iterable)), 101)

    def test_t03(self):
        self.assertEqual(int(max([item.split("_")[1] for item in self.iterable])), 456)

    def test_t04(self):
        self.assertEqual(max(map(int_(itemgetter2_(1)(partial(split_, "_"))), self.iterable)), 456)

    def test_t05(self):
        self.assertListEqual(sorted(self.iterable, key=int_(itemgetter2_(1)(partial(split_, "_")))), ["2016_00001", "2016_00002", "2016_00003", "2016_00101", "2015_00456"])

    def test_t06(self):
        self.assertListEqual(sorted(sorted(self.iterable, key=int_(itemgetter2_(1)(partial(split_, "_")))), key=int_(itemgetter2_()(partial(split_, "_")))),
                             ["2015_00456", "2016_00001", "2016_00002", "2016_00003", "2016_00101"])


class Test04(unittest.TestCase):
    def test_t01(self):
        self.assertTrue(ToBoolean("Y").boolean_value)

    def test_t02(self):
        self.assertFalse(ToBoolean("N").boolean_value)

    def test_t03(self):
        self.assertFalse(ToBoolean("O").boolean_value)

    def test_t04(self):
        self.assertFalse(ToBoolean("toto").boolean_value)


class TestTitleCaseConverter(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources", "titles.json"), encoding=UTF8) as stream:
            self.titles = json.load(stream)

    def test_t01(self):
        for title in self.titles:
            title_in, title_out = title
            with self.subTest(title=title_in):
                self.assertEqual(title_out, TitleCaseConverter().convert(title_in))


class TestGetRippingApplication(unittest.TestCase):
    """

    """

    def test_t01(self):
        self.assertEqual(get_rippingapplication(), "dBpoweramp Release 16.6")

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
        decorated_function = itemgetter_()(partial(eq_string, "alternative rock"))
        self.assertTrue(decorated_function(self.iterable))

    def test_t02(self):
        decorated_function = itemgetter_(1)(partial(eq_string, "black metal"))
        self.assertTrue(decorated_function(self.iterable))

    def test_t03(self):
        decorated_function = itemgetter_(1)(partial(eq_string, "Black Metal", sensitive=True))
        self.assertTrue(decorated_function(self.iterable))

    def test_t04(self):
        decorated_function = itemgetter_(1)(partial(eq_string, "black metal", sensitive=True))
        self.assertFalse(decorated_function(self.iterable))

    def test_t05(self):
        decorated_function = itemgetter_(2)(partial(eq_string, "black metal"))
        self.assertFalse(decorated_function(self.iterable))


class TestDecorator02(unittest.TestCase):
    """

    """

    def setUp(self):
        self.iterable = [(1, "first string"), (2, "second string"), (3, "third string")]

    def test_t01(self):
        decorated_function = itemgetter_()(partial(eq, 3))
        self.assertListEqual(list(filter(decorated_function, self.iterable)), [(3, "third string")])

    def test_t02(self):
        decorated_function = itemgetter_()(partial(eq, 2))
        self.assertListEqual(list(filter(decorated_function, self.iterable)), [(2, "second string")])


class TestDecorator03(unittest.TestCase):
    """

    """

    def setUp(self):
        self.iterable = [("console", "AA"), ("database", "BB"), ("debug", "CC"), ("foo", "DD"), ("bar", "EE")]

    def test_t01(self):
        decorated_function = itemgetter_()(partial(contains, ["console", "database", "debug"]))
        self.assertListEqual(list(itertools.filterfalse(decorated_function, self.iterable)), [("foo", "DD"), ("bar", "EE")])

    def test_t02(self):
        decorated_function = itemgetter_()(partial(contains, ["console", "database", "debug"]))
        self.assertListEqual(list(filter(decorated_function, self.iterable)), [("console", "AA"), ("database", "BB"), ("debug", "CC")])


@unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
class TestDecorator04(unittest.TestCase):
    """

    """

    def test_t01(self):
        _, genreid1 = list(filter(lambda i: i[0].lower() == "hard rock", shared.get_genres(DATABASE)))[0]
        _, genreid2 = next(filter(itemgetter_()(partial(eq_string, "hard rock")), shared.get_genres(DATABASE)))
        self.assertEqual(genreid1, genreid2)

    def test_t02(self):
        _, genreid1 = list(filter(lambda i: i[0].lower() == "hard rock", shared.get_genres(DATABASE)))[0]
        _, genreid2 = next(filter(itemgetter_()(partial(eq_string, "rock")), shared.get_genres(DATABASE)))
        self.assertNotEqual(genreid1, genreid2)

    def test_t03(self):
        genre = list(filter(itemgetter_()(partial(eq_string, "Hard Rock", sensitive=True)), shared.get_genres(DATABASE)))
        self.assertListEqual(genre, [("Hard Rock", 2)])

    def test_t04(self):
        genre = list(filter(itemgetter_()(partial(eq_string, "hard rock", sensitive=True)), shared.get_genres(DATABASE)))
        self.assertListEqual(genre, [])

    def test_t05(self):
        genre = list(filter(itemgetter_()(partial(eq_string, "hard rock")), shared.get_genres(DATABASE)))
        self.assertListEqual(genre, [("Hard Rock", 2)])

    def test_t06(self):
        genre = list(filter(itemgetter_()(partial(eq_string, "Hard Rock")), shared.get_genres(DATABASE)))
        self.assertListEqual(genre, [("Hard Rock", 2)])

    def test_t07(self):
        genre = list(filter(itemgetter_()(partial(eq_string, "some genre")), shared.get_genres(DATABASE)))
        self.assertListEqual(genre, [])


class TestDecorator05(unittest.TestCase):
    """

    """

    def setUp(self):
        self.iterable = ("1.20160000.10",)

    def test_t01(self):
        self.assertEqual(split1_(self.iterable), 10)

    def test_t02(self):
        self.assertEqual(split2_(self.iterable), 20160000)


class TestDecorator06(unittest.TestCase):
    """

    """

    def setUp(self):
        self.iterable = ["2.20160125.13", "2.20160201.13", "2.20160120.13", "1.20160625.13", "1.20160422.13", "2.20160422.15", "2.19841102.13", "2.19990822.13", "2.20021014.13", "2.20000823.13",
                         "2.20170101.13", "1.20160422.02"]

    def test_t01(self):
        self.assertListEqual(sorted(sorted(self.iterable, key=int_(itemgetter2_(2)(partial(split_, ".")))), key=int_(itemgetter2_(1)(partial(split_, ".")))), ["2.19841102.13",
                                                                                                                                                               "2.19990822.13",
                                                                                                                                                               "2.20000823.13",
                                                                                                                                                               "2.20021014.13",
                                                                                                                                                               "2.20160120.13",
                                                                                                                                                               "2.20160125.13",
                                                                                                                                                               "2.20160201.13",
                                                                                                                                                               "1.20160422.02",
                                                                                                                                                               "1.20160422.13",
                                                                                                                                                               "2.20160422.15",
                                                                                                                                                               "1.20160625.13",
                                                                                                                                                               "2.20170101.13"])

    def test_t02(self):
        self.assertListEqual(
                sorted(sorted(sorted(self.iterable, key=int_(itemgetter2_(2)(partial(split_, ".")))), key=int_(itemgetter2_(1)(partial(split_, ".")))), key=int_(itemgetter2_()(partial(split_, ".")))),
                ["1.20160422.02",
                 "1.20160422.13",
                 "1.20160625.13",
                 "2.19841102.13",
                 "2.19990822.13",
                 "2.20000823.13",
                 "2.20021014.13",
                 "2.20160120.13",
                 "2.20160125.13",
                 "2.20160201.13",
                 "2.20160422.15",
                 "2.20170101.13"])


class TestDecorator07(unittest.TestCase):
    """

    """

    def setUp(self):
        self.iterable = [("A", "2.20160125.13"), ("B", "2.20160201.13"), ("C", "2.20160120.13"), ("D", "1.20160625.13"), ("E", "1.20160422.13"), ("F", "2.20160422.15"), ("H", "2.19841102.13"),
                         ("I", "2.19990822.13"), ("K", "2.20021014.13"), ("L", "2.20000823.13"), ("M", "2.20170101.13"), ("N", "1.20160422.02")]

    def test_t01(self):
        self.assertListEqual(sorted(sorted(self.iterable, key=int_(itemgetter_(1, 2)(split3_))), key=int_(itemgetter_(1, 1)(split3_))), [("H", "2.19841102.13"),
                                                                                                                                         ("I", "2.19990822.13"),
                                                                                                                                         ("L", "2.20000823.13"),
                                                                                                                                         ("K", "2.20021014.13"),
                                                                                                                                         ("C", "2.20160120.13"),
                                                                                                                                         ("A", "2.20160125.13"),
                                                                                                                                         ("B", "2.20160201.13"),
                                                                                                                                         ("N", "1.20160422.02"),
                                                                                                                                         ("E", "1.20160422.13"),
                                                                                                                                         ("F", "2.20160422.15"),
                                                                                                                                         ("D", "1.20160625.13"),
                                                                                                                                         ("M", "2.20170101.13")])

    def test_t02(self):
        self.assertListEqual(sorted(sorted(sorted(self.iterable, key=int_(itemgetter_(1, 2)(split3_))), key=int_(itemgetter_(1, 1)(split3_))), key=int_(itemgetter_(1, 0)(split3_))),
                             [("N", "1.20160422.02"),
                              ("E", "1.20160422.13"),
                              ("D", "1.20160625.13"),
                              ("H", "2.19841102.13"),
                              ("I", "2.19990822.13"),
                              ("L", "2.20000823.13"),
                              ("K", "2.20021014.13"),
                              ("C", "2.20160120.13"),
                              ("A", "2.20160125.13"),
                              ("B", "2.20160201.13"),
                              ("F", "2.20160422.15"),
                              ("M", "2.20170101.13")])

    def test_t03(self):
        self.assertListEqual(sorted(sorted(sorted(self.iterable, key=split4_), key=split5_), key=split6_), [("N", "1.20160422.02"),
                                                                                                            ("E", "1.20160422.13"),
                                                                                                            ("D", "1.20160625.13"),
                                                                                                            ("H", "2.19841102.13"),
                                                                                                            ("I", "2.19990822.13"),
                                                                                                            ("L", "2.20000823.13"),
                                                                                                            ("K", "2.20021014.13"),
                                                                                                            ("C", "2.20160120.13"),
                                                                                                            ("A", "2.20160125.13"),
                                                                                                            ("B", "2.20160201.13"),
                                                                                                            ("F", "2.20160422.15"),
                                                                                                            ("M", "2.20170101.13")])


@patch("Applications.shared.datetime")
class TestMock01(unittest.TestCase):
    """

    """

    def setUp(self):
        self.locale = locale.getlocale()
        if sys.platform.startswith("win"):
            locale.setlocale(locale.LC_ALL, ("french", "fr_FR.ISO8859-1"))
        elif sys.platform.startswith("lin"):
            locale.setlocale(locale.LC_ALL, "fr_FR.utf8")
        self.datetime = datetime(2019, 9, 13, 3, 1)
        self.now = "Vendredi 13 Septembre 2019 05:01:00 CEST (UTC+0200)"

    def tearDown(self):
        locale.setlocale(locale.LC_ALL, self.locale)

    def test01(self, mock_datetime):
        mock_datetime.utcnow.return_value = self.datetime
        self.assertEqual(now(), self.now)
        mock_datetime.utcnow.assert_called()
        mock_datetime.utcnow.assert_called_once()
        self.assertEqual(mock_datetime.utcnow.call_count, 1)


@patch("Applications.shared.datetime")
class TestMock02(unittest.TestCase):
    """

    """

    def setUp(self):
        self.locale = locale.getlocale()
        if sys.platform.startswith("win"):
            locale.setlocale(locale.LC_ALL, ("french", "fr_FR.ISO8859-1"))
        elif sys.platform.startswith("lin"):
            locale.setlocale(locale.LC_ALL, "fr_FR.utf8")
        self.datetime = [datetime(2019, 9, 13, 3, 1), datetime(2019, 9, 13, 3, 2)]
        self.now1 = "Vendredi 13 Septembre 2019 05:01:00 CEST (UTC+0200)"
        self.now2 = "Vendredi 13 Septembre 2019 05:02:00 CEST (UTC+0200)"

    def tearDown(self):
        locale.setlocale(locale.LC_ALL, self.locale)

    def test01(self, mock_datetime):
        mock_datetime.utcnow.side_effect = self.datetime
        self.assertEqual(now(), self.now1)
        self.assertEqual(now(), self.now2)
        mock_datetime.utcnow.assert_called()
        self.assertEqual(mock_datetime.utcnow.call_count, 2)
