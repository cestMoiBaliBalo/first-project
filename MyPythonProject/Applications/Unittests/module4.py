# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import os
import sqlite3
import unittest
from pathlib import Path

from ..shared import TESTDATABASE

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Deprecated"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent


# ===============
# Global classes.
# ===============
# class SetUp(object):
#     _encoding = UTF8  # type: Optional[str]
#
#     def _decorate_callable(self, func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             with self as tempdir:
#                 database = join(tempdir, "database.db")
#                 jsontags = join(tempdir, "tags.json")
#                 create_tables(drop_tables(database))
#                 with open(_MYPARENT / "Resources" / "resource2.yml", encoding=self._encoding) as stream:
#                     collection = yaml.load(stream, Loader=yaml.FullLoader)
#                 for item in collection:
#                     track = Mock()
#                     for key, value in item.items():
#                         setattr(track, key, value)
#                     dump_audiotags_tojson(track, albums, database=database, jsonfile=jsontags)
#                 with open(jsontags, encoding=self._encoding) as stream:
#                     insert_albums_fromjson(stream)
#                 args += (database,)
#                 if self.args:
#                     args += self.args
#                 func(*args, **kwargs)
#
#         return wrapper
#
#     def _decorate_class(self, klass):
#         for attr in dir(klass):
#             if not attr.startswith("test"):
#                 continue
#             attr_value = getattr(klass, attr)
#             if not hasattr(attr_value, "__call__"):
#                 continue
#             setattr(klass, attr, self(attr_value))
#         return klass
#
#     def __init__(self, *args, suffix=None, prefix=None, root=None):
#         self.name = None
#         self.suffix = suffix
#         self.prefix = prefix
#         self.root = root
#         self.args = args
#
#     def __enter__(self):
#         self.name = mkdtemp(self.suffix, self.prefix, self.root)
#         return self.name
#
#     def __exit__(self, exc_type, exc_value, traceback):
#         shutil.rmtree(self.name)
#
#     def __call__(self, arg):
#         if isinstance(arg, type):
#             return self._decorate_class(arg)
#         return self._decorate_callable(arg)


# ==============
# Tests classes.
# ==============
# @unittest.skip
# class TestGetTagsFile(unittest.TestCase):
#
#     def setUp(self):
#         self.track = Mock()
#         self.track.album = "The Album"
#         self.track.albumsortcount = "1"
#         self.track.artistsort = "Artist, The"
#         self.track.artistsort_letter = "A"
#         self.track.bootleg = "N"
#         self.track.discnumber = "1"
#         self.track.foldersortcount = "N"
#         self.track.origyear = "2019"
#         self.track.totaldiscs = "1"
#
#     def test01(self):
#         self.assertEqual(get_tagsfile(self.track), r"A\Artist, The\2019 - The Album")
#
#     def test02(self):
#         self.track.totaldiscs = "2"
#         self.assertEqual(get_tagsfile(self.track), r"A\Artist, The\2019 - The Album\CD1")
#
#     def test03(self):
#         self.track.discnumber = "2"
#         self.track.totaldiscs = "2"
#         self.assertEqual(get_tagsfile(self.track), r"A\Artist, The\2019 - The Album\CD2")
#
#     def test04(self):
#         self.track.foldersortcount = "Y"
#         self.assertEqual(get_tagsfile(self.track), r"A\Artist, The\2019.1 - The Album")
#
#     def test05(self):
#         self.track.albumsortcount = "2"
#         self.track.foldersortcount = "Y"
#         self.assertEqual(get_tagsfile(self.track), r"A\Artist, The\2019.2 - The Album")
#
#     def test06(self):
#         self.track.albumsortcount = "2"
#         self.track.discnumber = "3"
#         self.track.foldersortcount = "Y"
#         self.track.totaldiscs = "3"
#         self.assertEqual(get_tagsfile(self.track), r"A\Artist, The\2019.2 - The Album\CD3")


# @unittest.skip
# @SetUp("A.Artist, The.1.20190000.1", 1)
# class TestDatabase01(unittest.TestCase):
#
#     def setUp(self):
#         self._count = 10  # type: int
#         self._played = 0  # type: int
#         self._datobj = datetime.now()  # type: datetime
#         self._datstr = get_readabledate(LOCAL.localize(self._datobj))  # type: str
#
#     def test_t01(self, database, albumid, discid):
#         """
#         Test `update_playeddisccount` function.
#         Test that database changes are the expected ones.
#         """
#         _, updated = update_playeddisccount(albumid, discid, db=database, local_played=self._datobj)
#         self.assertEqual(updated, 1)
#
#     def test_t02(self, database, albumid, discid):
#         """
#         Test `update_playeddisccount` function.
#         Test that played count is the expected one.
#         """
#         i, played = 1, 0  # type: int, int
#         while i <= self._count:
#             update_playeddisccount(albumid, discid, db=database)
#             i += 1
#         with DatabaseConnection(database) as conn:
#             curs = conn.cursor()
#             curs.execute("SELECT played FROM playeddiscs WHERE albumid=? AND discid=?", (albumid, discid))
#             with suppress(TypeError):
#                 (played,) = curs.fetchone()
#         self.assertEqual(played, self._played + self._count)
#
#     def test_t03(self, database, albumid, discid):
#         """
#         Test `update_playeddisccount` function.
#         Test that most recent played date is the expected one.
#         Use a naive local timestamp (Europe/Paris timezone).
#         """
#         utc_played = None  # type: Optional[datetime]
#         update_playeddisccount(albumid, discid, db=database, local_played=self._datobj)
#         with DatabaseConnection(database) as conn:
#             curs = conn.cursor()
#             curs.execute("SELECT utc_played FROM playeddiscs WHERE albumid=? AND discid=?", (albumid, discid))
#             with suppress(TypeError):
#                 (utc_played,) = curs.fetchone()
#         self.assertIsNotNone(utc_played)
#         self.assertEqual(get_readabledate(UTC.localize(utc_played).astimezone(LOCAL)), self._datstr)
#
#     def test_t04(self, database, albumid, discid):
#         """
#         Test `update_playeddisccount` function.
#         Test that most recent played date is the expected one.
#         Use an aware local timestamp (Europe/Paris timezone).
#         """
#         utc_played = None  # type: Optional[datetime]
#         update_playeddisccount(albumid, discid, db=database, local_played=LOCAL.localize(self._datobj))
#         with DatabaseConnection(database) as conn:
#             curs = conn.cursor()
#             curs.execute("SELECT utc_played FROM playeddiscs WHERE albumid=? AND discid=?", (albumid, discid))
#             with suppress(TypeError):
#                 (utc_played,) = curs.fetchone()
#         self.assertIsNotNone(utc_played)
#         self.assertEqual(get_readabledate(UTC.localize(utc_played).astimezone(LOCAL)), self._datstr)


# @unittest.skip
# @patch("Applications.Tables.Albums.shared.datetime")
# @SetUp("A.Artist, The.1.20190000.1", 1)
# class TestDatabase02(unittest.TestCase):
#
#     def setUp(self):
#         self._datobj = datetime(2019, 9, 19, 22)
#
#     def test_t01(self, mock_datetime, database, albumid, discid):
#         """
#         Test `update_playeddisccount` function.
#         Test that most recent played date is the expected one.
#         """
#         mock_datetime.now.return_value = self._datobj
#         mock_datetime.utcnow.return_value = datetime.utcnow()
#         utc_played = None  # type: Optional[datetime]
#         update_playeddisccount(albumid, discid, db=database)
#         with DatabaseConnection(database) as conn:
#             curs = conn.cursor()
#             curs.execute("SELECT utc_played FROM playeddiscs WHERE albumid=? AND discid=?", (albumid, discid))
#             with suppress(TypeError):
#                 (utc_played,) = curs.fetchone()
#         self.assertEqual(get_readabledate(UTC.localize(utc_played).astimezone(LOCAL)), get_readabledate(LOCAL.localize(self._datobj)))
#         mock_datetime.now.assert_called_once()
#         mock_datetime.utcnow.assert_called()
#         self.assertEqual(mock_datetime.utcnow.call_count, 2)


# @unittest.skip
# @SetUp()
# class TestDatabase03(unittest.TestCase):
#
#     def test_t01(self, database):
#         """
#         Test `get_albumidfromgenre` function.
#         """
#         self.assertListEqual(sorted(get_albumidfromgenre("Rock", db=database)), ["A.Artist, The.1.20110000.1",
#                                                                                  "A.Artist, The.1.20130000.1",
#                                                                                  "A.Artist, The.1.20150000.1",
#                                                                                  "A.Artist, The.1.20170000.1",
#                                                                                  "A.Artist, The.1.20190000.1"])
#
#     def test_t02(self, database):
#         """
#         Test `get_albumidfromgenre` function.
#         """
#         self.assertListEqual(sorted(get_albumidfromgenre("Alternative Rock", db=database)), ["A.Awesome Artist, The.1.20080000.1"])
#
#     def test_t03(self, database):
#         """
#         Test `exist_albumid` function.
#         """
#         self.assertTrue(exist_albumid("A.Awesome Artist, The.1.20080000.1", db=database))
#
#     def test_t04(self, database):
#         """
#         Test `exist_albumid` function.
#         """
#         self.assertFalse(exist_albumid("A.Awesome Artist, The.1.20080000.2", db=database))
#
#     def test_t05(self, database):
#         """
#         Test `exist_albumid` function.
#         """
#         self.assertFalse(exist_albumid("A.Awesome Artist.1.20080000.1", db=database))
#
#     def test_t06(self, database):
#         """
#         Test that total ripped discs are coherent after inserting new discs.
#         """
#         self.assertEqual(get_total_rippeddiscs(database), 16)
#
#     def test_t07(self, database):
#         """
#         Test `defaultalbums` function.
#         """
#         collection = sorted(set([track.genre for track in defaultalbums(db=database)]))
#         expected_collection = ["Alternative Rock", "Hard Rock", "Rock"]
#         self.assertListEqual(collection, expected_collection)
#
#     def test_t08(self, database):
#         """
#         Test `defaultalbums` function.
#         """
#         collection = sorted(set([(track.artistsort, track.genre) for track in defaultalbums(db=database)]), key=itemgetter(0))
#         expected_collection = [("Artist, The", "Rock"), ("Awesome Artist, The", "Alternative Rock"), ("Other Artist, The", "Hard Rock")]
#         self.assertListEqual(collection, expected_collection)
#
#     def test_t09(self, database):
#         """
#         Test `update_defaultalbums` function.
#         """
#         self.assertEqual(update_defaultalbums(*[f"O.Other Artist, The.1.{year}0000.1" for year in range(2012, 2020, 2)], db=database, label="Island Records"), 4)
#
#     def test_t10(self, database):
#         """
#         Test `defaultalbums` function.
#         """
#         collection = sorted(set([(track.artistsort, track.label) for track in defaultalbums(db=database)]), key=itemgetter(0))
#         expected_collection = [("Artist, The", "Columbia Records"), ("Awesome Artist, The", "Columbia Records"), ("Other Artist, The", "Roadrunner Records")]
#         self.assertListEqual(collection, expected_collection)
#
#     def test_t11(self, database):
#         """
#         Test `update_defaultalbums` function.
#         """
#         self.assertEqual(update_defaultalbums(*[f"O.Other Artist, The.1.{year}0000.1" for year in range(2012, 2020, 2)], db=database, label="Island Records", upc="123456789012"), 4)
#         collection = sorted(set([(track.artistsort, track.label) for track in defaultalbums(db=database)]), key=itemgetter(0))
#         expected_collection = [("Artist, The", "Columbia Records"), ("Awesome Artist, The", "Columbia Records"), ("Other Artist, The", "Island Records")]
#         self.assertListEqual(collection, expected_collection)
#
#     def test_t12(self, database):
#         """
#         Test `update_defaultalbums` function.
#         """
#         update_defaultalbums(*[f"O.Other Artist, The.1.{year}0000.1" for year in range(2012, 2020, 2)], db=database, label="Island Records")
#         collection = sorted(set([track.label for track in defaultalbums(db=database)]), key=itemgetter(0))
#         self.assertFalse("Roadrunner Records" in collection)
#         self.assertListEqual(collection, ["Columbia Records", "Island Records"])


# @unittest.skip
# @SetUp("A.Artist, The.1.20190000.1", 1)
# class TestDatabase04(unittest.TestCase):
#
#     def setUp(self):
#         self._count, self._played = 10, 0  # type: int, int
#
#     def test_t01(self, database, albumid, discid):
#         played = 0  # type: int
#         with DatabaseConnection(database) as conn:
#             curs = conn.cursor()
#             curs.execute("SELECT played FROM playeddiscs WHERE albumid=? AND discid=?", (albumid, discid))
#             with suppress(TypeError):
#                 (played,) = curs.fetchone()
#         self.assertEqual(played, self._played)
#
#     def test_t02(self, database, albumid, discid):
#         with DatabaseConnection(database) as conn:
#             curs = conn.cursor()
#             curs.execute("SELECT played FROM playeddiscs WHERE albumid=? AND discid=?", (albumid, discid))
#             with suppress(TypeError):
#                 (self._played,) = curs.fetchone()
#         update = partial(update_playeddisccount, db=database)
#         self.assertEqual(sum([updated for _, updated in map(update, *zip(*[(albumid, discid)] * self._count))]), self._count)


# @unittest.skip
# class TestDatabase05(unittest.TestCase):
#
#     def setUp(self):
#         self._albums = []
#         with DatabaseConnection(DATABASE) as conn:
#             self._albums = list(conn.execute("SELECT albumid, discid FROM playeddiscs ORDER BY albumid, discid"))
#
#     def test_t01(self):
#         with TemporaryDirectory() as tempdir:
#             copy(DATABASE, tempdir)
#             update = partial(update_playeddisccount, db=join(tempdir, "database.db"))
#             self.assertEqual(sum([updated for _, updated in map(update, *zip(*self._albums))]), len(self._albums))


# @unittest.skipUnless(sys.platform.lower().startswith("win"), "toto")
class TestDatabase01(unittest.TestCase):

    def setUp(self) -> None:
        self.conn = sqlite3.connect(TESTDATABASE)

    def tearDown(self) -> None:
        self.conn.close()

    def test01(self):
        cursor = self.conn.execute("SELECT count(*) FROM artists")
        (artists,) = cursor.fetchone()
        self.assertEqual(artists, 3)

    def test02(self):
        cursor = self.conn.execute("SELECT count(*) FROM albums")
        (albums,) = cursor.fetchone()
        self.assertEqual(albums, 3)

    def test03(self):
        cursor = self.conn.execute("SELECT count(*) FROM bootlegalbums")
        (albums,) = cursor.fetchone()
        self.assertEqual(albums, 1)

    def test04(self):
        cursor = self.conn.execute("SELECT count(*) FROM defaultalbums")
        (albums,) = cursor.fetchone()
        self.assertEqual(albums, 2)

    def test05(self):
        cursor = self.conn.execute("SELECT count(*) FROM discs")
        (discs,) = cursor.fetchone()
        self.assertEqual(discs, 3)

    def test06(self):
        cursor = self.conn.execute("SELECT count(*) FROM tracks")
        (tracks,) = cursor.fetchone()
        self.assertEqual(tracks, 4)
