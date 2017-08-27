# -*- coding: utf-8 -*-
import itertools
from operator import itemgetter
import xml.etree.ElementTree as ET
from collections import namedtuple
from datetime import datetime, date
from Applications.shared import dateformat, now, LOCAL, TEMPLATE4

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========
def audiofileslist(obj):

    root = ET.Element("Files", attrib={"css": "DigitalAudioFiles.css", "title": "Digital Audio Files"})
    
    #  1.a. Last update date.
    se = ET.SubElement(root, "Updated")
    se.text = now()
    
    #  1.b. Scanned directory.
    se = ET.SubElement(root, "Directory")
    se.text = obj.folder
    
    #  2. "FilesList" element.
    se = ET.SubElement(root, "FilesList")
    for file, ctime in sorted([(item[0], int(item[3])) for item in obj.reflist], key=itemgetter(0)):
        sse = ET.SubElement(se, "File", attrib={"seconds": str(ctime), "converted": dateformat(LOCAL.localize(datetime.fromtimestamp(ctime)), TEMPLATE4)})
        sse.text = file
    
    #  3. "RecentFiles" element.
    se = ET.SubElement(root, "RecentFilesList")
    for file, ctime in sorted(sorted([(item[0], int(item[3])) for item in obj.reflist], key=itemgetter(0)), key=itemgetter(1), reverse=True)[:50]:
        sse = ET.SubElement(se, "File", attrib={"seconds": str(ctime), "converted": dateformat(LOCAL.localize(datetime.fromtimestamp(ctime)), TEMPLATE4)})
        sse.text = file
    
    #  4. "FilesByArtist" element.
    se = ET.SubElement(root, "FilesByArtist")
    for artist, groups in obj.groupedby_artist:
        groups = list(groups)
        sse = ET.SubElement(se, "Artist", attrib={"name": artist, "count": str(len(groups))})
        for group in groups:
            ssse = ET.SubElement(sse, "File", attrib={"seconds": str(int(group[3])), "converted": dateformat(LOCAL.localize(datetime.fromtimestamp(group[3])), TEMPLATE4)})
            ssse.text = group[0]
    
    #  5. "ExtensionsList" element.
    se = ET.SubElement(root, "ExtensionsList")
    for extension, count in obj.countby_extension:
        sse = ET.SubElement(se, "Extension", attrib={"name": extension.upper()})
        sse.text = str(count)
    
    #  6. "ArtistsList" element.
    se = ET.SubElement(root, "ArtistsList")
    for artist1, groups in obj.groupedby_artist:
        groups = list(groups)
        sse = ET.SubElement(se, "Artist", attrib={"name": artist1, "count": str(len(groups))})
        groups = [(art, ext, len(list(groups))) for (art, ext), groups in obj.groupedby_artist_extension if art == artist1]
        for artist2, extension, count in groups:
            ssse = ET.SubElement(sse, "Extension", attrib={"name": extension.upper()})
            ssse.text = str(count)

    return root


def rippinglog(reflist):

    nt = namedtuple("nt", "uid date month ripped artist year album upc genre application albumsort artistsort")
    root = ET.Element("Data", attrib=dict(css="firstcss.css"))
    se = ET.SubElement(root, "Updated")
    se.text = now()

    se = ET.SubElement(root, "RippedAudioCD")
    for key, group in itertools.groupby(reflist, key=itemgetter(2)):
        group = list(group)

        sse = ET.SubElement(se, "Month", attrib={"month": dateformat(date(int(key[:4]), int(key[-2:]), 1), "$month $Y"), "count": str(len(group))})
        for row in map(nt._make, group):
            ssse = ET.SubElement(sse, "AudioCD", attrib={"uid": str(row.uid)})

            # Date.
            audiocd = ET.SubElement(ssse, "Ripped")
            audiocd.text = row.date

            # Artist.
            artist = ET.SubElement(ssse, "Artist")
            artist.text = row.artist

            # Year.
            year = ET.SubElement(ssse, "Year")
            year.text = str(row.year)

            # Album.
            album = ET.SubElement(ssse, "Album")
            album.text = row.album

            # Genre.
            genre = ET.SubElement(ssse, "Genre")
            genre.text = row.genre

            # UPC.
            upc = ET.SubElement(ssse, "UPC")
            upc.text = str(row.upc)

            # ArtistSort.
            artistsort = ET.SubElement(ssse, "ArtistSort")
            artistsort.text = row.artistsort

            # AlbumSort.
            albumsort = ET.SubElement(ssse, "AlbumSort")
            albumsort.text = row.albumsort

    return root
