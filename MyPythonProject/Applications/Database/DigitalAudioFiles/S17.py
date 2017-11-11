# -*- coding: utf-8 -*-
import csv
import json
import os
import sys

from Applications.Database.DigitalAudioFiles.shared import database_parser, insertfromfile

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

TAGS_TXT = os.path.join(os.path.expandvars("%TEMP%"), "trackslist.txt")
TAGS_JSON = os.path.join(os.path.expandvars("%TEMP%"), "trackslist.json")
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
database_parser.add_argument("step", type=int, nargs="+", choices=[1, 2])

if __name__ == "__main__":

    arguments = database_parser.parse_args()
    for step in sorted(arguments.step):

        if step == 1:
            with open(TAGS_TXT, encoding="UTF-8-SIG") as txtfile:
                reader = csv.DictReader(txtfile, fieldnames=FIELDNAMES, delimiter=";")
                with open(TAGS_JSON, mode="w") as jsonfile:
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

        if step == 2:
            inserted = []
            if os.path.exists(TAGS_JSON):
                with open(TAGS_JSON) as jsonfile:
                    inserted = insertfromfile(jsonfile, db=arguments.db)
            if inserted:
                print("Albums total changes: {0:>2d}".format(inserted[2]))
                print("Discs  total changes: {0:>2d}".format(inserted[1]))
                print("Tracks total changes: {0:>2d}".format(inserted[0]))

    sys.exit(0)
