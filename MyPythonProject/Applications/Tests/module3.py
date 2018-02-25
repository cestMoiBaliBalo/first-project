# -*- coding: utf-8 -*-
import json
import logging.config
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime
from itertools import cycle, groupby, repeat
from operator import itemgetter
from shutil import copy, rmtree

import yaml

import AudioCD.Interface as CD
# import AudioCD.RippedTracks as RT
# from .. import shared
from Applications.Database.AudioCD.shared import insertfromfile as insertlogfromfile
# from ..Database.DigitalAudioFiles.shared import deletealbum, insertfromfile as insertalbumfromfile, updatealbum
from Applications.shared import DATABASE, LOCAL, UTC

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# ========
# Classes.
# ========
class Test01(unittest.TestCase):
    """
    Tester la restitution d'un enregistrement de la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """
    logger = logging.getLogger("{0}.Test01".format(__name__))
    rowid = 28

    def setUp(self):
        self.artistsort, self.albumsort, self.artist, self.year, self.album, self.genre, self.upc = None, None, None, None, None, None, None

        # 1. Store data respective to the row ID.
        conn = sqlite3.connect(DATABASE)
        curs = conn.cursor()
        curs.execute("SELECT artistsort, albumsort, artist, year, album, genre, upc FROM rippinglog WHERE rowid=?", (self.rowid,))
        try:
            self.artistsort, self.albumsort, self.artist, self.year, self.album, self.genre, self.upc = curs.fetchone()
        except TypeError:
            pass
        finally:
            conn.close()

        # 2. Parse arguments.
        self.arguments = CD.parser.parse_args("rippinglog select {0}".format(self.rowid).split())

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "rippinglog")
        self.assertEqual(self.arguments.statement, "select")
        self.assertListEqual(self.arguments.rowid, [self.rowid])
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
        self.assertEqual(row.rowid, self.rowid)
        self.assertEqual(row.artistsort, self.artistsort)
        self.assertEqual(row.albumsort, self.albumsort)
        self.assertEqual(row.artist, self.artist)
        self.assertEqual(row.year, self.year)
        self.assertEqual(row.album, self.album)
        self.assertEqual(row.genre, self.genre)
        self.assertEqual(row.upc, self.upc)


class Test02(unittest.TestCase):
    """
    Tester la restitution d'un enregistrement de la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """
    logger = logging.getLogger("{0}.Test02".format(__name__))
    rowid = 28

    def setUp(self):
        self.artistsort, self.albumsort, self.artist, self.year, self.album, self.genre, self.upc = None, None, None, None, None, None, None

        # 1. Store data respective to the row ID.
        conn = sqlite3.connect(DATABASE)
        curs = conn.cursor()
        curs.execute("SELECT artistsort, albumsort, artist, year, album, genre, upc FROM rippinglog WHERE rowid=?", (self.rowid,))
        try:
            self.artistsort, self.albumsort, self.artist, self.year, self.album, self.genre, self.upc = curs.fetchone()
        except TypeError:
            pass
        finally:
            conn.close()

        # 2. Parse arguments.
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
        self.assertEqual(row.rowid, self.rowid)
        self.assertEqual(row.artistsort, self.artistsort)
        self.assertEqual(row.albumsort, self.albumsort)
        self.assertEqual(row.artist, self.artist)
        self.assertEqual(row.year, self.year)
        self.assertEqual(row.album, self.album)
        self.assertEqual(row.genre, self.genre)
        self.assertEqual(row.upc, self.upc)

    def test_03third(self):
        """
        3. Tester la restitution à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        row = self.arguments.function(ns=self.arguments)[-1]
        self.logger.debug(row)
        self.assertEqual(row.rowid, 33)
        self.assertEqual(row.artistsort, "Fleetwood Mac")
        self.assertEqual(row.albumsort, "1.19920000.1")
        self.assertEqual(row.artist, "Fleetwood Mac")
        self.assertEqual(row.year, 1992)
        self.assertEqual(row.album, "25 Years: The Chain (3/4)")
        self.assertEqual(row.genre, "Rock")
        self.assertEqual(row.upc, "081227973025")


class Test03(unittest.TestCase):
    """
    Tester la restitution d'un enregistrement de la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """
    logger = logging.getLogger("{0}.Test03".format(__name__))

    def setUp(self):
        self.arguments = CD.parser.parse_args(["rippinglog", "select", "28", "31", "32", "33", "--orderby", "artistsort", " albumsort", "--loglevel", "DEBUG"])

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
        self.assertEqual(self.arguments.loglevel, "DEBUG")

    def test_02second(self):
        """
        2. Tester la restitution à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        row = self.arguments.function(ns=self.arguments)[0]
        self.logger.debug(row)
        self.assertEqual(row.rowid, 32)
        self.assertEqual(row.artistsort, "Black Sabbath")
        self.assertEqual(row.albumsort, "1.19710000.1")
        self.assertEqual(row.artist, "Black Sabbath")
        self.assertEqual(row.year, 1971)
        self.assertEqual(row.album, "Master of Reality")
        self.assertEqual(row.genre, "Hard Rock")
        self.assertEqual(row.upc, "5017615830323")

    def test_03third(self):
        """
        3. Tester la restitution à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        row = self.arguments.function(ns=self.arguments)[-1]
        self.logger.debug(row)
        self.assertEqual(row.rowid, 31)
        self.assertEqual(row.artistsort, "Kiss")
        self.assertEqual(row.albumsort, "1.19760000.2")
        self.assertEqual(row.artist, "Kiss")
        self.assertEqual(row.year, 1976)
        self.assertEqual(row.album, "Rock and Roll over")
        self.assertEqual(row.genre, "Hard Rock")
        self.assertEqual(row.upc, "042282415028")


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
        self.assertEqual(row.rowid, 31)
        self.assertEqual(row.artistsort, "Kiss")
        self.assertEqual(row.albumsort, "1.19760000.2")
        self.assertEqual(row.artist, "Kiss")
        self.assertEqual(row.year, 1976)
        self.assertEqual(row.album, "Rock and Roll over")
        self.assertEqual(row.genre, "Hard Rock")
        self.assertEqual(row.upc, "042282415028")

    def test_03third(self):
        """
        3. Tester la restitution à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        row = self.arguments.function(ns=self.arguments)[-1]
        self.logger.debug(row)
        self.assertEqual(row.rowid, 28)
        self.assertEqual(row.artistsort, "Black Sabbath")
        self.assertEqual(row.albumsort, "1.19760000.1")
        self.assertEqual(row.artist, "Black Sabbath")
        self.assertEqual(row.year, 1976)
        self.assertEqual(row.album, "Technical Ecstasy")
        self.assertEqual(row.genre, "Hard Rock")
        self.assertEqual(row.upc, "5017615832822")


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
        self.assertEqual(row.rowid, 31)
        self.assertEqual(row.artistsort, "Kiss")
        self.assertEqual(row.albumsort, "1.19760000.2")
        self.assertEqual(row.artist, "Kiss")
        self.assertEqual(row.year, 1976)
        self.assertEqual(row.album, "Rock and Roll over")
        self.assertEqual(row.genre, "Hard Rock")
        self.assertEqual(row.upc, "042282415028")

    def test_03third(self):
        """
        3. Tester la restitution à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        row = self.arguments.function(ns=self.arguments)[-1]
        self.logger.debug(row)
        self.assertEqual(row.rowid, 32)
        self.assertEqual(row.artistsort, "Black Sabbath")
        self.assertEqual(row.albumsort, "1.19710000.1")
        self.assertEqual(row.artist, "Black Sabbath")
        self.assertEqual(row.year, 1971)
        self.assertEqual(row.album, "Master of Reality")
        self.assertEqual(row.genre, "Hard Rock")
        self.assertEqual(row.upc, "5017615830323")


class Test06(unittest.TestCase):
    """
    Tester la mise à jour d'un enregistrement de la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """
    logger = logging.getLogger("{0}.Test06".format(__name__))
    upc = "9999999999999"
    ripped = 1504122358
    genre = "Pop"
    rowid = 28

    def setUp(self):
        # 1. Define temporary directory.
        self.tempdir = tempfile.mkdtemp()

        # 2. Define temporary DB.
        self.db = os.path.join(self.tempdir, os.path.basename(DATABASE))

        # 3. Copy production DB into temporary folder.
        copy(src=DATABASE, dst=self.tempdir)

        # 4. Log both `genre` and `UPC` stored into temporary DB.
        self.conn = sqlite3.connect(self.db, detect_types=sqlite3.PARSE_DECLTYPES)
        self.curs = self.conn.cursor()
        self.curs.execute("SELECT genre, upc, ripped, count(*) FROM rippinglog WHERE rowid=?", (self.rowid,))
        self.prd_genre, self.prd_upc, self.prd_ripped, self.count = self.curs.fetchone()
        self.logger.debug(self.prd_genre)
        self.logger.debug(self.prd_upc)
        self.logger.debug(UTC.localize(self.prd_ripped).astimezone(LOCAL).strftime("%d/%m/%Y %H:%M:%S %Z (UTC%z)"))
        self.logger.debug(self.count)

        # 5. Parse arguments.
        self.arguments = CD.parser.parse_args("rippinglog update {1} --genre {3} --upc {2} --ripped {4} --database {0}".format(self.db, self.rowid, self.upc, self.genre, self.ripped).split())

    def tearDown(self):
        self.conn.close()
        rmtree(self.tempdir)

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "rippinglog")
        self.assertEqual(self.arguments.statement, "update")
        self.assertTrue(self.arguments.donotpropagate)
        self.assertListEqual(self.arguments.rowid, [self.rowid])
        self.assertEqual(self.arguments.genre, self.genre)
        self.assertEqual(self.arguments.upc, self.upc)
        self.assertEqual(self.arguments.ripped, self.ripped)
        self.assertIsNone(self.arguments.template(self.arguments))
        self.assertFalse(self.arguments.test)
        self.assertEqual(self.arguments.db, self.db)
        self.assertEqual(self.arguments.loglevel, "INFO")

    def test_02second(self):
        """
        2. Tester la mise à jour à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        self.assertEqual(self.arguments.function(ns=self.arguments), self.count)

    def test_03third(self):
        """
        3. Test that only temporary database was changed.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        self.curs.execute("SELECT genre, upc, ripped FROM rippinglog WHERE rowid=?", (self.rowid,))
        genre, upc, ripped = self.curs.fetchone()
        self.logger.debug(genre)
        self.logger.debug(upc)
        self.logger.debug(LOCAL.localize(ripped).strftime("%d/%m/%Y %H:%M:%S %Z (UTC%z)"))
        self.assertEqual(genre, self.genre)
        self.assertEqual(upc, self.upc)
        self.assertEqual(LOCAL.localize(ripped), LOCAL.localize(datetime.fromtimestamp(self.ripped)))

    def test_04fourth(self):
        """
        4. Test that production database remains unchanged.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        conn = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        curs = conn.cursor()
        curs.execute("SELECT genre, upc, ripped FROM rippinglog WHERE rowid=?", (self.rowid,))
        genre, upc, ripped = curs.fetchone()
        conn.close()
        self.logger.debug(genre)
        self.logger.debug(upc)
        self.logger.debug(LOCAL.localize(ripped).strftime("%d/%m/%Y %H:%M:%S %Z (UTC%z)"))
        self.assertEqual(genre, self.prd_genre)
        self.assertEqual(upc, self.prd_upc)
        self.assertEqual(ripped, self.prd_ripped)


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
        self.conn = sqlite3.connect(self.db)
        self.curs = self.conn.cursor()
        self.curs.execute("SELECT count(*) FROM rippinglog WHERE rowid=?", (self.rowid,))
        self.count = self.curs.fetchone()[0]
        self.logger.debug(self.count)

        # 5. Parse arguments.
        self.arguments = CD.parser.parse_args("rippinglog delete {1} --database {0} --loglevel DEBUG".format(self.db, self.rowid).split())

    def tearDown(self):
        self.conn.close()
        rmtree(self.tempdir)

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "rippinglog")
        self.assertEqual(self.arguments.statement, "delete")
        self.assertListEqual(self.arguments.rowid, [self.rowid])
        self.assertTrue(self.arguments.donotpropagate)
        self.assertIsNone(self.arguments.template(self.arguments))
        self.assertFalse(self.arguments.test)
        self.assertEqual(self.arguments.db, self.db)
        self.assertEqual(self.arguments.loglevel, "DEBUG")

    def test_02second(self):
        """
        2. Tester la suppression à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        self.assertEqual(self.arguments.function(ns=self.arguments), self.count)

    def test_03third(self):
        """
        3. Test that only temporary database was changed.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        self.curs.execute("SELECT count(*) FROM rippinglog WHERE rowid=?", (self.rowid,))
        count = self.curs.fetchone()[0]
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
        self.assertEqual(count, self.count)


class Test08(unittest.TestCase):
    """
    Tester la restitution d'un enregistrement de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """
    logger = logging.getLogger("{0}.Test08".format(__name__))
    rowid = 30

    def setUp(self):
        self.arguments = CD.parser.parse_args("albums select {0}".format(self.rowid).split())

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "albums")
        self.assertEqual(self.arguments.statement, "select")
        self.assertListEqual(self.arguments.rowid, [self.rowid])
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
        self.assertEqual(row.rowid, self.rowid)
        self.assertEqual(row.albumid, "D.Dire Straits.1.19800000.1")
        self.assertEqual(row.artist, "Dire Straits")
        self.assertEqual(row.year, 1980)
        self.assertEqual(row.album, "Making Movies")
        self.assertEqual(row.genre, "Rock")
        self.assertFalse(row.live)
        self.assertFalse(row.bootleg)
        self.assertTrue(row.incollection)
        self.assertEqual(row.language, "English")
        self.assertEqual(row.played, 4)


class Test09(unittest.TestCase):
    """
    Tester la suppression d'un enregistrement de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    Sans propagation à `discs` et `tracks`.
    """
    logger = logging.getLogger("{0}.Test09".format(__name__))
    rowid = 30

    def setUp(self):
        # 1. Define temporary directory.
        self.tempdir = tempfile.mkdtemp()

        # 2. Define temporary DB.
        self.db = os.path.join(self.tempdir, os.path.basename(DATABASE))

        # 3. Copy production DB into temporary folder.
        copy(src=DATABASE, dst=self.tempdir)

        # 4. Count initial records stored into temporary DB.
        self.conn = sqlite3.connect(self.db)
        self.curs = self.conn.cursor()
        self.curs.execute("SELECT albumid, count(*) FROM albums WHERE rowid=?", (self.rowid,))
        self.albumid, self.count = self.curs.fetchone()
        self.logger.debug(self.albumid)
        self.logger.debug(self.count)

        # 5. Store both `discs` and `tracks` respective rows IDs.
        conn = sqlite3.connect(self.db)
        conn.row_factory = sqlite3.Row
        self.discs = [row["rowid"] for row in conn.execute("SELECT rowid FROM discs WHERE albumid=? ORDER BY rowid", (self.albumid,))]
        self.tracks = [row["rowid"] for row in conn.execute("SELECT rowid FROM tracks WHERE albumid=? ORDER BY rowid", (self.albumid,))]
        conn.close()

        # 6. Parse arguments.
        self.arguments = CD.parser.parse_args("albums delete {0} --donotpropagate --database {1} --loglevel DEBUG".format(self.rowid, self.db).split())

    def tearDown(self):
        self.conn.close()
        rmtree(self.tempdir)

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "albums")
        self.assertEqual(self.arguments.statement, "delete")
        self.assertListEqual(self.arguments.rowid, [self.rowid])
        self.assertTrue(self.arguments.donotpropagate)
        self.assertIsNone(self.arguments.template(self.arguments))
        self.assertFalse(self.arguments.test)
        self.assertEqual(self.arguments.db, self.db)
        self.assertEqual(self.arguments.loglevel, "DEBUG")

    def test_02second(self):
        """
        2. Tester la suppression à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        self.assertEqual(self.arguments.function(ns=self.arguments), self.count)

    def test_03third(self):
        """
        3. Test that only temporary database was changed.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        self.curs.execute("SELECT count(*) FROM albums WHERE rowid=?", (self.rowid,))
        count = self.curs.fetchone()[0]
        self.logger.debug(count)
        self.assertEqual(count, 0)

    def test_04fourth(self):
        """
        4. Test that production database remains unchanged.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        conn = sqlite3.connect(DATABASE)
        curs = conn.cursor()
        curs.execute("SELECT count(*) FROM albums WHERE rowid=?", (self.rowid,))
        count = curs.fetchone()[0]
        conn.close()
        self.logger.debug(count)
        self.assertEqual(count, self.count)

    def test_05fifth(self):
        """
        5. Test that `self.db`.`discs` table remains unchanged.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        conn = sqlite3.connect(self.db)
        conn.row_factory = sqlite3.Row
        discs = [row["rowid"] for row in conn.execute("SELECT rowid FROM discs WHERE albumid=? ORDER BY rowid", (self.albumid,))]
        conn.close()
        self.assertListEqual(discs, self.discs)

    def test_06sixth(self):
        """
        6. Test that `self.db`.`tracks` table remains unchanged.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        conn = sqlite3.connect(self.db)
        conn.row_factory = sqlite3.Row
        tracks = [row["rowid"] for row in conn.execute("SELECT rowid FROM tracks WHERE albumid=? ORDER BY rowid", (self.albumid,))]
        conn.close()
        self.assertListEqual(tracks, self.tracks)

    def test_07seventh(self):
        """
        7. Test that `DATABASE`.`discs` table remains unchanged.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        discs = [row["rowid"] for row in conn.execute("SELECT rowid FROM discs WHERE albumid=? ORDER BY rowid", (self.albumid,))]
        conn.close()
        self.assertListEqual(discs, self.discs)

    def test_08eighth(self):
        """
        8. Test that `DATABASE`.`tracks` table remains unchanged.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        tracks = [row["rowid"] for row in conn.execute("SELECT rowid FROM tracks WHERE albumid=? ORDER BY rowid", (self.albumid,))]
        conn.close()
        self.assertListEqual(tracks, self.tracks)


class Test10(unittest.TestCase):
    """
    Tester la suppression d'un enregistrement de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    Avec propagation à `discs` et `tracks`.
    """
    logger = logging.getLogger("{0}.Test10".format(__name__))
    rowid = 30

    def setUp(self):
        # 1. Define temporary directory.
        self.tempdir = tempfile.mkdtemp()

        # 2. Define temporary DB.
        self.db = os.path.join(self.tempdir, os.path.basename(DATABASE))

        # 3. Copy production DB into temporary folder.
        copy(src=DATABASE, dst=self.tempdir)

        # 4. Count initial records stored into temporary DB.
        self.conn = sqlite3.connect(self.db)
        self.curs = self.conn.cursor()

        # `albums` table.
        self.curs.execute("SELECT albumid, count(*) FROM albums WHERE rowid=?", (self.rowid,))
        self.albumid, self.acount = self.curs.fetchone()
        self.logger.debug(self.albumid)
        self.logger.debug(self.acount)

        # `discs` table.
        self.curs.execute("SELECT count(*) FROM discs WHERE albumid=?", (self.albumid,))
        self.dcount = self.curs.fetchone()[0]
        self.logger.debug(self.dcount)

        # `tracks` table.
        self.curs.execute("SELECT count(*) FROM tracks WHERE albumid=?", (self.albumid,))
        self.tcount = self.curs.fetchone()[0]
        self.logger.debug(self.tcount)

        # 5. Store both `discs` and `tracks` respective rows IDs.
        conn = sqlite3.connect(self.db)
        conn.row_factory = sqlite3.Row
        self.discs = [row["rowid"] for row in conn.execute("SELECT rowid FROM discs WHERE albumid=? ORDER BY rowid", (self.albumid,))]
        self.tracks = [row["rowid"] for row in conn.execute("SELECT rowid FROM tracks WHERE albumid=? ORDER BY rowid", (self.albumid,))]
        conn.close()

        # 6. Parse arguments.
        self.arguments = CD.parser.parse_args("albums delete {0} --database {1} --loglevel DEBUG".format(self.rowid, self.db).split())

    def tearDown(self):
        self.conn.close()
        rmtree(self.tempdir)

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "albums")
        self.assertEqual(self.arguments.statement, "delete")
        self.assertListEqual(self.arguments.rowid, [self.rowid])
        self.assertFalse(self.arguments.donotpropagate)
        self.assertEqual(self.arguments.template(self.arguments), "T02")
        self.assertFalse(self.arguments.test)
        self.assertEqual(self.arguments.db, self.db)
        self.assertEqual(self.arguments.loglevel, "DEBUG")

    def test_02second(self):
        """
        2. Tester la suppression à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        self.assertListEqual(self.arguments.function(ns=self.arguments), [(self.albumid, self.acount, self.dcount, self.tcount)])

    def test_03third(self):
        """
        3. Test that only temporary database was changed.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        self.curs.execute("SELECT count(*) FROM albums WHERE rowid=?", (self.rowid,))
        count = self.curs.fetchone()[0]
        self.logger.debug(count)
        self.assertEqual(count, 0)

    def test_04fourth(self):
        """
        4. Test that production database remains unchanged.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        conn = sqlite3.connect(DATABASE)
        curs = conn.cursor()
        curs.execute("SELECT count(*) FROM albums WHERE rowid=?", (self.rowid,))
        count = curs.fetchone()[0]
        conn.close()
        self.logger.debug(count)
        self.assertEqual(count, self.acount)

    def test_05fifth(self):
        """
        5. Test that `self.db`.`discs` table was changed too.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        conn = sqlite3.connect(self.db)
        conn.row_factory = sqlite3.Row
        discs = [row["rowid"] for row in conn.execute("SELECT rowid FROM discs WHERE albumid=? ORDER BY rowid", (self.albumid,))]
        conn.close()
        self.assertListEqual(discs, [])

    def test_06sixth(self):
        """
        6. Test that `self.db`.`tracks` table was changed too.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        conn = sqlite3.connect(self.db)
        conn.row_factory = sqlite3.Row
        tracks = [row["rowid"] for row in conn.execute("SELECT rowid FROM tracks WHERE albumid=? ORDER BY rowid", (self.albumid,))]
        conn.close()
        self.assertListEqual(tracks, [])

    def test_07seventh(self):
        """
        7. Test that `DATABASE`.`discs` table remains unchanged.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        discs = [row["rowid"] for row in conn.execute("SELECT rowid FROM discs WHERE albumid=? ORDER BY rowid", (self.albumid,))]
        conn.close()
        self.assertListEqual(discs, self.discs)

    def test_08eighth(self):
        """
        8. Test that `DATABASE`.tracks` table remains unchanged.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        tracks = [row["rowid"] for row in conn.execute("SELECT rowid FROM tracks WHERE albumid=? ORDER BY rowid", (self.albumid,))]
        conn.close()
        self.assertListEqual(tracks, self.tracks)


class Test11(unittest.TestCase):
    """
    Tester la mise à jour d'un enregistrement de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    Album unique key is not updated.
    """
    logger = logging.getLogger("{0}.Test11".format(__name__))
    rowid = 30

    def setUp(self):
        # 1. Define temporary directory.
        self.tempdir = tempfile.mkdtemp()

        # 2. Define temporary DB.
        self.db = os.path.join(self.tempdir, os.path.basename(DATABASE))

        # 3. Copy production DB into temporary folder.
        copy(src=DATABASE, dst=self.tempdir)

        # 4. Count initial records stored into temporary DB.
        self.conn = sqlite3.connect(self.db)
        self.curs = self.conn.cursor()
        self.curs.execute("SELECT albumid, album, genre, live, bootleg, incollection, upc, count(*) FROM albums WHERE rowid=?", (self.rowid,))
        self.albumid, self.album, self.genre, self.live, self.bootleg, self.incollection, self.upc, self.records_count = self.curs.fetchone()
        self.logger.debug(self.albumid)
        self.logger.debug(self.album)
        self.logger.debug(self.genre)
        self.logger.debug(self.live)
        self.logger.debug(self.bootleg)
        self.logger.debug(self.incollection)
        self.logger.debug(self.upc)
        self.logger.debug(self.records_count)

        # 5. Parse arguments.
        self.arguments = CD.parser.parse_args(
                ["albums", "update", "{0}".format(self.rowid), "--genre", "Rock", "--upc", "9999999999999", "--album", "Communiqué", "--live", "Y", "--bootleg", "Y", "--incollection", "N", "--database",
                 self.db])

    def tearDown(self):
        self.conn.close()
        rmtree(self.tempdir)

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "albums")
        self.assertEqual(self.arguments.statement, "update")
        self.assertTrue(self.arguments.donotpropagate)
        self.assertListEqual(self.arguments.rowid, [self.rowid])
        self.assertEqual(self.arguments.album, "Communiqué")
        self.assertEqual(self.arguments.genre, "Rock")
        self.assertTrue(self.arguments.live.bool)
        self.assertTrue(self.arguments.bootleg.bool)
        self.assertFalse(self.arguments.incollection.bool)
        self.assertEqual(self.arguments.upc, "9999999999999")
        self.assertEqual(self.arguments.template(self.arguments), "T02")
        self.assertFalse(self.arguments.test)
        self.assertEqual(self.arguments.db, self.db)
        self.assertEqual(self.arguments.loglevel, "INFO")

    def test_02second(self):
        """
        2. Tester le nombre total de changements.
        """
        self.assertListEqual(self.arguments.function(ns=self.arguments), [(self.albumid, self.records_count, 0, 0)])

    def test_03third(self):
        """
        3. Test that only temporary database was changed.
        """
        album, genre, live, bootleg, incollection, upc = None, None, None, None, None, None
        self.logger.debug(self.arguments.function(ns=self.arguments))
        self.curs.execute("SELECT album, genre, live, bootleg, incollection, upc FROM albums WHERE rowid=?", (self.rowid,))
        try:
            album, genre, live, bootleg, incollection, upc = self.curs.fetchone()
        except TypeError:
            pass
        finally:
            self.assertEqual(album, self.arguments.album)
            self.assertEqual(genre, self.arguments.genre)
            self.assertTrue(live)
            self.assertTrue(bootleg)
            self.assertFalse(incollection)
            self.assertEqual(upc, self.arguments.upc)

    def test_04fourth(self):
        """
        4. Test that production database remains unchanged.
        """
        album, genre, live, bootleg, incollection, upc = None, None, None, None, None, None
        self.logger.debug(self.arguments.function(ns=self.arguments))
        conn = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        curs = conn.cursor()
        curs.execute("SELECT album, genre, live, bootleg, incollection, upc FROM albums WHERE rowid=?", (self.rowid,))
        try:
            album, genre, live, bootleg, incollection, upc = curs.fetchone()
        except TypeError:
            pass
        finally:
            self.assertEqual(album, "Making Movies")
            self.assertEqual(genre, "Rock")
            self.assertFalse(live)
            self.assertFalse(bootleg)
            self.assertTrue(incollection)
            self.assertEqual(upc, "042280005023")


class Test12(unittest.TestCase):
    """
    Tester la mise à jour du nombre de lectures et de la date de dernière lecture de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """
    logger = logging.getLogger("{0}.Test12".format(__name__))
    utcplayed = 1505040486
    countplayed = 100
    rowid = 30

    def setUp(self):
        # 1. Define temporary directory.
        self.tempdir = tempfile.mkdtemp()

        # 2. Define temporary DB.
        self.db = os.path.join(self.tempdir, os.path.basename(DATABASE))

        # 3. Copy production DB into temporary folder.
        copy(src=DATABASE, dst=self.tempdir)

        # 4. Count initial records stored into temporary DB.
        self.conn = sqlite3.connect(self.db, detect_types=sqlite3.PARSE_DECLTYPES)
        self.curs = self.conn.cursor()
        self.curs.execute("SELECT albumid, utc_played, played, count(*) FROM albums WHERE rowid=?", (self.rowid,))
        self.albumid, self.utc_played, self.played, self.records_count = self.curs.fetchone()
        self.logger.debug(self.albumid)
        self.logger.debug(self.utc_played)
        self.logger.debug(self.played)
        self.logger.debug(self.records_count)

        # 5. Parse arguments.
        self.arguments = CD.parser.parse_args(
                ["albums", "update", "{0}".format(self.rowid), "--played", "{0}".format(self.countplayed), "--utc_played", "{0}".format(self.utcplayed), "--database", self.db])

    def tearDown(self):
        self.conn.close()
        rmtree(self.tempdir)

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "albums")
        self.assertEqual(self.arguments.statement, "update")
        self.assertTrue(self.arguments.donotpropagate)
        self.assertListEqual(self.arguments.rowid, [self.rowid])
        self.assertEqual(self.arguments.played, self.countplayed)
        self.assertEqual(int(self.arguments.utc_played), self.utcplayed)
        self.assertEqual(self.arguments.template(self.arguments), "T02")
        self.assertFalse(self.arguments.test)
        self.assertEqual(self.arguments.db, self.db)
        self.assertEqual(self.arguments.loglevel, "INFO")

    def test_02second(self):
        """
        2. Tester le nombre total de changements.
        """
        self.assertListEqual(self.arguments.function(ns=self.arguments), [(self.albumid, self.records_count, 0, 0)])

    def test_03third(self):
        """
        3. Test that only temporary database was changed.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        self.curs.execute("SELECT utc_played, played FROM albums WHERE rowid=?", (self.rowid,))
        utc_played, played = self.curs.fetchone()
        self.logger.debug(utc_played)
        self.logger.debug(played)
        self.assertEqual(utc_played, datetime.utcfromtimestamp(self.utcplayed))
        self.assertEqual(played, self.countplayed)

    def test_04fourth(self):
        """
        4. Test that production database remains unchanged.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        conn = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        curs = conn.cursor()
        curs.execute("SELECT utc_played, played FROM albums WHERE rowid=?", (self.rowid,))
        utc_played, played = curs.fetchone()
        conn.close()
        self.logger.debug(utc_played)
        self.logger.debug(played)
        self.assertEqual(utc_played, self.utc_played)
        self.assertEqual(played, self.played)


class Test13(unittest.TestCase):
    """
    Tester la restitution d'un enregistrement de la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """
    logger = logging.getLogger("{0}.Test13".format(__name__))

    def setUp(self):
        self.arguments = CD.parser.parse_args(["rippinglog", "select", "--genre", "Hard Rock", "Heavy Metal"])
        conn = sqlite3.connect(DATABASE)
        curs = conn.cursor()
        curs.execute("SELECT count(*) FROM rippinglog WHERE lower(genre) IN ('hard rock', 'heavy metal')")
        self.count = curs.fetchone()[0]
        conn.close()
        self.logger.debug(self.count)

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "rippinglog")
        self.assertEqual(self.arguments.statement, "select")
        self.assertListEqual(self.arguments.genre, ["Hard Rock", "Heavy Metal"])
        self.assertTrue(self.arguments.donotpropagate)
        self.assertEqual(self.arguments.template(self.arguments), "T01")
        self.assertFalse(self.arguments.test)
        self.assertEqual(self.arguments.db, DATABASE)
        self.assertEqual(self.arguments.loglevel, "INFO")

    def test_02second(self):
        """
        2. Tester la restitution à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        self.assertEqual(len(self.arguments.function(ns=self.arguments)), self.count)


class Test14(unittest.TestCase):
    """
    Tester la restitution d'un enregistrement de la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """
    logger = logging.getLogger("{0}.Test14".format(__name__))

    def setUp(self):
        self.arguments = CD.parser.parse_args(["rippinglog", "select", "--artistsort", "Springsteen", "Minds"])
        conn = sqlite3.connect(DATABASE)
        curs = conn.cursor()
        curs.execute("SELECT count(*) FROM rippinglog WHERE lower(artistsort) LIKE '%springsteen%' OR lower(artistsort) LIKE '%minds%'")
        self.count = curs.fetchone()[0]
        conn.close()
        self.logger.debug(self.count)

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "rippinglog")
        self.assertEqual(self.arguments.statement, "select")
        self.assertListEqual(self.arguments.artistsort, ["Springsteen", "Minds"])
        self.assertTrue(self.arguments.donotpropagate)
        self.assertEqual(self.arguments.template(self.arguments), "T01")
        self.assertFalse(self.arguments.test)
        self.assertEqual(self.arguments.db, DATABASE)
        self.assertEqual(self.arguments.loglevel, "INFO")

    def test_02second(self):
        """
        2. Tester la restitution à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        self.assertEqual(len(self.arguments.function(ns=self.arguments)), self.count)


class Test15(unittest.TestCase):
    """
    Tester la restitution d'un enregistrement de la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """
    logger = logging.getLogger("{0}.Test15".format(__name__))

    def setUp(self):
        self.arguments = CD.parser.parse_args(["rippinglog", "select", "--year", "1977", "1985", "1987"])
        conn = sqlite3.connect(DATABASE)
        curs = conn.cursor()
        curs.execute("SELECT count(*) FROM rippinglog WHERE year IN (1977, 1985, 1987)")
        self.count = curs.fetchone()[0]
        conn.close()
        self.logger.debug(self.count)

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "rippinglog")
        self.assertEqual(self.arguments.statement, "select")
        self.assertListEqual(self.arguments.year, [1977, 1985, 1987])
        self.assertTrue(self.arguments.donotpropagate)
        self.assertEqual(self.arguments.template(self.arguments), "T01")
        self.assertFalse(self.arguments.test)
        self.assertEqual(self.arguments.db, DATABASE)
        self.assertEqual(self.arguments.loglevel, "INFO")

    def test_02second(self):
        """
        2. Tester la restitution à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        self.assertEqual(len(self.arguments.function(ns=self.arguments)), self.count)


class Test16(unittest.TestCase):
    """
    Tester la restitution d'un enregistrement de la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """
    logger = logging.getLogger("{0}.Test16".format(__name__))

    def setUp(self):
        self.arguments = CD.parser.parse_args(["rippinglog", "select", "--year", "1977", "1985", "1987", "--genre", "Rock"])
        conn = sqlite3.connect(DATABASE)
        curs = conn.cursor()
        curs.execute("SELECT count(*) FROM rippinglog WHERE year IN (1977, 1985, 1987) AND lower(genre) IN ('rock')")
        self.count = curs.fetchone()[0]
        conn.close()
        self.logger.debug(self.count)

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "rippinglog")
        self.assertEqual(self.arguments.statement, "select")
        self.assertListEqual(self.arguments.year, [1977, 1985, 1987])
        self.assertListEqual(self.arguments.genre, ["Rock"])
        self.assertTrue(self.arguments.donotpropagate)
        self.assertEqual(self.arguments.template(self.arguments), "T01")
        self.assertFalse(self.arguments.test)
        self.assertEqual(self.arguments.db, DATABASE)
        self.assertEqual(self.arguments.loglevel, "INFO")

    def test_02second(self):
        """
        2. Tester la restitution à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        self.assertEqual(len(self.arguments.function(ns=self.arguments)), self.count)


class Test17(unittest.TestCase):
    """
    Tester l'incrémentation du compteur de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """
    logger = logging.getLogger("{0}.Test17".format(__name__))
    rowid = 10

    def setUp(self):
        # 1. Define temporary directory.
        self.tempdir = tempfile.mkdtemp()

        # 2. Define temporary DB.
        self.db = os.path.join(self.tempdir, os.path.basename(DATABASE))

        # 3. Copy production DB into temporary folder.
        copy(src=DATABASE, dst=self.tempdir)

        # 4. Count initial records stored into temporary DB.
        self.conn = sqlite3.connect(self.db, detect_types=sqlite3.PARSE_DECLTYPES)
        self.curs = self.conn.cursor()
        self.curs.execute("SELECT albumid, played, count(*) FROM albums WHERE rowid=?", (self.rowid,))
        self.albumid, self.played, self.count = self.curs.fetchone()
        self.logger.debug(self.albumid)
        self.logger.debug(self.played)
        self.logger.debug(self.count)

        # 5. Parse arguments.
        self.arguments = CD.parser.parse_args(["albums", "update", "{0}".format(self.rowid), "--icount", "--database", self.db])

    def tearDown(self):
        self.conn.close()
        rmtree(self.tempdir)

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "albums")
        self.assertEqual(self.arguments.statement, "update")
        self.assertTrue(self.arguments.donotpropagate)
        self.assertListEqual(self.arguments.rowid, [self.rowid])
        self.assertTrue(self.arguments.icount)
        self.assertEqual(self.arguments.template(self.arguments), "T02")
        self.assertFalse(self.arguments.test)
        self.assertEqual(self.arguments.db, self.db)
        self.assertEqual(self.arguments.loglevel, "INFO")

    def test_02second(self):
        """
        2. Tester le nombre total de changements.
        """
        self.assertListEqual(self.arguments.function(ns=self.arguments), [(self.albumid, self.count, 0, 0)])

    def test_03third(self):
        """
        3. Test that only temporary database was changed.
        """
        played = 0
        self.logger.debug(self.arguments.function(ns=self.arguments))
        self.curs.execute("SELECT played FROM albums WHERE rowid=?", (self.rowid,))
        try:
            played = self.curs.fetchone()[0]
        except TypeError:
            pass
        finally:
            self.logger.debug(played)
            self.assertEqual(played, self.played + 1)

    def test_04fourth(self):
        """
        4. Test that production database remains unchanged.
        """
        played = 0
        self.logger.debug(self.arguments.function(ns=self.arguments))
        conn = sqlite3.connect(DATABASE)
        curs = conn.cursor()
        curs.execute("SELECT played FROM albums WHERE rowid=?", (self.rowid,))
        try:
            played = curs.fetchone()[0]
        except TypeError:
            pass
        finally:
            self.logger.debug(played)
            self.assertEqual(played, self.played)


class Test18(unittest.TestCase):
    """
    Tester la décrémentation du compteur de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """
    logger = logging.getLogger("{0}.Test18".format(__name__))
    rowid = 10

    def setUp(self):
        # 1. Define temporary directory.
        self.tempdir = tempfile.mkdtemp()

        # 2. Define temporary DB.
        self.db = os.path.join(self.tempdir, os.path.basename(DATABASE))

        # 3. Copy production DB into temporary folder.
        copy(src=DATABASE, dst=self.tempdir)

        # 4. Count initial records stored into temporary DB.
        self.conn = sqlite3.connect(self.db, detect_types=sqlite3.PARSE_DECLTYPES)
        self.curs = self.conn.cursor()
        self.curs.execute("SELECT albumid, played, count(*) FROM albums WHERE rowid=?", (self.rowid,))
        self.albumid, self.played, self.count = self.curs.fetchone()
        self.logger.debug(self.albumid)
        self.logger.debug(self.played)
        self.logger.debug(self.count)

        # 5. Parse arguments.
        self.arguments = CD.parser.parse_args(["albums", "update", "{0}".format(self.rowid), "--dcount", "--database", self.db])

    def tearDown(self):
        self.conn.close()
        rmtree(self.tempdir)

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "albums")
        self.assertEqual(self.arguments.statement, "update")
        self.assertTrue(self.arguments.donotpropagate)
        self.assertListEqual(self.arguments.rowid, [self.rowid])
        self.assertTrue(self.arguments.dcount)
        self.assertEqual(self.arguments.template(self.arguments), "T02")
        self.assertFalse(self.arguments.test)
        self.assertEqual(self.arguments.db, self.db)
        self.assertEqual(self.arguments.loglevel, "INFO")

    def test_02second(self):
        """
        2. Tester le nombre total de changements.
        """
        self.assertListEqual(self.arguments.function(ns=self.arguments), [(self.albumid, self.count, 0, 0)])

    def test_03third(self):
        """
        3. Test that only temporary database was changed.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        self.curs.execute("SELECT played FROM albums WHERE rowid=?", (self.rowid,))
        played = self.curs.fetchone()[0]
        self.logger.debug(played)
        self.assertEqual(played, self.played - 1)

    def test_04fourth(self):
        """
        4. Test that production database remains unchanged.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        conn = sqlite3.connect(DATABASE)
        curs = conn.cursor()
        curs.execute("SELECT played FROM albums WHERE rowid=?", (self.rowid,))
        played = curs.fetchone()[0]
        conn.close()
        self.logger.debug(played)
        self.assertEqual(played, self.played)


class Test19(unittest.TestCase):
    def test_01first(self):
        self.arguments = CD.parser.parse_args("rippinglog select 28".split())
        self.assertEqual(self.arguments.db, r"G:\Computing\database.db")

    def test_02second(self):
        self.arguments = CD.parser.parse_args("rippinglog select 28 --test".split())
        self.assertEqual(self.arguments.db, r"G:\Computing\MyPythonProject\Applications\Tests\database.db")

    @unittest.skip
    def test_03third(self):
        somedb = r"G:\Computing\SomeDB.db"
        self.arguments = CD.parser.parse_args("rippinglog select 28 --database {0}".format(somedb).split())
        self.assertEqual(self.arguments.db, somedb)


class Test20(unittest.TestCase):
    def test_01first(self):
        self.arguments = CD.parser.parse_args("rippinglog update 28 --genre Rock".split())
        self.assertEqual(self.arguments.db, r"G:\Computing\database.db")

    def test_02second(self):
        self.arguments = CD.parser.parse_args("rippinglog update 28 --genre Rock --test".split())
        self.assertEqual(self.arguments.db, r"G:\Computing\MyPythonProject\Applications\Tests\database.db")

    @unittest.skip
    def test_03third(self):
        somedb = r"G:\Computing\SomeDB.db"
        self.arguments = CD.parser.parse_args("rippinglog update 28 --genre Rock --database {0}".format(somedb).split())
        self.assertEqual(self.arguments.db, somedb)


class Test21(unittest.TestCase):
    def test_01first(self):
        self.arguments = CD.parser.parse_args("rippinglog delete 28".split())
        self.assertEqual(self.arguments.db, r"G:\Computing\database.db")

    def test_02second(self):
        self.arguments = CD.parser.parse_args("rippinglog delete 28 --test".split())
        self.assertEqual(self.arguments.db, r"G:\Computing\MyPythonProject\Applications\Tests\database.db")

    @unittest.skip
    def test_03third(self):
        somedb = r"G:\Computing\SomeDB.db"
        self.arguments = CD.parser.parse_args("rippinglog delete 28 --database {0}".format(somedb).split())
        self.assertEqual(self.arguments.db, somedb)


class Test22(unittest.TestCase):
    def test_01first(self):
        self.arguments = CD.parser.parse_args("albums select 28".split())
        self.assertEqual(self.arguments.db, r"G:\Computing\database.db")

    def test_02second(self):
        self.arguments = CD.parser.parse_args("albums select 28 --test".split())
        self.assertEqual(self.arguments.db, r"G:\Computing\MyPythonProject\Applications\Tests\database.db")

    @unittest.skip
    def test_03third(self):
        somedb = r"G:\Computing\SomeDB.db"
        self.arguments = CD.parser.parse_args("albums select 28 --database {0}".format(somedb).split())
        self.assertEqual(self.arguments.db, somedb)


class Test23(unittest.TestCase):
    def test_01first(self):
        self.arguments = CD.parser.parse_args("albums update 28 --genre Rock".split())
        self.assertEqual(self.arguments.db, r"G:\Computing\database.db")

    def test_02second(self):
        self.arguments = CD.parser.parse_args("albums update 28 --genre Rock --test".split())
        self.assertEqual(self.arguments.db, r"G:\Computing\MyPythonProject\Applications\Tests\database.db")

    @unittest.skip
    def test_03third(self):
        somedb = r"G:\Computing\SomeDB.db"
        self.arguments = CD.parser.parse_args("albums update 28 --genre Rock --database {0}".format(somedb).split())
        self.assertEqual(self.arguments.db, somedb)


class Test24(unittest.TestCase):
    def test_01first(self):
        self.arguments = CD.parser.parse_args("albums delete 28".split())
        self.assertEqual(self.arguments.db, r"G:\Computing\database.db")

    def test_02second(self):
        self.arguments = CD.parser.parse_args("albums delete 28 --test".split())
        self.assertEqual(self.arguments.db, r"G:\Computing\MyPythonProject\Applications\Tests\database.db")

    @unittest.skip
    def test_03third(self):
        somedb = r"G:\Computing\SomeDB.db"
        self.arguments = CD.parser.parse_args("albums delete 28 --database {0}".format(somedb).split())
        self.assertEqual(self.arguments.db, somedb)


class Test25(unittest.TestCase):
    def test_01first(self):
        self.arguments = CD.parser.parse_args("tracks select 28".split())
        self.assertEqual(self.arguments.db, r"G:\Computing\database.db")

    def test_02second(self):
        self.arguments = CD.parser.parse_args("tracks select 28 --test".split())
        self.assertEqual(self.arguments.db, r"G:\Computing\MyPythonProject\Applications\Tests\database.db")

    @unittest.skip
    def test_03third(self):
        somedb = r"G:\Computing\SomeDB.db"
        self.arguments = CD.parser.parse_args("tracks select 28 --database {0}".format(somedb).split())
        self.assertEqual(self.arguments.db, somedb)


class Test26(unittest.TestCase):
    def test_01first(self):
        self.arguments = CD.parser.parse_args("tracks update 28 Title".split())
        self.assertEqual(self.arguments.db, r"G:\Computing\database.db")

    def test_02second(self):
        self.arguments = CD.parser.parse_args("tracks update 28 Title --test".split())
        self.assertEqual(self.arguments.db, r"G:\Computing\MyPythonProject\Applications\Tests\database.db")

    @unittest.skip
    def test_03third(self):
        somedb = r"G:\Computing\SomeDB.db"
        self.arguments = CD.parser.parse_args("tracks update 28 Title --database {0}".format(somedb).split())
        self.assertEqual(self.arguments.db, somedb)


class Test27(unittest.TestCase):
    def test_01first(self):
        self.arguments = CD.parser.parse_args("tracks delete 28".split())
        self.assertEqual(self.arguments.db, r"G:\Computing\database.db")

    def test_02second(self):
        self.arguments = CD.parser.parse_args("tracks delete 28 --test".split())
        self.assertEqual(self.arguments.db, r"G:\Computing\MyPythonProject\Applications\Tests\database.db")

    @unittest.skip
    def test_03third(self):
        somedb = r"G:\Computing\SomeDB.db"
        self.arguments = CD.parser.parse_args("tracks delete 28 --database {0}".format(somedb).split())
        self.assertEqual(self.arguments.db, somedb)


class Test28(unittest.TestCase):
    """
    Tester l'insertion d'un enregistrement dans la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    Les données proviennent de la ligne de commande.
    """
    logger = logging.getLogger("{0}.Test28".format(__name__))
    artistsort = "Kiss"
    albumsort = "1.19890000.1"
    year = 1989
    album = "The Album"
    upc = "5017615832822"

    def setUp(self):
        # 1. Define temporary directory.
        self.tempdir = tempfile.mkdtemp()

        # 2. Define temporary DB.
        self.db = os.path.join(self.tempdir, os.path.basename(DATABASE))

        # 3. Copy production DB into temporary folder.
        copy(src=DATABASE, dst=self.tempdir)

        # 4. Count initial records stored into temporary DB.
        self.conn = sqlite3.connect(self.db)
        self.curs = self.conn.cursor()
        self.curs.execute("SELECT count(*) FROM rippinglog")
        self.count = self.curs.fetchone()[0]

        # 5. Parse arguments.
        self.arguments = CD.parser.parse_args(["rippinglog",
                                               "insert",
                                               self.artistsort,
                                               self.albumsort,
                                               self.artistsort,
                                               str(self.year),
                                               str(self.year),
                                               self.album,
                                               "1",
                                               "8",
                                               "Hard Rock",
                                               self.upc,
                                               "Mercury Records",
                                               "--application", "dBpoweramp 15.1",
                                               "--database", self.db,
                                               "--loglevel", "DEBUG"])

    def tearDown(self):
        self.conn.close()
        rmtree(self.tempdir)

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "rippinglog")
        self.assertEqual(self.arguments.statement, "insert")
        self.assertEqual(self.arguments.artistsort, self.artistsort)
        self.assertEqual(self.arguments.albumsort, self.albumsort)
        self.assertEqual(self.arguments.artist, self.artistsort)
        self.assertEqual(int(self.arguments.origyear), self.year)
        self.assertEqual(int(self.arguments.year), self.year)
        self.assertEqual(self.arguments.album, self.album)
        self.assertEqual(self.arguments.disc, 1)
        self.assertEqual(self.arguments.tracks, 8)
        self.assertEqual(self.arguments.genre, "Hard Rock")
        self.assertEqual(self.arguments.upc, self.upc)
        self.assertEqual(self.arguments.application, "dBpoweramp 15.1")
        self.assertFalse(self.arguments.test)
        self.assertEqual(self.arguments.db, self.db)

    def test_02second(self):
        """
        2. Tester le nombre total de changements.
        """
        self.assertEqual(self.arguments.function(ns=self.arguments), 1)

    def test_03third(self):
        """
        3. Test that only temporary database was changed.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        self.curs.execute("SELECT count(*) FROM rippinglog")
        count = self.curs.fetchone()[0]
        self.logger.debug(count)
        self.assertEqual(count, self.count + 1)

    def test_04fourth(self):
        """
        3. Test that only temporary database was changed.
        """
        artistsort, albumsort, year, album, upc = None, None, None, None, None
        self.logger.debug(self.arguments.function(ns=self.arguments))
        self.curs.execute("SELECT artistsort, albumsort, year, album, upc FROM rippinglog ORDER BY rowid DESC")
        try:
            artistsort, albumsort, year, album, upc = self.curs.fetchone()
        except TypeError:
            pass
        finally:
            self.assertEqual(artistsort, self.artistsort)
            self.assertEqual(albumsort, self.albumsort)
            self.assertEqual(year, self.year)
            self.assertEqual(album, self.album)
            self.assertEqual(upc, self.upc)

    def test_05fifth(self):
        """
        5. Test that production database remains unchanged.
        """
        self.logger.debug(self.arguments.function(ns=self.arguments))
        conn = sqlite3.connect(DATABASE)
        curs = conn.cursor()
        curs.execute("SELECT count(*) FROM rippinglog")
        count = curs.fetchone()[0]
        conn.close()
        self.logger.debug(count)
        self.assertEqual(count, self.count)


# class Test29(unittest.TestCase):
#     """
#     Tester l'insertion d'un enregistrement dans la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
#     Les données proviennent d'un fichier XML encodé en UTF-8.
#     """
#     logger = logging.getLogger("{0}.Test29".format(__name__))
#     xmlfile = r"G:\Computing\MyPythonProject\Applications\Tests\test_rippinglog.xml"
#
#     def setUp(self):
#         # 1. Define temporary directory.
#         self.tempdir = tempfile.mkdtemp()
#
#         # 2. Define temporary DB.
#         self.db = os.path.join(self.tempdir, os.path.basename(DATABASE))
#
#         # 3. Copy production DB into temporary folder.
#         copy(src=DATABASE, dst=self.tempdir)
#
#         # 4. Count initial records stored into temporary DB.
#         self.conn = sqlite3.connect(self.db)
#         self.curs = self.conn.cursor()
#         self.curs.execute("SELECT count(*) FROM rippinglog")
#         self.count = self.curs.fetchone()[0]
#         self.logger.debug(self.count)
#
#         # 5. Get logs from XML file.
#         self.logs = []
#         with open(self.xmlfile, encoding="UTF_8") as fr:
#             self.logs = yaml.load(fr)
#
#         # 6. Parse arguments.
#         self.arguments = CD.parser.parse_args(["rippinglog", "insertfromfile", self.xmlfile, "--database", self.db])
#
#     def tearDown(self):
#         self.conn.close()
#         rmtree(self.tempdir)
#
#     @unittest.skip
#     def test_01first(self):
#         """
#         1. Tester le fonctionnement du parser.
#         """
#         self.assertEqual(self.arguments.table, "rippinglog")
#         self.assertEqual(self.arguments.statement, "insertfromfile")
#         self.assertIsNone(self.arguments.template(self.arguments))
#         self.assertFalse(self.arguments.test)
#         self.assertEqual(self.arguments.db, self.db)
#
#     @unittest.skip
#     def test_02second(self):
#         """
#         2. Tester le nombre total de changements.
#         """
#         self.assertEqual(self.arguments.function(ns=self.arguments), len(self.logs))
#
#     @unittest.skip
#     def test_03third(self):
#         """
#         3. Test that only temporary database was changed.
#         """
#         self.logger.debug(self.arguments.function(ns=self.arguments))
#         self.curs.execute("SELECT count(*) FROM rippinglog")
#         count = self.curs.fetchone()[0]
#         self.logger.debug(count)
#         self.assertEqual(count, self.count + len(self.logs))
#
#     @unittest.skip
#     def test_04fourth(self):
#         """
#         4. Test that production database remains unchanged.
#         """
#         self.logger.debug(self.arguments.function(ns=self.arguments))
#         conn = sqlite3.connect(DATABASE)
#         curs = conn.cursor()
#         curs.execute("SELECT count(*) FROM rippinglog")
#         count = curs.fetchone()[0]
#         conn.close()
#         self.logger.debug(count)
#         self.assertEqual(count, self.count)
#
#     @unittest.skip
#     def test_05fifth(self):
#         """
#         5. Test that only temporary database was changed.
#         """
#         self.logger.debug(self.arguments.function(ns=self.arguments))
#         self.curs.execute("SELECT artistsort, albumsort, year, album, upc FROM rippinglog ORDER BY rowid DESC")
#         try:
#             artistsort, albumsort, year, album, upc = self.curs.fetchone()
#         except TypeError:
#             artistsort, albumsort, year, album, upc = None, None, None, None, None
#         finally:
#             self.assertEqual(artistsort, self.logs[-1][0])
#             self.assertEqual(albumsort, self.logs[-1][1])
#             self.assertEqual(year, self.logs[-1][2])
#             self.assertEqual(album, self.logs[-1][3])
#             self.assertEqual(upc, self.logs[-1][4])


class Test30(unittest.TestCase):
    """
    Tester la création d'un enregistrement dans la table `ripppinglog` à l'aide de la fonction `insertfromfile`.
    """
    logger = logging.getLogger("{0}.Test30".format(__name__))
    encoding = "UTF_8"
    inputjson = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tests", "test_rippinglog.json")

    def setUp(self):

        # 0. Initializations.
        self.changes = 0

        # 1. Define temporary directory.
        self.tempdir = tempfile.mkdtemp()

        # 2. Define JSON files storing test data.
        outputjson = os.path.join(self.tempdir, os.path.basename(self.inputjson))

        # 3. Define temporary DB.
        self.db = os.path.join(self.tempdir, os.path.basename(DATABASE))

        # 4. Copy production DB into temporary folder.
        copy(src=DATABASE, dst=self.tempdir)

        # 5. Count initial records stored into temporary DB.
        self.conn = sqlite3.connect(self.db, detect_types=sqlite3.PARSE_DECLTYPES)
        self.curs = self.conn.cursor()
        self.curs.execute("SELECT count(*) FROM rippinglog")
        self.records = self.curs.fetchone()[0]

        # 6. Prepare a JSON file compliant with `insertfromfile` signature.
        with open(self.inputjson, encoding=self.encoding) as fr:
            self.logs = json.load(fr)
        self.logs = sorted(sorted(self.logs, key=itemgetter(10)), key=itemgetter(11))
        logs = [(db, *log) for db, log in zip(repeat(self.db), self.logs)]
        with open(outputjson, "w", encoding=self.encoding) as fw:
            json.dump(logs, fw, ensure_ascii=False, indent=4)
        with open(outputjson, encoding=self.encoding) as fr:
            for item in json.load(fr):
                self.logger.debug(item)

        # 7. Insert records using `insertfromfile`.
        with open(outputjson, encoding=self.encoding) as fr:
            self.changes = insertlogfromfile(fr)

    def tearDown(self):
        self.conn.close()
        rmtree(self.tempdir)

    def test01_first(self):
        """
        1. Test number of changes.
        """
        self.assertEqual(self.changes, len(self.logs))

    def test02_second(self):
        """
        2. Test that temporary database was changed.
        """
        self.curs.execute("SELECT count(*) FROM rippinglog")
        records = self.curs.fetchone()[0]
        self.assertEqual(records - self.records, len(self.logs))

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
        self.curs.execute("SELECT artist, origyear, year, album, disc, tracks, genre, upc, label, application, albumsort, artistsort FROM rippinglog ORDER BY rowid DESC LIMIT ?", (len(self.logs),))
        extracted, expected = sorted(self.curs.fetchall(), reverse=True), []
        for log in self.logs:
            try:
                artist, origyear, year, album, disc, tracks, genre, upc, label, ripped, application, albumsort, artistsort = log
            except ValueError:
                artist, origyear, year, album, disc, tracks, genre, upc, label, application, albumsort, artistsort = log
            finally:
                expected.append([artist, origyear, year, album, disc, tracks, genre, upc, label, application, albumsort, artistsort])
        for i in range(len(expected)):
            with self.subTest(item=i):
                self.assertListEqual(list(extracted[i]), expected[i])


class Test31(unittest.TestCase):
    """
    Tester la création d'un enregistrement dans la table `ripppinglog` à l'aide de la fonction `insertfromfile`.
    """
    logger = logging.getLogger("{0}.Test31".format(__name__))
    encoding = "UTF_8"
    inputjson = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tests", "test_rippinglog.json")

    def setUp(self):

        # 0. Initializations.
        self.changes = 0

        # 1. Define temporary directory.
        self.tempdir = tempfile.mkdtemp()

        # 2. Define JSON files storing test data.
        outputjson = os.path.join(self.tempdir, os.path.basename(self.inputjson))

        # 3. Define temporary DB.
        self.db1 = os.path.join(self.tempdir, "db1")
        self.db2 = os.path.join(self.tempdir, "db2")

        # 4. Copy production DB into temporary folder.
        copy(src=DATABASE, dst=self.db1)
        copy(src=DATABASE, dst=self.db2)

        # 5. Count initial records stored into production DB.
        conn = sqlite3.connect(DATABASE)
        curs = conn.cursor()
        curs.execute("SELECT count(*) FROM rippinglog")
        self.records = curs.fetchone()[0]
        conn.close()

        # 6. Prepare a JSON file compliant with `insertfromfile` signature.
        with open(self.inputjson, encoding=self.encoding) as fr:
            self.logs = json.load(fr)
        self.logs = sorted(sorted(sorted([(db, *log) for db, log in zip(cycle([self.db1, self.db2]), self.logs)], key=itemgetter(11)), key=itemgetter(12)), key=itemgetter(0))
        self.groupedlogs = groupby(self.logs, key=itemgetter(0))
        with open(outputjson, "w", encoding=self.encoding) as fw:
            json.dump(self.logs, fw, ensure_ascii=False, indent=4)
        with open(outputjson, encoding=self.encoding) as fr:
            for item in json.load(fr):
                self.logger.debug(item)

        # 7. Insert records using `insertfromfile`.
        with open(outputjson, encoding=self.encoding) as fr:
            self.changes = insertlogfromfile(fr)

    def tearDown(self):
        rmtree(self.tempdir)

    def test01_first(self):
        """
        1. Test number of changes.
        """
        self.assertEqual(self.changes, len(self.logs))

    def test02_second(self):
        """
        2. Test that temporary databases were changed.
        """
        for key, group in self.groupedlogs:
            with self.subTest(db=key):
                conn = sqlite3.connect(key)
                curs = conn.cursor()
                curs.execute("SELECT count(*) FROM rippinglog")
                records = curs.fetchone()[0]
                conn.close()
                self.assertEqual(records - self.records, len(list(group)))

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
        extracted, expected = [], []
        for key, group in self.groupedlogs:
            conn = sqlite3.connect(key)
            curs = conn.cursor()
            curs.execute("SELECT artist, origyear, year, album, disc, tracks, genre, upc, label, application, albumsort, artistsort FROM rippinglog ORDER BY rowid DESC LIMIT ?", (len(list(group)),))
            extracted = sorted(curs.fetchall(), reverse=True)
            conn.close()
            for log in group:
                try:
                    database, artist, origyear, year, album, disc, tracks, genre, upc, label, ripped, application, albumsort, artistsort = log
                except ValueError:
                    database, artist, origyear, year, album, disc, tracks, genre, upc, label, application, albumsort, artistsort = log
                finally:
                    expected.append([artist, origyear, year, album, disc, tracks, genre, upc, label, application, albumsort, artistsort])
        for i in range(len(expected)):
            with self.subTest(item=i):
                self.assertListEqual(list(extracted[i]), expected[i])


if __name__ == "__main__":

    import sys
    import argparse
    from Applications.parsers import loglevel_parser

    # ==============
    # Get arguments.
    # ==============
    parser = argparse.ArgumentParser(parents=[loglevel_parser], argument_default=argparse.SUPPRESS)
    parser.add_argument("-v", "--verbosity", action="count")
    arguments = parser.parse_args()

    # ===================
    # Set logging levels.
    # ===================
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        config = yaml.load(fp)
    for logger in ["Applications.Database.AudioCD", "Applications.Database.DigitalAudioFiles", "Applications.Tests"]:
        try:
            config["loggers"][logger]["level"] = arguments.loglevel
        except KeyError:
            pass
    logging.config.dictConfig(config)

    # ==========
    # Run tests.
    # ==========
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            sys.argv.remove(arg)
    verbosity = 1
    try:
        verbosity = arguments.verbosity
    except AttributeError:
        pass
    if verbosity > 2:
        verbosity = 2
    unittest.main(verbosity=verbosity)

#
# def test04_fourth(self):
#     """
#     4. Test that inserted records are the expected ones.
#     """
#     self.curs.execute("SELECT artist, origyear, year, album, disc, tracks, genre, upc, label, application, albumsort, artistsort FROM rippinglog ORDER BY rowid DESC LIMIT ?", (len(self.logs),))
#     extracted = sorted(self.curs.fetchall(), reverse=True)
#     expected = []
#     for log in self.logs:
#         try:
#             artist, origyear, year, album, disc, tracks, genre, upc, label, ripped, application, albumsort, artistsort = log
#         except ValueError:
#             artist, origyear, year, album, disc, tracks, genre, upc, label, application, albumsort, artistsort = log
#         finally:
#             expected.append([artist, origyear, year, album, disc, tracks, genre, upc, label, application, albumsort, artistsort])
#     for i in range(len(expected)):
#         with self.subTest(item=i):
#             self.assertListEqual(list(extracted[i]), expected[i])

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
