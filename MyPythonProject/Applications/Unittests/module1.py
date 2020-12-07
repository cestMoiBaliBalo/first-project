# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import itertools
import json
import os
import shutil
import tempfile
import unittest
from datetime import datetime
from functools import partial
from itertools import filterfalse
from operator import contains, itemgetter
from pathlib import Path
from unittest.mock import patch

from ..callables import filter_extensions, filterfalse_
from ..decorators import itemgetter_, none_, split_
from ..more_shared import VorbisComment
from ..shared import Files, TitleCaseConverter, ToBoolean, UTF8, booleanify, eq_string_, get_rippingapplication, now

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent


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
        self.assertListEqual(sorted(self.iterable, key=split_("_")(itemgetter_(1)(int))),
                             ["2016_00001", "2016_00002", "2016_00003", "2016_00101", "2015_00456"])

    def test_t03(self):
        self.assertListEqual(sorted(sorted(self.iterable, key=split_("_")(itemgetter_(1)(int))), key=split_("_")(itemgetter_(0)(int))),
                             ["2015_00456", "2016_00001", "2016_00002", "2016_00003", "2016_00101"])


class TestDecorator07(unittest.TestCase):

    def setUp(self) -> None:
        self.iterable = [("defaultalbums", "Artist, The", "1", "1", True, False, "A", None), ("defaultalbums", "Artist, The", "1", "2", "A", "B", "C", "D")]

    def test_t01(self):
        self.assertListEqual(list(filterfalse(none_(itemgetter(7)), self.iterable)), [("defaultalbums", "Artist, The", "1", "2", "A", "B", "C", "D")])

    def test_t02(self):
        self.assertListEqual(list(filter(none_(itemgetter(7)), self.iterable)), [("defaultalbums", "Artist, The", "1", "1", True, False, "A", None)])


@patch("Applications.shared.datetime")
class TestMock01(unittest.TestCase):
    """

    """

    def setUp(self) -> None:
        self.datetime = datetime(2019, 9, 13, 3, 1)
        self.now = "Vendredi 13 Septembre 2019 05:01:00 CEST (UTC+0200)"

    def test_t01(self, mock_datetime):
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

    def test_t01(self, mock_datetime):
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

    def test_t01(self, mock_ospath_expandvars):
        mock_ospath_expandvars.return_value = self.tempdir
        self.assertEqual(os.path.expandvars("%TEMP%"), self.tempdir)
        mock_ospath_expandvars.assert_called_once()

    def test_t02(self, mock_ospath_expandvars):
        mock_ospath_expandvars.return_value = self.tempdir
        self.assertEqual(os.path.join(os.path.expandvars("%TEMP%"), "toto.txt"), os.path.join(self.tempdir, "toto.txt"))
        mock_ospath_expandvars.assert_called_once()

    def test_t03(self, mock_ospath_expandvars):
        mock_ospath_expandvars.return_value = self.tempdir
        self.assertEqual(os.path.join(os.path.expandvars("%BACKUP%"), "toto.txt"), os.path.join(self.tempdir, "toto.txt"))
        mock_ospath_expandvars.assert_called_once()

    def test_t04(self, mock_ospath_expandvars):
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


class Test02(unittest.TestCase):

    def setUp(self) -> None:
        self.iterable = [("defaultalbums", "Artist, The", "1", "1", "Y", "N", "N", "Y"), ("defaultalbums", "Artist, The", "1", "2", "Y", "N", "N", "Y")]

    def test_t01(self):
        self.assertListEqual(list(itertools.starmap(booleanify_, self.iterable)),
                             [("defaultalbums", "Artist, The", "1", "1", True, False, False, True), ("defaultalbums", "Artist, The", "1", "2", True, False, False, True)])


class Test03(unittest.TestCase):

    def setUp(self) -> None:
        self.iterable = [("defaultalbums", "Artist, The", "1", "1", "O", "N", "N", "O"), ("defaultalbums", "Artist, The", "1", "2", "Y", "N", "N", "Y")]

    def test_t01(self):
        self.assertListEqual(list(itertools.starmap(booleanify_, self.iterable)),
                             [("defaultalbums", "Artist, The", "1", "1", "O", False, False, "O"), ("defaultalbums", "Artist, The", "1", "2", True, False, False, True)])


class Test04(unittest.TestCase):

    def setUp(self) -> None:
        self.iterable = [("defaultalbums", "Artist, The", "1", "1", "A", "B", "C", "D"), ("defaultalbums", "Artist, The", "1", "2", "A", "B", "C", "D")]

    def test_t01(self):
        self.assertListEqual(list(itertools.starmap(booleanify_, self.iterable)),
                             [("defaultalbums", "Artist, The", "1", "1", "A", "B", "C", "D"), ("defaultalbums", "Artist, The", "1", "2", "A", "B", "C", "D")])


class Test05(unittest.TestCase):

    def setUp(self) -> None:
        self.iterable = [("defaultalbums", "Artist, The", "1", "1", True, False, "A", "B"), ("defaultalbums", "Artist, The", "1", "2", "A", "B", "C", "D")]

    def test_t01(self):
        self.assertListEqual(list(itertools.starmap(booleanify_, self.iterable)),
                             [("defaultalbums", "Artist, The", "1", "1", True, False, "A", "B"), ("defaultalbums", "Artist, The", "1", "2", "A", "B", "C", "D")])


class TestFiles(unittest.TestCase):

    @staticmethod
    def get_name(file: Path) -> str:
        return file.name

    def setUp(self) -> None:
        self._cwd = os.getcwd()
        os.chdir(_MYPARENT)

    def tearDown(self) -> None:
        os.chdir(self._cwd)

    def test_t01(self):
        files = Files(Path(os.path.abspath("Resources")))
        self.assertSetEqual(set(map(self.get_name, files)), {"audiotags.txt",
                                                             "batchconverter.txt",
                                                             "converter_idtags_01.txt",
                                                             "converter_idtags_02.txt",
                                                             "converter_idtags_03.txt",
                                                             "default_idtags_01_FDK.txt",
                                                             "default_idtags_01_FLAC.txt",
                                                             "default_idtags_01_LAME.txt",
                                                             "default_idtags_01_Monkeys.txt",
                                                             "default_idtags_02_FLAC.txt",
                                                             "default_idtags_03_FLAC.txt",
                                                             "default_idtags_04_FDK.txt",
                                                             "default_idtags_04_FLAC.txt",
                                                             "sbootleg1_idtags_01_FDK.txt",
                                                             "sbootleg1_idtags_01_FLAC.txt",
                                                             "sbootleg1_idtags_02_FDK.txt",
                                                             "sbootleg1_idtags_02_FLAC.txt",
                                                             "sbootleg1_idtags_03_FLAC.txt",
                                                             "sbootleg1_idtags_04_FLAC.txt",
                                                             "sbootleg1_idtags_05_FLAC.txt",
                                                             "sequences.json",
                                                             "titles.json"})

    def test_t02(self):
        files = Files(Path(os.path.abspath("Resources")), excluded=filterfalse_(filter_extensions("txt")))
        self.assertSetEqual(set(map(self.get_name, files)), {"audiotags.txt",
                                                             "batchconverter.txt",
                                                             "converter_idtags_01.txt",
                                                             "converter_idtags_02.txt",
                                                             "converter_idtags_03.txt",
                                                             "default_idtags_01_FDK.txt",
                                                             "default_idtags_01_FLAC.txt",
                                                             "default_idtags_01_LAME.txt",
                                                             "default_idtags_01_Monkeys.txt",
                                                             "default_idtags_02_FLAC.txt",
                                                             "default_idtags_03_FLAC.txt",
                                                             "default_idtags_04_FDK.txt",
                                                             "default_idtags_04_FLAC.txt",
                                                             "sbootleg1_idtags_01_FDK.txt",
                                                             "sbootleg1_idtags_01_FLAC.txt",
                                                             "sbootleg1_idtags_02_FDK.txt",
                                                             "sbootleg1_idtags_02_FLAC.txt",
                                                             "sbootleg1_idtags_03_FLAC.txt",
                                                             "sbootleg1_idtags_04_FLAC.txt",
                                                             "sbootleg1_idtags_05_FLAC.txt"})

    def test_t03(self):
        files = Files(Path(os.path.abspath("Resources")), excluded=filterfalse_(filter_extensions("json")))
        self.assertSetEqual(set(map(self.get_name, files)), {"sequences.json", "titles.json"})

    def test_t04(self):
        files = Files(Path(os.path.abspath("Resources")), excluded=filterfalse_(filter_extensions("json", "txt")))
        self.assertSetEqual(set(map(self.get_name, files)), {"audiotags.txt",
                                                             "batchconverter.txt",
                                                             "converter_idtags_01.txt",
                                                             "converter_idtags_02.txt",
                                                             "converter_idtags_03.txt",
                                                             "default_idtags_01_FDK.txt",
                                                             "default_idtags_01_FLAC.txt",
                                                             "default_idtags_01_LAME.txt",
                                                             "default_idtags_01_Monkeys.txt",
                                                             "default_idtags_02_FLAC.txt",
                                                             "default_idtags_03_FLAC.txt",
                                                             "default_idtags_04_FDK.txt",
                                                             "default_idtags_04_FLAC.txt",
                                                             "sbootleg1_idtags_01_FDK.txt",
                                                             "sbootleg1_idtags_01_FLAC.txt",
                                                             "sbootleg1_idtags_02_FDK.txt",
                                                             "sbootleg1_idtags_02_FLAC.txt",
                                                             "sbootleg1_idtags_03_FLAC.txt",
                                                             "sbootleg1_idtags_04_FLAC.txt",
                                                             "sbootleg1_idtags_05_FLAC.txt",
                                                             "sequences.json",
                                                             "titles.json"})

    def test_t05(self):
        files = Files(Path(os.path.abspath("Resources")), excluded=filterfalse_(filter_extensions("yml")))
        self.assertSetEqual(set(map(self.get_name, files)), set())


@unittest.skipIf(not Path("F:/").exists(), "Unit test run on local platform only!")
class TestVorbisComment(unittest.TestCase):

    def setUp(self) -> None:
        self._cwd = os.getcwd()
        os.chdir(Path("F:/") / "U" / "U2" / "1")

    def tearDown(self) -> None:
        os.chdir(self._cwd)

    def test_t01(self):
        comments = VorbisComment(Path(os.path.abspath(Path("2000 - All That You Can’t Leave Behind (20th Anniversary Edition)")
                                                      / "CD1"
                                                      / "1.Free Lossless Audio Codec"
                                                      / "1.20000000.1.13.D1.T01.flac")))
        comments = sorted(filter(itemgetter_(0)(partial(contains, ["album", "artist", "artistsort", "label", "upc"])), comments), key=itemgetter(0))
        self.assertListEqual(comments, [("album", "All That You Can’t Leave Behind (20th Anniversary Edition)"),
                                        ("artist", "U2"),
                                        ("artistsort", "U2"),
                                        ("label", "Island Records"),
                                        ("upc", "00602507404635")])

    def test_t02(self):
        comments = VorbisComment(Path(os.path.abspath(Path("2000 - All That You Can’t Leave Behind (20th Anniversary Edition)")
                                                      / "CD1"
                                                      / "1.Free Lossless Audio Codec"
                                                      / "1.20000000.1.13.D1.T01.flac")))
        comments = sorted(filter(itemgetter_(0)(partial(contains, ["mediaprovider", "source", "title"])), comments), key=itemgetter(0))
        self.assertListEqual(comments, [("mediaprovider", "HDtracks.com"),
                                        ("source", "Online provider"),
                                        ("title", "Beautiful Day")])
