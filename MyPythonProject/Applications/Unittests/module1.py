# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import itertools
import json
import locale
import os
import shutil
import sys
import tempfile
import unittest
from collections.abc import MutableSequence
from datetime import datetime
from functools import partial, wraps
from itertools import filterfalse
from operator import contains, eq, gt, itemgetter, lt
from pathlib import PurePath
from typing import Union
from unittest.mock import patch

import yaml

from Applications.Tables.Albums import shared
from Applications.callables import chain_
from Applications.decorators import itemgetter_, partial_
from Applications.shared import DATABASE, TitleCaseConverter, ToBoolean, UTF8, booleanify, eq_string_, get_rippingapplication, groupby, nested_groupby, now

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_THATFILE = PurePath(os.path.abspath(__file__))  # type: PurePath
locale.setlocale(locale.LC_ALL, "fr_FR.utf8")


# ===============
# Global classes.
# ===============
class SetUp(object):

    def _decorate_callable(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with open(self._path, encoding=self._encoding) as stream:
                collection = yaml.load(stream, Loader=yaml.FullLoader)
            args += (collection,)
            func(*args, **kwargs)

        return wrapper

    def _decorate_class(self, klass):
        for attr in dir(klass):
            if not attr.startswith("test"):
                continue
            attr_value = getattr(klass, attr)
            if not hasattr(attr_value, "__call__"):
                continue
            setattr(klass, attr, self(attr_value))
        return klass

    def __init__(self, path: Union[PurePath, str], *, encoding: str = "UTF_8") -> None:
        self._path = path
        self._encoding = encoding

    def __call__(self, arg):
        if isinstance(arg, type):
            return self._decorate_class(arg)
        return self._decorate_callable(arg)


# =================
# Global functions.
# =================
def booleanify_(*args):
    return tuple(map(booleanify, args))


def split_(char: str, strg: str):
    return strg.split(char)


@itemgetter_(1)
@partial_(".")
def split2_(char: str, strg: str):
    return strg.split(char)


@chain_(itemgetter(2), int)
@itemgetter_(1)
@partial_(".")
def split3_(char: str, strg: str):
    return strg.split(char)


@chain_(itemgetter(1), int)
@itemgetter_(1)
@partial_(".")
def split4_(char: str, strg: str):
    return strg.split(char)


@chain_(itemgetter(0), int)
@itemgetter_(1)
@partial_(".")
def split5_(char: str, strg: str):
    return strg.split(char)


# ==============
# Tests classes.
# ==============
class Test01(unittest.TestCase):
    def setUp(self) -> None:
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
    def setUp(self) -> None:

        class ThatClass(MutableSequence):

            def __init__(self, seq):
                self._index = -1
                self._seq = sorted(sorted(sorted(seq, key=chain_(itemgetter(2), int)(partial(split_, "."))), key=chain_(itemgetter(0))(partial(split_, "."))), key=chain_(itemgetter(1))(partial(split_, ".")))

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
    def setUp(self) -> None:
        self.iterable = ["2016_00001", "2016_00002", "2016_00003", "2016_00101", "2015_00456"]

    def test_t01(self):
        self.assertEqual(max(map(int, map(itemgetter(1), map(partial(split_, "_"), self.iterable)))), 456)

    def test_t02(self):
        self.assertEqual(max(map(chain_(itemgetter(1), int)(partial(split_, "_")), self.iterable)), 456)

    def test_t03(self):
        self.assertListEqual(sorted(self.iterable, key=chain_(itemgetter(1), int)(partial(split_, "_"))), ["2016_00001", "2016_00002", "2016_00003", "2016_00101", "2015_00456"])

    def test_t04(self):
        self.assertListEqual(sorted(sorted(self.iterable, key=chain_(itemgetter(1), int)(partial(split_, "_"))), key=chain_(itemgetter(0), int)(partial(split_, "_"))),
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
    def setUp(self) -> None:
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
        self.assertEqual(get_rippingapplication()[0], "dBpoweramp Release 16.6")

    def test_t02(self):
        self.assertEqual(get_rippingapplication(timestamp=1541702820)[0], "dBpoweramp 15.1")

    def test_t03(self):
        self.assertEqual(get_rippingapplication(timestamp=1547146020)[0], "dBpoweramp 15.1")

    def test_t04(self):
        self.assertEqual(get_rippingapplication(timestamp=1357843620)[0], "dBpoweramp 14.1")

    def test_t05(self):
        self.assertEqual(get_rippingapplication(timestamp=1548976600)[0], "dBpoweramp 15.1")

    def test_t06(self):
        self.assertEqual(get_rippingapplication(timestamp=1554026400)[0], "dBpoweramp 16.5")


class TestDecorator01(unittest.TestCase):
    """

    """

    def setUp(self) -> None:
        self.iterable = ["Alternative Rock", "Black Metal", "Hard Rock", "Rock"]

    def test_t01(self):
        decorated_function = itemgetter_()(partial(eq_string_, "alternative rock"))
        self.assertTrue(decorated_function(self.iterable))

    def test_t02(self):
        decorated_function = itemgetter_(1)(partial(eq_string_, "black metal"))
        self.assertTrue(decorated_function(self.iterable))

    def test_t03(self):
        decorated_function = itemgetter_(1)(partial(eq_string_, "Black Metal", sensitive=True))
        self.assertTrue(decorated_function(self.iterable))

    def test_t04(self):
        decorated_function = itemgetter_(1)(partial(eq_string_, "black metal", sensitive=True))
        self.assertFalse(decorated_function(self.iterable))

    def test_t05(self):
        decorated_function = itemgetter_(2)(partial(eq_string_, "black metal"))
        self.assertFalse(decorated_function(self.iterable))


class TestDecorator02(unittest.TestCase):
    """

    """

    def setUp(self) -> None:
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

    def setUp(self) -> None:
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
        _, genreid2 = next(filter(itemgetter_()(partial(eq_string_, "hard rock")), shared.get_genres(DATABASE)))
        self.assertEqual(genreid1, genreid2)

    def test_t02(self):
        _, genreid1 = list(filter(lambda i: i[0].lower() == "hard rock", shared.get_genres(DATABASE)))[0]
        _, genreid2 = next(filter(itemgetter_()(partial(eq_string_, "rock")), shared.get_genres(DATABASE)))
        self.assertNotEqual(genreid1, genreid2)

    def test_t03(self):
        genre = list(filter(itemgetter_()(partial(eq_string_, "Hard Rock", sensitive=True)), shared.get_genres(DATABASE)))
        self.assertListEqual(genre, [("Hard Rock", 2)])

    def test_t04(self):
        genre = list(filter(itemgetter_()(partial(eq_string_, "hard rock", sensitive=True)), shared.get_genres(DATABASE)))
        self.assertListEqual(genre, [])

    def test_t05(self):
        genre = list(filter(itemgetter_()(partial(eq_string_, "hard rock")), shared.get_genres(DATABASE)))
        self.assertListEqual(genre, [("Hard Rock", 2)])

    def test_t06(self):
        genre = list(filter(itemgetter_()(partial(eq_string_, "Hard Rock")), shared.get_genres(DATABASE)))
        self.assertListEqual(genre, [("Hard Rock", 2)])

    def test_t07(self):
        genre = list(filter(itemgetter_()(partial(eq_string_, "some genre")), shared.get_genres(DATABASE)))
        self.assertListEqual(genre, [])


class TestDecorator05(unittest.TestCase):
    """

    """

    def setUp(self) -> None:
        self.iterable = ("1.20160000.10",)

    def test_t01(self):
        self.assertEqual(int(itemgetter(2)(itemgetter_()(partial(split_, "."))(self.iterable))), 10)

    def test_t02(self):
        self.assertEqual(int(itemgetter(1)(itemgetter_()(partial(split_, "."))(self.iterable))), 20160000)


class TestDecorator06(unittest.TestCase):
    """

    """

    def setUp(self) -> None:
        self.iterable = ["2.20160125.13", "2.20160201.13", "2.20160120.13", "1.20160625.13", "1.20160422.13", "2.20160422.15", "2.19841102.13", "2.19990822.13", "2.20021014.13", "2.20000823.13",
                         "2.20170101.13", "1.20160422.02"]

    def test_t01(self):
        self.assertListEqual(sorted(sorted(self.iterable, key=chain_(itemgetter(2), int)(partial(split_, "."))), key=chain_(itemgetter(1), int)(partial(split_, "."))), ["2.19841102.13",
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
                sorted(sorted(sorted(self.iterable, key=chain_(itemgetter(2), int)(partial(split_, "."))), key=chain_(itemgetter(1), int)(partial(split_, "."))),
                       key=chain_(itemgetter(0), int)(partial(split_, "."))),
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

    def setUp(self) -> None:
        self.iterable = [("A", "2.20160125.13"), ("B", "2.20160201.13"), ("C", "2.20160120.13"), ("D", "1.20160625.13"), ("E", "1.20160422.13"), ("F", "2.20160422.15"), ("H", "2.19841102.13"),
                         ("I", "2.19990822.13"), ("K", "2.20021014.13"), ("L", "2.20000823.13"), ("M", "2.20170101.13"), ("N", "1.20160422.02")]

    def test_t01(self):
        self.assertListEqual(sorted(sorted(self.iterable, key=chain_(itemgetter(2), int)(split2_)), key=chain_(itemgetter(1), int)(split2_)), [("H", "2.19841102.13"),
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
        self.assertListEqual(sorted(sorted(sorted(self.iterable, key=chain_(itemgetter(2), int)(split2_)), key=chain_(itemgetter(1), int)(split2_)), key=chain_(itemgetter(0), int)(split2_)),
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
        self.assertListEqual(sorted(sorted(sorted(self.iterable, key=split3_), key=split4_), key=split5_), [("N", "1.20160422.02"),
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


class TestDecorator08(unittest.TestCase):

    def test_t01(self):
        self.assertListEqual(list(filterfalse(partial(contains, ["A", "C", "E", "G"]), ["A", "B", "C", "D", "E", "F", "G"])), ["B", "D", "F"])

    def test_t02(self):
        self.assertListEqual(list(filterfalse(partial(contains, ["A", "B", "C", "D", "E", "F", "G"]), ["A", "C", "E", "G", "H"])), ["H"])


@patch("Applications.shared.datetime")
class TestMock01(unittest.TestCase):
    """

    """

    def setUp(self) -> None:
        self.datetime = datetime(2019, 9, 13, 3, 1)
        self.now = "Vendredi 13 Septembre 2019 05:01:00 CEST (UTC+0200)"

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

    def setUp(self) -> None:
        self.datetime = [datetime(2019, 9, 13, 3, 1), datetime(2019, 9, 13, 3, 2)]
        self.now1 = "Vendredi 13 Septembre 2019 05:01:00 CEST (UTC+0200)"
        self.now2 = "Vendredi 13 Septembre 2019 05:02:00 CEST (UTC+0200)"

    def test01(self, mock_datetime):
        mock_datetime.utcnow.side_effect = self.datetime
        self.assertEqual(now(), self.now1)
        self.assertEqual(now(), self.now2)
        mock_datetime.utcnow.assert_called()
        self.assertEqual(mock_datetime.utcnow.call_count, 2)


@patch.object(os.path, "expandvars")
class TestMock03(unittest.TestCase):
    """

    """

    def setUp(self) -> None:
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        shutil.rmtree(self.tempdir)

    def test01(self, mock_ospath_expandvars):
        mock_ospath_expandvars.return_value = self.tempdir
        self.assertEqual(os.path.expandvars("%TEMP%"), self.tempdir)
        mock_ospath_expandvars.assert_called_once()

    def test02(self, mock_ospath_expandvars):
        mock_ospath_expandvars.return_value = self.tempdir
        self.assertEqual(os.path.join(os.path.expandvars("%TEMP%"), "toto.txt"), os.path.join(self.tempdir, "toto.txt"))
        mock_ospath_expandvars.assert_called_once()

    def test03(self, mock_ospath_expandvars):
        mock_ospath_expandvars.return_value = self.tempdir
        self.assertEqual(os.path.join(os.path.expandvars("%BACKUP%"), "toto.txt"), os.path.join(self.tempdir, "toto.txt"))
        mock_ospath_expandvars.assert_called_once()

    def test04(self, mock_ospath_expandvars):
        mock_ospath_expandvars.return_value = "some_folder"
        self.assertEqual(os.path.expandvars("%SOME_FOLDER%"), "some_folder")
        mock_ospath_expandvars.assert_called_once()


@SetUp(_THATFILE.parent / "Resources" / "resource4.yml")
class Test05(unittest.TestCase):

    def setUp(self) -> None:
        self.collection = [("artist1", "album1", 1, 1, "X"),
                           ("artist1", "album1", 1, 2, "X"),
                           ("artist1", "album1", 2, 1, "X"),
                           ("artist1", "album1", 1, 3, "X"),
                           ("artist2", "album1", 1, 1, "X"),
                           ("artist1", "album2", 1, 1, "X"),
                           ("artist1", "album2", 1, 2, "X"),
                           ("artist1", "album1", 2, 2, "X"),
                           ("artist1", "album1", 2, 3, "X"),
                           ("artist2", "album1", 2, 3, "X"),
                           ("artist2", "album2", 2, 2, "X"),
                           ("artist2", "album2", 2, 1, "X"),
                           ("artist2", "album2", 2, 3, "X")]

    def test_t01(self, collection):
        in_collection = sorted(sorted(sorted(sorted(sorted(self.collection, key=itemgetter(3)), key=itemgetter(2)), key=itemgetter(1)), key=itemgetter(0)), key=itemgetter(4))
        out_collection = collection["test_t01"]
        self.assertListEqual(list(nested_groupby(in_collection, 4, 0, 1, 2)), out_collection)

    def test_t02(self, collection):
        in_collection = sorted(sorted(sorted(sorted(sorted(self.collection, key=itemgetter(3)), key=itemgetter(2)), key=itemgetter(1)), key=itemgetter(0)), key=itemgetter(4))
        out_collection = collection["test_t02"]
        self.assertListEqual(list(groupby(in_collection, 4)), out_collection)

    def test_t03(self, collection):
        in_collection = sorted(sorted(sorted(sorted(sorted(self.collection, key=itemgetter(3)), key=itemgetter(2)), key=itemgetter(1)), key=itemgetter(0)), key=itemgetter(4))
        out_collection = collection["test_t03"]
        self.assertListEqual(list(nested_groupby(in_collection, 4)), out_collection)

    def test_t04(self, collection):
        in_collection = sorted(sorted(sorted(sorted(sorted(self.collection, key=itemgetter(3)), key=itemgetter(2)), key=itemgetter(1)), key=itemgetter(0)), key=itemgetter(4))
        out_collection = collection["test_t04"]
        self.assertListEqual(list(nested_groupby(in_collection, 0, 1)), out_collection)


class Test06(unittest.TestCase):

    def setUp(self) -> None:
        self.iterable = [("defaultalbums", "Artist, The", "1", "1", "Y", "N", "N", "Y"), ("defaultalbums", "Artist, The", "1", "2", "Y", "N", "N", "Y")]

    def test_t01(self):
        self.assertListEqual(list(itertools.starmap(booleanify_, self.iterable)),
                             [("defaultalbums", "Artist, The", "1", "1", True, False, False, True), ("defaultalbums", "Artist, The", "1", "2", True, False, False, True)])


class Test07(unittest.TestCase):

    def setUp(self) -> None:
        self.iterable = [("defaultalbums", "Artist, The", "1", "1", "O", "N", "N", "O"), ("defaultalbums", "Artist, The", "1", "2", "Y", "N", "N", "Y")]

    def test_t01(self):
        self.assertListEqual(list(itertools.starmap(booleanify_, self.iterable)),
                             [("defaultalbums", "Artist, The", "1", "1", "O", False, False, "O"), ("defaultalbums", "Artist, The", "1", "2", True, False, False, True)])


class Test08(unittest.TestCase):

    def setUp(self) -> None:
        self.iterable = [("defaultalbums", "Artist, The", "1", "1", "A", "B", "C", "D"), ("defaultalbums", "Artist, The", "1", "2", "A", "B", "C", "D")]

    def test_t01(self):
        self.assertListEqual(list(itertools.starmap(booleanify_, self.iterable)),
                             [("defaultalbums", "Artist, The", "1", "1", "A", "B", "C", "D"), ("defaultalbums", "Artist, The", "1", "2", "A", "B", "C", "D")])


class Test09(unittest.TestCase):

    def setUp(self) -> None:
        self.iterable = [("defaultalbums", "Artist, The", "1", "1", True, False, "A", "B"), ("defaultalbums", "Artist, The", "1", "2", "A", "B", "C", "D")]

    def test_t01(self):
        self.assertListEqual(list(itertools.starmap(booleanify_, self.iterable)),
                             [("defaultalbums", "Artist, The", "1", "1", True, False, "A", "B"), ("defaultalbums", "Artist, The", "1", "2", "A", "B", "C", "D")])
