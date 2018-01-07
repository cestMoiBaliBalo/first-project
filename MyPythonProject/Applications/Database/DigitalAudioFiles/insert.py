# -*- coding: utf-8 -*-
import argparse
import csv
import json
import logging.config
import os
import sys

import yaml

from .shared import insertfromfile
from ...parsers import database_parser

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ----------
# Constants.
# ----------
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

# -------
# Parser.
# -------
parser = argparse.ArgumentParser(parents=[database_parser])
parser.add_argument("step", type=int, nargs="+", choices=[1, 2])

# ---------------
# Main algorithm.
# ---------------
if __name__ == "__main__":

    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        logging.config.dictConfig(yaml.load(fp))
    logger = logging.getLogger("Applications.Database.DigitalAudioFiles.insert")

    arguments = parser.parse_args()
    for step in sorted(arguments.step):

        if step == 1:
            with open(TAGS_TXT, encoding="UTF-8-SIG") as txtfile:
                reader = csv.DictReader(txtfile, fieldnames=FIELDNAMES, delimiter=";")
                with open(TAGS_JSON, mode="w") as jsonfile:
                    json.dump([(arguments.db,
                                row["index"],
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
                                row["origyear"])
                               for row in reader], jsonfile, indent=4, ensure_ascii=False)

        if step == 2:
            inserted = []
            if os.path.exists(TAGS_JSON):
                with open(TAGS_JSON) as jsonfile:
                    inserted = insertfromfile(jsonfile)
            logger.debug(inserted)
    sys.exit(0)
