# -*- coding: utf-8 -*-
import json
import logging.config
import os
import unittest
from itertools import chain, dropwhile, groupby, zip_longest
from operator import itemgetter

import yaml

from ..shared import StringFormatter

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
    def setUp(self):
        self.stringformatter = StringFormatter()
        with open(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tests", "test_stringformatter.json")) as fp:
            self.thatlist = json.load(fp)

    def test_01first(self):
        for inp_string, out_string in self.thatlist:
            with self.subTest(inp=inp_string, out=out_string):
                self.assertEqual(self.stringformatter.convert(inp_string), out_string)


class Test02(unittest.TestCase):
    """
    Tester et comprendre la fonction intégrée `itertools.zip_longest`.
    """

    def setUp(self):
        self.mylist = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T"]

    def test_01first(self):
        myiterator = [iter(self.mylist)] * 3
        self.assertListEqual(list(zip_longest(*myiterator)), [("A", "B", "C"), ("D", "E", "F"), ("G", "H", "I"), ("J", "K", "L"), ("M", "N", "O"), ("P", "Q", "R"), ("S", "T", None)])

    def test_02second(self):
        myiterator = [iter(self.mylist)] * 4
        self.assertListEqual(list(zip_longest(*myiterator)), [("A", "B", "C", "D"), ("E", "F", "G", "H"), ("I", "J", "K", "L"), ("M", "N", "O", "P"), ("Q", "R", "S", "T")])

    def test_03third(self):
        myiterator = [iter(self.mylist)] * 6
        self.assertListEqual(list(zip_longest(*myiterator)), [("A", "B", "C", "D", "E", "F"), ("G", "H", "I", "J", "K", "L"), ("M", "N", "O", "P", "Q", "R"), ("S", "T", None, None, None, None)])

    def test_04fourth(self):
        myiterator = [iter(self.mylist)] * 6
        self.assertListEqual(list(enumerate(zip_longest(*myiterator), start=1)),
                             [(1, ("A", "B", "C", "D", "E", "F")), (2, ("G", "H", "I", "J", "K", "L")), (3, ("M", "N", "O", "P", "Q", "R")), (4, ("S", "T", None, None, None, None))])


class Test03(unittest.TestCase):
    """
    Tester le regroupement (par `artistsort`, `albumsort`, `discid` et `trackid`) des albums composant la Digital Audio database.
    """

    def setUp(self):
        with open(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tests", "test2_digitalalbums.json")) as fp:
            self.tree = json.load(fp)

    def test_01first(self):
        mylist = list()
        for artistsort, artist, albums in self.tree:
            mylist.append(artistsort)
        self.assertListEqual(mylist, ["Adams, Bryan", "Judas Priest"])

    def test_02second(self):
        mylist = list()
        for artistsort, artist, albums in self.tree:
            for albumsort, discs in albums:
                mylist.append(albumsort)
        self.assertListEqual(sorted(set(mylist)),
                             ['1.19770000.1',
                              '1.19780000.1',
                              '1.19780000.2',
                              '1.19790000.1',
                              '1.19810000.1',
                              '1.19830000.1',
                              '1.19840000.1',
                              '1.19860000.1',
                              '1.19870000.1',
                              '1.19880000.1',
                              '1.19910000.1',
                              '1.20080000.1'])

    def test_03third(self):
        mylist = list()
        for artistsort, artist, albums in self.tree:
            for albumsort, discs in albums:
                for discid, tracks in discs:
                    for trackid, detail in tracks:
                        mylist.append(list(chain.from_iterable(detail))[5])
        self.assertListEqual(mylist,
                             ['The Only One',
                              'Take Me Back',
                              'This Time',
                              'Straight from the Heart',
                              'Cuts Like a Knife',
                              "I'm Ready",
                              "What's It Gonna Be",
                              "Don't Leave Me Lonely",
                              'Let Him Know',
                              'The Best Was Yet to Come',
                              'One Night Love Affair',
                              "She's Only Happy When She's Dancin'",
                              'Run To You',
                              'Heaven',
                              'Somebody',
                              "Summer Of '69",
                              'Kids Wanna Rock',
                              "It's Only Love",
                              'Long Gone',
                              "Ain't Gonna Cry",
                              'Heat of the Night',
                              'Into the Fire',
                              'Victim of Love',
                              'Another Day',
                              'Native Son',
                              'Only the Strong Survive',
                              'Rebel',
                              'Remembrance Day',
                              'Hearts on Fire',
                              'Home Again',
                              'Is Your Mama Gonna Miss Ya?',
                              "Hey Honey - I'm Packin' You in!",
                              "Can't Stop This Thing We Started",
                              "Thought I'd Died and Gone To Heaven",
                              'Not Guilty',
                              'Vanishing',
                              'House Arrest',
                              'Do I Have To Say the Words?',
                              'There Will Never Be Another Tonight',
                              'All I Want Is You',
                              'Depend on Me',
                              '(Everything) I Do I Do It for You',
                              'If You Wanna Leave Me (Can I Come Too?)',
                              'Touch the Hand',
                              "Don't Drop That Bomb on Me",
                              'Sinner',
                              'Diamonds and Rust',
                              'Starbreaker',
                              'Last Rose of Summer',
                              'Let US Prey/Call for the Priest',
                              'Raw Deal',
                              'Here Come the Tears',
                              'Dissident Aggressor',
                              'Race With the Devil',
                              'Jawbreaker',
                              'Exciter',
                              'White Heat, Red Hot',
                              'Better By You, Better Than Me',
                              'Stained Class',
                              'Invader',
                              'Saints In Hell',
                              'Savage',
                              'Beyond the Realms of Death',
                              'Heroes End',
                              'Fire Burns Below',
                              'Better By You, Better Than Me',
                              'Delivering the Goods',
                              'Rock Forever',
                              'Evening Star',
                              'Hell Bent for Leather',
                              'Take on the World',
                              "Burnin' up",
                              'The Green Manalishi (With the Two-Pronged Crown)',
                              'Killing Machine',
                              'Running Wild',
                              'Before the Dawn',
                              'Evil Fantasies',
                              'Fight for Your Life',
                              'Riding on the Wind',
                              'Exciter',
                              'Running Wild',
                              'Sinner',
                              'The Ripper',
                              'The Green Manalishi (With the Two-Pronged Crown)',
                              'Diamonds and Rust',
                              'Victim of Changes',
                              'Genocide',
                              'Tyrant',
                              'Rock Forever',
                              'Delivering the Goods',
                              'Hell Bent for Leather',
                              'Starbreaker',
                              'Heading out To the Highway',
                              "Don't Go",
                              "Hot Rockin'",
                              'Turning Circles',
                              'Desert Plains',
                              'Solar Angels',
                              'You Say Yes',
                              'All the Way',
                              'Troubleshooter',
                              'On the Run',
                              'Thunder Road',
                              'Desert Plains',
                              'Freewheel Burning',
                              'Jawbreaker',
                              'Rock Hard Ride Free',
                              'The Sentinel',
                              'Love Bites',
                              'Eat Me Alive',
                              'Some Heads Are Gonna Roll',
                              'Night Comes Down',
                              'Heavy Duty',
                              'Defenders of the Faith',
                              'Turbo Lover',
                              'Locked in',
                              'Private Property',
                              'Parental Guidance',
                              'Rock You All around the World',
                              'Out in the Cold',
                              'Wild Nights, Hot & Crazy Days',
                              'Hot for Love',
                              'Reckless',
                              'All Fired up',
                              'Locked in',
                              'Out in the Cold',
                              'Heading out To the Highway',
                              'Metal Gods',
                              'Breaking the Law',
                              'Love Bites',
                              'Some Heads Are Gonna Roll',
                              'The Sentinel',
                              'Private Property',
                              'Rock You All around the World',
                              'Electric Eye',
                              'Turbo Lover',
                              'Freewheel Burning',
                              'Parental Guidance',
                              'Living after Midnight',
                              "You've Got Another Thing Comin'",
                              'Ram It down',
                              'Heavy Metal',
                              'Love Zone',
                              'Come and Get It',
                              'Hard as Iron',
                              'Blood Red Skies',
                              "I'm a Rocker",
                              'Johnny B. Goode',
                              'Love You To Death',
                              'Monsters of Rock',
                              'Night Comes down',
                              'Bloodstone',
                              'Dawn of Creation',
                              'Prophecy',
                              'Awakening',
                              'Revelations',
                              'The Four Horsemen',
                              'War',
                              'Sands of Time',
                              'Pestilence and Plague',
                              'Death',
                              'Peace',
                              'Conquest',
                              'Lost Love',
                              'Persecution',
                              'Solitude',
                              'Exiled',
                              'Alone',
                              'Shadows in the Flame',
                              'Visions',
                              'Hope',
                              'New Beginnings',
                              'Calm before the Storm',
                              'Nostradamus',
                              'Future of Mankind'])


class Test08(unittest.TestCase):
    """
    Tester et comprendre la fonction intégrée `itertools.chain`.
    """

    def setUp(self):
        self.mylist = [("A", "B", "C"), ("D", "E", "F"), ("G", "H", "I"), ("J", "K", "L"), ("M", "N", "O"), ("P", "Q", "R"), ("S", "T", "U")]

    def test_01first(self):
        self.assertListEqual(list(chain(*self.mylist)), ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U"])

    def test_02second(self):
        self.assertListEqual(list(chain.from_iterable(self.mylist)), ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U"])


class Test09(unittest.TestCase):
    """
    Tester et comprendre l'utilisation d'un iterator object à l'aide de la fonction intégrée `iter`.
    """

    def setUp(self):
        self.mylist = iter([4, 3, 8, 7, 5, 9, 6, 0, 1, 2])

    def test_01first(self):
        mylist = list()
        for item in self.mylist:
            if item >= 9:
                mylist.append(item)
                break
        for item in self.mylist:
            mylist.append(item)
        self.assertListEqual(mylist, [9, 6, 0, 1, 2])

    def test_02second(self):
        mylist = list()
        for item in self.mylist:
            if item >= 4:
                mylist.append(item)
                break
        for item in self.mylist:
            mylist.append(item)
        self.assertListEqual(mylist, [4, 3, 8, 7, 5, 9, 6, 0, 1, 2])


class Test10(unittest.TestCase):
    """
    Tester et comprendre l'utilisation d'un iterator object à l'aide de la fonction intégrée `iter`.
    """

    def setUp(self):
        self.mylist = iter([4, 5, 7, 3, 8, 9, 6, 0, 1, 2])

    def test_01first(self):

        def myfunc(x):
            if not x % 3:
                return True
            return False

        mylist = list()
        for item in self.mylist:
            if myfunc(item):
                mylist.append(item)
                break
        for item in self.mylist:
            mylist.append(item)
        self.assertListEqual(mylist, [3, 8, 9, 6, 0, 1, 2])


class Test11(unittest.TestCase):
    """
    Tester et comprendre l'utilisation de la fonction intégrée `itertools.dropwhile`.
    """

    def setUp(self):
        self.mylist = [4, 5, 7, 3, 8, 9, 6, 0, 1, 2]

    def test_01first(self):
        def myfunc(x):
            if x % 3:
                return True
            return False

        self.assertListEqual(list(dropwhile(myfunc, self.mylist)), [3, 8, 9, 6, 0, 1, 2])


class Test12(unittest.TestCase):
    """
    Tester la création du regroupement (par `artistsort`, `albumsort`, `discid` et `trackid`) des albums composant la Digital Audio base.
    """

    def setUp(self):
        with open(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tests", "test1_digitalalbums.json")) as fp:
            albumslist = json.load(fp)
        if albumslist:
            albumslist = sorted(sorted(sorted(sorted(albumslist, key=itemgetter(4)), key=itemgetter(3)), key=itemgetter(2)), key=lambda i: (i[0], i[1]))
            self.albumslist = [(artistsort, artist,
                                [(albumid, [(discid, [(trackid, list(sssgroup)) for trackid, sssgroup in groupby(ssgroup, key=itemgetter(4))]) for discid, ssgroup in groupby(subgroup, key=itemgetter(3))]) for
                                 albumid, subgroup in
                                 groupby(group, key=itemgetter(2))]) for (artistsort, artist), group in groupby(albumslist, key=lambda i: (i[0], i[1]))]

    def test_01first(self):
        mylist = list()
        for artistsort, artist, albums in self.albumslist:
            mylist.append(artistsort)
        self.assertListEqual(mylist, ["Adams, Bryan", "Judas Priest"])

    def test_02second(self):
        mylist = list()
        for artistsort, artist, albums in self.albumslist:
            for albumsort, discs in albums:
                mylist.append(albumsort)
        self.assertListEqual(sorted(set(mylist)),
                             ['1.19770000.1',
                              '1.19780000.1',
                              '1.19780000.2',
                              '1.19790000.1',
                              '1.19810000.1',
                              '1.19830000.1',
                              '1.19840000.1',
                              '1.19860000.1',
                              '1.19870000.1',
                              '1.19880000.1',
                              '1.19910000.1',
                              '1.20080000.1'])

    def test_03third(self):
        mylist = list()
        for artistsort, artist, albums in self.albumslist:
            for albumsort, discs in albums:
                for discid, tracks in discs:
                    for trackid, detail in tracks:
                        mylist.append(list(chain.from_iterable(detail))[5])
        self.assertListEqual(mylist,
                             ['The Only One',
                              'Take Me Back',
                              'This Time',
                              'Straight from the Heart',
                              'Cuts Like a Knife',
                              "I'm Ready",
                              "What's It Gonna Be",
                              "Don't Leave Me Lonely",
                              'Let Him Know',
                              'The Best Was Yet to Come',
                              'One Night Love Affair',
                              "She's Only Happy When She's Dancin'",
                              'Run To You',
                              'Heaven',
                              'Somebody',
                              "Summer Of '69",
                              'Kids Wanna Rock',
                              "It's Only Love",
                              'Long Gone',
                              "Ain't Gonna Cry",
                              'Heat of the Night',
                              'Into the Fire',
                              'Victim of Love',
                              'Another Day',
                              'Native Son',
                              'Only the Strong Survive',
                              'Rebel',
                              'Remembrance Day',
                              'Hearts on Fire',
                              'Home Again',
                              'Is Your Mama Gonna Miss Ya?',
                              "Hey Honey - I'm Packin' You in!",
                              "Can't Stop This Thing We Started",
                              "Thought I'd Died and Gone To Heaven",
                              'Not Guilty',
                              'Vanishing',
                              'House Arrest',
                              'Do I Have To Say the Words?',
                              'There Will Never Be Another Tonight',
                              'All I Want Is You',
                              'Depend on Me',
                              '(Everything) I Do I Do It for You',
                              'If You Wanna Leave Me (Can I Come Too?)',
                              'Touch the Hand',
                              "Don't Drop That Bomb on Me",
                              'Sinner',
                              'Diamonds and Rust',
                              'Starbreaker',
                              'Last Rose of Summer',
                              'Let US Prey/Call for the Priest',
                              'Raw Deal',
                              'Here Come the Tears',
                              'Dissident Aggressor',
                              'Race With the Devil',
                              'Jawbreaker',
                              'Exciter',
                              'White Heat, Red Hot',
                              'Better By You, Better Than Me',
                              'Stained Class',
                              'Invader',
                              'Saints In Hell',
                              'Savage',
                              'Beyond the Realms of Death',
                              'Heroes End',
                              'Fire Burns Below',
                              'Better By You, Better Than Me',
                              'Delivering the Goods',
                              'Rock Forever',
                              'Evening Star',
                              'Hell Bent for Leather',
                              'Take on the World',
                              "Burnin' up",
                              'The Green Manalishi (With the Two-Pronged Crown)',
                              'Killing Machine',
                              'Running Wild',
                              'Before the Dawn',
                              'Evil Fantasies',
                              'Fight for Your Life',
                              'Riding on the Wind',
                              'Exciter',
                              'Running Wild',
                              'Sinner',
                              'The Ripper',
                              'The Green Manalishi (With the Two-Pronged Crown)',
                              'Diamonds and Rust',
                              'Victim of Changes',
                              'Genocide',
                              'Tyrant',
                              'Rock Forever',
                              'Delivering the Goods',
                              'Hell Bent for Leather',
                              'Starbreaker',
                              'Heading out To the Highway',
                              "Don't Go",
                              "Hot Rockin'",
                              'Turning Circles',
                              'Desert Plains',
                              'Solar Angels',
                              'You Say Yes',
                              'All the Way',
                              'Troubleshooter',
                              'On the Run',
                              'Thunder Road',
                              'Desert Plains',
                              'Freewheel Burning',
                              'Jawbreaker',
                              'Rock Hard Ride Free',
                              'The Sentinel',
                              'Love Bites',
                              'Eat Me Alive',
                              'Some Heads Are Gonna Roll',
                              'Night Comes Down',
                              'Heavy Duty',
                              'Defenders of the Faith',
                              'Turbo Lover',
                              'Locked in',
                              'Private Property',
                              'Parental Guidance',
                              'Rock You All around the World',
                              'Out in the Cold',
                              'Wild Nights, Hot & Crazy Days',
                              'Hot for Love',
                              'Reckless',
                              'All Fired up',
                              'Locked in',
                              'Out in the Cold',
                              'Heading out To the Highway',
                              'Metal Gods',
                              'Breaking the Law',
                              'Love Bites',
                              'Some Heads Are Gonna Roll',
                              'The Sentinel',
                              'Private Property',
                              'Rock You All around the World',
                              'Electric Eye',
                              'Turbo Lover',
                              'Freewheel Burning',
                              'Parental Guidance',
                              'Living after Midnight',
                              "You've Got Another Thing Comin'",
                              'Ram It down',
                              'Heavy Metal',
                              'Love Zone',
                              'Come and Get It',
                              'Hard as Iron',
                              'Blood Red Skies',
                              "I'm a Rocker",
                              'Johnny B. Goode',
                              'Love You To Death',
                              'Monsters of Rock',
                              'Night Comes down',
                              'Bloodstone',
                              'Dawn of Creation',
                              'Prophecy',
                              'Awakening',
                              'Revelations',
                              'The Four Horsemen',
                              'War',
                              'Sands of Time',
                              'Pestilence and Plague',
                              'Death',
                              'Peace',
                              'Conquest',
                              'Lost Love',
                              'Persecution',
                              'Solitude',
                              'Exiled',
                              'Alone',
                              'Shadows in the Flame',
                              'Visions',
                              'Hope',
                              'New Beginnings',
                              'Calm before the Storm',
                              'Nostradamus',
                              'Future of Mankind'])
