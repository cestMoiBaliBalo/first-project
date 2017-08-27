# -*- coding: ISO-8859-1 -*-
import os
import tempfile
from contextlib import ExitStack
from Applications.shared import WRITE, UTF16
from Applications.AudioCD.shared import RippedCD

__author__ = 'Xavier ROSSET'


tags = {
    "Album": "Abigail",
    "Year": "1987",
    "Disc": "1/1",
    "Label": "Roadrunner Records",
    "UPC": "016861878825",
    "Artist": "King Diamond",
    "AlbumSortCount": "1",
    "Live": "N",
    "_albumart_1_Front Album Cover": r"C:\Users\Xavier\AppData\Local\Temp\dbp49F2.tmp\9.bin",
    "Track": "9/13",
    "Profile": "Default",
    "Rating": "8",
    "Source": "CD (Lossless)",
    "Encoder": "(FLAC 1.3.0)",
    "ArtistSort": "King Diamond",
    "AlbumArtistSort": "King Diamond",
    "AlbumArtist": "King Diamond",
    "Genre": "Rock",
    "InCollection": "Y",
    "TitleLanguage": "English",
    "Bootleg": "N",
    "Title": "A Mansion in Darkness"
}


with tempfile.TemporaryDirectory() as dir:
    itags = os.path.join(dir, "tags.txt")
    with open(itags, mode=WRITE, encoding=UTF16) as fo:
        for k, v in tags.items():
            fo.write("{0}={1}\n".format(k, v))
    try:
        with RippedCD("default1", itags):
            print("toto")
            raise ValueError("Error!")
    except ValueError as err:
        print(err)


with tempfile.TemporaryDirectory() as dir:
    itags = os.path.join(dir, "tags.txt")
    with open(itags, mode=WRITE, encoding=UTF16) as fo:
        for k, v in tags.items():
            fo.write("{0}={1}\n".format(k, v))
    stack = ExitStack()
    try:
        stack.enter_context(RippedCD("default1", itags))
    except ValueError as err:
        print(err)
    else:
        with stack:
            print("toto")
            raise ValueError("Error!")

