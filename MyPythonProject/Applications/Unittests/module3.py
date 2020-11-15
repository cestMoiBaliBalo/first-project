# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import datetime
import locale
import os
import unittest
from pathlib import Path

from pytz import timezone

from ..shared import LOCAL, TEMPLATE3, UTC, adjust_datetime, format_date, get_readabledate, valid_albumid, valid_albumsort, valid_datetime, valid_genre, valid_year

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
class TestValidAlbumSort01(unittest.TestCase):

    def test_t01(self):
        self.assertEqual(valid_albumsort("1.19840000.1"), "1.19840000.1")

    def test_t02(self):
        self.assertRaises(ValueError, valid_albumsort, "1.19840000.1.13")

    def test_t03(self):
        self.assertEqual(valid_albumsort("2.19840808.1"), "2.19840808.1")

    def test_t04(self):
        self.assertRaises(ValueError, valid_albumsort, "2.19840808.1.13")

    def test_t05(self):
        self.assertRaises(ValueError, valid_albumsort, "2.12345678.1")

    def test_t06(self):
        self.assertRaises(ValueError, valid_albumsort, "Some String")

    def test_t07(self):
        self.assertRaises(ValueError, valid_albumsort, "3.20180000.1")

    def test_t08(self):
        self.assertRaises(ValueError, valid_albumsort, "4.20180000.1")

    def test_t09(self):
        self.assertRaises(ValueError, valid_albumsort, "5.20180000.1")

    def test_t10(self):
        self.assertRaises(ValueError, valid_albumsort, "6.20180000.1")

    def test_t11(self):
        self.assertRaises(ValueError, valid_albumsort, "7.20180000.1")

    def test_t12(self):
        self.assertRaises(ValueError, valid_albumsort, "8.20180000.1")

    def test_t13(self):
        self.assertRaises(ValueError, valid_albumsort, "9.20180000.1")

    def test_t14(self):
        self.assertRaises(ValueError, valid_albumsort, "123456789012")

    def test_t15(self):
        self.assertEqual(valid_albumid("A.Adams, Bryan.1.19840000.1"), "A.Adams, Bryan.1.19840000.1")

    def test_t16(self):
        self.assertRaises(ValueError, valid_albumid, "B.Adams, Bryan.1.19840000.1")

    def test_t17(self):
        self.assertRaises(ValueError, valid_albumid, "Adams, Bryan.1.19840000.1")

    def test_t18(self):
        self.assertRaises(ValueError, valid_albumid, "A.Adams, Bryan.1.19840000.1.13")

    def test_t19(self):
        self.assertEqual(valid_albumid("S.Springsteen, Bruce.2.20120704.1"), "S.Springsteen, Bruce.2.20120704.1")

    def test_t20(self):
        self.assertRaises(ValueError, valid_albumid, "Some String")

    def test_t21(self):
        self.assertEqual(valid_albumid("I.Iron Maiden.1.19830000.1"), "I.Iron Maiden.1.19830000.1")

    def test_t22(self):
        self.assertRaises(ValueError, valid_albumid, "1.19840000.1")

    def test_t23(self):
        self.assertRaises(ValueError, valid_albumsort, "S.Springsteen, Bruce.2.20120704.1")


class TestValidAlbumSort02(unittest.TestCase):
    """
    Test `valid_albumsort` function.
    """

    def test_t01(self):
        for argument in ["1.20170000.1", "1.20170000.2", "2.20171019.1"]:
            with self.subTest(albumsort=argument):
                self.assertEqual(valid_albumsort(argument), argument)

    def test_t02(self):
        for argument in ["abcdefghijklmnopqrstuvwxyz", "20171", "2a2", [2015, 2016, 2017], 9999, "1.20170000.1.13.D1.T01.NNN", 10.5]:
            with self.subTest(year=argument):
                self.assertRaises(ValueError, valid_albumsort, argument)

    def test_t03(self):
        with self.assertRaises(ValueError) as cm:
            valid_albumsort("1.20180000.1.13")
        exception, = cm.exception.args
        self.assertEqual(exception, '"1.20180000.1.13" is not a valid albumsort.')


class TestValidYear(unittest.TestCase):
    """
    Test `valid_year` function.
    """

    def test_t01(self):
        for argument in ["2017", 2017]:
            with self.subTest(year=argument):
                self.assertEqual(valid_year(argument), 2017)

    def test_t02(self):
        for argument in ["abcdefghijklmnopqrstuvwxyz", "20171", "2a2", [2015, 2016, 2017], 9999, 10.5]:
            with self.subTest(year=argument):
                self.assertRaises(ValueError, valid_year, argument)

    def test_t03(self):
        with self.assertRaises(ValueError) as cm:
            valid_year("20171")
        exception, = cm.exception.args
        self.assertEqual(exception, '"20171" is not a valid year.')


class TestValidGenre(unittest.TestCase):
    """
    Test `valid_genre` function.
    """

    def test_t01(self):
        for argument in ["Rock", "Hard Rock", "black metal"]:
            with self.subTest(genre=argument):
                self.assertEqual(valid_genre(argument), argument)

    def test_t02(self):
        for argument in ["abcdefghijklmnopqrstuvwxyz", "20171", "2a2", [2015, 2016, 2017], 9999, "1.20170000.1.13.D1.T01.NNN", "some genre", 10.5]:
            with self.subTest(genre=argument):
                self.assertRaises(ValueError, valid_genre, argument)

    def test_t03(self):
        with self.assertRaises(ValueError) as cm:
            valid_genre("Some Genre")
        exception, = cm.exception.args
        self.assertEqual(exception, '"Some Genre" is not a valid genre.')


class TestAdjustDatetime(unittest.TestCase):

    def test_t01(self):
        self.assertEqual(adjust_datetime(2018, 11, 17, 14, 8, 0), datetime.datetime(2018, 11, 17, 14, 8, 0))

    def test_t02(self):
        self.assertEqual(adjust_datetime(2018, 2, 31, 14, 8, 0), datetime.datetime(2018, 3, 3, 14, 8, 0))

    def test_t03(self):
        self.assertEqual(adjust_datetime(2018, 11, 31, 14, 8, 0), datetime.datetime(2018, 12, 1, 14, 8, 0))

    def test_t04(self):
        self.assertRaises(ValueError, adjust_datetime, *(2018, 13, 31, 14, 8, 0))


class TestGetReadableDate(unittest.TestCase):

    def test_t01(self):
        self.assertEqual(get_readabledate(datetime.datetime(2018, 11, 17, 14, 8, 0)), "Samedi 17 Novembre 2018 14:08:00  (UTC)")

    def test_t02(self):
        self.assertEqual(get_readabledate(datetime.datetime(2018, 11, 17, 14, 8, 0), tz=LOCAL), "Samedi 17 Novembre 2018 14:08:00 CET (UTC+0100)")

    def test_t03(self):
        self.assertEqual(get_readabledate(datetime.datetime(2018, 11, 17, 14, 8, 0), template=TEMPLATE3, tz=LOCAL), "17/11/2018 14:08:00 CET (UTC+0100)")


class TestFormatDate(unittest.TestCase):

    def test_t01(self):
        self.assertEqual(format_date(LOCAL.localize(datetime.datetime(2018, 11, 17, 14, 8, 0))), "Samedi 17 Novembre 2018 14:08:00 CET (UTC+0100)")

    def test_t02(self):
        self.assertEqual(format_date(UTC.localize(datetime.datetime(2018, 11, 17, 14, 8, 0))), "Samedi 17 Novembre 2018 14:08:00 UTC (UTC+0000)")

    def test_t03(self):
        self.assertEqual(format_date(timezone("US/Eastern").localize(datetime.datetime(2018, 11, 17, 14, 8, 0))), "Samedi 17 Novembre 2018 14:08:00 EST (UTC-0500)")

    def test_t04(self):
        self.assertEqual(format_date(timezone("US/Pacific").localize(datetime.datetime(2018, 11, 17, 14, 8, 0))), "Samedi 17 Novembre 2018 14:08:00 PST (UTC-0800)")

    def test_t05(self):
        self.assertEqual(format_date(LOCAL.localize(datetime.datetime(2018, 6, 17, 14, 8, 0))), "Dimanche 17 Juin 2018 14:08:00 CEST (UTC+0200)")


class ValidDatetime(unittest.TestCase):

    def test_t01(self):
        self.assertRaises(ValueError, valid_datetime, "some_string")

    def test_t02(self):
        timestamp, _, time_structure = valid_datetime(1542464410)
        self.assertEqual(timestamp, 1542464410)
        self.assertTupleEqual(tuple(time_structure), (2018, 11, 17, 15, 20, 10, 5, 321, 0))

    def test_t03(self):
        timestamp, _, time_structure = valid_datetime(1529238003)
        self.assertEqual(timestamp, 1529238003)
        self.assertTupleEqual(tuple(time_structure), (2018, 6, 17, 14, 20, 3, 6, 168, 1))

    def test_t04(self):
        timestamp, _, time_structure = valid_datetime("1542464410")
        self.assertEqual(timestamp, 1542464410)
        self.assertTupleEqual(tuple(time_structure), (2018, 11, 17, 15, 20, 10, 5, 321, 0))

    def test_t05(self):
        timestamp, _, time_structure = valid_datetime("1529238003")
        self.assertEqual(timestamp, 1529238003)
        self.assertTupleEqual(tuple(time_structure), (2018, 6, 17, 14, 20, 3, 6, 168, 1))

    def test_t06(self):
        timestamp, _, time_structure = valid_datetime(1542464410)
        self.assertEqual(timestamp, 1542464410)
        self.assertTupleEqual(tuple(time_structure), (2018, 11, 17, 15, 20, 10, 5, 321, 0))

    def test_t07(self):
        timestamp, _, time_structure = valid_datetime(datetime.datetime(2018, 6, 17, 14, 20, 3, 6))
        self.assertEqual(timestamp, 1529238003)
        self.assertTupleEqual(tuple(time_structure), (2018, 6, 17, 14, 20, 3, 6, 168, 1))

    def test_t08(self):
        self.assertRaises(ValueError, valid_datetime, "1111aa2222b")

    def test_t09(self):
        timestamp, _, time_structure = valid_datetime(timezone("Europe/Paris").localize(datetime.datetime(2018, 6, 17, 14, 20, 3, 6)))
        self.assertEqual(timestamp, 1529238003)
        self.assertTupleEqual(tuple(time_structure), (2018, 6, 17, 14, 20, 3, 6, 168, 1))
