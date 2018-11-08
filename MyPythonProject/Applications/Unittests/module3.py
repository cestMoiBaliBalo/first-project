# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import re
import sys
import unittest

from .. import shared
from ..AudioCD.shared import get_xreferences

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


@unittest.skipUnless(sys.platform.startswith("win"), "Tests requiring local Windows system")
class TestRegexT01(unittest.TestCase):

    def test_t01(self):
        found, (artistid, albumid, artist_path, album_path, album, is_bootleg, basename, extension) = get_xreferences(r"F:\K\Kiss\1\1975.2 - Alive_\CD2\1.Monkey's Audio\1.19750000.2.12.D2.T01.ape")
        self.assertTrue(found)
        self.assertEqual(artistid, "Kiss")
        self.assertEqual(albumid, "1.19750000.2")
        self.assertEqual(artist_path, r"F:\K\Kiss")
        self.assertEqual(album_path, r"F:\K\Kiss\1\1975.2 - Alive_")
        self.assertEqual(album, "Alive_")
        self.assertFalse(is_bootleg)
        self.assertEqual(basename, "1.19750000.2.12.D2.T01")
        self.assertEqual(extension, "ape")

    def test_t02(self):
        found, (artistid, albumid, artist_path, album_path, album, is_bootleg, basename, extension) = get_xreferences(
                r"F:\J\Judas Priest\1990 - Painkiller\1.Free Lossless Audio Codec\1.19900000.1.13.D1.T01.flac")
        self.assertTrue(found)
        self.assertEqual(artistid, "Judas Priest")
        self.assertEqual(albumid, "1.19900000.1")
        self.assertEqual(artist_path, r"F:\J\Judas Priest")
        self.assertEqual(album_path, r"F:\J\Judas Priest\1990 - Painkiller")
        self.assertEqual(album, "Painkiller")
        self.assertFalse(is_bootleg)
        self.assertEqual(basename, "1.19900000.1.13.D1.T01")
        self.assertEqual(extension, "flac")

    def test_t03(self):
        found, (artistid, albumid, artist_path, album_path, album, is_bootleg, basename, extension) = get_xreferences(
                r"F:\J\Judas Priest\1990 - Painkiller\1.Free Lossless Audio Codec\1.19900000.1.01.D1.T01.flac")
        self.assertFalse(found)
        self.assertIsNone(artistid)
        self.assertIsNone(albumid)
        self.assertIsNone(artist_path)
        self.assertIsNone(album_path)
        self.assertIsNone(album)
        self.assertFalse(is_bootleg)
        self.assertIsNone(basename)
        self.assertIsNone(extension)


class TestRegexT02(unittest.TestCase):

    def setUp(self):
        lookextensions = shared.CustomTemplate(shared.LOOKEXTENSIONS).substitute(extensions="|".join(shared.EXTENSIONS["music"]))
        artist = shared.CustomTemplate(shared.ARTIST).substitute(letter="\\3")
        file = shared.CustomTemplate(shared.FILE).substitute(year="\\6", month="00", day="00", encoder="\\9")
        self.regex = re.compile(
                f"^{shared.LOOKDEFAULTALBUM}{lookextensions}(({shared.DRIVE}\\\\{shared.LETTER}\\\\{artist}\\\\){shared.FOLDER}{shared.DEFAULTALBUM}\\\\){shared.DISC}{shared.COMPRESSION}\\\\{file}$")

    def test_t01(self):
        self.assertRegex(r"F:\A\Adams, Bryan\1984 - Reckless\1.Free Lossless Audio Codec\1.19840000.1.13.D1.T01.flac", self.regex)

    def test_t02(self):
        self.assertNotRegex(r"F:\A\Adams, Bryan\1984 - Reckless\1.Free Lossless Audio Codec\1.19850000.1.13.D1.T01.flac", self.regex)

    def test_t03(self):
        self.assertNotRegex(r"F:\A\Adams, Bryan\1984 - Reckless\1.Free Lossless Audio Codec\1.19850000.1.02.D1.T01.flac", self.regex)

    def test_t04(self):
        self.assertNotRegex(r"F:\B\Adams, Bryan\1984 - Reckless\1.Free Lossless Audio Codec\1.19850000.1.13.D1.T01.flac", self.regex)

    def test_t05(self):
        self.assertNotRegex(r"F:\B\Adams, Bryan\Reckless\1.Free Lossless Audio Codec\1.19850000.1.13.D1.T01.flac", self.regex)

    def test_t06(self):
        self.assertNotRegex(r"F:\A\Adams, Bryan\1984 - Reckless\1.Free Lossless Audio Codec\1.19840000.1.13..T01.flac", self.regex)

    def test_t07(self):
        self.assertNotRegex(r"F:\A\Adams, Bryan\1984 - Reckless\1.Free Lossless Audio Codec\1.19840000.1.13.D1..flac", self.regex)

    def test_t08(self):
        self.assertNotRegex(r"F:\A\Adams, Bryan\1984 - Reckless\1.Free Lossless Audio Codec\1.19840000.1.13.T01.flac", self.regex)

    def test_t09(self):
        self.assertNotRegex(r"F:\A\Adams, Bryan\1984 - Reckless\1.Free Lossless Audio Codec\1.19840000.1.13.D1.flac", self.regex)

    def test_t10(self):
        self.assertNotRegex(r"F:\A\Adams, Bryan\1984 - Reckless\1.Free Lossless Audio Codec\1.19840000.1..D1.T01.flac", self.regex)

    def test_t11(self):
        self.assertNotRegex(r"F:\A\Adams, Bryan\1984 - Reckless\1.Free Lossless Audio Codec\1.19840000.1.D1.T01.flac", self.regex)

    def test_t12(self):
        self.assertRegex(r"F:\A\Adams, Bryan\1\1984 - Reckless\CD1\1.Free Lossless Audio Codec\1.19840000.1.13.D1.T01.flac", self.regex)

    def test_t13(self):
        self.assertRegex(r"F:\A\Adams, Bryan\1\1984 - Reckless\1.Free Lossless Audio Codec\1.19840000.1.13.D1.T01.flac", self.regex)

    def test_t14(self):
        self.assertRegex(r"F:\A\Adams, Bryan\1984 - Reckless\CD1\1.Free Lossless Audio Codec\1.19840000.1.13.D1.T01.flac", self.regex)

    def test_t15(self):
        self.assertNotRegex(r"F:\A\Adams, Bryan\1\1984 - Reckless\CD1\Some Folder\1.Free Lossless Audio Codec\1.19840000.1.13.D1.T01.flac", self.regex)

    def test_t16(self):
        self.assertNotRegex(r"F:\A\Adams, Bryan\1984 - Reckless\1.19840000.1.13.D1.T01.flac", self.regex)

    def test_t17(self):
        self.assertNotRegex(r"F:\A\Adams, Bryan\1984 - Reckless\1.Free Lossless Audio Codec\1.19840000.1.13.D1.T01", self.regex)

    def test_t18(self):
        self.assertNotRegex(r"F:\A\Adams, Bryan\1984 - Reckless\1.Free Lossless Audio Codec\1.19840000.1.13.D1.T01.ex", self.regex)

    def test_t19(self):
        self.assertNotRegex(r"F:\A\Adams, Bryan\1984 - Reckless\1.Free Lossless Audio Codec\1.19840000.1.13.D1.T01.m_3", self.regex)

    def test_t20(self):
        self.assertNotRegex(r"F:\A\Adams, Bryan\1984 - Reckless\1.Free Lossless Audio Codec\1.19840000.1.13.D1.T01.FLAC", self.regex)

    def test_t21(self):
        self.assertNotRegex(r"F:\A\Adams, Bryan\1984 - Reckless\1.Free Lossless Audio Codec\1.04.Somebody.flac", self.regex)

    def test_t22(self):
        self.assertRegex(r"F:\K\Kiss\1\1977.2 - Alive II\CD2\0.MPEG-4 AAC\1.19770000.2.02.D2.T01.m4a", self.regex)

    def test_t23(self):
        self.assertRegex(r"F:\K\Kiss\1\1977.2 - Alive II\CD2\0.MPEG-4 AAC\1.19770000.2.02.D2.T02.m4a", self.regex)

    def test_t24(self):
        self.assertRegex(r"F:\K\Kiss\1\1977.2 - Alive II\CD2\1.Monkey's Audio\1.19770000.2.12.D2.T01.ape", self.regex)

    def test_t25(self):
        self.assertRegex(r"F:\K\Kiss\1\1977.2 - Alive II\CD2\1.Monkey's Audio\1.19770000.2.12.D2.T02.ape", self.regex)

    def test_t26(self):
        self.assertRegex(r"F:\S\Springsteen, Bruce\1\1973.2 - The Wild, The Innocent & The E Street Shuffle\0.MPEG-4 AAC\1.19730000.2.02.D1.T06.m4a", self.regex)

    def test_t27(self):
        self.assertRegex(r"F:\S\Springsteen, Bruce\1\1973.2 - The Wild, The Innocent & The E Street Shuffle\0.MPEG-4 AAC\1.19730000.2.02.D1.T07.m4a", self.regex)

    def test_t28(self):
        self.assertNotRegex(r"F:\J\Judas Priest\1977 - Sin After Sin\0.MPEG 1 Layer III\[Judas Priest] - 1977 - Sin After Sin - D1 T09.mp3", self.regex)

    def test_t29(self):
        self.assertNotRegex(r"F:\J\Judas Priest\1977 - Sin After Sin\0.MPEG 1 Layer III\[Judas Priest] - 1977 - Sin After Sin - D1 T09.mp3", self.regex)


class TestRegexT03(unittest.TestCase):

    def test_t01(self):
        self.assertEqual(shared.valid_albumsort("1.19840000.1"), "1.19840000.1")

    def test_t02(self):
        self.assertRaises(ValueError, shared.valid_albumsort, "1.19840000.1.13")

    def test_t03(self):
        self.assertEqual(shared.valid_albumsort("2.19840808.1"), "2.19840808.1")

    def test_t04(self):
        self.assertRaises(ValueError, shared.valid_albumsort, "2.19840808.1.13")

    def test_t05(self):
        self.assertRaises(ValueError, shared.valid_albumsort, "2.12345678.1")

    def test_t06(self):
        self.assertRaises(ValueError, shared.valid_albumsort, "Some String")

    def test_t07(self):
        self.assertRaises(ValueError, shared.valid_albumsort, "3.20180000.1")

    def test_t08(self):
        self.assertRaises(ValueError, shared.valid_albumsort, "4.20180000.1")

    def test_t09(self):
        self.assertRaises(ValueError, shared.valid_albumsort, "5.20180000.1")

    def test_t10(self):
        self.assertRaises(ValueError, shared.valid_albumsort, "6.20180000.1")

    def test_t11(self):
        self.assertRaises(ValueError, shared.valid_albumsort, "7.20180000.1")

    def test_t12(self):
        self.assertRaises(ValueError, shared.valid_albumsort, "8.20180000.1")

    def test_t13(self):
        self.assertRaises(ValueError, shared.valid_albumsort, "9.20180000.1")

    def test_t14(self):
        self.assertRaises(ValueError, shared.valid_albumsort, "123456789012")

    def test_t15(self):
        self.assertEqual(shared.valid_albumid("A.Adams, Bryan.1.19840000.1"), "A.Adams, Bryan.1.19840000.1")

    def test_t16(self):
        self.assertRaises(ValueError, shared.valid_albumid, "B.Adams, Bryan.1.19840000.1")

    def test_t17(self):
        self.assertRaises(ValueError, shared.valid_albumid, "Adams, Bryan.1.19840000.1")

    def test_t18(self):
        self.assertRaises(ValueError, shared.valid_albumid, "A.Adams, Bryan.1.19840000.1.13")

    def test_t19(self):
        self.assertEqual(shared.valid_albumid("S.Springsteen, Bruce.2.20120704.1"), "S.Springsteen, Bruce.2.20120704.1")

    def test_t20(self):
        self.assertRaises(ValueError, shared.valid_albumid, "Some String")

    def test_t21(self):
        self.assertEqual(shared.valid_albumid("I.Iron Maiden.1.19830000.1"), "I.Iron Maiden.1.19830000.1")

    def test_t22(self):
        self.assertRaises(ValueError, shared.valid_albumid, "1.19840000.1")

    def test_t23(self):
        self.assertRaises(ValueError, shared.valid_albumsort, "S.Springsteen, Bruce.2.20120704.1")


class TestValidYear(unittest.TestCase):
    """
    Test `valid_year` function.
    """

    def test_t01(self):
        for argument in ["2017", 2017]:
            with self.subTest(year=argument):
                self.assertEqual(shared.valid_year(argument), 2017)

    def test_t02(self):
        for argument in ["abcdefghijklmnopqrstuvwxyz", "20171", "2a2", [2015, 2016, 2017], 9999, 10.5]:
            with self.subTest(year=argument):
                self.assertRaises(ValueError, shared.valid_year, argument)

    def test_t03(self):
        with self.assertRaises(ValueError) as cm:
            shared.valid_year("20171")
        exception, = cm.exception.args
        self.assertEqual(exception, '"20171" is not a valid year.')


class TestValid_albumsort(unittest.TestCase):
    """
    Test `valid_albumsort` function.
    """

    def test_t01(self):
        for argument in ["1.20170000.1", "1.20170000.2", "2.20171019.1"]:
            with self.subTest(albumsort=argument):
                self.assertEqual(shared.valid_albumsort(argument), argument)

    def test_t02(self):
        for argument in ["abcdefghijklmnopqrstuvwxyz", "20171", "2a2", [2015, 2016, 2017], 9999, "1.20170000.1.13.D1.T01.NNN", 10.5]:
            with self.subTest(year=argument):
                self.assertRaises(ValueError, shared.valid_albumsort, argument)

    def test_t03(self):
        with self.assertRaises(ValueError) as cm:
            shared.valid_albumsort("1.20180000.1.13")
        exception, = cm.exception.args
        self.assertEqual(exception, '"1.20180000.1.13" is not a valid albumsort.')


class TestValidGenre(unittest.TestCase):
    """
    Test `valid_genre` function.
    """

    def test_t01(self):
        for argument in ["Rock", "Hard Rock", "black metal"]:
            with self.subTest(genre=argument):
                self.assertEqual(shared.valid_genre(argument), argument)

    def test_t02(self):
        for argument in ["abcdefghijklmnopqrstuvwxyz", "20171", "2a2", [2015, 2016, 2017], 9999, "1.20170000.1.13.D1.T01.NNN", "some genre", 10.5]:
            with self.subTest(genre=argument):
                self.assertRaises(ValueError, shared.valid_genre, argument)

    def test_t03(self):
        with self.assertRaises(ValueError) as cm:
            shared.valid_genre("Some Genre")
        exception, = cm.exception.args
        self.assertEqual(exception, '"Some Genre" is not a valid genre.')
