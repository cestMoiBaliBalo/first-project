# -*- coding: utf-8 -*-
import os
import re
import sqlite3
import argparse
from Applications.shared import now
import xml.etree.ElementTree as ElementTree

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========
def validdb(arg):
    if not os.path.exists(arg):
        raise argparse.ArgumentTypeError('"{0}" doesn\'t exist.'.format(arg))
    return arg


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--db", dest="database", default=os.path.join(os.path.expandvars("%_COMPUTING%"), "database.db"), type=validdb)


# ================
# Initializations.
# ================
previousart, regex1, regex2, regex3, arguments = "", re.compile(r"[, ]"), re.compile(r"\s+"), re.compile(r"\\"), parser.parse_args()


# ===============
# Main algorithm.
# ===============
c = sqlite3.connect(arguments.database, detect_types=sqlite3.PARSE_DECLTYPES)
c.row_factory = sqlite3.Row


# 1. Initialisation de la structure XML.
root = ElementTree.Element("Data", attrib=dict(css1="digitalaudiobase.css", css2="../backtotop.css", timestamp=now()))


# 2. Itération sur les données composant les tables ALBUMS, DISCS et TRACKS.
for rowa in c.execute("SELECT artist, year, album, albumid FROM albums ORDER BY albumid"):

    # ------------
    # Artist node.
    # ------------
    if previousart != rowa["artist"]:
        previousart = rowa["artist"]
        artist = ElementTree.SubElement(root, "Artist", attrib=dict(name=rowa["artist"]))
        artistid = ElementTree.SubElement(artist, "ArtistID")
        artistid.text = regex1.sub("", rowa["albumid"][2:-13])

    # ---------------
    # AlbumSort node.
    # ---------------
    albumsort = ElementTree.SubElement(artist, "AlbumSort", attrib=dict(id=rowa["albumid"][-12:]))

    # --> Album ID.
    albumid = ElementTree.SubElement(albumsort, "AlbumID")
    albumid.text = "%s%s" % (regex1.sub("", rowa["albumid"][2:-13]), rowa["albumid"][-12:].replace(".", ""))

    # --> Album year.
    year = ElementTree.SubElement(albumsort, "Year")
    year.text = str(rowa["year"])

    # --> Album title.
    album = ElementTree.SubElement(albumsort, "Album")
    album.text = rowa["album"]

    # --> Album cover.
    cover = ElementTree.SubElement(albumsort, "Cover")
    cover.text = "file:///%s" % (regex3.sub("/", regex2.sub(r"%20", os.path.join(r"C:\Users\Xavier\Documents\Album Art", rowa["albumid"][:1], rowa["albumid"][2:-13], rowa["albumid"][-12:], r"iPod-Front.jpg"))),)

    # ----------
    # Disc node.
    # ----------
    for rowd in c.execute("SELECT discid FROM discs WHERE albumid=? ORDER BY discid", (rowa["albumid"],)):

        # --> Disc ID.
        disc = ElementTree.SubElement(albumsort, "Disc", attrib=dict(id=str(rowd["discid"])))

        # --> Tracks listing.
        for rowt in c.execute("SELECT trackid, title FROM tracks WHERE albumid=? and discid=? ORDER BY trackid", (rowa["albumid"], rowd["discid"])):
            track = ElementTree.SubElement(disc, "Track", attrib=dict(id=str(rowt["trackid"])))
            track.text = rowt["title"]


# 3. Restitution des données.
ElementTree.ElementTree(root).write(os.path.join(os.path.expandvars("%TEMP%"), "digitalaudiobase.xml"), encoding="UTF-8", xml_declaration=True)


c.close()
