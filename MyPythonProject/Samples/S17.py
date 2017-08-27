# -*- coding: utf-8 -*-
import os
import csv
import json
from Applications.Database.DigitalAudioFiles.shared import insertfromfile

__author__ = 'Xavier ROSSET'


FIELDNAMES = ["index",
              "albumsort",
              "titlesort",
              "artistsort",
              "artist",
              "year",
              "album",
              "genre",
              "discid",
              "discs",
              "publisher",
              "trackid",
              "tracks",
              "title",
              "live",
              "bootleg",
              "incollection",
              "upc",
              "encodingyear",
              "titlelanguage",
              "origyear"]
TAGS = os.path.join(os.path.expandvars("%TEMP%"), "audiotags.json")


with open(os.path.join(os.path.expandvars("%TEMP%"), "audiotags.txt"), encoding="UTF-8") as txtfile:
    reader = csv.DictReader(txtfile, fieldnames=FIELDNAMES, delimiter=";")
    with open(TAGS, mode="w", encoding="UTF-8") as jsonfile:
        json.dump([(row["index"],
                    row["albumsort"],
                    row["titlesort"],
                    row["artist"],
                    row["year"],
                    row["album"],
                    row["genre"],
                    row["discid"],
                    row["discs"],
                    row["publisher"],
                    row["trackid"],
                    row["tracks"],
                    row["title"],
                    row["live"],
                    row["bootleg"],
                    row["incollection"],
                    row["upc"],
                    row["encodingyear"],
                    row["titlelanguage"],
                    row["origyear"]) for row in reader], jsonfile, indent=4, ensure_ascii=False)

inserted = []
if os.path.exists(TAGS):
    with open(TAGS, encoding="UTF-8") as jsonfile:
        inserted = insertfromfile(jsonfile)
print(inserted)
