# -*- coding: utf-8 -*-
import os
import sqlite3
import xml.etree.ElementTree as ElementTree
from itertools import groupby
from operator import itemgetter

from Applications.Tables.shared import convert_tobooleanvalue
from Applications.parsers import database_parser
from Applications.shared import now

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ===============
# Main algorithm.
# ===============

# 1. Register integer to boolean sqlite3 converter.
sqlite3.register_converter("boolean", convert_tobooleanvalue)

# 2. Parse arguments.
arguments = database_parser.parse_args()

# 3. Get albums.
conn = sqlite3.connect(arguments.db, detect_types=sqlite3.PARSE_DECLTYPES)
conn.row_factory = sqlite3.Row
albums = [(None,
           row["artistsort"],
           row["albumsort"],
           row["discid"],
           row["is_live_disc"],
           row["album"],
           row["origyear"],
           row["year"],
           row["genre"],
           row["label"],
           row["upc"],
           row["is_bootleg_album"],
           row["trackid"],
           row["title"],
           row["is_live_track"],
           row["is_bonus"],
           row["track_rowid"],
           row["bootleg_date"],
           row["bootleg_city"],
           row["bootleg_country"],
           row["bootleg_tour"]) for row in conn.execute("SELECT "
                                                        "artistsort, "
                                                        "albumsort, "
                                                        "discid, "
                                                        "is_live_disc, "
                                                        "album, "
                                                        "origyear, "
                                                        "year, "
                                                        "genre, "
                                                        "label, "
                                                        "upc, "
                                                        "is_bootleg AS is_bootleg_album, "
                                                        "trackid, "
                                                        "title, "
                                                        "is_live_track, "
                                                        "is_bonus, "
                                                        "track_rowid, "
                                                        "bootleg_date, "
                                                        "bootleg_city, "
                                                        "bootleg_country, "
                                                        "bootleg_tour "
                                                        "FROM tracks_vw")]
conn.close()

# 4. Build XML structure.
root = ElementTree.Element("Albums", attrib=dict(timestamp=now()))
for artistsort, group1 in groupby(sorted(sorted(sorted(sorted(set(albums), key=itemgetter(12)), key=itemgetter(3)), key=itemgetter(2)), key=itemgetter(1)), key=itemgetter(1)):
    group1 = list(group1)

    artist = ElementTree.SubElement(root, "Artist", attrib=dict(name=artistsort))
    for albumsort, group2 in groupby(group1, key=itemgetter(2)):
        group2 = list(group2)
        albumid = ElementTree.SubElement(artist, "AlbumSort", attrib=dict(id=group2[0][2]))

        # --> Album origyear.
        element = ElementTree.SubElement(albumid, "OrigYear")
        element.text = str(group2[0][6])

        # --> Album year.
        element = ElementTree.SubElement(albumid, "Year")
        element.text = str(group2[0][7])

        # --> Album title.
        element = ElementTree.SubElement(albumid, "Title")
        element.text = group2[0][5]

        # --> Album genre.
        element = ElementTree.SubElement(albumid, "Genre")
        element.text = group2[0][8]

        # --> Album label.
        element = ElementTree.SubElement(albumid, "Label")
        element.text = group2[0][9]

        # --> Album UPC.
        element = ElementTree.SubElement(albumid, "UPC")
        element.text = group2[0][10]

        discs = ElementTree.SubElement(albumid, "Discs")
        for discsort, group3 in groupby(group2, key=itemgetter(3)):
            group3 = list(group3)
            discid = ElementTree.SubElement(discs, "Disc", attrib=dict(id=str(discsort)))
            element = ElementTree.SubElement(discid, "IsLive")
            element.text = str(group3[0][4]).lower()
            tracks = ElementTree.SubElement(discid, "Tracks")
            for track in group3:
                element = ElementTree.SubElement(tracks, "Track", attrib=dict(id=str(track[16])))
                subelement = ElementTree.SubElement(element, "Number")
                subelement.text = str(track[12])
                subelement = ElementTree.SubElement(element, "Title")
                subelement.text = track[13]
                subelement = ElementTree.SubElement(element, "IsLive")
                subelement.text = str(track[14]).lower()
                subelement = ElementTree.SubElement(element, "IsBonus")
                subelement.text = str(track[15]).lower()

# 5. Write XML structure into an UTF-8 plain text file.
ElementTree.ElementTree(root).write(os.path.join(os.path.expandvars("%TEMP%"), "albums.xml"), encoding="UTF-8", xml_declaration=True)
