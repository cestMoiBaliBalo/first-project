# -*- coding: utf-8 -*-
# import datetime
import json
import logging.config
import os
import sqlite3
import tempfile
import unittest
from operator import itemgetter
# from itertools import accumulate
from shutil import copy, rmtree

import yaml

import AudioCD.Interface as CD
# import AudioCD.RippedTracks as RT
# from .. import shared
from ..Database.AudioCD.shared import insertfromfile as insertlogfromfile
# from ..Database.DigitalAudioFiles.shared import deletealbum, insertfromfile as insertalbumfromfile, updatealbum
from ..shared import DATABASE

# from ..xml import digitalalbums_in, rippinglog_in

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))


# ========
# Classes.
# ========
class Test01(unittest.TestCase):
    """
    Tester la restitution d'un enregistrement de la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """
    logger = logging.getLogger("{0}.Test01".format(__name__))

    def setUp(self):
        self.arguments = CD.parser.parse_args("rippinglog select 28".split())

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "rippinglog")
        self.assertEqual(self.arguments.statement, "select")
        self.assertListEqual(self.arguments.rowid, [28])
        self.assertTrue(self.arguments.donotpropagate)
        self.assertEqual(self.arguments.template(self.arguments), "T01")
        self.assertFalse(self.arguments.test)
        self.assertEqual(self.arguments.db, DATABASE)
        self.assertEqual(self.arguments.loglevel, "INFO")

    def test_02second(self):
        """
        2. Tester la restitution à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        row = self.arguments.function(ns=self.arguments)[0]
        self.logger.debug(row)
        self.assertEqual(row.rowid, 28)
        self.assertEqual(row.artistsort, "Black Sabbath")
        self.assertEqual(row.albumsort, "1.19760000.1")
        self.assertEqual(row.artist, "Black Sabbath")
        self.assertEqual(row.year, 1976)
        self.assertEqual(row.album, "Technical Ecstasy")
        self.assertEqual(row.genre, "Hard Rock")
        self.assertEqual(row.upc, "5017615832822")


class Test02(unittest.TestCase):
    """
    Tester la restitution d'un enregistrement de la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """
    logger = logging.getLogger("{0}.Test02".format(__name__))

    def setUp(self):
        self.arguments = CD.parser.parse_args("rippinglog select 28 31 32 33".split())

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "rippinglog")
        self.assertEqual(self.arguments.statement, "select")
        self.assertListEqual(self.arguments.rowid, [28, 31, 32, 33])
        self.assertTrue(self.arguments.donotpropagate)
        self.assertEqual(self.arguments.template(self.arguments), "T01")
        self.assertFalse(self.arguments.test)
        self.assertEqual(self.arguments.db, DATABASE)
        self.assertEqual(self.arguments.loglevel, "INFO")

    def test_02second(self):
        """
        2. Tester la restitution à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        row = self.arguments.function(ns=self.arguments)[0]
        self.logger.debug(row)
        self.assertEqual(row.rowid, 28)
        self.assertEqual(row.artistsort, "Black Sabbath")
        self.assertEqual(row.albumsort, "1.19760000.1")
        self.assertEqual(row.artist, "Black Sabbath")
        self.assertEqual(row.year, 1976)
        self.assertEqual(row.album, "Technical Ecstasy")
        self.assertEqual(row.genre, "Hard Rock")
        self.assertEqual(row.upc, "5017615832822")


class Test03(unittest.TestCase):
    """
    Tester la restitution d'un enregistrement de la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """
    logger = logging.getLogger("{0}.Test03".format(__name__))

    def setUp(self):
        self.arguments = CD.parser.parse_args("rippinglog select 28 31 32 33 --orderby artistsort albumsort".split())

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "rippinglog")
        self.assertEqual(self.arguments.statement, "select")
        self.assertListEqual(self.arguments.rowid, [28, 31, 32, 33])
        self.assertTrue(self.arguments.donotpropagate)
        self.assertEqual(self.arguments.template(self.arguments), "T01")
        self.assertFalse(self.arguments.test)
        self.assertEqual(self.arguments.db, DATABASE)
        self.assertEqual(self.arguments.loglevel, "INFO")

    def test_02second(self):
        """
        2. Tester la restitution à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        row = self.arguments.function(ns=self.arguments)[0]
        self.logger.debug(row)
        self.assertEqual(row.artistsort, "Black Sabbath")
        self.assertEqual(row.albumsort, "1.19710000.1")
        self.assertEqual(row.artist, "Black Sabbath")
        self.assertEqual(row.year, 1971)
        self.assertEqual(row.album, "Master of Reality")
        self.assertEqual(row.genre, "Hard Rock")
        self.assertEqual(row.upc, "5017615830323")


class Test04(unittest.TestCase):
    """
    Tester la restitution d'un enregistrement de la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """
    logger = logging.getLogger("{0}.Test04".format(__name__))

    def setUp(self):
        self.arguments = CD.parser.parse_args(["rippinglog", "select", "28", "31", "32", "33", "--orderby", "artistsort DESC", "albumsort"])

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "rippinglog")
        self.assertEqual(self.arguments.statement, "select")
        self.assertListEqual(self.arguments.rowid, [28, 31, 32, 33])
        self.assertTrue(self.arguments.donotpropagate)
        self.assertEqual(self.arguments.template(self.arguments), "T01")
        self.assertFalse(self.arguments.test)
        self.assertEqual(self.arguments.db, DATABASE)
        self.assertEqual(self.arguments.loglevel, "INFO")

    def test_02second(self):
        """
        2. Tester la restitution à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        row = self.arguments.function(ns=self.arguments)[0]
        self.logger.debug(row)
        self.assertEqual(row.artistsort, "Kiss")
        self.assertEqual(row.albumsort, "1.19760000.2")
        self.assertEqual(row.artist, "Kiss")
        self.assertEqual(row.year, 1976)
        self.assertEqual(row.album, "Rock and Roll over")
        self.assertEqual(row.genre, "Hard Rock")
        self.assertEqual(row.upc, "042282415028")


class Test05(unittest.TestCase):
    """
    Tester la restitution d'un enregistrement de la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """
    logger = logging.getLogger("{0}.Test05".format(__name__))

    def setUp(self):
        self.arguments = CD.parser.parse_args(["rippinglog", "select", "28", "31", "32", "33", "--orderby", "artistsort DESC", "albumsort DESC"])

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "rippinglog")
        self.assertEqual(self.arguments.statement, "select")
        self.assertListEqual(self.arguments.rowid, [28, 31, 32, 33])
        self.assertTrue(self.arguments.donotpropagate)
        self.assertEqual(self.arguments.template(self.arguments), "T01")
        self.assertFalse(self.arguments.test)
        self.assertEqual(self.arguments.db, DATABASE)
        self.assertEqual(self.arguments.loglevel, "INFO")

    def test_02second(self):
        """
        2. Tester la restitution à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        row = self.arguments.function(ns=self.arguments)[0]
        self.logger.debug(row)
        self.assertEqual(row.artistsort, "Kiss")
        self.assertEqual(row.albumsort, "1.19760000.2")
        self.assertEqual(row.artist, "Kiss")
        self.assertEqual(row.year, 1976)
        self.assertEqual(row.album, "Rock and Roll over")
        self.assertEqual(row.genre, "Hard Rock")
        self.assertEqual(row.upc, "042282415028")


class Test06(unittest.TestCase):
    """
    Tester la mise à jour d'un enregistrement de la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """
    logger = logging.getLogger("{0}.Test06".format(__name__))
    rowid = 28

    def setUp(self):
        # 1. Define temporary directory.
        self.tempdir = tempfile.mkdtemp()

        # 2. Define temporary DB.
        self.db = os.path.join(self.tempdir, os.path.basename(DATABASE))

        # 3. Copy production DB into temporary folder.
        copy(src=DATABASE, dst=self.tempdir)

        # 4. Log both `genre` and `UPC` stored into temporary DB.
        conn = sqlite3.connect(self.db)
        curs = conn.cursor()
        curs.execute("SELECT genre, upc FROM rippinglog WHERE rowid=?", (self.rowid,))
        genre, upc = curs.fetchone()
        conn.close()
        self.logger.debug(genre)
        self.logger.debug(upc)

        # 5. Parse arguments.
        self.arguments = CD.parser.parse_args("rippinglog update {1} --genre Pop --upc 9999999999999 --ripped 1504122358 --database {0}".format(self.db, self.rowid).split())

    def tearDown(self):
        rmtree(self.tempdir)

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "rippinglog")
        self.assertEqual(self.arguments.statement, "update")
        self.assertTrue(self.arguments.donotpropagate)
        self.assertListEqual(self.arguments.rowid, [28])
        self.assertEqual(self.arguments.genre, "Pop")
        self.assertEqual(self.arguments.upc, "9999999999999")
        self.assertEqual(self.arguments.ripped, 1504122358)
        self.assertIsNone(self.arguments.template(self.arguments))
        self.assertFalse(self.arguments.test)
        self.assertEqual(self.arguments.db, self.db)
        self.assertEqual(self.arguments.loglevel, "INFO")

    def test_02second(self):
        """
        2. Tester la mise à jour à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        self.assertEqual(self.arguments.function(ns=self.arguments), 1)

    def test_03third(self):
        """
        3. Test that only temporary database was changed.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        conn = sqlite3.connect(self.db)
        curs = conn.cursor()
        curs.execute("SELECT genre, upc FROM rippinglog WHERE rowid=?", (self.rowid,))
        genre, upc = curs.fetchone()
        conn.close()
        self.logger.debug(genre)
        self.logger.debug(upc)
        self.assertEqual(genre, "Pop")
        self.assertEqual(upc, "9999999999999")

    def test_04fourth(self):
        """
        4. Test that production database remains unchanged.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        conn = sqlite3.connect(DATABASE)
        curs = conn.cursor()
        curs.execute("SELECT genre, upc FROM rippinglog WHERE rowid=?", (self.rowid,))
        genre, upc = curs.fetchone()
        conn.close()
        self.logger.debug(genre)
        self.logger.debug(upc)
        self.assertEqual(genre, "Hard Rock")
        self.assertEqual(upc, "5017615832822")


class Test07(unittest.TestCase):
    """
    Tester la suppression d'un enregistrement de la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """
    logger = logging.getLogger("{0}.Test07".format(__name__))
    rowid = 28

    def setUp(self):
        # 1. Define temporary directory.
        self.tempdir = tempfile.mkdtemp()

        # 2. Define temporary DB.
        self.db = os.path.join(self.tempdir, os.path.basename(DATABASE))

        # 3. Copy production DB into temporary folder.
        copy(src=DATABASE, dst=self.tempdir)

        # 4. Count initial records stored into temporary DB.
        conn = sqlite3.connect(self.db)
        curs = conn.cursor()
        curs.execute("SELECT count(*) FROM rippinglog WHERE rowid=?", (self.rowid,))
        count = curs.fetchone()[0]
        conn.close()
        self.logger.debug(count)

        # 5. Parse arguments.
        self.arguments = CD.parser.parse_args("rippinglog delete {1} --database {0} --loglevel DEBUG".format(self.db, self.rowid).split())

    def tearDown(self):
        rmtree(self.tempdir)

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "rippinglog")
        self.assertEqual(self.arguments.statement, "delete")
        self.assertListEqual(self.arguments.rowid, [28])
        self.assertTrue(self.arguments.donotpropagate)
        self.assertIsNone(self.arguments.template(self.arguments))
        self.assertFalse(self.arguments.test)
        self.assertEqual(self.arguments.db, self.db)
        self.assertEqual(self.arguments.loglevel, "DEBUG")

    def test_02second(self):
        """
        2. Tester la suppression à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        self.assertEqual(self.arguments.function(ns=self.arguments), 1)

    def test_03third(self):
        """
        3. Test that only temporary database was changed.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        conn = sqlite3.connect(self.db)
        curs = conn.cursor()
        curs.execute("SELECT count(*) FROM rippinglog WHERE rowid=?", (self.rowid,))
        count = curs.fetchone()[0]
        conn.close()
        self.logger.debug(count)
        self.assertEqual(count, 0)

    def test_04fourth(self):
        """
        4. Test that production database remains unchanged.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        conn = sqlite3.connect(DATABASE)
        curs = conn.cursor()
        curs.execute("SELECT count(*) FROM rippinglog WHERE rowid=?", (self.rowid,))
        count = curs.fetchone()[0]
        conn.close()
        self.logger.debug(count)
        self.assertEqual(count, 1)


# class Test05a(unittest.TestCase):
#     """
#     Tester la restitution d'un enregistrement de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
#     Sans propagation.
#     """
#
#     def setUp(self):
#         self.arguments = CD.parser.parse_args("albums select 30 --donotpropagate".split())
#
#     def test_01first(self):
#         """
#         1. Tester le fonctionnement du parser.
#         """
#         self.assertEqual(self.arguments.table, "albums")
#         self.assertEqual(self.arguments.statement, "select")
#         self.assertListEqual(self.arguments.rowid, [30])
#         self.assertTrue(self.arguments.donotpropagate)
#         self.assertEqual(self.arguments.template(self.arguments), "T02")
#         self.assertFalse(self.arguments.test)
#         self.assertEqual(self.arguments.db, DATABASE)
#
#     def test_02second(self):
#         """
#         2. Tester la restitution à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
#         """
#         for row in self.arguments.function(ns=self.arguments):
#             self.assertEqual(row.rowid, 30)
#             self.assertEqual(row.albumid, "I.Iron Maiden.1.19900000.4")
#             self.assertEqual(row.artist, "Iron Maiden")
#             self.assertEqual(row.year, 1990)
#             self.assertEqual(row.album, "The First Ten Years - IV")
#             self.assertEqual(row.genre, "Heavy Metal")
#             self.assertFalse(row.live)
#             self.assertFalse(row.bootleg)
#             self.assertTrue(row.incollection)
#             self.assertEqual(row.language, "English")
#             self.assertEqual(row.count, 0)
#
#
# class Test05b(unittest.TestCase):
#     """
#     Tester la restitution d'un enregistrement de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
#     Avec propagation.
#     """
#
#     def setUp(self):
#         self.arguments = CD.parser.parse_args("albums select 30".split())
#
#     def test_01first(self):
#         """
#         1. Tester le fonctionnement du parser.
#         """
#         self.assertEqual(self.arguments.table, "albums")
#         self.assertEqual(self.arguments.statement, "select")
#         self.assertListEqual(self.arguments.rowid, [30])
#         self.assertFalse(self.arguments.donotpropagate)
#         self.assertEqual(self.arguments.template(self.arguments), "T04")
#         self.assertFalse(self.arguments.test)
#         self.assertEqual(self.arguments.db, DATABASE)
#
#     @unittest.skip
#     def test_02second(self):
#         """
#         2. Tester la restitution à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
#         """
#         for row in self.arguments.function(ns=self.arguments):
#             self.assertEqual(row.rowid, 30)
#             self.assertEqual(row.albumid, "I.Iron Maiden.1.19900000.4")
#             self.assertEqual(row.artist, "Iron Maiden")
#             self.assertEqual(row.year, 1990)
#             self.assertEqual(row.album, "The First Ten Years - IV")
#             self.assertEqual(row.genre, "Heavy Metal")
#             self.assertFalse(row.live)
#             self.assertFalse(row.bootleg)
#             self.assertTrue(row.incollection)
#             self.assertEqual(row.language, "English")
#             self.assertEqual(row.count, 0)
#
#
# class Test06(unittest.TestCase):
#     """
#     Tester la suppression d'un enregistrement de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
#     Sans propagation à `discs` et `tracks`.
#     """
#
#     def setUp(self):
#         self.arguments = CD.parser.parse_args("albums delete 30 --donotpropagate".split())
#
#     def test_01first(self):
#         """
#         1. Tester le fonctionnement du parser.
#         """
#         self.assertEqual(self.arguments.table, "albums")
#         self.assertEqual(self.arguments.statement, "delete")
#         self.assertListEqual(self.arguments.rowid, [30])
#         self.assertTrue(self.arguments.donotpropagate)
#         self.assertIsNone(self.arguments.template(self.arguments))
#         self.assertFalse(self.arguments.test)
#         self.assertEqual(self.arguments.db, DATABASE)
#
#     def test_02second(self):
#         """
#         Tester le fonctionnement du parser.
#         """
#         discs, tracks = list(), list()
#         conn = sqlite3.connect(self.arguments.db, detect_types=sqlite3.PARSE_DECLTYPES)
#         conn.row_factory = sqlite3.Row
#         with conn:
#             for row in conn.execute("SELECT rowid FROM discs WHERE albumid='I.Iron Maiden.1.19900000.4'"):
#                 discs.append(row["rowid"])
#             for row in conn.execute("SELECT rowid FROM tracks WHERE albumid='I.Iron Maiden.1.19900000.4'"):
#                 tracks.append(row["rowid"])
#         conn.close()
#         self.assertEqual(sorted(discs), [34])
#         self.assertEqual(sorted(tracks), [384, 385, 386, 387])
#
#
# class Test07(unittest.TestCase):
#     """
#     Tester la suppression d'un enregistrement de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
#     Avec propagation à `discs` et `tracks`.
#     """
#
#     def setUp(self):
#         self.arguments = CD.parser.parse_args("albums delete 30".split())
#
#     def test_01first(self):
#         """
#         1. Tester le fonctionnement du parser.
#         """
#         self.assertEqual(self.arguments.table, "albums")
#         self.assertEqual(self.arguments.statement, "delete")
#         self.assertListEqual(self.arguments.rowid, [30])
#         self.assertFalse(self.arguments.donotpropagate)
#         self.assertEqual(self.arguments.template(self.arguments), "T03")
#         self.assertFalse(self.arguments.test)
#         self.assertEqual(self.arguments.db, DATABASE)
#
#     def test_02second(self):
#         """
#         2. Tester la suppression à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(self.arguments.db))
#             copy(src=self.arguments.db, dst=dst)
#             kwargs = {key: val for key, val in vars(self.arguments).items() if val}
#             kwargs["db"] = dst
#             self.assertListEqual(self.arguments.function(**kwargs), [("I.Iron Maiden.1.19900000.4", 1, 1, 4)])
#
#     def test_03third(self):
#         """
#         3. Tester la suppression à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(self.arguments.db))
#             copy(src=self.arguments.db, dst=dst)
#             kwargs = {key: val for key, val in vars(self.arguments).items() if val}
#             kwargs["db"] = dst
#             if self.arguments.function(**kwargs):
#                 albums, discs, tracks = 0, 0, 0
#                 conn = sqlite3.connect(dst, detect_types=sqlite3.PARSE_DECLTYPES)
#                 conn.row_factory = sqlite3.Row
#                 with conn:
#                     for row in conn.execute("SELECT count(*) AS count FROM albums WHERE rowid=?", (30,)):
#                         albums = row["count"]
#                     for row in conn.execute("SELECT count(*) AS count FROM discs WHERE rowid=?", (34,)):
#                         discs = row["count"]
#                     for row in conn.execute("SELECT count(*) AS count FROM tracks WHERE rowid BETWEEN ? AND ?", (384, 387)):
#                         tracks = row["count"]
#                 conn.close()
#                 self.assertEqual(albums, 0)
#                 self.assertEqual(discs, 0)
#                 self.assertEqual(tracks, 0)
#
#
# class Test08a(unittest.TestCase):
#     """
#     Tester la mise à jour d'un enregistrement de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
#     Album unique key is not updated.
#     """
#
#     def setUp(self):
#         self.arguments = CD.parser.parse_args(["albums", "update", "30", "--genre", "Rock", "--upc", "9999999999999", "--album", "Communiqué", "--live", "Y", "--bootleg", "Y", "--incollection", "N"])
#
#     def test_01first(self):
#         """
#         1. Tester le fonctionnement du parser.
#         """
#         self.assertEqual(self.arguments.table, "albums")
#         self.assertEqual(self.arguments.statement, "update")
#         self.assertTrue(self.arguments.donotpropagate)
#         self.assertListEqual(self.arguments.rowid, [30])
#         self.assertEqual(self.arguments.album, "Communiqué")
#         self.assertEqual(self.arguments.genre, "Rock")
#         self.assertTrue(self.arguments.live.bool)
#         self.assertTrue(self.arguments.bootleg.bool)
#         self.assertFalse(self.arguments.incollection.bool)
#         self.assertEqual(self.arguments.upc, "9999999999999")
#         self.assertEqual(self.arguments.template(self.arguments), "T03")
#         self.assertFalse(self.arguments.test)
#         self.assertEqual(self.arguments.db, DATABASE)
#
#     def test_02second(self):
#         """
#         2. Tester le nombre total de changements.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(self.arguments.db))
#             copy(src=self.arguments.db, dst=dst)
#             kwargs = {key: val for key, val in vars(self.arguments).items() if val}
#             kwargs["db"] = dst
#             self.assertListEqual(self.arguments.function(**kwargs), [("I.Iron Maiden.1.19900000.4", 1, 0, 0)])
#
#     def test_03third(self):
#         """
#         3. Tester la mise à jour à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(self.arguments.db))
#             copy(src=self.arguments.db, dst=dst)
#             kwargs = {key: val for key, val in vars(self.arguments).items() if val}
#             kwargs["db"] = dst
#             if self.arguments.function(**kwargs):
#                 conn = sqlite3.connect(dst, detect_types=sqlite3.PARSE_DECLTYPES)
#                 curs = conn.cursor()
#                 try:
#                     curs.execute("SELECT album, genre, live, bootleg, incollection, upc FROM albums WHERE rowid=?", (30,))
#                     row = curs.fetchone()
#                     if row:
#                         self.assertEqual(row[0], self.arguments.album)
#                         self.assertEqual(row[1], self.arguments.genre)
#                         self.assertTrue(row[2])
#                         self.assertTrue(row[3])
#                         self.assertFalse(row[4])
#                         self.assertEqual(row[5], self.arguments.upc)
#                 finally:
#                     conn.close()
#
#
# class Test08b(unittest.TestCase):
#     """
#     Tester la mise à jour de la date de dernière lecture de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
#     Le timestamp communiqué au parser est exprimé par rapport à l'UTC !
#     La mise à jour du nombre de lectures est également testée.
#     """
#
#     def setUp(self):
#         self.arguments = CD.parser.parse_args(["albums", "update", "30", "--count", "100", "--played", "1505040486"])
#
#     def test_01first(self):
#         """
#         1. Tester le fonctionnement du parser.
#         """
#         self.assertEqual(self.arguments.table, "albums")
#         self.assertEqual(self.arguments.statement, "update")
#         self.assertTrue(self.arguments.donotpropagate)
#         self.assertListEqual(self.arguments.rowid, [30])
#         self.assertEqual(self.arguments.count, 100)
#         self.assertEqual(self.arguments.template(self.arguments), "T03")
#         self.assertFalse(self.arguments.test)
#         self.assertEqual(self.arguments.db, DATABASE)
#
#     def test_02second(self):
#         """
#         2. Tester le nombre total de changements.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(self.arguments.db))
#             copy(src=self.arguments.db, dst=dst)
#             kwargs = {key: val for key, val in vars(self.arguments).items() if val}
#             kwargs["db"] = dst
#             self.assertListEqual(self.arguments.function(**kwargs), [("I.Iron Maiden.1.19900000.4", 1, 0, 0)])
#
#     def test_03third(self):
#         """
#         3. Tester la mise à jour à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(self.arguments.db))
#             copy(src=self.arguments.db, dst=dst)
#             kwargs = {key: val for key, val in vars(self.arguments).items() if val}
#             kwargs["db"] = dst
#             if self.arguments.function(**kwargs):
#                 conn = sqlite3.connect(dst, detect_types=sqlite3.PARSE_DECLTYPES)
#                 curs = conn.cursor()
#                 try:
#                     curs.execute("SELECT count, played FROM albums WHERE rowid=?", (30,))
#                     row = curs.fetchone()
#                     if row:
#                         self.assertEqual(row[0], self.arguments.count)
#                         self.assertEqual(int(UTC.localize(row[1]).timestamp()), self.arguments.played)
#                         self.assertEqual(dateformat(UTC.localize(row[1]).astimezone(LOCAL), "$d/$m/$Y $H:$M:$S"), "10/09/2017 12:48:06")
#                 finally:
#                     conn.close()


# class Test08c(unittest.TestCase):
#     """
#     Tester l'incrémentation du compteur de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
#     """
#
#     def setUp(self):
#         self.arguments = CD.parser.parse_args(["albums", "update", "139", "--icount"])
#
#     def test_01first(self):
#         """
#         1. Tester le fonctionnement du parser.
#         """
#         self.assertEqual(self.arguments.table, "albums")
#         self.assertEqual(self.arguments.statement, "update")
#         self.assertTrue(self.arguments.donotpropagate)
#         self.assertListEqual(self.arguments.rowid, [139])
#         self.assertTrue(self.arguments.icount)
#         self.assertEqual(self.arguments.template(self.arguments), "T03")
#         self.assertFalse(self.arguments.test)
#         self.assertEqual(self.arguments.db, DATABASE)
#
#     def test_02second(self):
#         """
#         2. Tester le nombre total de changements.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(self.arguments.db))
#             copy(src=self.arguments.db, dst=dst)
#             kwargs = {key: val for key, val in vars(self.arguments).items() if val}
#             kwargs["db"] = dst
#             self.assertListEqual(self.arguments.function(**kwargs), [("K.Kiss.1.19870000.1", 1, 0, 0)])
#
#     def test_03third(self):
#         """
#         3. Tester la mise à jour à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
#         """
#
#         # Extraire le nombre de lectures stocké dans la base de production.
#         conn = sqlite3.connect(self.arguments.db, detect_types=sqlite3.PARSE_DECLTYPES)
#         conn.row_factory = sqlite3.Row
#         count = 0
#         for row in conn.execute("SELECT count FROM albums WHERE rowid=?", (139,)):
#             count = row["count"]
#         conn.close()
#         count += 1
#
#         # Comparer avec le résultat de la mise à jour.
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(self.arguments.db))
#             copy(src=self.arguments.db, dst=dst)
#             kwargs = {key: val for key, val in vars(self.arguments).items() if val}
#             kwargs["db"] = dst
#             if self.arguments.function(**kwargs):
#                 conn = sqlite3.connect(dst, detect_types=sqlite3.PARSE_DECLTYPES)
#                 curs = conn.cursor()
#                 try:
#                     curs.execute("SELECT count FROM albums WHERE rowid=?", (139,))
#                     row = curs.fetchone()
#                     if row:
#                         self.assertEqual(row[0], count)
#                 finally:
#                     conn.close()
#
#
# class Test08d(unittest.TestCase):
#     """
#     Tester la décrémentation du compteur de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
#     """
#
#     def setUp(self):
#         self.arguments = CD.parser.parse_args(["albums", "update", "139", "--dcount"])
#
#     def test_01first(self):
#         """
#         1. Tester le fonctionnement du parser.
#         """
#         self.assertEqual(self.arguments.table, "albums")
#         self.assertEqual(self.arguments.statement, "update")
#         self.assertTrue(self.arguments.donotpropagate)
#         self.assertListEqual(self.arguments.rowid, [139])
#         self.assertTrue(self.arguments.dcount)
#         self.assertEqual(self.arguments.template(self.arguments), "T03")
#         self.assertFalse(self.arguments.test)
#         self.assertEqual(self.arguments.db, DATABASE)
#
#     def test_02second(self):
#         """
#         2. Tester le nombre total de changements.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(self.arguments.db))
#             copy(src=self.arguments.db, dst=dst)
#             kwargs = {key: val for key, val in vars(self.arguments).items() if val}
#             kwargs["db"] = dst
#             self.assertListEqual(self.arguments.function(**kwargs), [("K.Kiss.1.19870000.1", 1, 0, 0)])
#
#     def test_03third(self):
#         """
#         3. Tester la mise à jour à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
#         """
#
#         # Extraire le nombre de lectures stocké dans la base de production.
#         conn = sqlite3.connect(self.arguments.db, detect_types=sqlite3.PARSE_DECLTYPES)
#         conn.row_factory = sqlite3.Row
#         count = 0
#         for row in conn.execute("SELECT count FROM albums WHERE rowid=?", (139,)):
#             count = row["count"]
#         conn.close()
#         count -= 1
#         if count < 0:
#             count = 0
#
#         # Comparer avec le résultat de la mise à jour.
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(self.arguments.db))
#             copy(src=self.arguments.db, dst=dst)
#             kwargs = {key: val for key, val in vars(self.arguments).items() if val}
#             kwargs["db"] = dst
#             if self.arguments.function(**kwargs):
#                 conn = sqlite3.connect(dst, detect_types=sqlite3.PARSE_DECLTYPES)
#                 curs = conn.cursor()
#                 try:
#                     curs.execute("SELECT count FROM albums WHERE rowid=?", (139,))
#                     row = curs.fetchone()
#                     if row:
#                         self.assertEqual(row[0], count)
#                 finally:
#                     conn.close()
#
#
# class Test09(unittest.TestCase):
#     """
#     Tester la fonction `Database.DigitalAudioFiles.shared.updatealbum`
#     """
#
#     def test_01first(self):
#         """
#         Test total changes when row unique ID is used as primary key.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             database = os.path.join(directory, os.path.basename(DATABASE))
#             copy(src=DATABASE, dst=database)
#             albumid, acount, dcount, tcount = updatealbum(30, db=database, album="The Album", genre="Some Genre")
#             self.assertEqual(albumid, "I.Iron Maiden.1.19900000.4")
#             self.assertEqual(acount, 1)
#             self.assertEqual(dcount, 0)
#             self.assertEqual(tcount, 0)
#
#     def test_02second(self):
#         """
#         Test field value when row unique ID is used as primary key.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             database = os.path.join(directory, os.path.basename(DATABASE))
#             copy(src=DATABASE, dst=database)
#             updatealbum(30, db=database, album="The Album", genre="Some Genre")
#             conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
#             conn.row_factory = sqlite3.Row
#             with conn:
#                 for row in conn.execute("SELECT album, genre FROM albums WHERE rowid=?", (30,)):
#                     self.assertEqual(row["album"], "The Album")
#                     self.assertEqual(row["genre"], "Some Genre")
#             conn.close()
#
#     def test_03third(self):
#         """
#         Test total changes when album unique ID is used as primary key.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             database = os.path.join(directory, os.path.basename(DATABASE))
#             copy(src=DATABASE, dst=database)
#             albumid, acount, dcount, tcount = updatealbum(30, db=database, albumid="I.Iron Maiden.1.19900000.9")
#             self.assertEqual(albumid, "I.Iron Maiden.1.19900000.4")
#             self.assertEqual(acount, 1)
#             self.assertEqual(dcount, 1)
#             self.assertEqual(tcount, 4)
#
#     def test_04fourth(self):
#         """
#         Test field value when album unique ID is used as primary key.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             database = os.path.join(directory, os.path.basename(DATABASE))
#             copy(src=DATABASE, dst=database)
#             updatealbum(30, db=database, albumid="I.Iron Maiden.1.19900000.9")
#             conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
#             conn.row_factory = sqlite3.Row
#             with conn:
#                 for row in conn.execute("SELECT albumid FROM albums WHERE rowid=?", (30,)):
#                     self.assertEqual(row["albumid"], "I.Iron Maiden.1.19900000.9")
#                 for row in conn.execute("SELECT albumid FROM discs WHERE rowid=?", (34,)):
#                     self.assertEqual(row["albumid"], "I.Iron Maiden.1.19900000.9")
#                 for i in [384, 385, 386, 387]:
#                     for row in conn.execute("SELECT albumid FROM tracks WHERE rowid=?", (i,)):
#                         self.assertEqual(row["albumid"], "I.Iron Maiden.1.19900000.9")
#             conn.close()
#
#
# class Test10(unittest.TestCase):
#     """
#     Tester la fonction `Database.DigitalAudioFiles.shared.delete`
#     Row unique ID is used as primary key.
#     """
#
#     def test_01first(self):
#         """
#         Test total changes.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             database = os.path.join(directory, os.path.basename(DATABASE))
#             copy(src=DATABASE, dst=database)
#             albumid, acount, dcount, tcount = deletealbum(db=database, uid=30)
#             self.assertEqual(albumid, "I.Iron Maiden.1.19900000.4")
#             self.assertEqual(acount, 1)
#             self.assertEqual(dcount, 1)
#             self.assertEqual(tcount, 4)
#
#     def test_02second(self):
#         """
#         Test propagation from `albums` table to both `discs` and `tracks` tables.
#         """
#         albums, discs, tracks = 0, 0, 0
#         with tempfile.TemporaryDirectory() as directory:
#             database = os.path.join(directory, os.path.basename(DATABASE))
#             copy(src=DATABASE, dst=database)
#             deletealbum(db=database, uid=30)
#             conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
#             conn.row_factory = sqlite3.Row
#             with conn:
#                 for row in conn.execute("SELECT count(*) AS count FROM albums WHERE albumid=?", ("I.Iron Maiden.1.19900000.4",)):
#                     albums = row["count"]
#                 for row in conn.execute("SELECT count(*) AS count FROM discs WHERE albumid=?", ("I.Iron Maiden.1.19900000.4",)):
#                     discs = row["count"]
#                 for row in conn.execute("SELECT count(*) AS count FROM tracks WHERE albumid=?", ("I.Iron Maiden.1.19900000.4",)):
#                     tracks = row["count"]
#             conn.close()
#             self.assertEqual(albums, 0)
#             self.assertEqual(discs, 0)
#             self.assertEqual(tracks, 0)
#
#
# class Test11(unittest.TestCase):
#     """
#     Tester la fonction `Database.DigitalAudioFiles.shared.delete`
#     Album unique ID is used as primary key.
#     """
#
#     def test_01first(self):
#         """
#         Test total changes.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             database = os.path.join(directory, os.path.basename(DATABASE))
#             copy(src=DATABASE, dst=database)
#             albumid, acount, dcount, tcount = deletealbum(db=database, albumid="I.Iron Maiden.1.19900000.4")
#             self.assertEqual(albumid, "I.Iron Maiden.1.19900000.4")
#             self.assertEqual(acount, 1)
#             self.assertEqual(dcount, 1)
#             self.assertEqual(tcount, 4)
#
#     def test_02second(self):
#         """
#         Test propagation from `albums` table to both `discs` and `tracks` tables.
#         """
#         albums, discs, tracks = 0, 0, 0
#         with tempfile.TemporaryDirectory() as directory:
#             database = os.path.join(directory, os.path.basename(DATABASE))
#             copy(src=DATABASE, dst=database)
#             deletealbum(db=database, uid=30)
#             conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
#             conn.row_factory = sqlite3.Row
#             with conn:
#                 for row in conn.execute("SELECT count(*) AS count FROM albums WHERE albumid=?", ("I.Iron Maiden.1.19900000.4",)):
#                     albums = row["count"]
#                 for row in conn.execute("SELECT count(*) AS count FROM discs WHERE albumid=?", ("I.Iron Maiden.1.19900000.4",)):
#                     discs = row["count"]
#                 for row in conn.execute("SELECT count(*) AS count FROM tracks WHERE albumid=?", ("I.Iron Maiden.1.19900000.4",)):
#                     tracks = row["count"]
#             conn.close()
#             self.assertEqual(albums, 0)
#             self.assertEqual(discs, 0)
#             self.assertEqual(tracks, 0)
#
#
# class Test12(unittest.TestCase):
#     """
#     Tester la mise à jour d'un enregistrement de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
#     Album unique key is updated.
#     """
#
#     def setUp(self):
#         self.arguments = CD.parser.parse_args(
#                 ["albums", "update", "30", "--genre", "Rock", "--upc", "9999999999999", "--album", "Communiqué", "--live", "Y", "--bootleg", "Y", "--incollection", "N", "--albumid",
#                  "I.Iron Maiden.1.19900000.9"])
#
#     def test_01first(self):
#         """
#         1. Tester le fonctionnement du parser.
#         """
#         self.assertEqual(self.arguments.table, "albums")
#         self.assertEqual(self.arguments.statement, "update")
#         self.assertTrue(self.arguments.donotpropagate)
#         self.assertListEqual(self.arguments.rowid, [30])
#         self.assertEqual(self.arguments.albumid, "I.Iron Maiden.1.19900000.9")
#         self.assertEqual(self.arguments.album, "Communiqué")
#         self.assertEqual(self.arguments.genre, "Rock")
#         self.assertTrue(self.arguments.live.bool)
#         self.assertTrue(self.arguments.bootleg.bool)
#         self.assertFalse(self.arguments.incollection.bool)
#         self.assertEqual(self.arguments.upc, "9999999999999")
#         self.assertEqual(self.arguments.template(self.arguments), "T03")
#         self.assertFalse(self.arguments.test)
#         self.assertEqual(self.arguments.db, DATABASE)
#
#     def test_02second(self):
#         """
#         2. Tester le nombre total de changements.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             database = os.path.join(directory, os.path.basename(self.arguments.db))
#             copy(src=self.arguments.db, dst=database)
#             kwargs = {key: val for key, val in vars(self.arguments).items() if val}
#             kwargs["db"] = database
#             self.assertListEqual(self.arguments.function(**kwargs), [("I.Iron Maiden.1.19900000.4", 1, 1, 4)])
#
#     def test_03third(self):
#         """
#         3. Tester la mise à jour à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             database = os.path.join(directory, os.path.basename(self.arguments.db))
#             copy(src=self.arguments.db, dst=database)
#             kwargs = {key: val for key, val in vars(self.arguments).items() if val}
#             kwargs["db"] = database
#             self.arguments.function(**kwargs)
#             conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
#             curs = conn.cursor()
#             try:
#
#                 # ALBUMS table.
#                 curs.execute("SELECT albumid, album, genre, live, bootleg, incollection, upc FROM albums WHERE rowid=?", (30,))
#                 row = curs.fetchone()
#                 if row:
#                     self.assertEqual(row[0], self.arguments.albumid)
#                     self.assertEqual(row[1], self.arguments.album)
#                     self.assertEqual(row[2], self.arguments.genre)
#                     self.assertTrue(row[3])
#                     self.assertTrue(row[4])
#                     self.assertFalse(row[5])
#                     self.assertEqual(row[6], self.arguments.upc)
#
#                 # DISCS table.
#                 curs.execute("SELECT albumid FROM discs WHERE rowid=?", (34,))
#                 row = curs.fetchone()
#                 if row:
#                     self.assertEqual(row[0], "I.Iron Maiden.1.19900000.9")
#
#                 # TRACKS table.
#                 for i in [384, 385, 386, 387]:
#                     curs.execute("SELECT albumid FROM tracks WHERE rowid=?", (i,))
#                     row = curs.fetchone()
#                     if row:
#                         self.assertEqual(row[0], "I.Iron Maiden.1.19900000.9")
#
#             finally:
#                 conn.close()


# class Test13a(unittest.TestCase):
#     """
#     Tester l'insertion d'un enregistrement dans la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
#     Les données proviennent de la ligne de commande.
#     """
#
#     def setUp(self):
#         self.arguments = CD.parser.parse_args(["rippinglog",
#                                                "insert",
#                                                "Kiss",
#                                                "1.19890000.1",
#                                                "Kiss",
#                                                "1989",
#                                                "1989",
#                                                "The Album",
#                                                "1",
#                                                "8",
#                                                "Hard Rock",
#                                                "5017615832822",
#                                                "Mercury Records",
#                                                "--application", "dBpoweramp 15.1"])
#
#     def test_01first(self):
#         """
#         1. Tester le fonctionnement du parser.
#         """
#         self.assertEqual(self.arguments.table, "rippinglog")
#         self.assertEqual(self.arguments.statement, "insert")
#         self.assertEqual(self.arguments.artistsort, "Kiss")
#         self.assertEqual(self.arguments.albumsort, "1.19890000.1")
#         self.assertEqual(self.arguments.artist, "Kiss")
#         self.assertEqual(self.arguments.origyear, "1989")
#         self.assertEqual(self.arguments.year, "1989")
#         self.assertEqual(self.arguments.album, "The Album")
#         self.assertEqual(self.arguments.disc, 1)
#         self.assertEqual(self.arguments.tracks, 8)
#         self.assertEqual(self.arguments.genre, "Hard Rock")
#         self.assertEqual(self.arguments.upc, "5017615832822")
#         self.assertEqual(self.arguments.application, "dBpoweramp 15.1")
#         self.assertFalse(self.arguments.test)
#         self.assertEqual(self.arguments.db, DATABASE)
#
#     def test_02second(self):
#         """
#         2. Tester l'insertion à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(self.arguments.db))
#             copy(src=self.arguments.db, dst=dst)
#             kwargs = {key: val for key, val in vars(self.arguments).items() if val}
#             kwargs["db"] = dst
#             self.assertEqual(self.arguments.function(**kwargs), 1)
#
#     def test_03third(self):
#         """
#         3. Tester l'insertion à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(self.arguments.db))
#             copy(src=self.arguments.db, dst=dst)
#             kwargs = {key: val for key, val in vars(self.arguments).items() if val}
#             kwargs["db"] = dst
#             if self.arguments.function(**kwargs):
#                 conn = sqlite3.connect(dst, detect_types=sqlite3.PARSE_DECLTYPES)
#                 curs = conn.cursor()
#                 try:
#                     curs.execute("SELECT artistsort, albumsort, artist, year, album, genre, upc, application, origyear, label FROM rippinglog ORDER BY rowid DESC")
#                     row = curs.fetchone()
#                     if row:
#                         self.assertEqual(row[0], "Kiss")
#                         self.assertEqual(row[1], "1.19890000.1")
#                         self.assertEqual(row[2], "Kiss")
#                         self.assertEqual(row[3], 1989)
#                         self.assertEqual(row[4], "The Album")
#                         self.assertEqual(row[5], "Hard Rock")
#                         self.assertEqual(row[6], "5017615832822")
#                         self.assertEqual(row[7], "dBpoweramp 15.1")
#                         self.assertEqual(row[8], 1989)
#                         self.assertEqual(row[9], "Mercury Records")
#                 finally:
#                     conn.close()
#
#
# class Test13b(unittest.TestCase):
#     """
#     Tester l'insertion d'un enregistrement dans la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
#     Les données proviennent de la ligne de commande.
#     """
#
#     def setUp(self):
#         self.arguments = CD.parser.parse_args(["rippinglog",
#                                                "insert",
#                                                "Kiss",
#                                                "1.19890000.1",
#                                                "Kiss",
#                                                "1989",
#                                                "1989",
#                                                "The Album",
#                                                "1",
#                                                "8",
#                                                "Hard Rock",
#                                                "5017615832822",
#                                                "Mercury Records"])
#
#     def test_01first(self):
#         """
#         1. Tester le fonctionnement du parser.
#         """
#         self.assertEqual(self.arguments.table, "rippinglog")
#         self.assertEqual(self.arguments.statement, "insert")
#         self.assertEqual(self.arguments.artistsort, "Kiss")
#         self.assertEqual(self.arguments.albumsort, "1.19890000.1")
#         self.assertEqual(self.arguments.artist, "Kiss")
#         self.assertEqual(self.arguments.origyear, "1989")
#         self.assertEqual(self.arguments.year, "1989")
#         self.assertEqual(self.arguments.album, "The Album")
#         self.assertEqual(self.arguments.disc, 1)
#         self.assertEqual(self.arguments.tracks, 8)
#         self.assertEqual(self.arguments.genre, "Hard Rock")
#         self.assertEqual(self.arguments.upc, "5017615832822")
#         self.assertEqual(self.arguments.application, "dBpoweramp 15.1")
#         self.assertFalse(self.arguments.test)
#         self.assertEqual(self.arguments.db, DATABASE)
#
#     def test_02second(self):
#         """
#         2. Tester l'insertion à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(self.arguments.db))
#             copy(src=self.arguments.db, dst=dst)
#             kwargs = {key: val for key, val in vars(self.arguments).items() if val}
#             kwargs["db"] = dst
#             self.assertEqual(self.arguments.function(**kwargs), 1)
#
#     def test_03third(self):
#         """
#         3. Tester l'insertion à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(self.arguments.db))
#             copy(src=self.arguments.db, dst=dst)
#             kwargs = {key: val for key, val in vars(self.arguments).items() if val}
#             kwargs["db"] = dst
#             if self.arguments.function(**kwargs):
#                 conn = sqlite3.connect(dst, detect_types=sqlite3.PARSE_DECLTYPES)
#                 curs = conn.cursor()
#                 try:
#                     curs.execute("SELECT artistsort, albumsort, artist, year, album, genre, upc, application, origyear, label FROM rippinglog ORDER BY rowid DESC")
#                     row = curs.fetchone()
#                     if row:
#                         self.assertEqual(row[0], "Kiss")
#                         self.assertEqual(row[1], "1.19890000.1")
#                         self.assertEqual(row[2], "Kiss")
#                         self.assertEqual(row[3], 1989)
#                         self.assertEqual(row[4], "The Album")
#                         self.assertEqual(row[5], "Hard Rock")
#                         self.assertEqual(row[6], "5017615832822")
#                         self.assertEqual(row[7], "dBpoweramp 15.1")
#                         self.assertEqual(row[8], 1989)
#                         self.assertEqual(row[9], "Mercury Records")
#                 finally:
#                     conn.close()
#
#
# class Test13c(unittest.TestCase):
#     """
#     Tester l'insertion d'un enregistrement dans la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
#     Les données proviennent d'un fichier XML encodé en UTF-8.
#     """
#
#     def setUp(self):
#         self.arguments = CD.parser.parse_args(["rippinglog", "insertfromfile", r"G:\Computing\MyPythonProject\Applications\Tests\test_rippinglog.xml"])
#
#     def test_01first(self):
#         """
#         1. Tester le fonctionnement du parser.
#         """
#         self.assertEqual(self.arguments.table, "rippinglog")
#         self.assertEqual(self.arguments.statement, "insertfromfile")
#         self.assertIsNone(self.arguments.template(self.arguments))
#         self.assertFalse(self.arguments.test)
#         self.assertEqual(self.arguments.db, DATABASE)
#
#     def test_02second(self):
#         """
#         2. Tester l'insertion à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(self.arguments.db))
#             copy(src=self.arguments.db, dst=dst)
#             kwargs = {key: val for key, val in vars(self.arguments).items() if val}
#             kwargs["db"] = dst
#             self.assertEqual(self.arguments.function(**kwargs), 3)
#
#     def test_03third(self):
#         """
#         3. Tester l'insertion à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(self.arguments.db))
#             copy(src=self.arguments.db, dst=dst)
#             kwargs = {key: val for key, val in vars(self.arguments).items() if val}
#             kwargs["db"] = dst
#             if self.arguments.function(**kwargs):
#                 conn = sqlite3.connect(dst, detect_types=sqlite3.PARSE_DECLTYPES)
#                 curs = conn.cursor()
#                 try:
#                     curs.execute("SELECT artistsort, albumsort, artist, year, album, application FROM rippinglog ORDER BY rowid DESC")
#                     row = curs.fetchone()
#                     if row:
#                         self.assertEqual(row[0], "Artist 3, The")
#                         self.assertEqual(row[1], "1.20150000.1")
#                         self.assertEqual(row[2], "The Artist 3")
#                         self.assertEqual(row[3], 2015)
#                         self.assertEqual(row[4], "Album 3")
#                         self.assertEqual(row[5], "dBpoweramp 15.1")
#                 finally:
#                     conn.close()
#
#
# class Test13d(unittest.TestCase):
#     """
#     Tester l'insertion d'un enregistrement dans la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
#     Les données proviennent d'un fichier JSON encodé en UTF-8.
#     """
#
#     def setUp(self):
#         self.arguments = CD.parser.parse_args(["rippinglog", "insertfromfile", r"G:\Computing\MyPythonProject\Applications\Tests\test_rippinglog.json"])
#
#     def test_01first(self):
#         """
#         1. Tester le fonctionnement du parser.
#         """
#         self.assertEqual(self.arguments.table, "rippinglog")
#         self.assertEqual(self.arguments.statement, "insertfromfile")
#         self.assertIsNone(self.arguments.template(self.arguments))
#         self.assertFalse(self.arguments.test)
#         self.assertEqual(self.arguments.db, DATABASE)
#
#     def test_02second(self):
#         """
#         2. Tester l'insertion à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(self.arguments.db))
#             copy(src=self.arguments.db, dst=dst)
#             kwargs = {key: val for key, val in vars(self.arguments).items() if val}
#             kwargs["db"] = dst
#             self.assertEqual(self.arguments.function(**kwargs), 3)
#
#     def test_03third(self):
#         """
#         3. Tester l'insertion à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
#         """
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(self.arguments.db))
#             copy(src=self.arguments.db, dst=dst)
#             kwargs = {key: val for key, val in vars(self.arguments).items() if val}
#             kwargs["db"] = dst
#             if self.arguments.function(**kwargs):
#                 conn = sqlite3.connect(dst, detect_types=sqlite3.PARSE_DECLTYPES)
#                 curs = conn.cursor()
#                 try:
#                     curs.execute("SELECT artistsort, albumsort, artist, year, album, application FROM rippinglog ORDER BY rowid DESC")
#                     row = curs.fetchone()
#                     if row:
#                         self.assertEqual(row[0], "Artist 3, The")
#                         self.assertEqual(row[1], "1.20150000.1")
#                         self.assertEqual(row[2], "The Artist 3")
#                         self.assertEqual(row[3], 2015)
#                         self.assertEqual(row[4], "Album 3")
#                         self.assertEqual(row[5], "dBpoweramp 15.1")
#                 finally:
#                     conn.close()


# class Test14a(unittest.TestCase):
#     """
#     Tester l'insertion d'un enregistrement dans la table `rippinglog` depuis les données exposées par un fichier XML encodé en UTF-8.
#     Tester individuellement les fonctions `Applications.xml.rippinglog_in` et `Applications.Database.AudioCD.shared.insertfromfile`.
#     """
#
#     def setUp(self):
#         self.file = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tests", "test_rippinglog.xml")
#
#     def test_01first(self):
#         self.artist, self.origyear, self.year, self.album, self.disc, self.tracks, self.genre, self.upc, self.label, self.ripped, self.application, self.artistsort, self.albumsort = \
#             list(rippinglog_in(self.file))[0]
#         self.assertEqual(self.artistsort, "Artist 1, The")
#         self.assertEqual(self.albumsort, "1.20170000.1")
#         self.assertEqual(self.artist, "The Artist 1")
#         self.assertEqual(self.origyear, "2017")
#         self.assertEqual(self.year, "2017")
#         self.assertEqual(self.album, "Album 1")
#         self.assertEqual(self.disc, 1)
#         self.assertEqual(self.tracks, 10)
#         self.assertEqual(self.genre, "Hard Rock")
#         self.assertEqual(self.upc, "1234567890123")
#         self.assertIsNone(self.label)
#         self.assertEqual(self.application, "dBpoweramp 15.1")
#
#     def test_02second(self):
#         filobj = open(self.file)
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(DATABASE))
#             copy(src=DATABASE, dst=dst)
#             self.assertEqual(insertlogfromfile(filobj, db=dst), 3)
#         if not filobj.closed:
#             filobj.close()
#
#     def test_03third(self):
#         filobj = open(self.file)
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(DATABASE))
#             copy(src=DATABASE, dst=dst)
#             if insertlogfromfile(filobj, db=dst):
#                 conn = sqlite3.connect(dst, detect_types=sqlite3.PARSE_DECLTYPES)
#                 curs = conn.cursor()
#                 try:
#                     curs.execute("SELECT artistsort, albumsort, artist, year, album, application FROM rippinglog ORDER BY ripped DESC")
#                     row = curs.fetchone()
#                     if row:
#                         self.assertEqual(row[0], "Artist 2, The")
#                         self.assertEqual(row[1], "1.20160000.1")
#                         self.assertEqual(row[2], "The Artist 2")
#                         self.assertEqual(row[3], 2016)
#                         self.assertEqual(row[4], "Album 2")
#                         self.assertEqual(row[5], "dBpoweramp 15.1")
#                 finally:
#                     conn.close()
#         if not filobj.closed:
#             filobj.close()
#
#
# class Test14b(unittest.TestCase):
#     """
#     Tester l'insertion d'un enregistrement dans la table `rippinglog` depuis les données exposées par un fichier JSON encodé en UTF-8.
#     Tester individuellement les fonctions `Applications.xml.rippinglog_in` et `Applications.Database.AudioCD.shared.insertfromfile`.
#     """
#
#     def setUp(self):
#         self.file = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tests", "test_rippinglog.json")
#
#     def test_01first(self):
#         filobj = open(self.file)
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(DATABASE))
#             copy(src=DATABASE, dst=dst)
#             self.assertEqual(insertlogfromfile(filobj, db=dst), 3)
#         if not filobj.closed:
#             filobj.close()
#
#     def test_02second(self):
#         filobj = open(self.file)
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(DATABASE))
#             copy(src=DATABASE, dst=dst)
#             if insertlogfromfile(filobj, db=dst):
#                 conn = sqlite3.connect(dst, detect_types=sqlite3.PARSE_DECLTYPES)
#                 curs = conn.cursor()
#                 try:
#                     curs.execute("SELECT artistsort, albumsort, artist, year, album, application FROM rippinglog ORDER BY rowid DESC")
#                     row = curs.fetchone()
#                     if row:
#                         self.assertEqual(row[0], "Artist 3, The")
#                         self.assertEqual(row[1], "1.20150000.1")
#                         self.assertEqual(row[2], "The Artist 3")
#                         self.assertEqual(row[3], 2015)
#                         self.assertEqual(row[4], "Album 3")
#                         self.assertEqual(row[5], "dBpoweramp 15.1")
#                 finally:
#                     conn.close()
#         if not filobj.closed:
#             filobj.close()
#
#
# class Test15(unittest.TestCase):
#     def test_01first(self):
#         self.assertEqual(getrippingapplication(), "dBpoweramp 15.1")
#         self.assertEqual(getrippingapplication(timestamp=1505586912), "dBpoweramp 15.1")
#         self.assertEqual(getrippingapplication(timestamp=1474050912), "dBpoweramp 15.1")
#         self.assertEqual(getrippingapplication(timestamp=1512082800), "dBpoweramp 16.1")
#         self.assertEqual(getrippingapplication(timestamp=1514818800), "dBpoweramp 16.1")
#
#
# class Test16a(unittest.TestCase):
#     """
#     Tester la création d'un album digital depuis les données exposées par un fichier XML encodé en UTF-8.
#     Tester individuellement les fonctions `Applications.xml.digitalalbums_in` et `Applications.Database.DigitalAudioFiles.shared.insertfromfile`.
#     """
#
#     def setUp(self):
#         self.file = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tests", "test_digitalalbums.xml")
#
#     def test_01firstA(self):
#         filobj = open(self.file)
#         self.track = list(digitalalbums_in(filobj))[0]
#         self.assertEqual(self.track.albumid, "A.Artist 1, The.1.20170000.9")
#         self.assertEqual(self.track.artist, "The Artist 1")
#         self.assertEqual(self.track.year, "2017")
#         self.assertEqual(self.track.album, "Album 1")
#         self.assertEqual(self.track.genre, "Hard Rock")
#         self.assertEqual(self.track.discnumber, "1")
#         self.assertEqual(self.track.totaldiscs, "2")
#         self.assertEqual(self.track.label, "")
#         self.assertEqual(self.track.tracknumber, "1")
#         self.assertEqual(self.track.totaltracks, "12")
#         self.assertEqual(self.track.title, "Track #1")
#         self.assertEqual(self.track.live, "N")
#         self.assertEqual(self.track.bootleg, "N")
#         self.assertEqual(self.track.incollection, "N")
#         self.assertEqual(self.track.upc, "1234567890123")
#         self.assertEqual(self.track.encodingyear, dateformat(UTC.localize(datetime.datetime.utcnow()), "$Y"))
#         self.assertEqual(self.track.language, "English")
#         self.assertEqual(self.track.origyear, "2017")
#         if not filobj.closed:
#             filobj.close()
#
#     def test_01firstB(self):
#         filobj = open(self.file)
#         self.track = list(digitalalbums_in(filobj))[-1]
#         self.assertEqual(self.track.albumid, "A.Artist 2, The.1.20160000.9")
#         self.assertEqual(self.track.artist, "The Artist 2")
#         self.assertEqual(self.track.year, "2016")
#         self.assertEqual(self.track.album, "Album 2")
#         self.assertEqual(self.track.genre, "Hard Rock")
#         self.assertEqual(self.track.discnumber, "1")
#         self.assertEqual(self.track.totaldiscs, "1")
#         self.assertEqual(self.track.label, "")
#         self.assertEqual(self.track.tracknumber, "5")
#         self.assertEqual(self.track.totaltracks, "5")
#         self.assertEqual(self.track.title, "Track #5")
#         self.assertEqual(self.track.live, "Y")
#         self.assertEqual(self.track.bootleg, "N")
#         self.assertEqual(self.track.incollection, "N")
#         self.assertEqual(self.track.upc, "1234567890124")
#         self.assertEqual(self.track.encodingyear, dateformat(UTC.localize(datetime.datetime.utcnow()), "$Y"))
#         self.assertEqual(self.track.language, "English")
#         self.assertEqual(self.track.origyear, "2016")
#         self.assertEqual(self.track.disc_created, 1503469361)
#         if not filobj.closed:
#             filobj.close()
#
#     def test_02second(self):
#         filobj = open(self.file)
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(DATABASE))
#             copy(src=DATABASE, dst=dst)
#             self.assertListEqual(insertalbumfromfile(filobj, db=dst), [25, 3, 2])
#         if not filobj.closed:
#             filobj.close()
#
#     def test_03third(self):
#         filobj = open(self.file)
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(DATABASE))
#             copy(src=DATABASE, dst=dst)
#             if list(accumulate(insertalbumfromfile(filobj, db=dst)))[-1]:
#                 conn = sqlite3.connect(dst, detect_types=sqlite3.PARSE_DECLTYPES)
#                 curs = conn.cursor()
#                 try:
#                     curs.execute("SELECT played, count FROM albums WHERE albumid=?", ("A.Artist 1, The.1.20170000.9",))
#                     row = curs.fetchone()
#                     if row:
#                         self.assertEqual(dateformat(UTC.localize(row[0]).astimezone(LOCAL), "$d/$m/$Y $H:$M:$S"), "22/09/2017 23:24:33")
#                         self.assertEqual(dateformat(UTC.localize(row[0]), "$d/$m/$Y $H:$M:$S"), "22/09/2017 21:24:33")
#                         self.assertEqual(row[1], 15)
#                 finally:
#                     conn.close()
#         if not filobj.closed:
#             filobj.close()
#
#     def test_04fourth(self):
#         filobj = open(self.file)
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(DATABASE))
#             copy(src=DATABASE, dst=dst)
#             if list(accumulate(insertalbumfromfile(filobj, db=dst)))[-1]:
#                 conn = sqlite3.connect(dst, detect_types=sqlite3.PARSE_DECLTYPES)
#                 curs = conn.cursor()
#                 try:
#                     curs.execute("SELECT played, count FROM albums WHERE albumid=?", ("A.Artist 2, The.1.20160000.9",))
#                     row = curs.fetchone()
#                     if row:
#                         self.assertIsNone(row[0])
#                         self.assertEqual(row[1], 0)
#                 finally:
#                     conn.close()
#         if not filobj.closed:
#             filobj.close()
#
#     def test_05fifth(self):
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(DATABASE))
#             copy(src=DATABASE, dst=dst)
#             arguments = CD.parser.parse_args(["albums", "insertfromfile", self.file, "--database", dst])
#             self.assertEqual(arguments.function(**{key: val for key, val in vars(arguments).items() if val}), 30)
#             for file in arguments.file:
#                 if not file.closed:
#                     file.close()
#
#
# class Test16b(unittest.TestCase):
#     """
#     Tester la création d'un album digital depuis les données exposées par un fichier JSON encodé en UTF-8.
#     Tester directement la fonction `Applications.Database.DigitalAudioFiles.shared.insertfromfile`.
#     """
#
#     def setUp(self):
#         self.file = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tests", "test_digitalalbums.json")
#
#     def test_01first(self):
#         filobj = open(self.file)
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(DATABASE))
#             copy(src=DATABASE, dst=dst)
#             self.assertListEqual(insertalbumfromfile(filobj, db=dst), [5, 2, 2])
#         if not filobj.closed:
#             filobj.close()
#
#     def test_02second(self):
#         with tempfile.TemporaryDirectory() as directory:
#             dst = os.path.join(directory, os.path.basename(DATABASE))
#             copy(src=DATABASE, dst=dst)
#             arguments = RT.parser.parse_args([self.file, "--database", dst])
#             self.assertListEqual(insertalbumfromfile(arguments.tracks, db=arguments.db), [5, 2, 2])
#             if not arguments.tracks.closed:
#                 arguments.tracks.close()
#
#
# class Test17(unittest.TestCase):
#     """
#     Tester le comportement des attributs optionnels `database` et `test` reçus par le parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
#     """
#
#     def test_01first(self):
#         """
#         L'attribut `test` est reçu : la database utilisée doit être la database de test.
#         """
#         arguments = CD.parser.parse_args("rippinglog select 30 --test".split())
#         self.assertEqual(arguments.table, "rippinglog")
#         self.assertEqual(arguments.statement, "select")
#         self.assertListEqual(arguments.rowid, [30])
#         self.assertTrue(arguments.donotpropagate)
#         self.assertEqual(arguments.template(arguments), "T01")
#         self.assertTrue(arguments.test)
#         self.assertEqual(arguments.db, TESTDATABASE)
#
#     def test_02second(self):
#         """
#         L'attribut `database` est reçu : la database utilisée doit être celle respective à la valeur reçue par le parser.
#         """
#         arguments = CD.parser.parse_args("rippinglog select 30 --database G:\Computing\MyPythonProject\Applications\Tests\database.db".split())
#         self.assertEqual(arguments.table, "rippinglog")
#         self.assertEqual(arguments.statement, "select")
#         self.assertListEqual(arguments.rowid, [30])
#         self.assertTrue(arguments.donotpropagate)
#         self.assertEqual(arguments.template(arguments), "T01")
#         self.assertFalse(arguments.test)
#         self.assertEqual(arguments.db, r"G:\Computing\MyPythonProject\Applications\Tests\database.db")
#
#     def test_03third(self):
#         """
#         Aucun attribut n'est reçu : la database utilisée doit être la database de production.
#         """
#         arguments = CD.parser.parse_args("rippinglog select 30".split())
#         self.assertEqual(arguments.table, "rippinglog")
#         self.assertEqual(arguments.statement, "select")
#         self.assertListEqual(arguments.rowid, [30])
#         self.assertTrue(arguments.donotpropagate)
#         self.assertEqual(arguments.template(arguments), "T01")
#         self.assertFalse(arguments.test)
#         self.assertEqual(arguments.db, DATABASE)


class Test18(unittest.TestCase):
    """
    Tester la création d'un enregistrement dans la table `ripppinglog` à l'aide de la fonction `insertfromfile`.
    """
    logger = logging.getLogger("{0}.Test18".format(__name__))

    def setUp(self):

        # 0. Initializations.
        self.changes, self.expected = 0, [("Artist 1, The", "1.20170000.1"), ("Artist 2, The", "1.20160000.1"), ("Artist 3, The", "1.20150000.1")]

        # 1. Define temporary directory.
        self.tempdir = tempfile.mkdtemp()

        # 2. Define JSON files storing test data.
        inputjson = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tests", "test_rippinglog.json")
        outputjson = os.path.join(self.tempdir, "rippinglog.json")

        # 3. Define temporary DB.
        self.db = os.path.join(self.tempdir, os.path.basename(DATABASE))

        # 4. Copy production DB into temporary folder.
        copy(src=DATABASE, dst=self.tempdir)

        # 5. Count initial records stored into temporary DB.
        self.conn = sqlite3.connect(self.db)
        self.curs = self.conn.cursor()
        self.curs.execute("SELECT count(*) FROM rippinglog")
        self.records = self.curs.fetchone()[0]

        # 6. Prepare a JSON file compliant with `insertfromfile` function signature.
        thatlist = []
        with open(inputjson, encoding="UTF_8") as fr:
            with open(outputjson, "w", encoding="UTF_8") as fw:
                for item in json.load(fr):
                    item.insert(0, self.db)
                    thatlist.append(item)
                json.dump(thatlist, fw, ensure_ascii=False, indent=4)
        with open(outputjson, encoding="UTF_8") as fr:
            for item in json.load(fr):
                self.logger.debug(item)

        # 7. Insert records using `insertfromfile` function.
        with open(outputjson, encoding="UTF_8") as fr:
            self.changes = insertlogfromfile(fr)

    def tearDown(self):
        self.conn.close()
        rmtree(self.tempdir)

    def test01_first(self):
        """
        1. Test number of changes.
        """
        self.assertEqual(self.changes, 3)

    def test02_second(self):
        """
        2. Test that temporary database was changed.
        """
        self.curs.execute("SELECT count(*) FROM rippinglog")
        records = self.curs.fetchone()[0]
        self.assertEqual(records - self.records, 3)

    def test03_third(self):
        """
        3. Test that production database remains unchanged.
        """
        conn = sqlite3.connect(DATABASE)
        curs = conn.cursor()
        curs.execute("SELECT count(*) FROM rippinglog")
        records = curs.fetchone()[0]
        conn.close()
        self.assertEqual(records - self.records, 0)

    def test04_fourth(self):
        """
        4. Test that inserted records are the expected ones.
        """
        self.curs.execute("SELECT artistsort, albumsort FROM rippinglog ORDER BY rowid DESC LIMIT 3")
        extracted = sorted(sorted(self.curs.fetchall(), key=itemgetter(1)), key=itemgetter(0))
        for i in range(2):
            for j in range(2):
                with self.subTest(item=extracted[i][j]):
                    self.assertEqual(extracted[i][j], self.expected[i][j])
