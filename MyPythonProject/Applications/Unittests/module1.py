# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import itertools
import json
import locale
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime
from functools import partial, wraps
from itertools import filterfalse
from operator import contains, itemgetter
from pathlib import Path, PurePath
from typing import Union
from unittest.mock import patch

import yaml

from Applications.decorators import itemgetter_, split_
from Applications.shared import TitleCaseConverter, ToBoolean, UTF8, booleanify, eq_string_, get_rippingapplication, groupby_, nested_groupby_, now

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent

# ===================
# Global environment.
# ===================
if sys.platform.startswith("win"):
    locale.setlocale(locale.LC_ALL, "")
elif sys.platform.startswith("lin"):
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


# ==========
# Functions.
# ==========
def booleanify_(*args):
    return tuple(map(booleanify, args))


# ==========
# Callables.
# ==========
split1_ = itemgetter_(1)(split_(".")(itemgetter_(2)(int)))
split2_ = itemgetter_(1)(split_(".")(itemgetter_(0)(int)))
split3_ = itemgetter_(1)(split_(".")(itemgetter_(1)(int)))


# ==============
# Tests classes.
# ==============
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
        self.iterable = ("1.20160000.10",)

    def test_t01(self):
        self.assertEqual(itemgetter_(0)(split_(".")(itemgetter_(2)(int)))(self.iterable), 10)

    def test_t02(self):
        self.assertEqual(itemgetter_(0)(split_(".")(itemgetter_(1)(int)))(self.iterable), 20160000)


class TestDecorator03(unittest.TestCase):
    """

    """

    def setUp(self) -> None:
        self.iterable = ["2.20160125.13", "2.20160201.13", "2.20160120.13", "1.20160625.13", "1.20160422.13", "2.20160422.15", "2.19841102.13", "2.19990822.13", "2.20021014.13", "2.20000823.13",
                         "2.20170101.13", "1.20160422.02"]

    def test_t01(self):
        self.assertListEqual(sorted(sorted(self.iterable, key=split_(".")(itemgetter_(2)(int))), key=split_(".")(itemgetter_(1)(int))), ["2.19841102.13",
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
        self.assertListEqual(sorted(sorted(sorted(self.iterable, key=split_(".")(itemgetter_(2)(int))), key=split_(".")(itemgetter_(1)(int))), key=split_(".")(itemgetter_(0)(int))), ["1.20160422.02",
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


class TestDecorator04(unittest.TestCase):
    """

    """

    def setUp(self) -> None:
        self.iterable = [("A", "2.20160125.13"), ("B", "2.20160201.13"), ("C", "2.20160120.13"), ("D", "1.20160625.13"), ("E", "1.20160422.13"), ("F", "2.20160422.15"), ("H", "2.19841102.13"),
                         ("I", "2.19990822.13"), ("K", "2.20021014.13"), ("L", "2.20000823.13"), ("M", "2.20170101.13"), ("N", "1.20160422.02")]

    def test_t01(self):
        self.assertListEqual(sorted(sorted(self.iterable, key=split1_), key=split3_), [("H", "2.19841102.13"),
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
        self.assertListEqual(sorted(sorted(sorted(self.iterable, key=split1_), key=split3_), key=split2_), [("N", "1.20160422.02"),
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
        self.assertListEqual(sorted(sorted(sorted(self.iterable, key=split1_), key=split3_), key=split2_), [("N", "1.20160422.02"),
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


class TestDecorator05(unittest.TestCase):

    def test_t01(self):
        self.assertListEqual(list(filterfalse(partial(contains, ["A", "C", "E", "G"]), ["A", "B", "C", "D", "E", "F", "G"])), ["B", "D", "F"])

    def test_t02(self):
        self.assertListEqual(list(filterfalse(partial(contains, ["A", "B", "C", "D", "E", "F", "G"]), ["A", "C", "E", "G", "H"])), ["H"])


class TestDecorator06(unittest.TestCase):
    def setUp(self) -> None:
        self.iterable = ["2016_00001", "2016_00002", "2016_00003", "2016_00101", "2015_00456"]

    def test_t01(self):
        self.assertEqual(max(map(split_("_")(itemgetter_(1)(int)), self.iterable)), 456)

    def test_t02(self):
        self.assertListEqual(sorted(self.iterable, key=split_("_")(itemgetter_(1)(int))), ["2016_00001", "2016_00002", "2016_00003", "2016_00101", "2015_00456"])

    def test_t03(self):
        self.assertListEqual(sorted(sorted(self.iterable, key=split_("_")(itemgetter_(1)(int))), key=split_("_")(itemgetter_(0)(int))),
                             ["2015_00456", "2016_00001", "2016_00002", "2016_00003", "2016_00101"])


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


class Test01(unittest.TestCase):
    def test_t01(self):
        self.assertTrue(ToBoolean("Y").boolean_value)

    def test_t02(self):
        self.assertFalse(ToBoolean("N").boolean_value)

    def test_t03(self):
        self.assertFalse(ToBoolean("O").boolean_value)

    def test_t04(self):
        self.assertFalse(ToBoolean("toto").boolean_value)


@SetUp(_MYPARENT / "Resources" / "resource4.yml")
class Test02(unittest.TestCase):

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
        self.assertListEqual(list(nested_groupby_(in_collection, 4, 0, 1, 2)), out_collection)

    def test_t02(self, collection):
        in_collection = sorted(sorted(sorted(sorted(sorted(self.collection, key=itemgetter(3)), key=itemgetter(2)), key=itemgetter(1)), key=itemgetter(0)), key=itemgetter(4))
        out_collection = collection["test_t02"]
        self.assertListEqual(list(groupby_(in_collection, 4)), out_collection)

    def test_t03(self, collection):
        in_collection = sorted(sorted(sorted(sorted(sorted(self.collection, key=itemgetter(3)), key=itemgetter(2)), key=itemgetter(1)), key=itemgetter(0)), key=itemgetter(4))
        out_collection = collection["test_t03"]
        self.assertListEqual(list(nested_groupby_(in_collection, 4)), out_collection)

    def test_t04(self, collection):
        in_collection = sorted(sorted(sorted(sorted(sorted(self.collection, key=itemgetter(3)), key=itemgetter(2)), key=itemgetter(1)), key=itemgetter(0)), key=itemgetter(4))
        out_collection = collection["test_t04"]
        self.assertListEqual(list(nested_groupby_(in_collection, 0, 1)), out_collection)


class Test03(unittest.TestCase):

    def setUp(self) -> None:
        self.iterable = [("defaultalbums", "Artist, The", "1", "1", "Y", "N", "N", "Y"), ("defaultalbums", "Artist, The", "1", "2", "Y", "N", "N", "Y")]

    def test_t01(self):
        self.assertListEqual(list(itertools.starmap(booleanify_, self.iterable)),
                             [("defaultalbums", "Artist, The", "1", "1", True, False, False, True), ("defaultalbums", "Artist, The", "1", "2", True, False, False, True)])


class Test04(unittest.TestCase):

    def setUp(self) -> None:
        self.iterable = [("defaultalbums", "Artist, The", "1", "1", "O", "N", "N", "O"), ("defaultalbums", "Artist, The", "1", "2", "Y", "N", "N", "Y")]

    def test_t01(self):
        self.assertListEqual(list(itertools.starmap(booleanify_, self.iterable)),
                             [("defaultalbums", "Artist, The", "1", "1", "O", False, False, "O"), ("defaultalbums", "Artist, The", "1", "2", True, False, False, True)])


class Test05(unittest.TestCase):

    def setUp(self) -> None:
        self.iterable = [("defaultalbums", "Artist, The", "1", "1", "A", "B", "C", "D"), ("defaultalbums", "Artist, The", "1", "2", "A", "B", "C", "D")]

    def test_t01(self):
        self.assertListEqual(list(itertools.starmap(booleanify_, self.iterable)),
                             [("defaultalbums", "Artist, The", "1", "1", "A", "B", "C", "D"), ("defaultalbums", "Artist, The", "1", "2", "A", "B", "C", "D")])


class Test06(unittest.TestCase):

    def setUp(self) -> None:
        self.iterable = [("defaultalbums", "Artist, The", "1", "1", True, False, "A", "B"), ("defaultalbums", "Artist, The", "1", "2", "A", "B", "C", "D")]

    def test_t01(self):
        self.assertListEqual(list(itertools.starmap(booleanify_, self.iterable)),
                             [("defaultalbums", "Artist, The", "1", "1", True, False, "A", "B"), ("defaultalbums", "Artist, The", "1", "2", "A", "B", "C", "D")])
