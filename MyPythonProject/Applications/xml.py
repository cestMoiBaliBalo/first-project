# -*- coding: utf-8 -*-
import itertools
import os
import re
import xml.etree.ElementTree as ET
from collections import namedtuple
from datetime import date, datetime
from operator import itemgetter

from Applications.shared import LOCAL, TEMPLATE4, UTC, dateformat, getrippingapplication, now

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


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

    # 3. "RecentFiles" element.
    se = ET.SubElement(root, "RecentFilesList")
    for file, ctime in sorted(sorted([(item[0], int(item[3])) for item in obj.reflist], key=itemgetter(0)), key=itemgetter(1), reverse=True)[:50]:
        sse = ET.SubElement(se, "File", attrib={"seconds": str(ctime), "converted": dateformat(LOCAL.localize(datetime.fromtimestamp(ctime)), TEMPLATE4)})
        sse.text = file

    # 4. "FilesByArtist" element.
    se = ET.SubElement(root, "FilesByArtist")
    for artist, groups in obj.groupedby_artist:
        groups = list(groups)
        sse = ET.SubElement(se, "Artist", attrib={"name": artist, "count": str(len(groups))})
        for group in groups:
            ssse = ET.SubElement(sse, "File", attrib={"seconds": str(int(group[3])), "converted": dateformat(LOCAL.localize(datetime.fromtimestamp(group[3])), TEMPLATE4)})
            ssse.text = group[0]

    # 5. "ExtensionsList" element.
    se = ET.SubElement(root, "ExtensionsList")
    for extension, count in obj.countby_extension:
        sse = ET.SubElement(se, "Extension", attrib={"name": extension.upper()})
        sse.text = str(count)

    # 6. "ArtistsList" element.
    se = ET.SubElement(root, "ArtistsList")
    for artist1, groups in obj.groupedby_artist:
        groups = list(groups)
        sse = ET.SubElement(se, "Artist", attrib={"name": artist1, "count": str(len(groups))})
        groups = [(art, ext, len(list(groups))) for (art, ext), groups in obj.groupedby_artist_extension if art == artist1]
        for artist2, extension, count in groups:
            ssse = ET.SubElement(sse, "Extension", attrib={"name": extension.upper()})
            ssse.text = str(count)

    return root


def rippinglog_view1(reflist):
    """

    :param reflist:
    :return:
    """
    record = namedtuple("record", "rowid readable_date readable_month ripped artist year album upc genre application albumsort artistsort")
    root = ET.Element("rippinglogs")
    se = ET.SubElement(root, "created")
    se.text = now()

    for key, group in itertools.groupby(reflist, key=itemgetter(2)):
        group = list(group)
        se = ET.SubElement(root, "month", attrib={"label": dateformat(date(int(key[:4]), int(key[-2:]), 1), "$month $Y"), "count": str(len(group))})
        for row in map(record._make, group):
            sse = ET.SubElement(se, "rippinglog", attrib={"uid": str(row.rowid)})

            # ArtistSort.
            _artistsort = ET.SubElement(sse, "artistsort")
            _artistsort.text = row.artistsort

            # AlbumSort.
            _albumsort = ET.SubElement(sse, "albumsort")
            _albumsort.text = row.albumsort

            # Artist.
            _artist = ET.SubElement(sse, "artist")
            _artist.text = row.artist

            # Year.
            _year = ET.SubElement(sse, "year")
            _year.text = str(row.year)

            # Album.
            _album = ET.SubElement(sse, "album")
            _album.text = row.album

            # Genre.
            _genre = ET.SubElement(sse, "genre")
            _genre.text = row.genre

            # UPC.
            _upc = ET.SubElement(sse, "upc")
            _upc.text = str(row.upc)

            # Ripped date.
            _rippeddate = ET.SubElement(sse, "ripped", attrib=dict(ts=str(row.readable_date[1])))
            _rippeddate.text = row.readable_date[0]

    return root


def rippinglog_view2(reflist):
    """

    :param reflist:
    :return:
    """
    root = ET.Element("rippinglogs")
    se = ET.SubElement(root, "created")
    se.text = now()

    for rowid, readable_date, ripped, artist, year, album, upc, genre, application, albumsort, artistsort in reflist:
        sse = ET.SubElement(root, "rippinglog", attrib={"uid": str(rowid)})

        # ArtistSort.
        _artistsort = ET.SubElement(sse, "artistsort")
        _artistsort.text = artistsort

        # AlbumSort.
        _albumsort = ET.SubElement(sse, "albumsort")
        _albumsort.text = albumsort

        # Artist.
        _artist = ET.SubElement(sse, "artist")
        _artist.text = artist

        # Year.
        _year = ET.SubElement(sse, "year")
        _year.text = str(year)

        # Album.
        _album = ET.SubElement(sse, "album")
        _album.text = album

        # Genre.
        _genre = ET.SubElement(sse, "genre")
        _genre.text = genre

        # UPC.
        _upc = ET.SubElement(sse, "upc")
        _upc.text = str(upc)

        # Ripped date.
        _rippeddate = ET.SubElement(sse, "ripped", attrib=dict(ts=str(readable_date[1])))
        _rippeddate.text = readable_date[0]

    return root


def rippinglog_in(source):
    """
    Parse an XML ripping log(s) tree taken from `source`.

    :param source: XML ripping log(s) tree.
    :return: ripping log(s) record(s) gathered together into a namedtuple `record`.
    """
    record = namedtuple("record", "artist origyear year album disc tracks genre upc label ripped application artistsort albumsort")
    tree = ET.parse(source)
    rippinglogs = tree.getroot()
    for log in rippinglogs.findall("./rippinglog"):
        yield record._make((log.findtext("artist", ""),
                            log.findtext("origyear", log.findtext("year", "0")),
                            log.findtext("year", "0"),
                            log.findtext("album", ""),
                            log.findtext("disc", 1),
                            log.findtext("tracks", 10),
                            log.findtext("genre", "Rock"),
                            log.findtext("upc", "0"),
                            log.findtext("publisher"),
                            int(log.get("ripped", UTC.localize(datetime.utcnow()).timestamp())),  # Unix epoch time composed of 10 digits.
                            log.findtext("application", getrippingapplication()),
                            log.findtext("artistsort", ""),
                            log.findtext("albumsort", "")))


def digitalalbums_in(source):
    """
    Parse an XML digital albums(s) tree taken from `source`.

    :param source: XML digital albums(s) tree.
    :return:
    """
    onetrack = namedtuple("onetrack",
                          "albumid albumsort titlesort artist year album genre discnumber totaldiscs label tracknumber totaltracks title live bootleg incollection upc encodingyear language origyear "
                          "lastplayed playedcount album_created disc_created track_created")
    tree = ET.parse(source)
    albums = tree.getroot()
    for album in albums.findall("./album"):
        albumid = "{0}.{1}.{2}".format(album.findtext("artistsort", "")[0], album.findtext("artistsort", ""), album.findtext("albumsort", ""))
        artist = album.findtext("artist", "")
        year = album.findtext("year", "0")
        album_title = album.findtext("title", "")
        genre = album.findtext("genre", "Rock")
        totaldiscs = album.findtext("totaldiscs", "0")
        label = album.findtext("label", "")
        live = album.findtext("live", "N")
        bootleg = album.findtext("bootleg", "N")
        incollection = album.findtext("incollection", "N")
        upc = album.findtext("upc", "")
        encodingyear = album.findtext("encodingyear", dateformat(UTC.localize(datetime.utcnow()), "$Y"))
        language = album.findtext("language", "English")
        origyear = album.findtext("origyear", album.findtext("year", "0"))
        lastplayed = album.findtext("lastplayed")
        playedcount = album.findtext("playedcount", "0")
        album_created = int(album.get("created", str(int(UTC.localize(datetime.utcnow()).timestamp()))))

        for disc in album.findall("./discs/disc"):
            disc_number = disc.get("uid", "0")
            disc_created = int(disc.get("created", str(int(UTC.localize(datetime.utcnow()).timestamp()))))
            totaltracks = disc.findtext("totaltracks", "0")

            for track in disc.findall("./tracks/track"):
                track_number = track.get("uid", "0")
                track_title = track.findtext("title", "")
                track_created = int(track.get("created", str(int(UTC.localize(datetime.utcnow()).timestamp()))))
                yield onetrack._make((albumid, "", "", artist, year, album_title, genre, disc_number, totaldiscs, label, track_number, totaltracks, track_title, live, bootleg, incollection, upc, encodingyear,
                                      language, origyear, lastplayed, playedcount, album_created, disc_created, track_created))


def toto():
    regex = re.compile(r"\B\((\d)/\d\)$")
    tree = ET.parse(r"C:\Users\Xavier\AppData\Local\Temp\rippedcd.xml")
    logs = tree.getroot()
    for log in logs.findall("./rippinglog"):

        disc_element = log.find("./disc")
        if not disc_element:
            disc = "1"
            album = log.findtext("./album")
            if album:
                match = regex.search(album)
                if match:
                    disc = match.group(1)
            if int(disc) > 1:
                disc_element = ET.Element("disc")
                disc_element.text = disc
                log.append(disc_element)

        origyear_element = log.find("./origyear")
        if not origyear_element:
            origyear_element = ET.Element("origyear")
            origyear_element.text = log.findtext("./year")
            log.append(origyear_element)

    ET.ElementTree(logs).write(os.path.join(os.path.expandvars("%TEMP%"), "rippedcd.xml"), encoding="UTF-8", xml_declaration=True)


if __name__ == "__main__":
    toto()
