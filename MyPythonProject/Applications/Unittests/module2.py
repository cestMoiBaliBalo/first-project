# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import datetime
import operator
import os
import unittest
from functools import partial
from pathlib import Path
from unittest.mock import patch

import iso8601  # type: ignore

import Applications.parsers
from ..callables import filter_audiofiles, filter_extension, filter_extensions, filter_losslessaudiofiles, filter_portabledocuments, filterfalse_
from ..parsers import database_parser, tags_grabber, tasks_parser
from ..shared import LOCAL, UTC, find_files

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent


# ==============
# Tests classes.
# ==============
@patch.object(Applications.parsers.Database, "__call__")
class Test02a(unittest.TestCase):
    """
    Undocumented.
    """

    def setUp(self) -> None:
        self.prod_db = _MYPARENT.parents[1] / "Resources" / "database.db"

    def test_t01(self, mock_function):
        mock_function.return_value = str(self.prod_db)
        arguments = database_parser.parse_args(["--database", str(self.prod_db)])
        self.assertEqual(arguments.db, str(self.prod_db))
        self.assertIsNone(arguments.test)
        mock_function.assert_called_once()
        mock_function.assert_called_once_with(str(self.prod_db))

    def test_t02(self, mock_function):
        mock_function.return_value = str(self.prod_db)
        arguments = database_parser.parse_args([])
        self.assertEqual(arguments.db, str(self.prod_db))
        self.assertIsNone(arguments.test)
        mock_function.assert_called_once()
        mock_function.assert_called_once_with(str(self.prod_db))

    def test_t03(self, mock_function):
        mock_function.return_value = "some_database"
        arguments = database_parser.parse_args(["--database", "some_database"])
        self.assertEqual(arguments.db, "some_database")
        self.assertIsNone(arguments.test)
        mock_function.assert_called_once()
        mock_function.assert_called_once_with("some_database")


@patch("Applications.shared")
class Test02b(unittest.TestCase):
    """
    Undocumented.
    """

    def test_t01(self, mock_database):
        mock_database.TESTDATABASE = "some_test_database"
        arguments = database_parser.parse_args(["--test"])
        self.assertEqual(arguments.db, "some_test_database")
        self.assertIsNotNone(arguments.test)
        self.assertTrue(arguments.test)


class Test02c(unittest.TestCase):
    """
    Undocumented.
    """

    def test_t01(self):
        arguments = database_parser.parse_args(["--test"])
        self.assertEqual(arguments.db, str(Path(os.path.expandvars("%TEMP%")) / "database.db"))
        self.assertIsNotNone(arguments.test)
        self.assertTrue(arguments.test)


@patch.object(argparse.FileType, "__call__")
class Test03(unittest.TestCase):
    """
    Undocumented.
    """

    def test_t01(self, mock_function):
        mock_function.return_value = None
        self.arguments = tags_grabber.parse_args(["some_tags_file", "default", "C1", "--tags_processing", "defaultalbum"])
        self.assertEqual(self.arguments.profile, "default")
        self.assertEqual(self.arguments.sequence, "C1")
        self.assertEqual(self.arguments.tags_processing, "defaultalbum")
        self.assertListEqual(self.arguments.decorators, [])
        mock_function.assert_called_once()
        mock_function.assert_called_with("some_tags_file")

    def test_t02(self, mock_function):
        mock_function.return_value = None
        self.arguments = tags_grabber.parse_args(["some_tags_file", "default", "C2"])
        self.assertEqual(self.arguments.profile, "default")
        self.assertEqual(self.arguments.sequence, "C2")
        self.assertEqual(self.arguments.tags_processing, "default")
        self.assertListEqual(self.arguments.decorators, [])
        mock_function.assert_called_once()
        mock_function.assert_called_with("some_tags_file")

    def test_t03(self, mock_function):
        mock_function.return_value = None
        self.arguments = tags_grabber.parse_args(["some_tags_file", "default", "C3", "decorator1", "decorator2", "decorator3", "--tags_processing", "test_defaultalbum"])
        self.assertEqual(self.arguments.profile, "default")
        self.assertEqual(self.arguments.sequence, "C3")
        self.assertEqual(self.arguments.tags_processing, "test_defaultalbum")
        self.assertListEqual(self.arguments.decorators, ["decorator1", "decorator2", "decorator3"])
        mock_function.assert_called_once()
        mock_function.assert_called_with("some_tags_file")


@patch("Applications.shared")
class Test04a(unittest.TestCase):
    """

    """

    def setUp(self):
        self.taskid = "123456800"

    def test_t01(self, mock_attribute):
        mock_attribute.TESTDATABASE = "some_test_database"
        arguments = vars(tasks_parser.parse_args(["-t", self.taskid, "update", "--timestamp", "1549913936"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertEqual(arguments.get("timestamp"), 1549913936)
        self.assertIsNone(arguments.get("datstring"))
        self.assertIsNone(arguments.get("delta"))
        self.assertTrue(arguments.get("test"))
        self.assertEqual(arguments.get("db"), "some_test_database")

    def test_t02(self, mock_database):
        mock_database.TESTDATABASE = "some_test_database"
        arguments = vars(tasks_parser.parse_args(["-t", self.taskid, "update", "--datstring", "2019-02-11T20:38:56+01:00"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertIsNone(arguments.get("timestamp"))
        self.assertIsNone(arguments.get("delta"))
        self.assertEqual(arguments.get("datstring"), "2019-02-11T20:38:56+01:00")
        self.assertEqual(iso8601.parse_date(arguments.get("datstring")).replace(tzinfo=None), datetime.datetime(2019, 2, 11, 20, 38, 56))
        self.assertEqual(LOCAL.localize(iso8601.parse_date(arguments.get("datstring")).replace(tzinfo=None)).astimezone(UTC).replace(tzinfo=None), datetime.datetime(2019, 2, 11, 19, 38, 56))
        self.assertTrue(arguments.get("test"))
        self.assertEqual(arguments.get("db"), "some_test_database")

    def test_t03(self, mock_database):
        mock_database.TESTDATABASE = "some_test_database"
        arguments = vars(tasks_parser.parse_args(["-t", self.taskid, "update", "--datstring", "2019-02-11T20:38:56"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertIsNone(arguments.get("timestamp"))
        self.assertIsNone(arguments.get("delta"))
        self.assertEqual(arguments.get("datstring"), "2019-02-11T20:38:56")
        self.assertEqual(iso8601.parse_date(arguments.get("datstring")).replace(tzinfo=None), datetime.datetime(2019, 2, 11, 20, 38, 56))
        self.assertEqual(LOCAL.localize(iso8601.parse_date(arguments.get("datstring")).replace(tzinfo=None)).astimezone(UTC).replace(tzinfo=None), datetime.datetime(2019, 2, 11, 19, 38, 56))
        self.assertTrue(arguments.get("test"))
        self.assertEqual(arguments.get("db"), "some_test_database")

    def test_t04(self, mock_database):
        mock_database.TESTDATABASE = "some_test_database"
        arguments = vars(tasks_parser.parse_args(["-t", self.taskid, "update"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertIsNone(arguments.get("timestamp"))
        self.assertIsNone(arguments.get("datstring"))
        self.assertIsNone(arguments.get("delta"))
        self.assertTrue(arguments.get("test"))
        self.assertEqual(arguments.get("db"), "some_test_database")

    def test_t05(self, mock_database):
        mock_database.TESTDATABASE = "some_test_database"
        arguments = vars(tasks_parser.parse_args(["-t", self.taskid, "update", "add", "5"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertIsNone(arguments.get("timestamp"))
        self.assertIsNone(arguments.get("datstring"))
        self.assertIsNone(arguments.get("delta"))
        self.assertEqual(arguments.get("func"), operator.add)
        self.assertEqual(arguments.get("days"), 5)
        self.assertTrue(arguments.get("test"))
        self.assertEqual(arguments.get("db"), "some_test_database")

    def test_t06(self, mock_database):
        mock_database.TESTDATABASE = "some_test_database"
        arguments = vars(tasks_parser.parse_args(["-t", self.taskid, "update", "sub", "23"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertIsNone(arguments.get("timestamp"))
        self.assertIsNone(arguments.get("datstring"))
        self.assertIsNone(arguments.get("delta"))
        self.assertEqual(arguments.get("func"), operator.sub)
        self.assertEqual(arguments.get("days"), 23)
        self.assertTrue(arguments.get("test"))
        self.assertEqual(arguments.get("db"), "some_test_database")

    def test_t07(self, mock_database):
        mock_database.TESTDATABASE = "some_test_database"
        arguments = vars(tasks_parser.parse_args(["-t", self.taskid, "check"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertEqual(arguments.get("delta"), 10)
        self.assertIsNone(arguments.get("timestamp"))
        self.assertIsNone(arguments.get("datstring"))
        self.assertIsNone(arguments.get("func"))
        self.assertIsNone(arguments.get("days"))
        self.assertTrue(arguments.get("test"))
        self.assertEqual(arguments.get("db"), "some_test_database")

    def test_t08(self, mock_database):
        mock_database.TESTDATABASE = "some_test_database"
        arguments = vars(tasks_parser.parse_args(["-t", self.taskid, "check", "--delta", "28"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertEqual(arguments.get("delta"), 28)
        self.assertIsNone(arguments.get("timestamp"))
        self.assertIsNone(arguments.get("datstring"))
        self.assertIsNone(arguments.get("func"))
        self.assertIsNone(arguments.get("days"))
        self.assertTrue(arguments.get("test"))
        self.assertEqual(arguments.get("db"), "some_test_database")

    def test_t09(self, mock_database):
        mock_database.TESTDATABASE = "some_test_database"
        arguments = vars(tasks_parser.parse_args(["-t", self.taskid, "update", "--datstring", "2019-02-11T20:38:56+01:00", "add", "5"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertIsNone(arguments.get("timestamp"))
        self.assertIsNone(arguments.get("delta"))
        self.assertEqual(arguments.get("datstring"), "2019-02-11T20:38:56+01:00")
        self.assertEqual(iso8601.parse_date(arguments.get("datstring")).replace(tzinfo=None), datetime.datetime(2019, 2, 11, 20, 38, 56))
        self.assertEqual(LOCAL.localize(iso8601.parse_date(arguments.get("datstring")).replace(tzinfo=None)).astimezone(UTC).replace(tzinfo=None), datetime.datetime(2019, 2, 11, 19, 38, 56))
        self.assertEqual(arguments["func"](LOCAL.localize(iso8601.parse_date(arguments["datstring"]).replace(tzinfo=None)).astimezone(UTC).replace(tzinfo=None), datetime.timedelta(arguments["days"])),
                         datetime.datetime(2019, 2, 16, 19, 38, 56))
        self.assertTrue(arguments.get("test"))
        self.assertEqual(arguments.get("db"), "some_test_database")

    def test_t10(self, mock_database):
        mock_database.TESTDATABASE = "some_test_database"
        arguments = vars(tasks_parser.parse_args(["-t", self.taskid, "update", "--datstring", "2019-02-11T20:38:56+01:00", "add", "28"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertIsNone(arguments.get("timestamp"))
        self.assertIsNone(arguments.get("delta"))
        self.assertEqual(arguments.get("datstring"), "2019-02-11T20:38:56+01:00")
        self.assertEqual(iso8601.parse_date(arguments.get("datstring")).replace(tzinfo=None), datetime.datetime(2019, 2, 11, 20, 38, 56))
        self.assertEqual(LOCAL.localize(iso8601.parse_date(arguments.get("datstring")).replace(tzinfo=None)).astimezone(UTC).replace(tzinfo=None), datetime.datetime(2019, 2, 11, 19, 38, 56))
        self.assertEqual(arguments["func"](LOCAL.localize(iso8601.parse_date(arguments["datstring"]).replace(tzinfo=None)).astimezone(UTC).replace(tzinfo=None), datetime.timedelta(arguments["days"])),
                         datetime.datetime(2019, 3, 11, 19, 38, 56))
        self.assertTrue(arguments.get("test"))
        self.assertEqual(arguments.get("db"), "some_test_database")

    def test_t11(self, mock_database):
        mock_database.TESTDATABASE = "some_test_database"
        arguments = vars(tasks_parser.parse_args(["-t", self.taskid, "update", "--datstring", "2019-02-11T20:38:56+01:00", "sub", "10"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertIsNone(arguments.get("timestamp"))
        self.assertIsNone(arguments.get("delta"))
        self.assertEqual(arguments.get("datstring"), "2019-02-11T20:38:56+01:00")
        self.assertEqual(iso8601.parse_date(arguments.get("datstring")).replace(tzinfo=None), datetime.datetime(2019, 2, 11, 20, 38, 56))
        self.assertEqual(LOCAL.localize(iso8601.parse_date(arguments.get("datstring")).replace(tzinfo=None)).astimezone(UTC).replace(tzinfo=None), datetime.datetime(2019, 2, 11, 19, 38, 56))
        self.assertEqual(arguments["func"](LOCAL.localize(iso8601.parse_date(arguments["datstring"]).replace(tzinfo=None)).astimezone(UTC).replace(tzinfo=None), datetime.timedelta(arguments["days"])),
                         datetime.datetime(2019, 2, 1, 19, 38, 56))
        self.assertTrue(arguments.get("test"))
        self.assertEqual(arguments.get("db"), "some_test_database")


@patch.object(Applications.shared, "valid_database", return_value=str(_MYPARENT.parents[1] / "Resources" / "database.db"))
class Test04b(unittest.TestCase):

    def setUp(self):
        self.prod_db = _MYPARENT.parents[1] / "Resources" / "database.db"
        self.test_db = str(Path(os.path.expandvars("%TEMP%")) / "database.db")

    def test_t01(self, mock_function):
        arguments = vars(database_parser.parse_args([]))
        self.assertFalse(arguments.get("test"))
        self.assertEqual(arguments.get("db"), str(self.prod_db))
        mock_function.assert_called_once()
        mock_function.assert_called_with(str(self.prod_db))

    def test_t02(self, mock_function):
        arguments = vars(database_parser.parse_args(["--database", "some_database"]))
        self.assertFalse(arguments.get("test"))
        self.assertEqual(arguments.get("db"), str(self.prod_db))
        mock_function.assert_called_once()
        mock_function.assert_called_with("some_database")

    def test_t03(self, mock_function):
        arguments = vars(database_parser.parse_args(["--test"]))
        self.assertTrue(arguments.get("test"))
        self.assertEqual(arguments.get("db"), str(self.test_db))
        with self.assertRaises(AssertionError):
            mock_function.assert_called_once()


@patch("os.walk")
class Test05(unittest.TestCase):

    def setUp(self):
        self.files = ["file1.flac", "file2.flac", "file3.flac", "file1.mp3", "file2.mp3", "file3.mp3", "file1.m4a", "file2.m4a", "file3.m4a"]
        self.side_effect = [((str(Path("G:/")), [], self.files),)]

    def test01(self, mock_os_walk):
        mock_os_walk.side_effect = self.side_effect
        out_files = sorted(find_files(Path("F:/A"), excluded=filterfalse_(partial(filter_extension, extension="flac"))))
        self.assertListEqual(out_files, [str(Path("G:/") / "file1.flac"), str(Path("G:/") / "file2.flac"), str(Path("G:/") / "file3.flac")])
        mock_os_walk.assert_called_once()

    def test02(self, mock_os_walk):
        mock_os_walk.side_effect = self.side_effect
        self.assertTrue(set(find_files(Path("F:/B"), excluded=filterfalse_(partial(filter_extension, extension="flac")))))
        mock_os_walk.assert_called_once()

    def test03(self, mock_os_walk):
        mock_os_walk.side_effect = self.side_effect
        out_files = sorted(find_files(Path("F:/C"), excluded=filterfalse_(partial(filter_extension, extension="pdf"))))
        self.assertListEqual(out_files, [])
        mock_os_walk.assert_called_once()

    def test04(self, mock_os_walk):
        mock_os_walk.side_effect = self.side_effect
        out_files = sorted(find_files(Path("F:/D"), excluded=filterfalse_(filter_portabledocuments)))
        self.assertListEqual(out_files, [])
        mock_os_walk.assert_called_once()

    def test05(self, mock_os_walk):
        mock_os_walk.side_effect = self.side_effect
        self.assertFalse(set(find_files(Path("F:/E"), excluded=filterfalse_(filter_extensions("doc", "pdf", "txt")))))
        mock_os_walk.assert_called_once()

    def test06(self, mock_os_walk):
        mock_os_walk.side_effect = self.side_effect
        out_files = sorted(find_files(Path("F:/F"), excluded=filterfalse_(filter_extensions("mp3", "m4a"))))
        self.assertListEqual(out_files, [str(Path("G:/") / "file1.m4a"),
                                         str(Path("G:/") / "file1.mp3"),
                                         str(Path("G:/") / "file2.m4a"),
                                         str(Path("G:/") / "file2.mp3"),
                                         str(Path("G:/") / "file3.m4a"),
                                         str(Path("G:/") / "file3.mp3")])
        mock_os_walk.assert_called_once()

    def test07(self, mock_os_walk):
        mock_os_walk.side_effect = self.side_effect
        out_files = sorted(find_files(Path("F:/G"), excluded=filterfalse_(filter_losslessaudiofiles)))
        self.assertListEqual(out_files, [str(Path("G:/") / "file1.flac"), str(Path("G:/") / "file2.flac"), str(Path("G:/") / "file3.flac")])
        mock_os_walk.assert_called_once()

    def test08(self, mock_os_walk):
        mock_os_walk.side_effect = self.side_effect
        out_files = sorted(find_files(Path("F:/H"), excluded=filterfalse_(filter_audiofiles)))
        self.assertListEqual(out_files, sorted(str(Path("G:/") / file) for file in self.files))
        mock_os_walk.assert_called_once()
