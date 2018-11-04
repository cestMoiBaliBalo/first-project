# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import logging.config
import os
import sqlite3

import yaml

from Applications.AudioCD.shared import get_xreferences

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))

found, (artistid, albumid, artist_path, album_path, album, is_bootleg, basename, extension) = get_xreferences(r"F:\K\Kiss\1\1975.2 - Alive_\CD2\1.Monkey's Audio\1.19750000.2.12.D2.T01.ape")
if found:
    print(artistid)
    print(albumid)
    print(artist_path)
    print(album_path)
    print(album)
    print(is_bootleg)
    print(basename)
    print(extension)

# for items in get_albums(r"f:\a\adams, bryan"):
#     print(items)
# for items in get_albums(r"f:\s\springsteen, bruce\2"):
#     print(items)


conn = sqlite3.connect(r"G:\Computing\Resources\xreferences.db")
# for row in conn.execute("SELECT * FROM artists ORDER BY artistid"):
#     print(row)
# for row in conn.execute("SELECT * FROM albums ORDER BY artistid, albumid"):
#     print(row)
for row in conn.execute("SELECT * FROM files WHERE artistid=? AND extension=? ORDER BY artistid, albumid, file", ("Dire Straits", "mp3")):
    print(row)
conn.close()
