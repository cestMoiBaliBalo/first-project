# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import os
import sys
import unittest

from ..parsers import database_parser, epochconverter, loglevel_parser, tags_grabber, tasks_parser, zipfile
from ..shared import GetPath, get_dirname, valid_path

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

that_file = os.path.abspath(__file__)


def local_validpath(path):
    """
    :param path:
    :return:
    """
    try:
        path = valid_path(path)
    except ValueError as error:
        raise argparse.ArgumentTypeError(error)
    return path


@unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
class Test01(unittest.TestCase):
    """

    """

    def setUp(self):
        destinations = {"documents": os.path.expandvars("%_MYDOCUMENTS%"),
                        "onedrive": os.path.join(os.path.expandvars("%USERPROFILE%"), "OneDrive"),
                        "temp": os.path.expandvars("%TEMP%"),
                        "backup": os.path.expandvars("%_BACKUP%")}
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("directory", help="browsed directory", type=local_validpath)
        self.parser.add_argument("archive", help="archive name")
        self.parser.add_argument("destination", help="archive destination", action=GetPath, choices=list(destinations))
        self.parser.add_argument("-e", "--ext", dest="extensions", help="archived extension(s)", nargs="*")

    def test_t01(self):
        arguments = self.parser.parse_args([os.path.expandvars("%_MYDOCUMENTS%"), "documents", "temp", "-e", "txt", "doc"])
        self.assertEqual(arguments.directory, os.path.expandvars("%_MYDOCUMENTS%"))
        self.assertEqual(arguments.archive, "documents")
        self.assertEqual(arguments.destination, os.path.expandvars("%TEMP%"))
        self.assertListEqual(arguments.extensions, ["txt", "doc"])

    def test_t02(self):
        arguments = self.parser.parse_args([os.path.expandvars("%_MYDOCUMENTS%"), "documents", "temp"])
        self.assertEqual(arguments.directory, os.path.expandvars("%_MYDOCUMENTS%"))
        self.assertEqual(arguments.archive, "documents")
        self.assertEqual(arguments.destination, os.path.expandvars("%TEMP%"))
        self.assertIsNone(arguments.extensions)


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
class Test03(unittest.TestCase):
    """

    """

    def test_t01(self):
        arguments = epochconverter.parse_args(["1480717470", "1480717479"])
        self.assertEqual(arguments.beg, 1480717470)
        self.assertEqual(arguments.end, 1480717479)
        self.assertEqual(arguments.zone, "Europe/Paris")

    def test_t02(self):
        arguments = epochconverter.parse_args(["1480717470"])
        self.assertEqual(arguments.beg, 1480717470)
        self.assertEqual(arguments.end, 1480717470)
        self.assertEqual(arguments.zone, "Europe/Paris")

    def test_t03(self):
        arguments = epochconverter.parse_args(["1480717470", "-z", "US/Eastern"])
        self.assertEqual(arguments.beg, 1480717470)
        self.assertEqual(arguments.end, 1480717470)
        self.assertEqual(arguments.zone, "US/Eastern")

    def test_t04(self):
        arguments = epochconverter.parse_args(["1480717470", "1480717479", "-z", "US/Eastern"])
        self.assertEqual(arguments.beg, 1480717470)
        self.assertEqual(arguments.end, 1480717479)
        self.assertEqual(arguments.zone, "US/Eastern")


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


@unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
class Test05(unittest.TestCase):
    """

    """

    def test_t01(self):
        arguments = loglevel_parser.parse_args([])
        self.assertEqual(arguments.loglevel, "INFO")

    def test_t02(self):
        arguments = loglevel_parser.parse_args(["--loglevel", "DEBUG"])
        self.assertEqual(arguments.loglevel, "DEBUG")


@unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
class Test06(unittest.TestCase):
    """

    """

    def test_t01(self):
        arguments = tasks_parser.parse_args(["select", "123456789"])
        self.assertEqual(arguments.action, "select")
        self.assertEqual(arguments.table, "tasks")
        self.assertEqual(arguments.taskid, 123456789)
        self.assertEqual(arguments.days, 10)

    def test_t02(self):
        arguments = tasks_parser.parse_args(["update", "123456789"])
        self.assertEqual(arguments.action, "update")
        self.assertEqual(arguments.table, "tasks")
        self.assertEqual(arguments.taskid, 123456789)

    def test_t03(self):
        arguments = tasks_parser.parse_args(["select", "123456789", "--days", "20", "--debug"])
        self.assertEqual(arguments.action, "select")
        self.assertEqual(arguments.table, "tasks")
        self.assertEqual(arguments.taskid, 123456789)
        self.assertEqual(arguments.days, 20)
        self.assertEqual(arguments.debug, True)

    @unittest.skip
    def test_t04(self):
        arguments = tasks_parser.parse_args(["--table", "sometable", "select", "123456789", "--days", "20", "--debug"])
        self.assertEqual(arguments.action, "select")
        self.assertEqual(arguments.table, "sometable")
        self.assertEqual(arguments.taskid, 123456789)
        self.assertEqual(arguments.days, 20)
        self.assertEqual(arguments.debug, True)


@unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
class Test07(unittest.TestCase):
    """

    """

    def test_t01(self):
        arguments = tags_grabber.parse_args([os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources", "resource4.txt"), "default", "--tags_processing", "defaultalbum"])
        self.assertEqual(arguments.profile, "default")
        self.assertEqual(arguments.tags_processing, "defaultalbum")
        self.assertListEqual(arguments.decorators, [])

    def test_t02(self):
        arguments = tags_grabber.parse_args([os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources", "resource4.txt"), "default"])
        self.assertEqual(arguments.profile, "default")
        self.assertEqual(arguments.tags_processing, "no_tags_processing")
        self.assertListEqual(arguments.decorators, [])

    def test_t03(self):
        arguments = tags_grabber.parse_args(
                [os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources", "resource4.txt"), "default", "deco1", "deco2", "deco3", "--tags_processing", "test_defaultalbum"])
        self.assertEqual(arguments.profile, "default")
        self.assertEqual(arguments.tags_processing, "test_defaultalbum")
        self.assertListEqual(arguments.decorators, ["deco1", "deco2", "deco3"])
