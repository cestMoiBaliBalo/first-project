# -*- coding: utf-8 -*-
import json
import logging.config
import os
import tempfile
import unittest
from datetime import datetime

import yaml

from .. import shared
from ..AudioCD.shared import DefaultAudioCDTags, RippedCD, changealbum, changetrack, digitalaudiobase, rippinglog

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))


# ========
# Classes.
# ========
class Test01DefaultCDTrack(unittest.TestCase):
    """
    Test "Applications.AudioCD.shared.DefaultAudioCDTags" class.
    """

    def setUp(self):
        self.maxDiff = None

        # Default single CD tags.
        # Both "artist" and "artistsort" are identical.
        # "origyear" is not provided.
        # "offset" is provided.
        # Input tags given by dBpoweramp.
        tags1 = {
            "Album": "Abigail",
            "Year": "1987",
            "Disc": "1/1",
            "Label": "Roadrunner Records",
            "UPC": "016861878825",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "9/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness",
            "Offset": "0"
        }

        # Default single CD tags.
        # Both "artist" and "artistsort" are identical.
        # "origyear" is provided.
        # "offset" is provided.
        # Input tags given by dBpoweramp.
        tags2 = {
            "Album": "Abigail",
            "Year": "2016",
            "Disc": "1/1",
            "Label": "Roadrunner Records",
            "UPC": "016861878825",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "9/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness",
            "OrigYear": "1987",
            "Offset": "0"
        }

        self.track1 = DefaultAudioCDTags(**{k.lower(): v for k, v in tags1.items()})
        self.track2 = DefaultAudioCDTags(**{k.lower(): v for k, v in tags2.items()})

    def test_01first(self):
        self.assertEqual(self.track1.discnumber, "1")

    def test_02second(self):
        self.assertEqual(self.track1.totaldiscs, "1")

    def test_03third(self):
        self.assertEqual(self.track1.tracknumber, "9")

    def test_04fourth(self):
        self.assertEqual(self.track1.totaltracks, "13")

    def test_05fifth(self):
        self.assertEqual(self.track1.albumsort, "1.19870000.1.13")

    def test_06sixth(self):
        self.assertEqual(self.track1.genre, "Hard Rock")

    def test_07seventh(self):
        self.assertEqual(self.track1.titlesort, "D1.T09.NNN")

    def test_08eighth(self):
        self.assertIn("taggingtime", self.track1)

    def test_09ninth(self):
        self.assertIn("encodingtime", self.track1)

    def test_10tenth(self):
        self.assertEqual(self.track1.origyear, "1987")

    def test_11eleventh(self):
        self.assertEqual(self.track1.year, "1987")

    def test_12twelfth(self):
        self.assertEqual(self.track2.origyear, "1987")

    def test_13thirteenth(self):
        self.assertEqual(self.track2.year, "2016")

    def test_14fourteenth(self):
        self.assertEqual(self.track2.albumsort, "1.19870000.1.13")


class Test02DefaultCDTrack(unittest.TestCase):
    """
    Test "Applications.AudioCD.shared.RippedCD" context manager.
    "default" is used as ripping profile.
    """

    def setUp(self):
        self.maxDiff = None

        # Default single CD tags.
        # Both "artist" and "artistsort" are identical.
        # "origyear" is not provided.
        # "offset" is provided.
        # Input tags given by dBpoweramp.
        itags = {
            "Album": "Abigail",
            "Year": "1987",
            "Disc": "1/1",
            "Label": "Roadrunner Records",
            "UPC": "016861878825",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "9/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness",
            "Offset": "13"
        }

        # Output tags expected from external python script.
        self.reftags = {
            "_albumart_1_front album cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "album": "Abigail",
            "albumartist": "King Diamond",
            "albumartistsort": "King Diamond",
            "albumsort": "1.19870000.1.13",
            "artist": "King Diamond",
            "artistsort": "King Diamond",
            "disc": "1",
            "disctotal": "1",
            "encoder": "(FLAC 1.3.0)",
            "genre": "Hard Rock",
            "incollection": "Y",
            "label": "Roadrunner Records",
            "origyear": "1987",
            "profile": "Default",
            "rating": "8",
            "source": "CD (Lossless)",
            "title": "A Mansion in Darkness",
            "titlelanguage": "English",
            "titlesort": "D1.T09.NNN",
            "track": "9",
            "tracktotal": "13",
            "upc": "016861878825",
            "year": "1987"
        }

        ofile, ifile = None, None
        with tempfile.TemporaryDirectory() as directory:
            ifile = os.path.join(directory, "tags.txt")

            # Create input tags text file.
            with open(ifile, mode=shared.WRITE, encoding=shared.UTF16) as fo:
                for k, v in itags.items():
                    fo.write("{0}={1}\n".format(k, v))
                    if k.lower() == "track":
                        ofile = "T{0:0>2}.json".format(v.split("/")[0])

            # Create output tags json file.
            with RippedCD("default", ifile):
                pass

        # Extract output tags into a dictionary.
        ofile = os.path.join(os.path.expandvars("%TEMP%"), ofile)
        if os.path.exists(ofile):
            with open(ofile, encoding=shared.UTF8) as fo:
                self.otags = json.load(fo)

    def test_01first(self):
        self.assertIn("encodedby", self.otags)

    def test_02second(self):
        self.assertIn("encodingtime", self.otags)

    def test_03third(self):
        self.assertIn("taggingtime", self.otags)

    def test_04fourth(self):
        logger = logging.getLogger("{0}.Test02DefaultCDTrack.test_04fourth".format(__name__))
        del self.otags["encodedby"]
        del self.otags["taggingtime"]
        del self.otags["encodingtime"]
        self.reftags["encodingyear"] = shared.dateformat(shared.UTC.localize(datetime.utcnow()).astimezone(shared.LOCAL), "$Y")
        for k, v in self.otags.items():
            logger.debug("{0}: {1}".format(k, v))
        self.assertDictEqual(self.otags, self.reftags)


@unittest.skip
class Test03DefaultCDTrack(unittest.TestCase):
    """
    Test "Applications.AudioCD.shared.rippinglog" function for default single CD.
    Both "artist" and "artistsort" are identical.
    "origyear" is not provided.
    "offset" is provided.
    """

    def setUp(self):
        self.maxDiff = None
        tags = {
            "Album": "Abigail",
            "Year": "1987",
            "Disc": "1/1",
            "Label": "Roadrunner Records",
            "UPC": "016861878825",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "9/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness"
        }
        self.first, self.second = ["King Diamond", "1987", "1987", "Abigail", "1", "13", "Hard Rock", "016861878825", "dBpoweramp 15.1", "1.19870000.1", "King Diamond"], None
        with tempfile.TemporaryDirectory() as directory:
            outfile = os.path.join(directory, "rippinglog.json")

            # Create ripping data into a JSON structure using the default API.
            rippinglog(DefaultAudioCDTags(**{k.lower(): v for k, v in tags.items()}), fil=outfile)

            # Load JSON structure into a list.
            if os.path.exists(outfile):
                with open(outfile, encoding=shared.UTF8) as fr:
                    self.second = json.load(fr)[0]
            if self.second:
                self.second = self.second[0:8] + self.second[9:]

    def test_01first(self):
        self.assertTrue(self.second)

    def test_02second(self):
        self.assertListEqual(self.first, self.second)


@unittest.skip
class Test04DefaultCDTrack(unittest.TestCase):
    """
    Test "Applications.AudioCD.shared.digitalaudiobase" function for default single CD.
    Both "artist" and "artistsort" are identical.
    "origyear" is not provided.
    "offset" is provided.
    """

    def setUp(self):
        self.maxDiff = None
        tags = {
            "Album": "Abigail",
            "Year": "1987",
            "Disc": "1/1",
            "Label": "Roadrunner Records",
            "UPC": "016861878825",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "9/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness",
            "Offset": "0"
        }
        self.first, self.second = ["K.King Diamond.1.19870000.1.D1.T09.NNN", "1.19870000.1", "D1.T09.NNN", "King Diamond", "1987", "Abigail", "Hard Rock", "1", "1", "Roadrunner Records", "9",
                                   "13", "A Mansion in Darkness", "N", "N", "Y", "016861878825", "English", "1987"], None
        self.first.insert(17, "{0:>4}".format(shared.dateformat(shared.UTC.localize(datetime.utcnow()).astimezone(shared.LOCAL), "$Y")))
        with tempfile.TemporaryDirectory() as directory:
            outfile = os.path.join(directory, "digitalaudiodatabase.json")

            # Create digital audio data into a JSON structure using the default API.
            digitalaudiobase(DefaultAudioCDTags(**{k.lower(): v for k, v in tags.items()}), fil=outfile)

            # Load JSON structure into a list.
            if os.path.exists(outfile):
                with open(outfile, encoding=shared.UTF8) as fr:
                    self.second = json.load(fr)[0]

    def test_01first(self):
        self.assertTrue(self.second)

    def test_02second(self):
        self.assertListEqual(self.first, self.second)


@unittest.skip
class Test05DefaultCDTrack(unittest.TestCase):
    """
    Test "Applications.AudioCD.shared.rippinglog" function for a multi CDs album.
    Both "artist" and "artistsort" are identical.
    "origyear" is provided.
    "offset" is provided.
    """

    def setUp(self):
        self.maxDiff = None
        tags = {
            "Album": "Abigail",
            "Year": "2016",
            "Disc": "1/2",
            "Label": "Roadrunner Records",
            "UPC": "016861878825",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "9/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness",
            "OrigYear": "1987",
            "Offset": "0"
        }
        self.first, self.second = ["King Diamond", "1987", "2016", "Abigail (1/2)", "1", "13", "Hard Rock", "016861878825", "dBpoweramp 15.1", "1.19870000.1", "King Diamond"], None
        with tempfile.TemporaryDirectory() as directory:
            outfile = os.path.join(directory, "rippinglog.json")

            # Create ripping data into a JSON structure using the default API.
            rippinglog(DefaultAudioCDTags(**{k.lower(): v for k, v in tags.items()}), fil=outfile)

            # Load JSON structure into a list.
            if os.path.exists(outfile):
                with open(outfile, encoding=shared.UTF8) as fr:
                    self.second = json.load(fr)[0]
            if self.second:
                self.second = self.second[0:8] + self.second[9:]

    def test_01first(self):
        self.assertTrue(self.second)

    def test_02second(self):
        self.assertListEqual(self.first, self.second)


class Test06DefaultCDTrack(unittest.TestCase):
    """
    Test "Applications.AudioCD.shared.ChangeAlbum" decorating class.
    """

    def setUp(self):
        self.maxDiff = None

        # Default single CD tags.
        # Both "artist" and "artistsort" are identical.
        # "origyear" is not provided.
        tags1 = {
            "Album": "Abigail",
            "Year": "1987",
            "Disc": "1/1",
            "Label": "Roadrunner Records",
            "UPC": "016861878825",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "9/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness",
            "Offset": "0"
        }

        # Default single CD tags.
        # Both "artist" and "artistsort" are identical.
        # "origyear" is provided.
        tags2 = {
            "Album": "Abigail",
            "Year": "2016",
            "Disc": "1/1",
            "Label": "Roadrunner Records",
            "UPC": "016861878825",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "9/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness",
            "OrigYear": "1987",
            "Offset": "0"
        }

        self.track1 = changealbum(DefaultAudioCDTags(**{k.lower(): v for k, v in tags1.items()}), "$albumsortyear.$albumsortcount - $album")
        self.track2 = changealbum(DefaultAudioCDTags(**{k.lower(): v for k, v in tags2.items()}), "$albumsortyear.$albumsortcount - $album")
        self.track3 = changealbum(DefaultAudioCDTags(**{k.lower(): v for k, v in tags1.items()}), "$year (Self Titled)")

    def test_01first(self):
        self.assertEqual(self.track1.discnumber, "1")

    def test_02second(self):
        self.assertEqual(self.track1.totaldiscs, "1")

    def test_03third(self):
        self.assertEqual(self.track1.tracknumber, "9")

    def test_04fourth(self):
        self.assertEqual(self.track1.totaltracks, "13")

    def test_05fifth(self):
        self.assertEqual(self.track1.albumsort, "1.19870000.1.13")

    def test_06sixth(self):
        self.assertEqual(self.track1.genre, "Hard Rock")

    def test_07seventh(self):
        self.assertEqual(self.track1.titlesort, "D1.T09.NNN")

    def test_08eighth(self):
        self.assertIn("taggingtime", self.track1)

    def test_09ninth(self):
        self.assertIn("encodingtime", self.track1)

    def test_10tenth(self):
        self.assertEqual(self.track1.origyear, "1987")

    def test_11eleventh(self):
        self.assertEqual(self.track1.year, "1987")

    def test_12twelfth(self):
        self.assertEqual(self.track2.origyear, "1987")

    def test_13thirteenth(self):
        self.assertEqual(self.track2.year, "2016")

    def test_14fourteenth(self):
        self.assertEqual(self.track2.albumsort, "1.19870000.1.13")

    def test_15fifteen(self):
        self.assertEqual(self.track1.album, "1987.1 - Abigail")

    def test_16sixteen(self):
        self.assertEqual(self.track2.album, "1987.1 - Abigail")

    def test_18eighteen(self):
        self.assertEqual(self.track3.album, "1987 (Self Titled)")


class Test07DefaultCDTrack(unittest.TestCase):
    """
    Test "Applications.AudioCD.shared.ChangeTrack" decorationg class.
    """

    def setUp(self):
        self.maxDiff = None
        tags = {
            "Album": "Abigail",
            "Year": "1987",
            "Disc": "1/1",
            "Label": "Roadrunner Records",
            "UPC": "016861878825",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "9/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness",
            "Offset": "8"
        }
        self.track = changetrack(DefaultAudioCDTags(**{k.lower(): v for k, v in tags.items()}), 8)

    def test_01first(self):
        self.assertEqual(self.track.tracknumber, "17")


class Test08DefaultCDTrack(unittest.TestCase):
    """
    Test both "Applications.AudioCD.shared.ChangeAlbum" and "Applications.AudioCD.shared.ChangeTrack" decorating classes.
    """

    def setUp(self):
        self.maxDiff = None
        tags = {
            "Album": "Abigail",
            "Year": "1987",
            "Disc": "1/1",
            "Label": "Roadrunner Records",
            "UPC": "016861878825",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "1/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness",
            "Offset": "8"
        }
        self.track = changetrack(changealbum(DefaultAudioCDTags(**{k.lower(): v for k, v in tags.items()}), "$albumsortyear.$albumsortcount - $album"), 8)

    def test_01first(self):
        self.assertEqual(self.track.tracknumber, "9")

    def test_02second(self):
        self.assertEqual(self.track.album, "1987.1 - Abigail")


class Test09DefaultCDTrack(unittest.TestCase):
    """
    Test "Applications.AudioCD.shared.RippedCD" context manager.
    "default" is used as ripping profile.
    Both "dftupdalbum" and "updtrack" are used as decorating profiles.
    """

    def setUp(self):
        self.maxDiff = None

        # Default single CD tags.
        # Both "artist" and "artistsort" are identical.
        # "origyear" is not provided.
        # Input tags given by dBpoweramp.
        itags = {
            "Album": "Abigail",
            "Year": "1987",
            "Disc": "1/1",
            "Label": "Roadrunner Records",
            "UPC": "016861878825",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "9/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness",
            "Offset": "10"
        }

        # Output tags expected from external python script.
        self.reftags = {
            "_albumart_1_front album cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "album": "1987.1 - Abigail",
            "albumartist": "King Diamond",
            "albumartistsort": "King Diamond",
            "albumsort": "1.19870000.1.13",
            "artist": "King Diamond",
            "artistsort": "King Diamond",
            "disc": "1",
            "disctotal": "1",
            "encoder": "(FLAC 1.3.0)",
            "genre": "Hard Rock",
            "incollection": "Y",
            "label": "Roadrunner Records",
            "origyear": "1987",
            "profile": "Default",
            "rating": "8",
            "source": "CD (Lossless)",
            "title": "A Mansion in Darkness",
            "titlelanguage": "English",
            "titlesort": "D1.T09.NNN",
            "track": "19",
            "tracktotal": "13",
            "upc": "016861878825",
            "year": "1987"
        }

        ofile, ifile, track, offset = None, None, None, None
        with tempfile.TemporaryDirectory() as directory:
            ifile = os.path.join(directory, "tags.txt")

            # Create input tags text file.
            with open(ifile, mode=shared.WRITE, encoding=shared.UTF16) as fo:
                for k, v in itags.items():
                    fo.write("{0}={1}\n".format(k, v))
                    if k.lower() == "track":
                        track = int(v.split("/")[0])
                    elif k.lower() == "offset":
                        offset = int(v.split("/")[0])
                ofile = "T{0:0>2}.json".format(track + offset)

            # Create output tags json file.
            with RippedCD("default", ifile, "dftupdalbum", "updtrack"):
                pass

        # Extract output tags into a dictionary.
        ofile = os.path.join(os.path.expandvars("%TEMP%"), ofile)
        if os.path.exists(ofile):
            with open(ofile, encoding=shared.UTF8) as fo:
                self.otags = json.load(fo)

    def test_01first(self):
        logger = logging.getLogger("{0}.Test09DefaultCDTrack.test_01first".format(__name__))
        del self.otags["encodedby"]
        del self.otags["taggingtime"]
        del self.otags["encodingtime"]
        self.reftags["encodingyear"] = shared.dateformat(shared.UTC.localize(datetime.utcnow()).astimezone(shared.LOCAL), "$Y")
        for k, v in self.otags.items():
            logger.debug("{0}: {1}".format(k, v))
        self.assertDictEqual(self.otags, self.reftags)


class Test10DefaultCDTrack(unittest.TestCase):
    """
    Test "Applications.AudioCD.shared.RippedCD" context manager.
    "default" is used as ripping profile.
    "dftupdalbum", "altupdalbum" and "updtrack" are used as decorating profiles.
    """

    def setUp(self):

        self.maxDiff = None

        # Default single CD tags.
        # Both "artist" and "artistsort" are identical.
        # "origyear" is not provided.
        # Input tags given by dBpoweramp.
        itags = {
            "Album": "Abigail",
            "Year": "1987",
            "Disc": "1/1",
            "Label": "Roadrunner Records",
            "UPC": "016861878825",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "9/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness",
            "Offset": "13"
        }

        # Output tags expected from external python script.
        self.reftags = {
            "_albumart_1_front album cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "album": "1987 (Self Titled)",
            "albumartist": "King Diamond",
            "albumartistsort": "King Diamond",
            "albumsort": "1.19870000.1.13",
            "artist": "King Diamond",
            "artistsort": "King Diamond",
            "disc": "1",
            "disctotal": "1",
            "encoder": "(FLAC 1.3.0)",
            "genre": "Hard Rock",
            "incollection": "Y",
            "label": "Roadrunner Records",
            "origyear": "1987",
            "profile": "Default",
            "rating": "8",
            "source": "CD (Lossless)",
            "title": "A Mansion in Darkness",
            "titlelanguage": "English",
            "titlesort": "D1.T09.NNN",
            "track": "22",
            "tracktotal": "13",
            "upc": "016861878825",
            "year": "1987"
        }

        ofile, ifile, track, offset = None, None, None, None
        with tempfile.TemporaryDirectory() as directory:
            ifile = os.path.join(directory, "tags.txt")

            # Create input tags text file.
            with open(ifile, mode=shared.WRITE, encoding=shared.UTF16) as fo:
                for k, v in itags.items():
                    fo.write("{0}={1}\n".format(k, v))
                    if k.lower() == "track":
                        track = int(v.split("/")[0])
                    elif k.lower() == "offset":
                        offset = int(v.split("/")[0])
                ofile = "T{0:0>2}.json".format(track + offset)

            # Create output tags json file.
            with RippedCD("default", ifile, "dftupdalbum", "altupdalbum", "updtrack"):
                pass

        # Extract output tags into a dictionary.
        ofile = os.path.join(os.path.expandvars("%TEMP%"), ofile)
        if os.path.exists(ofile):
            with open(ofile, encoding=shared.UTF8) as fo:
                self.otags = json.load(fo)

    def test_01first(self):
        logger = logging.getLogger("{0}.Test10DefaultCDTrack.test_01first".format(__name__))
        del self.otags["encodedby"]
        del self.otags["taggingtime"]
        del self.otags["encodingtime"]
        self.reftags["encodingyear"] = shared.dateformat(shared.UTC.localize(datetime.utcnow()).astimezone(shared.LOCAL), "$Y")
        for k, v in self.otags.items():
            logger.debug("{0}: {1}".format(k, v))
        self.assertDictEqual(self.otags, self.reftags)


class Test11DefaultCDTrack(unittest.TestCase):
    """
    Test "Applications.AudioCD.shared.RippedCD" context manager.
    "default" is used as ripping profile.
    Both "altupdalbum" and "updtrack" are used as decorating profiles.
    """

    def setUp(self):

        self.maxDiff = None

        # Default single CD tags.
        # Both "artist" and "artistsort" are identical.
        # "origyear" is not provided.
        # Input tags given by dBpoweramp.
        itags = {
            "Album": "Abigail",
            "Year": "1987",
            "Disc": "2/2",
            "Label": "Roadrunner Records",
            "UPC": "016861878825",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "3/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness",
            "Offset": "8"
        }

        # Output tags expected from external python script.
        self.reftags = {
            "_albumart_1_front album cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "album": "1987 (Self Titled)",
            "albumartist": "King Diamond",
            "albumartistsort": "King Diamond",
            "albumsort": "1.19870000.1.13",
            "artist": "King Diamond",
            "artistsort": "King Diamond",
            "disc": "2",
            "disctotal": "2",
            "encoder": "(FLAC 1.3.0)",
            "genre": "Hard Rock",
            "incollection": "Y",
            "label": "Roadrunner Records",
            "origyear": "1987",
            "profile": "Default",
            "rating": "8",
            "source": "CD (Lossless)",
            "title": "A Mansion in Darkness",
            "titlelanguage": "English",
            "titlesort": "D2.T03.NNN",
            "track": "11",
            "tracktotal": "13",
            "upc": "016861878825",
            "year": "1987"
        }

        ofile, ifile, track, offset = None, None, None, None
        with tempfile.TemporaryDirectory() as directory:
            ifile = os.path.join(directory, "tags.txt")

            # Create input tags text file.
            with open(ifile, mode=shared.WRITE, encoding=shared.UTF16) as fo:
                for k, v in itags.items():
                    fo.write("{0}={1}\n".format(k, v))
                    if k.lower() == "track":
                        track = int(v.split("/")[0])
                    elif k.lower() == "offset":
                        offset = int(v.split("/")[0])
                ofile = "T{0:0>2}.json".format(track + offset)

            # Create output tags json file.
            with RippedCD("default", ifile, "altupdalbum", "updtrack"):
                pass

        # Extract output tags into a dictionary.
        ofile = os.path.join(os.path.expandvars("%TEMP%"), ofile)
        if os.path.exists(ofile):
            with open(ofile, encoding=shared.UTF8) as fo:
                self.otags = json.load(fo)

    def test_01first(self):
        logger = logging.getLogger("{0}.Test11DefaultCDTrack.test_01first".format(__name__))
        del self.otags["encodedby"]
        del self.otags["taggingtime"]
        del self.otags["encodingtime"]
        self.reftags["encodingyear"] = shared.dateformat(shared.UTC.localize(datetime.utcnow()).astimezone(shared.LOCAL), "$Y")
        for k, v in self.otags.items():
            logger.debug("{0}: {1}".format(k, v))
        self.assertDictEqual(self.otags, self.reftags)


@unittest.skip
class Test12DefaultCDTrack(unittest.TestCase):
    """
    Test "Applications.AudioCD.shared.RippedCD" context manager with missing mandatory tags.
    """

    def setUp(self):
        self.maxDiff = None

        # Default single CD tags.
        # "offset" is not provided.
        self.itags = {
            "Album": "Abigail",
            "Year": "1987",
            "Disc": "2/2",
            "Label": "Roadrunner Records",
            "UPC": "016861878825",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "3/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness"
        }
        with self.assertRaises(ValueError) as cm:
            with tempfile.TemporaryDirectory() as directory:
                ifile = os.path.join(directory, "tags.txt")

                # Create input tags text file.
                with open(ifile, mode=shared.WRITE, encoding=shared.UTF16) as fo:
                    for k, v in self.itags.items():
                        fo.write("{0}={1}\n".format(k, v))

                with RippedCD("default", ifile):
                    pass

        self.msg, = cm.exception.args

    def test_01first(self):
        self.assertEqual(self.msg, "offset isn\'t available.")

    def test_02second(self):
        self.assertNotEqual(self.msg, "artist isn\'t available.")


class Test13DefaultCDTrack(unittest.TestCase):
    """
    Test "Applications.AudioCD.shared.RippedCD" context manager with missing mandatory tags.
    """

    def setUp(self):
        self.maxDiff = None
        self.itags = {
            "Album": "Abigail",
            "Year": "1987",
            "Disc": "2/2",
            "Label": "Roadrunner Records",
            "Artist": "King Diamond",
            "AlbumSortCount": "1",
            "Live": "N",
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Track": "3/13",
            "Profile": "Default",
            "Rating": "8",
            "Source": "CD (Lossless)",
            "Encoder": "(FLAC 1.3.0)",
            "ArtistSort": "King Diamond",
            "AlbumArtistSort": "King Diamond",
            "AlbumArtist": "King Diamond",
            "Genre": "Rock",
            "InCollection": "Y",
            "TitleLanguage": "English",
            "Bootleg": "N",
            "Title": "A Mansion in Darkness",
            "Offset": "8"
        }
        with self.assertRaises(ValueError) as cm:
            with tempfile.TemporaryDirectory() as directory:
                ifile = os.path.join(directory, "tags.txt")

                # Create input tags text file.
                with open(ifile, mode=shared.WRITE, encoding=shared.UTF16) as fo:
                    for k, v in self.itags.items():
                        fo.write("{0}={1}\n".format(k, v))

                with RippedCD("default", ifile):
                    pass

        self.msg, = cm.exception.args

    def test_01first(self):
        self.assertEqual(self.msg, "upc isn\'t available.")

    def test_02second(self):
        self.assertNotEqual(self.msg, "offset isn\'t available.")


class Test14DefaultCDTrack(unittest.TestCase):
    """
    Test "Applications.AudioCD.shared.RippedCD" context manager.
    "sbootlegs" is used as ripping profile.
    "sbootlegs" is used as decorating profile.
    """

    def setUp(self):
        self.maxDiff = None
        itags = {
            "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "Artist": "Bruce Springsteen",
            "ArtistSort": "Springsteen, Bruce",
            "AlbumArtist": "Bruce Springsteen",
            "AlbumArtistSort": "Springsteen, Bruce",
            "AlbumSortCount": "1",
            "Bonus": "N",
            "Bootleg": "Y",
            "BootlegTrackCity": "East Rutherford, NJ",
            "BootlegTrackCountry": "United States",
            "BootlegTrackTour": "The River Tour 2016",
            "BootlegTrackYear": "2016 07 24",
            "Disc": "2/3",
            "Encoder": "(FLAC 1.3.0)",
            "Genre": "Rock",
            "InCollection": "Y",
            "Live": "Y",
            "Title": "A Mansion in Darkness",
            "TitleLanguage": "English",
            "Offset": "13",
            "Profile": "SBootlegs",
            "Source": "CD (Lossless)",
            "Track": "10/13",
            "TotalTracks": "37",
            "Year": "1987"
        }
        self.reftags = {
            "_albumart_1_front album cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
            "album": "The River Tour 2016 - 2016.07.24 - [East Rutherford, NJ]",
            "albumartist": "Bruce Springsteen And The E Street Band",
            "albumartistsort": "Springsteen, Bruce",
            "albumsort": "2.20160724.1.13",
            "artist": "Bruce Springsteen",
            "artistsort": "Springsteen, Bruce",
            "bootlegtrackcity": "East Rutherford, NJ",
            "bootlegtrackcountry": "United States",
            "bootlegtracktour": "The River Tour 2016",
            "bootlegtrackyear": "2016-07-24",
            "disc": "2",
            "disctotal": "3",
            "encoder": "(FLAC 1.3.0)",
            "genre": "Rock",
            "incollection": "Y",
            "profile": "SBootlegs",
            "source": "CD (Lossless)",
            "title": "A Mansion in Darkness",
            "titlelanguage": "English",
            "titlesort": "D2.T10.NYY",
            "track": "23",
            "tracktotal": "37",
            "year": "2016"
        }
        ofile, ifile, track, offset = None, None, None, None

        with tempfile.TemporaryDirectory() as directory:
            ifile = os.path.join(directory, "tags.txt")

            # Create input tags text file.
            with open(ifile, mode=shared.WRITE, encoding=shared.UTF16) as fo:
                for k, v in itags.items():
                    fo.write("{0}={1}\n".format(k, v))
                    if k.lower() == "track":
                        track = int(v.split("/")[0])
                    elif k.lower() == "offset":
                        offset = int(v.split("/")[0])
                ofile = "T{0:0>2}.json".format(track + offset)

            # Create output tags json file.
            with RippedCD("sbootlegs", ifile, "sbootlegs", "updtotaltracks"):
                pass

        # Extract output tags into a dictionary.
        ofile = os.path.join(os.path.expandvars("%TEMP%"), ofile)
        if os.path.exists(ofile):
            with open(ofile, encoding=shared.UTF8) as fo:
                self.otags = json.load(fo)

    def test_01first(self):
        logger = logging.getLogger("{0}.Test14DefaultCDTrack.test_01first".format(__name__))
        del self.otags["encodedby"]
        del self.otags["taggingtime"]
        del self.otags["encodingtime"]
        self.reftags["encodingyear"] = shared.dateformat(shared.UTC.localize(datetime.utcnow()).astimezone(shared.LOCAL), "$Y")
        for k, v in self.otags.items():
            logger.debug("{0}: {1}".format(k, v))
        self.assertDictEqual(self.otags, self.reftags)

    def test_02second(self):
        self.assertEqual(self.otags["tracktotal"], "37")

    def test_03third(self):
        self.assertIn("tracktotal", self.otags)

    def test_04third(self):
        self.assertNotIn("totaltracks", self.otags)
