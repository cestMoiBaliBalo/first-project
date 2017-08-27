# -*- coding: utf-8 -*-
from Applications.Database.DigitalAudioFiles.shared import selectfromartist, selectdiscs, selecttracks, selectalbums
from contextlib import contextmanager

__author__ = 'Xavier ROSSET'


@contextmanager
def toto(s, char="-"):
    print("\n{0}".format(char*len(s)))
    yield s
    print(char*len(s))


for albumid in [row.albumid for row in selectfromartist(artist="david bowie") if row]:
    with toto(albumid):
        print(albumid)
    print([row.album for row in selectalbums(albumid=albumid)][0])
    for discid in [row.discid for row in selectdiscs(albumid=albumid) if row]:
        print("\nCD #{0}".format(discid))
        for trackid, title in [(row.trackid, row.title) for row in selecttracks(albumid=albumid, discid=discid) if row]:
            print("{0:>2d}. {1}".format(trackid, title))
