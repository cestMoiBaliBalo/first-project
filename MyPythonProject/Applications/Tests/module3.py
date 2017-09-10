# -*- coding: utf-8 -*-
import logging.config
import os
import sqlite3
import tempfile
import unittest
from shutil import copy

import yaml

import AudioCD.Interface as CD
from .. import shared
from ..Database.DigitalAudioFiles.shared import deletealbum, updatealbum
from ..shared import DATABASE, LOCAL, UTC, dateformat

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

    def setUp(self):
        self.arguments = CD.parser.parse_args("rippinglog select 30".split())

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "rippinglog")
        self.assertEqual(self.arguments.statement, "select")
        self.assertListEqual(self.arguments.rowid, [30])
        self.assertTrue(self.arguments.donotpropagate)
        self.assertEqual(self.arguments.template(self.arguments), "T01")

    def test_02second(self):
        """
        2. Tester la restitution à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        for row in self.arguments.function(ns=self.arguments):
            self.assertEqual(row.rowid, 30)
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

    def setUp(self):
        self.arguments = CD.parser.parse_args("rippinglog select 30 31 32 33".split())

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "rippinglog")
        self.assertEqual(self.arguments.statement, "select")
        self.assertListEqual(self.arguments.rowid, [30, 31, 32, 33])
        self.assertTrue(self.arguments.donotpropagate)
        self.assertEqual(self.arguments.template(self.arguments), "T01")


class Test03(unittest.TestCase):
    """
    Tester la mise à jour d'un enregistrement de la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """

    def setUp(self):
        self.arguments = CD.parser.parse_args("rippinglog update 30 --genre Rock --upc 9999999999999 --ripped 1504122358".split())

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "rippinglog")
        self.assertEqual(self.arguments.statement, "update")
        self.assertTrue(self.arguments.donotpropagate)
        self.assertListEqual(self.arguments.rowid, [30])
        self.assertEqual(self.arguments.genre, "Rock")
        self.assertEqual(self.arguments.upc, "9999999999999")
        self.assertEqual(self.arguments.ripped, 1504122358)
        self.assertIsNone(self.arguments.template(self.arguments))

    def test_02second(self):
        """
        2. Tester la mise à jour à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        with tempfile.TemporaryDirectory() as directory:
            dst = os.path.join(directory, os.path.basename(self.arguments.db))
            copy(src=self.arguments.db, dst=dst)
            kwargs = {key: val for key, val in vars(self.arguments).items() if val}
            kwargs["db"] = dst
            self.assertEqual(self.arguments.function(**kwargs), 1)

    def test_03third(self):
        """
        3. Tester la mise à jour à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        with tempfile.TemporaryDirectory() as directory:
            dst = os.path.join(directory, os.path.basename(self.arguments.db))
            copy(src=self.arguments.db, dst=dst)
            kwargs = {key: val for key, val in vars(self.arguments).items() if val}
            kwargs["db"] = dst
            if self.arguments.function(**kwargs):
                conn = sqlite3.connect(dst, detect_types=sqlite3.PARSE_DECLTYPES)
                conn.row_factory = sqlite3.Row
                try:
                    for row in conn.execute("SELECT genre, upc, ripped FROM rippinglog WHERE rowid=30"):
                        self.assertEqual(row["genre"], self.arguments.genre)
                        self.assertEqual(row["upc"], self.arguments.upc)
                        self.assertEqual(shared.dateformat(shared.LOCAL.localize(row["ripped"]), shared.TEMPLATE4), "Mercredi 30 Août 2017 21:45:58 (CEST+0200)")
                except AssertionError:
                    raise
                finally:
                    conn.close()


class Test04(unittest.TestCase):
    """
    Tester la suppression d'un enregistrement de la table `rippinglog` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """

    def setUp(self):
        self.arguments = CD.parser.parse_args("rippinglog delete 30".split())

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "rippinglog")
        self.assertEqual(self.arguments.statement, "delete")
        self.assertListEqual(self.arguments.rowid, [30])
        self.assertTrue(self.arguments.donotpropagate)
        self.assertIsNone(self.arguments.template(self.arguments))

    def test_02second(self):
        """
        2. Tester la suppression à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        with tempfile.TemporaryDirectory() as directory:
            dst = os.path.join(directory, os.path.basename(self.arguments.db))
            copy(src=self.arguments.db, dst=dst)
            kwargs = {key: val for key, val in vars(self.arguments).items() if val}
            kwargs["db"] = dst
            self.assertEqual(self.arguments.function(**kwargs), 1)

    def test_03third(self):
        """
        3. Tester la suppression à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        with tempfile.TemporaryDirectory() as directory:
            dst = os.path.join(directory, os.path.basename(self.arguments.db))
            copy(src=self.arguments.db, dst=dst)
            kwargs = {key: val for key, val in vars(self.arguments).items() if val}
            kwargs["db"] = dst
            if self.arguments.function(**kwargs):
                log = 0
                conn = sqlite3.connect(dst)
                conn.row_factory = sqlite3.Row
                with conn:
                    for row in conn.execute("SELECT count(*) AS count FROM rippinglog WHERE rowid=30"):
                        log = row["count"]
                conn.close()
                self.assertEqual(log, 0)


class Test05a(unittest.TestCase):
    """
    Tester la restitution d'un enregistrement de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    Sans propagation.
    """

    def setUp(self):
        self.arguments = CD.parser.parse_args("albums select 30 --donotpropagate".split())

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "albums")
        self.assertEqual(self.arguments.statement, "select")
        self.assertListEqual(self.arguments.rowid, [30])
        self.assertTrue(self.arguments.donotpropagate)
        self.assertEqual(self.arguments.template(self.arguments), "T02")

    def test_02second(self):
        """
        2. Tester la restitution à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        for row in self.arguments.function(ns=self.arguments):
            self.assertEqual(row.rowid, 30)
            self.assertEqual(row.albumid, "I.Iron Maiden.1.19900000.4")
            self.assertEqual(row.artist, "Iron Maiden")
            self.assertEqual(row.year, 1990)
            self.assertEqual(row.album, "The First Ten Years - IV")
            self.assertEqual(row.genre, "Heavy Metal")
            self.assertFalse(row.live)
            self.assertFalse(row.bootleg)
            self.assertTrue(row.incollection)
            self.assertEqual(row.language, "English")
            self.assertEqual(row.count, 0)


class Test05b(unittest.TestCase):
    """
    Tester la restitution d'un enregistrement de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    Avec propagation.
    """

    def setUp(self):
        self.arguments = CD.parser.parse_args("albums select 30".split())

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "albums")
        self.assertEqual(self.arguments.statement, "select")
        self.assertListEqual(self.arguments.rowid, [30])
        self.assertFalse(self.arguments.donotpropagate)
        self.assertEqual(self.arguments.template(self.arguments), "T04")

    @unittest.skip
    def test_02second(self):
        """
        2. Tester la restitution à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        for row in self.arguments.function(ns=self.arguments):
            self.assertEqual(row.rowid, 30)
            self.assertEqual(row.albumid, "I.Iron Maiden.1.19900000.4")
            self.assertEqual(row.artist, "Iron Maiden")
            self.assertEqual(row.year, 1990)
            self.assertEqual(row.album, "The First Ten Years - IV")
            self.assertEqual(row.genre, "Heavy Metal")
            self.assertFalse(row.live)
            self.assertFalse(row.bootleg)
            self.assertTrue(row.incollection)
            self.assertEqual(row.language, "English")
            self.assertEqual(row.count, 0)


class Test06(unittest.TestCase):
    """
    Tester la suppression d'un enregistrement de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    Sans propagation à `discs` et `tracks`.
    """

    def setUp(self):
        self.arguments = CD.parser.parse_args("albums delete 30 --donotpropagate".split())

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "albums")
        self.assertEqual(self.arguments.statement, "delete")
        self.assertListEqual(self.arguments.rowid, [30])
        self.assertTrue(self.arguments.donotpropagate)
        self.assertIsNone(self.arguments.template(self.arguments))

    def test_02second(self):
        """
        Tester le fonctionnement du parser.
        """
        discs, tracks = list(), list()
        conn = sqlite3.connect(self.arguments.db, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        with conn:
            for row in conn.execute("SELECT rowid FROM discs WHERE albumid='I.Iron Maiden.1.19900000.4'"):
                discs.append(row["rowid"])
            for row in conn.execute("SELECT rowid FROM tracks WHERE albumid='I.Iron Maiden.1.19900000.4'"):
                tracks.append(row["rowid"])
        conn.close()
        self.assertEqual(sorted(discs), [34])
        self.assertEqual(sorted(tracks), [384, 385, 386, 387])


class Test07(unittest.TestCase):
    """
    Tester la suppression d'un enregistrement de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    Avec propagation à `discs` et `tracks`.
    """

    def setUp(self):
        self.arguments = CD.parser.parse_args("albums delete 30".split())

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "albums")
        self.assertEqual(self.arguments.statement, "delete")
        self.assertListEqual(self.arguments.rowid, [30])
        self.assertFalse(self.arguments.donotpropagate)
        self.assertEqual(self.arguments.template(self.arguments), "T03")

    def test_02second(self):
        """
        2. Tester la suppression à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        with tempfile.TemporaryDirectory() as directory:
            dst = os.path.join(directory, os.path.basename(self.arguments.db))
            copy(src=self.arguments.db, dst=dst)
            kwargs = {key: val for key, val in vars(self.arguments).items() if val}
            kwargs["db"] = dst
            self.assertListEqual(self.arguments.function(**kwargs), [("I.Iron Maiden.1.19900000.4", 1, 1, 4)])

    def test_03third(self):
        """
        3. Tester la suppression à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        with tempfile.TemporaryDirectory() as directory:
            dst = os.path.join(directory, os.path.basename(self.arguments.db))
            copy(src=self.arguments.db, dst=dst)
            kwargs = {key: val for key, val in vars(self.arguments).items() if val}
            kwargs["db"] = dst
            if self.arguments.function(**kwargs):
                albums, discs, tracks = 0, 0, 0
                conn = sqlite3.connect(dst, detect_types=sqlite3.PARSE_DECLTYPES)
                conn.row_factory = sqlite3.Row
                with conn:
                    for row in conn.execute("SELECT count(*) AS count FROM albums WHERE rowid=?", (30,)):
                        albums = row["count"]
                    for row in conn.execute("SELECT count(*) AS count FROM discs WHERE rowid=?", (34,)):
                        discs = row["count"]
                    for row in conn.execute("SELECT count(*) AS count FROM tracks WHERE rowid BETWEEN ? AND ?", (384, 387)):
                        tracks = row["count"]
                conn.close()
                self.assertEqual(albums, 0)
                self.assertEqual(discs, 0)
                self.assertEqual(tracks, 0)


class Test08a(unittest.TestCase):
    """
    Tester la mise à jour d'un enregistrement de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    Album unique key is not updated.
    """

    def setUp(self):
        self.arguments = CD.parser.parse_args(["albums", "update", "30", "--genre", "Rock", "--upc", "9999999999999", "--album", "Communiqué", "--live", "Y", "--bootleg", "Y", "--incollection", "N"])

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "albums")
        self.assertEqual(self.arguments.statement, "update")
        self.assertTrue(self.arguments.donotpropagate)
        self.assertListEqual(self.arguments.rowid, [30])
        self.assertEqual(self.arguments.album, "Communiqué")
        self.assertEqual(self.arguments.genre, "Rock")
        self.assertTrue(self.arguments.live.bool)
        self.assertTrue(self.arguments.bootleg.bool)
        self.assertFalse(self.arguments.incollection.bool)
        self.assertEqual(self.arguments.upc, "9999999999999")
        self.assertEqual(self.arguments.template(self.arguments), "T03")

    def test_02second(self):
        """
        2. Tester le nombre total de changements.
        """
        with tempfile.TemporaryDirectory() as directory:
            dst = os.path.join(directory, os.path.basename(self.arguments.db))
            copy(src=self.arguments.db, dst=dst)
            kwargs = {key: val for key, val in vars(self.arguments).items() if val}
            kwargs["db"] = dst
            self.assertListEqual(self.arguments.function(**kwargs), [("I.Iron Maiden.1.19900000.4", 1, 0, 0)])

    def test_03third(self):
        """
        3. Tester la mise à jour à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        with tempfile.TemporaryDirectory() as directory:
            dst = os.path.join(directory, os.path.basename(self.arguments.db))
            copy(src=self.arguments.db, dst=dst)
            kwargs = {key: val for key, val in vars(self.arguments).items() if val}
            kwargs["db"] = dst
            if self.arguments.function(**kwargs):
                conn = sqlite3.connect(dst, detect_types=sqlite3.PARSE_DECLTYPES)
                conn.row_factory = sqlite3.Row
                try:
                    for row in conn.execute("SELECT album, genre, live, bootleg, incollection, upc FROM albums WHERE rowid=?", (30,)):
                        self.assertEqual(row["album"], self.arguments.album)
                        self.assertEqual(row["genre"], self.arguments.genre)
                        self.assertTrue(row["live"])
                        self.assertTrue(row["bootleg"])
                        self.assertFalse(row["incollection"])
                        self.assertEqual(row["upc"], self.arguments.upc)
                except AssertionError:
                    raise
                finally:
                    conn.close()


class Test08b(unittest.TestCase):
    """
    Tester la mise à jour de la date de dernière lecture de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    Le timestamp communiqué au parser est exprimé par rapport à l'UTC !
    La mise à jour du nombre de lectures est également testée.
    """

    def setUp(self):
        self.arguments = CD.parser.parse_args(["albums", "update", "30", "--count", "100", "--played", "1505040486"])

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "albums")
        self.assertEqual(self.arguments.statement, "update")
        self.assertTrue(self.arguments.donotpropagate)
        self.assertListEqual(self.arguments.rowid, [30])
        self.assertEqual(self.arguments.count, 100)
        self.assertEqual(self.arguments.template(self.arguments), "T03")

    def test_02second(self):
        """
        2. Tester le nombre total de changements.
        """
        with tempfile.TemporaryDirectory() as directory:
            dst = os.path.join(directory, os.path.basename(self.arguments.db))
            copy(src=self.arguments.db, dst=dst)
            kwargs = {key: val for key, val in vars(self.arguments).items() if val}
            kwargs["db"] = dst
            self.assertListEqual(self.arguments.function(**kwargs), [("I.Iron Maiden.1.19900000.4", 1, 0, 0)])

    def test_03third(self):
        """
        3. Tester la mise à jour à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        with tempfile.TemporaryDirectory() as directory:
            dst = os.path.join(directory, os.path.basename(self.arguments.db))
            copy(src=self.arguments.db, dst=dst)
            kwargs = {key: val for key, val in vars(self.arguments).items() if val}
            kwargs["db"] = dst
            if self.arguments.function(**kwargs):
                conn = sqlite3.connect(dst, detect_types=sqlite3.PARSE_DECLTYPES)
                conn.row_factory = sqlite3.Row
                try:
                    for row in conn.execute("SELECT count, played FROM albums WHERE rowid=?", (30,)):
                        self.assertEqual(row["count"], self.arguments.count)
                        self.assertEqual(int(UTC.localize(row["played"]).timestamp()), self.arguments.played)
                        self.assertEqual(dateformat(UTC.localize(row["played"]).astimezone(LOCAL), "$d/$m/$Y $H:$M:$S"), "10/09/2017 12:48:06")
                except AssertionError:
                    raise
                finally:
                    conn.close()


class Test08c(unittest.TestCase):
    """
    Tester l'incrémentation du compteur de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """

    def setUp(self):
        self.arguments = CD.parser.parse_args(["albums", "update", "139", "--icount"])

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "albums")
        self.assertEqual(self.arguments.statement, "update")
        self.assertTrue(self.arguments.donotpropagate)
        self.assertListEqual(self.arguments.rowid, [139])
        self.assertTrue(self.arguments.icount)
        self.assertFalse(self.arguments.dcount)
        self.assertEqual(self.arguments.template(self.arguments), "T03")

    def test_02second(self):
        """
        2. Tester le nombre total de changements.
        """
        with tempfile.TemporaryDirectory() as directory:
            dst = os.path.join(directory, os.path.basename(self.arguments.db))
            copy(src=self.arguments.db, dst=dst)
            kwargs = {key: val for key, val in vars(self.arguments).items() if val}
            kwargs["db"] = dst
            self.assertListEqual(self.arguments.function(**kwargs), [("K.Kiss.1.19870000.1", 1, 0, 0)])

    def test_03third(self):
        """
        3. Tester la mise à jour à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """

        # Extraire le nombre de lectures stocké la base de production.
        conn = sqlite3.connect(self.arguments.db, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        count = 0
        for row in conn.execute("SELECT count FROM albums WHERE rowid=?", (139,)):
            count = row["count"]
        conn.close()
        count += 1

        # Comparer avec le résultat de la mise à jour.
        with tempfile.TemporaryDirectory() as directory:
            dst = os.path.join(directory, os.path.basename(self.arguments.db))
            copy(src=self.arguments.db, dst=dst)
            kwargs = {key: val for key, val in vars(self.arguments).items() if val}
            kwargs["db"] = dst
            if self.arguments.function(**kwargs):
                conn = sqlite3.connect(dst, detect_types=sqlite3.PARSE_DECLTYPES)
                conn.row_factory = sqlite3.Row
                try:
                    for row in conn.execute("SELECT count FROM albums WHERE rowid=?", (139,)):
                        self.assertEqual(row["count"], count)
                except AssertionError:
                    raise
                finally:
                    conn.close()


class Test08d(unittest.TestCase):
    """
    Tester la décrémentation du compteur de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    """

    def setUp(self):
        self.arguments = CD.parser.parse_args(["albums", "update", "139", "--dcount"])

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "albums")
        self.assertEqual(self.arguments.statement, "update")
        self.assertTrue(self.arguments.donotpropagate)
        self.assertListEqual(self.arguments.rowid, [139])
        self.assertFalse(self.arguments.icount)
        self.assertTrue(self.arguments.dcount)
        self.assertEqual(self.arguments.template(self.arguments), "T03")

    def test_02second(self):
        """
        2. Tester le nombre total de changements.
        """
        with tempfile.TemporaryDirectory() as directory:
            dst = os.path.join(directory, os.path.basename(self.arguments.db))
            copy(src=self.arguments.db, dst=dst)
            kwargs = {key: val for key, val in vars(self.arguments).items() if val}
            kwargs["db"] = dst
            self.assertListEqual(self.arguments.function(**kwargs), [("K.Kiss.1.19870000.1", 1, 0, 0)])

    def test_03third(self):
        """
        3. Tester la mise à jour à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """

        # Extraire le nombre de lectures stocké la base de production.
        conn = sqlite3.connect(self.arguments.db, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        count = 0
        for row in conn.execute("SELECT count FROM albums WHERE rowid=?", (139,)):
            count = row["count"]
        conn.close()
        count -= 1
        if count < 0:
            count = 0

        # Comparer avec le résultat de la mise à jour.
        with tempfile.TemporaryDirectory() as directory:
            dst = os.path.join(directory, os.path.basename(self.arguments.db))
            copy(src=self.arguments.db, dst=dst)
            kwargs = {key: val for key, val in vars(self.arguments).items() if val}
            kwargs["db"] = dst
            if self.arguments.function(**kwargs):
                conn = sqlite3.connect(dst, detect_types=sqlite3.PARSE_DECLTYPES)
                conn.row_factory = sqlite3.Row
                try:
                    for row in conn.execute("SELECT count FROM albums WHERE rowid=?", (139,)):
                        self.assertEqual(row["count"], count)
                except AssertionError:
                    raise
                finally:
                    conn.close()


class Test09(unittest.TestCase):
    """
    Tester la fonction `Database.DigitalAudioFiles.shared.updatealbum.py`
    """

    def test_01first(self):
        """
        Test total changes when row unique ID is used as primary key.
        """
        with tempfile.TemporaryDirectory() as directory:
            database = os.path.join(directory, os.path.basename(DATABASE))
            copy(src=DATABASE, dst=database)
            albumid, acount, dcount, tcount = updatealbum(30, db=database, album="The Album", genre="Some Genre")
            self.assertEqual(albumid, "I.Iron Maiden.1.19900000.4")
            self.assertEqual(acount, 1)
            self.assertEqual(dcount, 0)
            self.assertEqual(tcount, 0)

    def test_02second(self):
        """
        Test field value when row unique ID is used as primary key.
        """
        with tempfile.TemporaryDirectory() as directory:
            database = os.path.join(directory, os.path.basename(DATABASE))
            copy(src=DATABASE, dst=database)
            updatealbum(30, db=database, album="The Album", genre="Some Genre")
            conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
            conn.row_factory = sqlite3.Row
            with conn:
                for row in conn.execute("SELECT album, genre FROM albums WHERE rowid=?", (30,)):
                    self.assertEqual(row["album"], "The Album")
                    self.assertEqual(row["genre"], "Some Genre")
            conn.close()

    def test_03third(self):
        """
        Test total changes when album unique ID is used as primary key.
        """
        with tempfile.TemporaryDirectory() as directory:
            database = os.path.join(directory, os.path.basename(DATABASE))
            copy(src=DATABASE, dst=database)
            albumid, acount, dcount, tcount = updatealbum(30, db=database, albumid="I.Iron Maiden.1.19900000.9")
            self.assertEqual(albumid, "I.Iron Maiden.1.19900000.4")
            self.assertEqual(acount, 1)
            self.assertEqual(dcount, 1)
            self.assertEqual(tcount, 4)

    def test_04fourth(self):
        """
        Test field value when album unique ID is used as primary key.
        """
        with tempfile.TemporaryDirectory() as directory:
            database = os.path.join(directory, os.path.basename(DATABASE))
            copy(src=DATABASE, dst=database)
            updatealbum(30, db=database, albumid="I.Iron Maiden.1.19900000.9")
            conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
            conn.row_factory = sqlite3.Row
            with conn:
                for row in conn.execute("SELECT albumid FROM albums WHERE rowid=?", (30,)):
                    self.assertEqual(row["albumid"], "I.Iron Maiden.1.19900000.9")
                for row in conn.execute("SELECT albumid FROM discs WHERE rowid=?", (34,)):
                    self.assertEqual(row["albumid"], "I.Iron Maiden.1.19900000.9")
                for i in [384, 385, 386, 387]:
                    for row in conn.execute("SELECT albumid FROM tracks WHERE rowid=?", (i,)):
                        self.assertEqual(row["albumid"], "I.Iron Maiden.1.19900000.9")
            conn.close()


class Test10(unittest.TestCase):
    """
    Tester la fonction `Database.DigitalAudioFiles.shared.delete.py`
    Row unique ID is used as primary key.
    """

    def test_01first(self):
        """
        Test total changes.
        """
        with tempfile.TemporaryDirectory() as directory:
            database = os.path.join(directory, os.path.basename(DATABASE))
            copy(src=DATABASE, dst=database)
            albumid, acount, dcount, tcount = deletealbum(db=database, uid=30)
            self.assertEqual(albumid, "I.Iron Maiden.1.19900000.4")
            self.assertEqual(acount, 1)
            self.assertEqual(dcount, 1)
            self.assertEqual(tcount, 4)

    def test_02second(self):
        """
        Test propagation from `albums` table to both `discs` and `tracks` tables.
        """
        albums, discs, tracks = 0, 0, 0
        with tempfile.TemporaryDirectory() as directory:
            database = os.path.join(directory, os.path.basename(DATABASE))
            copy(src=DATABASE, dst=database)
            deletealbum(db=database, uid=30)
            conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
            conn.row_factory = sqlite3.Row
            with conn:
                for row in conn.execute("SELECT count(*) AS count FROM albums WHERE albumid=?", ("I.Iron Maiden.1.19900000.4",)):
                    albums = row["count"]
                for row in conn.execute("SELECT count(*) AS count FROM discs WHERE albumid=?", ("I.Iron Maiden.1.19900000.4",)):
                    discs = row["count"]
                for row in conn.execute("SELECT count(*) AS count FROM tracks WHERE albumid=?", ("I.Iron Maiden.1.19900000.4",)):
                    tracks = row["count"]
            conn.close()
            self.assertEqual(albums, 0)
            self.assertEqual(discs, 0)
            self.assertEqual(tracks, 0)


class Test11(unittest.TestCase):
    """
    Tester la fonction `Database.DigitalAudioFiles.shared.delete.py`
    Album unique ID is used as primary key.
    """

    def test_01first(self):
        """
        Test total changes.
        """
        with tempfile.TemporaryDirectory() as directory:
            database = os.path.join(directory, os.path.basename(DATABASE))
            copy(src=DATABASE, dst=database)
            albumid, acount, dcount, tcount = deletealbum(db=database, albumid="I.Iron Maiden.1.19900000.4")
            self.assertEqual(albumid, "I.Iron Maiden.1.19900000.4")
            self.assertEqual(acount, 1)
            self.assertEqual(dcount, 1)
            self.assertEqual(tcount, 4)

    def test_02second(self):
        """
        Test propagation from `albums` table to both `discs` and `tracks` tables.
        """
        albums, discs, tracks = 0, 0, 0
        with tempfile.TemporaryDirectory() as directory:
            database = os.path.join(directory, os.path.basename(DATABASE))
            copy(src=DATABASE, dst=database)
            deletealbum(db=database, uid=30)
            conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
            conn.row_factory = sqlite3.Row
            with conn:
                for row in conn.execute("SELECT count(*) AS count FROM albums WHERE albumid=?", ("I.Iron Maiden.1.19900000.4",)):
                    albums = row["count"]
                for row in conn.execute("SELECT count(*) AS count FROM discs WHERE albumid=?", ("I.Iron Maiden.1.19900000.4",)):
                    discs = row["count"]
                for row in conn.execute("SELECT count(*) AS count FROM tracks WHERE albumid=?", ("I.Iron Maiden.1.19900000.4",)):
                    tracks = row["count"]
            conn.close()
            self.assertEqual(albums, 0)
            self.assertEqual(discs, 0)
            self.assertEqual(tracks, 0)


class Test12(unittest.TestCase):
    """
    Tester la mise à jour d'un enregistrement de la table `albums` à l'aide du parser configuré dans `MyPythonProject\AudioCD\Interface.py`.
    Album unique key is updated.
    """

    def setUp(self):
        self.arguments = CD.parser.parse_args(
                ["albums", "update", "30", "--genre", "Rock", "--upc", "9999999999999", "--album", "Communiqué", "--live", "Y", "--bootleg", "Y", "--incollection", "N", "--albumid",
                 "I.Iron Maiden.1.19900000.9"])

    def test_01first(self):
        """
        1. Tester le fonctionnement du parser.
        """
        self.assertEqual(self.arguments.table, "albums")
        self.assertEqual(self.arguments.statement, "update")
        self.assertTrue(self.arguments.donotpropagate)
        self.assertListEqual(self.arguments.rowid, [30])
        self.assertEqual(self.arguments.albumid, "I.Iron Maiden.1.19900000.9")
        self.assertEqual(self.arguments.album, "Communiqué")
        self.assertEqual(self.arguments.genre, "Rock")
        self.assertTrue(self.arguments.live.bool)
        self.assertTrue(self.arguments.bootleg.bool)
        self.assertFalse(self.arguments.incollection.bool)
        self.assertEqual(self.arguments.upc, "9999999999999")
        self.assertEqual(self.arguments.template(self.arguments), "T03")

    def test_02second(self):
        """
        2. Tester le nombre total de changements.
        """
        with tempfile.TemporaryDirectory() as directory:
            database = os.path.join(directory, os.path.basename(self.arguments.db))
            copy(src=self.arguments.db, dst=database)
            kwargs = {key: val for key, val in vars(self.arguments).items() if val}
            kwargs["db"] = database
            self.assertListEqual(self.arguments.function(**kwargs), [("I.Iron Maiden.1.19900000.4", 1, 1, 4)])

    def test_03third(self):
        """
        3. Tester la mise à jour à l'aide de la fonction configurée dans `MyPythonProject\AudioCD\Interface.py`.
        """
        with tempfile.TemporaryDirectory() as directory:
            database = os.path.join(directory, os.path.basename(self.arguments.db))
            copy(src=self.arguments.db, dst=database)
            kwargs = {key: val for key, val in vars(self.arguments).items() if val}
            kwargs["db"] = database
            self.arguments.function(**kwargs)
            conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
            conn.row_factory = sqlite3.Row
            try:
                with conn:

                    # ALBUMS table.
                    for row in conn.execute("SELECT albumid, album, genre, live, bootleg, incollection, upc FROM albums WHERE rowid=?", (30,)):
                        self.assertEqual(row["albumid"], self.arguments.albumid)
                        self.assertEqual(row["album"], self.arguments.album)
                        self.assertEqual(row["genre"], self.arguments.genre)
                        self.assertTrue(row["live"])
                        self.assertTrue(row["bootleg"])
                        self.assertFalse(row["incollection"])
                        self.assertEqual(row["upc"], self.arguments.upc)

                    # DISCS table.
                    for row in conn.execute("SELECT albumid FROM discs WHERE rowid=?", (34,)):
                        self.assertEqual(row["albumid"], "I.Iron Maiden.1.19900000.9")

                    # TRACKS table.
                    for i in [384, 385, 386, 387]:
                        for row in conn.execute("SELECT albumid FROM tracks WHERE rowid=?", (i,)):
                            self.assertEqual(row["albumid"], "I.Iron Maiden.1.19900000.9")

                conn.close()

            except AssertionError:
                raise
