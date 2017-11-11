# -*- coding: utf-8 -*-
import os
import re
import sqlite3
import xml.etree.ElementTree as ElementTree

from Applications.parsers import database_parser
from Applications.shared import now

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ================
# Initializations.
# ================
previousart, regex1, regex2, regex3 = "", re.compile(r"[, ]"), re.compile(r"\s+"), re.compile(r"\\")

# ===============
# Main algorithm.
# ===============

# 1. Parse arguments.
arguments = database_parser.parse_args()

# 2. Open database.
c = sqlite3.connect(arguments.db, detect_types=sqlite3.PARSE_DECLTYPES)
c.row_factory = sqlite3.Row

# 3. Initialize XML structure.
root = ElementTree.Element("Data", attrib=dict(timestamp=now()))

# 4. Fetch `albums`, `discs` and `tracks` tables.
for row in c.execute("SELECT DISTINCT substr(albumid, 3, length(albumid)-15) AS key FROM albums ORDER BY key"):

    artist = ElementTree.SubElement(root, "Artist", attrib=dict(name=row["key"]))
    artistid = ElementTree.SubElement(artist, "ArtistID")
    artistid.text = regex1.sub("", row["key"])
    for rowa in c.execute("SELECT artist, year, album, albumid FROM albums WHERE substr(albumid, 3, length(albumid)-15)=? ORDER BY albumid", (row["key"],)):

        # ---------------
        # Albumsort node.
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
        cover.text = "file:///%s" % (
            regex3.sub("/", regex2.sub(r"%20", os.path.join(r"C:\Users\Xavier\Documents\Album Art", rowa["albumid"][:1], rowa["albumid"][2:-13], rowa["albumid"][-12:], r"iPod-Front.jpg"))),)

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

# 5. Display data.
ElementTree.ElementTree(root).write(os.path.join(os.path.expandvars("%TEMP%"), "digitalaudiobase.xml"), encoding="UTF-8", xml_declaration=True)

# 6. Close database.
c.close()
