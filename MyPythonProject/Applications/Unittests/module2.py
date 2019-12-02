# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import datetime
import operator
import os
import sys
import unittest
from functools import partial
from pathlib import Path, PurePath
from typing import Mapping
from unittest.mock import Mock, patch

import iso8601

from ..callables import filter_audiofiles, filter_extension, filter_extensions, filter_losslessaudiofiles, filter_portabledocuments, filterfalse_
from ..parsers import GetPath, database_parser, tags_grabber, tasks_parser
from ..shared import LOCAL, UTC, find_files, get_dirname

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_THATFILE = PurePath(os.path.abspath(__file__))  # type: PurePath
USERPROFILE = PurePath("C:/") / "Users" / "Xavier"  # type: PurePath
BACKUP = str(PurePath("Y:/") / "Backup")  # type: str
MYDOCUMENTS = str(USERPROFILE / "Documents")  # type: str
ONEDRIVE = str(USERPROFILE / "OneDrive")  # type: str
TEMP = str(USERPROFILE / "AppData" / "Local" / "Temp")  # type: str
DESTINATIONS = {"backup": BACKUP, "documents": MYDOCUMENTS, "onedrive": ONEDRIVE, "temp": TEMP}  # type: Mapping[str, str]


@patch.object(GetPath, "destinations", {"temp": TEMP})
class Test01a(unittest.TestCase):
    """

    """

    def setUp(self):
        local_validpath = Mock(return_value=MYDOCUMENTS)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("directory", help="browsed directory", type=local_validpath)
        self.parser.add_argument("archive", help="archive name")
        self.parser.add_argument("destination", help="archive destination", action=GetPath, choices=list(DESTINATIONS))
        self.parser.add_argument("-e", "--ext", dest="extensions", help="archived extension(s)", nargs="*")

    def test_t01(self):
        arguments = self.parser.parse_args([MYDOCUMENTS, "documents", "temp", "-e", "txt", "doc"])
        self.assertEqual(arguments.directory, MYDOCUMENTS)
        self.assertEqual(arguments.archive, "documents")
        self.assertEqual(arguments.destination, TEMP)
        self.assertListEqual(arguments.extensions, ["txt", "doc"])

    def test_t02(self):
        arguments = self.parser.parse_args([MYDOCUMENTS, "documents", "temp"])
        self.assertEqual(arguments.directory, MYDOCUMENTS)
        self.assertEqual(arguments.archive, "documents")
        self.assertEqual(arguments.destination, TEMP)
        self.assertIsNone(arguments.extensions)


@patch.object(GetPath, "destinations", {"onedrive": ONEDRIVE})
class Test01b(unittest.TestCase):
    """

    """

    def setUp(self):
        local_validpath = Mock(return_value=MYDOCUMENTS)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("directory", help="browsed directory", type=local_validpath)
        self.parser.add_argument("archive", help="archive name")
        self.parser.add_argument("destination", help="archive destination", action=GetPath, choices=list(DESTINATIONS))
        self.parser.add_argument("-e", "--ext", dest="extensions", help="archived extension(s)", nargs="*")

    def test_t01(self):
        arguments = self.parser.parse_args([MYDOCUMENTS, "documents", "onedrive", "-e", "txt", "doc"])
        self.assertEqual(arguments.directory, MYDOCUMENTS)
        self.assertEqual(arguments.archive, "documents")
        self.assertEqual(arguments.destination, ONEDRIVE)
        self.assertListEqual(arguments.extensions, ["txt", "doc"])

    def test_t02(self):
        arguments = self.parser.parse_args([MYDOCUMENTS, "documents", "onedrive"])
        self.assertEqual(arguments.directory, MYDOCUMENTS)
        self.assertEqual(arguments.archive, "documents")
        self.assertEqual(arguments.destination, ONEDRIVE)
        self.assertIsNone(arguments.extensions)


@patch.object(GetPath, "destinations", {"some_destination": str(PurePath("c:/some_destination"))})
class Test01c(unittest.TestCase):
    """

    """

    def setUp(self):
        self.some_source = str(PurePath("c:/some_source"))
        self.some_destination = str(PurePath("c:/some_destination"))
        local_validpath = Mock(return_value=self.some_source)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("directory", help="browsed directory", type=local_validpath)
        self.parser.add_argument("archive", help="archive name")
        self.parser.add_argument("destination", help="archive destination", action=GetPath)
        self.parser.add_argument("-e", "--ext", dest="extensions", help="archived extension(s)", nargs="*")

    def test_t01(self):
        arguments = self.parser.parse_args([self.some_source, "documents", "some_destination", "-e", "txt", "doc"])
        self.assertEqual(arguments.directory, self.some_source)
        self.assertEqual(arguments.archive, "documents")
        self.assertEqual(arguments.destination, self.some_destination)
        self.assertListEqual(arguments.extensions, ["txt", "doc"])

    def test_t02(self):
        arguments = self.parser.parse_args([self.some_source, "documents", "some_destination"])
        self.assertEqual(arguments.directory, self.some_source)
        self.assertEqual(arguments.archive, "documents")
        self.assertEqual(arguments.destination, self.some_destination)
        self.assertIsNone(arguments.extensions)


@patch.object(GetPath, "destinations", {"temp": str(PurePath("c:/some_destination"))})
class Test01d(unittest.TestCase):
    """

    """

    def setUp(self):
        self.some_source = str(PurePath("c:/some_source"))
        self.some_destination = str(PurePath("c:/some_destination"))
        self.local_validpath = Mock(return_value=self.some_source)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("directory", help="browsed directory", type=self.local_validpath)
        self.parser.add_argument("archive", help="archive name")
        self.parser.add_argument("destination", help="archive destination", action=GetPath)
        self.parser.add_argument("-e", "--ext", dest="extensions", help="archived extension(s)", nargs="*")

    def test_t01(self):
        arguments = self.parser.parse_args([self.some_source, "documents", "temp", "-e", "txt", "doc"])
        self.assertEqual(arguments.directory, self.some_source)
        self.assertEqual(arguments.archive, "documents")
        self.assertEqual(arguments.destination, self.some_destination)
        self.assertListEqual(arguments.extensions, ["txt", "doc"])
        self.local_validpath.assert_called_once_with(self.some_source)

    def test_t02(self):
        arguments = self.parser.parse_args([self.some_source, "documents", "temp"])
        self.assertEqual(arguments.directory, self.some_source)
        self.assertEqual(arguments.archive, "documents")
        self.assertEqual(arguments.destination, self.some_destination)
        self.assertIsNone(arguments.extensions)
        self.local_validpath.assert_called_once_with(self.some_source)
        self.local_validpath.assert_called()


# @unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
# class Test02(unittest.TestCase):
#     """
#
#     """
#
#     def setUp(self):
#         self.documents = os.path.expandvars("%_MYDOCUMENTS%")
#
#     def test_t01(self):
#         arguments = zipfile.parse_args([self.documents, "temp", "grouped", "documents"])
#         self.assertListEqual(arguments.extensions, ["doc", "txt", "pdf", "xav"])
#
#     def test_t02(self):
#         arguments = zipfile.parse_args([self.documents, "temp", "grouped", "documents", "-e", "doc"])
#         self.assertListEqual(arguments.extensions, ["txt", "pdf", "xav"])
#
#     def test_t03(self):
#         arguments = zipfile.parse_args([self.documents, "temp", "grouped", "documents", "-k", "pdf"])
#         self.assertListEqual(arguments.extensions, ["pdf"])
#
#     def test_t04(self):
#         arguments = zipfile.parse_args([self.documents, "temp", "grouped", "documents", "-e", "doc", "txt", "pdf", "xav"])
#         self.assertListEqual(arguments.extensions, [])
#
#     def test_t05(self):
#         arguments = zipfile.parse_args([self.documents, "temp", "grouped", "computing"])
#         self.assertListEqual(arguments.extensions, ["py", "json", "yaml", "cmd", "css", "xsl"])
#
#     def test_t06(self):
#         arguments = zipfile.parse_args([self.documents, "temp", "grouped", "computing", "-i", "pdf"])
#         self.assertListEqual(arguments.extensions, ["py", "json", "yaml", "cmd", "css", "xsl", "pdf"])
#
#     def test_t07(self):
#         arguments = zipfile.parse_args([self.documents, "temp", "grouped", "computing", "-e", "cmd", "-i", "pdf", "txt"])
#         self.assertListEqual(arguments.extensions, ["py", "json", "yaml", "css", "xsl", "pdf", "txt"])
#
#     def test_t08(self):
#         arguments = zipfile.parse_args([self.documents, "temp", "grouped", "computing", "-k", "py", "-i", "pdf", "txt"])
#         self.assertListEqual(arguments.extensions, ["py", "pdf", "txt"])
#
#     def test_t09(self):
#         arguments = zipfile.parse_args([self.documents, "temp", "grouped", "computing", "documents"])
#         self.assertListEqual(arguments.extensions, ["py", "json", "yaml", "cmd", "css", "xsl", "doc", "txt", "pdf", "xav"])
#
#     def test_t10(self):
#         arguments = zipfile.parse_args([self.documents, "temp", "grouped", "computing", "documents", "-e", "doc", "css"])
#         self.assertListEqual(arguments.extensions, ["py", "json", "yaml", "cmd", "xsl", "txt", "pdf", "xav"])
#
#     def test_t11(self):
#         arguments = zipfile.parse_args([self.documents, "temp", "singled", "doc", "pdf", "txt", "css", "abc"])
#         self.assertListEqual(arguments.extensions, ["doc", "pdf", "txt", "css", "abc"])


@unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
class Test02(unittest.TestCase):
    """

    """

    def test_t01(self):
        arguments = database_parser.parse_args(["--database", os.path.join(get_dirname(os.path.abspath(__file__), level=3), "Resources", "database.db")])
        self.assertEqual(arguments.db.lower(), os.path.join(get_dirname(os.path.abspath(__file__), level=3), "Resources", "database.db").lower())
        self.assertFalse(arguments.test)

    def test_t02(self):
        arguments = database_parser.parse_args(["--test"])
        self.assertEqual(arguments.db.lower(), os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources", "database.db").lower())
        self.assertTrue(arguments.test)

    def test_t03(self):
        arguments = database_parser.parse_args([])
        self.assertEqual(arguments.db.lower(), os.path.join(get_dirname(os.path.abspath(__file__), level=3), "Resources", "database.db").lower())
        self.assertFalse(arguments.test)

    def test_t04(self):
        arguments = database_parser.parse_args(["--database", os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources", "database.db")])
        self.assertEqual(arguments.db.lower(), os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources", "database.db").lower())
        self.assertFalse(arguments.test)


class Test03(unittest.TestCase):
    """

    """

    def setUp(self):
        self.arguments = None
        self.resource = str(PurePath(_THATFILE.parent, "Resources", "resource1.txt"))

    def test_t01(self):
        self.arguments = tags_grabber.parse_args([self.resource, "default", "C1", "--tags_processing", "defaultalbum"])
        self.assertEqual(self.arguments.profile, "default")
        self.assertEqual(self.arguments.sequence, "C1")
        self.assertEqual(self.arguments.tags_processing, "defaultalbum")
        self.assertListEqual(self.arguments.decorators, [])

    def test_t02(self):
        self.arguments = tags_grabber.parse_args([self.resource, "default", "C2"])
        self.assertEqual(self.arguments.profile, "default")
        self.assertEqual(self.arguments.sequence, "C2")
        self.assertEqual(self.arguments.tags_processing, "default")
        self.assertListEqual(self.arguments.decorators, [])

    def test_t03(self):
        self.arguments = tags_grabber.parse_args([self.resource, "default", "C3", "decorator1", "decorator2", "decorator3", "--tags_processing", "test_defaultalbum"])
        self.assertEqual(self.arguments.profile, "default")
        self.assertEqual(self.arguments.sequence, "C3")
        self.assertEqual(self.arguments.tags_processing, "test_defaultalbum")
        self.assertListEqual(self.arguments.decorators, ["decorator1", "decorator2", "decorator3"])

    def tearDown(self):
        self.arguments.source.close()


@unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
class Test04(unittest.TestCase):
    """

    """

    def setUp(self):
        self.taskid = "123456800"

    def test_t01(self):
        arguments = vars(tasks_parser.parse_args([self.taskid, "update", "--timestamp", "1549913936"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertEqual(arguments.get("timestamp"), 1549913936)
        self.assertIsNone(arguments.get("datstring"))
        self.assertIsNone(arguments.get("delta"))

    def test_t02(self):
        arguments = vars(tasks_parser.parse_args([self.taskid, "update", "--datstring", "2019-02-11T20:38:56+01:00"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertIsNone(arguments.get("timestamp"))
        self.assertIsNone(arguments.get("delta"))
        self.assertEqual(arguments.get("datstring"), "2019-02-11T20:38:56+01:00")
        self.assertEqual(iso8601.parse_date(arguments.get("datstring")).replace(tzinfo=None), datetime.datetime(2019, 2, 11, 20, 38, 56))
        self.assertEqual(LOCAL.localize(iso8601.parse_date(arguments.get("datstring")).replace(tzinfo=None)).astimezone(UTC).replace(tzinfo=None), datetime.datetime(2019, 2, 11, 19, 38, 56))

    def test_t03(self):
        arguments = vars(tasks_parser.parse_args([self.taskid, "update", "--datstring", "2019-02-11T20:38:56"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertIsNone(arguments.get("timestamp"))
        self.assertIsNone(arguments.get("delta"))
        self.assertEqual(arguments.get("datstring"), "2019-02-11T20:38:56")
        self.assertEqual(iso8601.parse_date(arguments.get("datstring")).replace(tzinfo=None), datetime.datetime(2019, 2, 11, 20, 38, 56))
        self.assertEqual(LOCAL.localize(iso8601.parse_date(arguments.get("datstring")).replace(tzinfo=None)).astimezone(UTC).replace(tzinfo=None), datetime.datetime(2019, 2, 11, 19, 38, 56))

    def test_t04(self):
        arguments = vars(tasks_parser.parse_args([self.taskid, "update"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertIsNone(arguments.get("timestamp"))
        self.assertIsNone(arguments.get("datstring"))
        self.assertIsNone(arguments.get("delta"))

    def test_t05(self):
        arguments = vars(tasks_parser.parse_args([self.taskid, "update", "add", "5"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertIsNone(arguments.get("timestamp"))
        self.assertIsNone(arguments.get("datstring"))
        self.assertIsNone(arguments.get("delta"))
        self.assertEqual(arguments.get("func"), operator.add)
        self.assertEqual(arguments.get("days"), 5)

    def test_t06(self):
        arguments = vars(tasks_parser.parse_args([self.taskid, "update", "sub", "23"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertIsNone(arguments.get("timestamp"))
        self.assertIsNone(arguments.get("datstring"))
        self.assertIsNone(arguments.get("delta"))
        self.assertEqual(arguments.get("func"), operator.sub)
        self.assertEqual(arguments.get("days"), 23)

    def test_t07(self):
        arguments = vars(tasks_parser.parse_args([self.taskid, "check"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertEqual(arguments.get("delta"), 10)
        self.assertIsNone(arguments.get("timestamp"))
        self.assertIsNone(arguments.get("datstring"))
        self.assertIsNone(arguments.get("func"))
        self.assertIsNone(arguments.get("days"))

    def test_t08(self):
        arguments = vars(tasks_parser.parse_args([self.taskid, "check", "--delta", "28"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertEqual(arguments.get("delta"), 28)
        self.assertIsNone(arguments.get("timestamp"))
        self.assertIsNone(arguments.get("datstring"))
        self.assertIsNone(arguments.get("func"))
        self.assertIsNone(arguments.get("days"))

    def test_t09(self):
        arguments = vars(tasks_parser.parse_args([self.taskid, "update", "--datstring", "2019-02-11T20:38:56+01:00", "add", "5"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertIsNone(arguments.get("timestamp"))
        self.assertIsNone(arguments.get("delta"))
        self.assertEqual(arguments.get("datstring"), "2019-02-11T20:38:56+01:00")
        self.assertEqual(iso8601.parse_date(arguments.get("datstring")).replace(tzinfo=None), datetime.datetime(2019, 2, 11, 20, 38, 56))
        self.assertEqual(LOCAL.localize(iso8601.parse_date(arguments.get("datstring")).replace(tzinfo=None)).astimezone(UTC).replace(tzinfo=None), datetime.datetime(2019, 2, 11, 19, 38, 56))
        self.assertEqual(arguments["func"](LOCAL.localize(iso8601.parse_date(arguments["datstring"]).replace(tzinfo=None)).astimezone(UTC).replace(tzinfo=None), datetime.timedelta(arguments["days"])),
                         datetime.datetime(2019, 2, 16, 19, 38, 56))

    def test_t10(self):
        arguments = vars(tasks_parser.parse_args([self.taskid, "update", "--datstring", "2019-02-11T20:38:56+01:00", "add", "28"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertIsNone(arguments.get("timestamp"))
        self.assertIsNone(arguments.get("delta"))
        self.assertEqual(arguments.get("datstring"), "2019-02-11T20:38:56+01:00")
        self.assertEqual(iso8601.parse_date(arguments.get("datstring")).replace(tzinfo=None), datetime.datetime(2019, 2, 11, 20, 38, 56))
        self.assertEqual(LOCAL.localize(iso8601.parse_date(arguments.get("datstring")).replace(tzinfo=None)).astimezone(UTC).replace(tzinfo=None), datetime.datetime(2019, 2, 11, 19, 38, 56))
        self.assertEqual(arguments["func"](LOCAL.localize(iso8601.parse_date(arguments["datstring"]).replace(tzinfo=None)).astimezone(UTC).replace(tzinfo=None), datetime.timedelta(arguments["days"])),
                         datetime.datetime(2019, 3, 11, 19, 38, 56))

    def test_t11(self):
        arguments = vars(tasks_parser.parse_args([self.taskid, "update", "--datstring", "2019-02-11T20:38:56+01:00", "sub", "10"]))
        self.assertEqual(arguments.get("taskid"), int(self.taskid))
        self.assertIsNone(arguments.get("timestamp"))
        self.assertIsNone(arguments.get("delta"))
        self.assertEqual(arguments.get("datstring"), "2019-02-11T20:38:56+01:00")
        self.assertEqual(iso8601.parse_date(arguments.get("datstring")).replace(tzinfo=None), datetime.datetime(2019, 2, 11, 20, 38, 56))
        self.assertEqual(LOCAL.localize(iso8601.parse_date(arguments.get("datstring")).replace(tzinfo=None)).astimezone(UTC).replace(tzinfo=None), datetime.datetime(2019, 2, 11, 19, 38, 56))
        self.assertEqual(arguments["func"](LOCAL.localize(iso8601.parse_date(arguments["datstring"]).replace(tzinfo=None)).astimezone(UTC).replace(tzinfo=None), datetime.timedelta(arguments["days"])),
                         datetime.datetime(2019, 2, 1, 19, 38, 56))


@patch("Applications.shared.os.walk")
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
