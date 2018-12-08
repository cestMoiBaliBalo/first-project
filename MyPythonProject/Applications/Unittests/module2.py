# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import os
import sys
import unittest
from pathlib import PurePath
from typing import Mapping
from unittest.mock import Mock, patch

from ..parsers import database_parser, loglevel_parser, tags_grabber, zipfile
from ..shared import GetPath, get_dirname

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

THAT_FILE = PurePath(os.path.abspath(__file__))  # type: PurePath
USERPROFILE = PurePath("C:/Users/Xavier")  # type: PurePath
BACKUP = str(PurePath("Y:/Backup"))  # type: str
MYDOCUMENTS = str(PurePath(USERPROFILE, "Documents"))  # type: str
ONEDRIVE = str(PurePath(USERPROFILE, "OneDrive"))  # type: str
TEMP = str(PurePath(USERPROFILE, "AppData", "Local", "Temp"))  # type: str
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


@unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
class Test02(unittest.TestCase):
    """

    """

    def setUp(self):
        self.documents = os.path.expandvars("%_MYDOCUMENTS%")

    def test_t01(self):
        arguments = zipfile.parse_args([self.documents, "temp", "grouped", "documents"])
        self.assertListEqual(arguments.extensions, ["doc", "txt", "pdf", "xav"])

    def test_t02(self):
        arguments = zipfile.parse_args([self.documents, "temp", "grouped", "documents", "-e", "doc"])
        self.assertListEqual(arguments.extensions, ["txt", "pdf", "xav"])

    def test_t03(self):
        arguments = zipfile.parse_args([self.documents, "temp", "grouped", "documents", "-k", "pdf"])
        self.assertListEqual(arguments.extensions, ["pdf"])

    def test_t04(self):
        arguments = zipfile.parse_args([self.documents, "temp", "grouped", "documents", "-e", "doc", "txt", "pdf", "xav"])
        self.assertListEqual(arguments.extensions, [])

    def test_t05(self):
        arguments = zipfile.parse_args([self.documents, "temp", "grouped", "computing"])
        self.assertListEqual(arguments.extensions, ["py", "json", "yaml", "cmd", "css", "xsl"])

    def test_t06(self):
        arguments = zipfile.parse_args([self.documents, "temp", "grouped", "computing", "-i", "pdf"])
        self.assertListEqual(arguments.extensions, ["py", "json", "yaml", "cmd", "css", "xsl", "pdf"])

    def test_t07(self):
        arguments = zipfile.parse_args([self.documents, "temp", "grouped", "computing", "-e", "cmd", "-i", "pdf", "txt"])
        self.assertListEqual(arguments.extensions, ["py", "json", "yaml", "css", "xsl", "pdf", "txt"])

    def test_t08(self):
        arguments = zipfile.parse_args([self.documents, "temp", "grouped", "computing", "-k", "py", "-i", "pdf", "txt"])
        self.assertListEqual(arguments.extensions, ["py", "pdf", "txt"])

    def test_t09(self):
        arguments = zipfile.parse_args([self.documents, "temp", "grouped", "computing", "documents"])
        self.assertListEqual(arguments.extensions, ["py", "json", "yaml", "cmd", "css", "xsl", "doc", "txt", "pdf", "xav"])

    def test_t10(self):
        arguments = zipfile.parse_args([self.documents, "temp", "grouped", "computing", "documents", "-e", "doc", "css"])
        self.assertListEqual(arguments.extensions, ["py", "json", "yaml", "cmd", "xsl", "txt", "pdf", "xav"])

    def test_t11(self):
        arguments = zipfile.parse_args([self.documents, "temp", "singled", "doc", "pdf", "txt", "css", "abc"])
        self.assertListEqual(arguments.extensions, ["doc", "pdf", "txt", "css", "abc"])


@unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
class Test04(unittest.TestCase):
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


class Test05(unittest.TestCase):
    """

    """

    def test_t01(self):
        arguments = loglevel_parser.parse_args([])
        self.assertEqual(arguments.loglevel, "INFO")

    def test_t02(self):
        arguments = loglevel_parser.parse_args(["--loglevel", "DEBUG"])
        self.assertEqual(arguments.loglevel, "DEBUG")


class Test06(unittest.TestCase):
    """

    """

    def test_t01(self):
        arguments = tags_grabber.parse_args([str(PurePath(THAT_FILE.parent, "Resources", "resource4.txt")), "default", "--tags_processing", "defaultalbum"])
        self.assertEqual(arguments.profile, "default")
        self.assertEqual(arguments.tags_processing, "defaultalbum")
        self.assertListEqual(arguments.decorators, [])

    def test_t02(self):
        arguments = tags_grabber.parse_args([str(PurePath(THAT_FILE.parent, "Resources", "resource4.txt")), "default"])
        self.assertEqual(arguments.profile, "default")
        self.assertEqual(arguments.tags_processing, "no_tags_processing")
        self.assertListEqual(arguments.decorators, [])

    def test_t03(self):
        arguments = tags_grabber.parse_args([str(PurePath(THAT_FILE.parent, "Resources", "resource4.txt")), "default", "decorator1", "decorator2", "decorator3", "--tags_processing", "test_defaultalbum"])
        self.assertEqual(arguments.profile, "default")
        self.assertEqual(arguments.tags_processing, "test_defaultalbum")
        self.assertListEqual(arguments.decorators, ["decorator1", "decorator2", "decorator3"])
