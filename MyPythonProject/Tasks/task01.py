# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import logging.config
import os
import sys
from collections import OrderedDict

import yaml

from Applications.Database.AudioCD.shared import selectlogs_fromuid
from Applications.shared import LOCAL, TEMPLATE4, UTC, dateformat, DATABASE, TESTDATABASE

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))

db = {True: TESTDATABASE, False: DATABASE}

parser = argparse.ArgumentParser()
parser.add_argument("uid", type=int)
parser.add_argument("-t", "--test", action="store_true")

arguments = parser.parse_args()

result = list(selectlogs_fromuid(arguments.uid, db=db[arguments.test]))
if not result:
    sys.exit(1)
row = result[0]
with open(os.path.join(os.path.expandvars("%TEMP%"), "rippinglog_{0}.txt".format(arguments.uid)), mode="w", encoding="ISO-8859-1") as fw:
    for k, v in OrderedDict(zip(("rowid", "ripped", "artistsort", "albumsort", "artist", "origyear", "year", "album", "label", "genre", "upc", "application", "disc", "tracks", "utc_created", "utc_modified"),
                                (row.rowid,
                                 dateformat(UTC.localize(row.ripped).astimezone(LOCAL), TEMPLATE4),
                                 row.artistsort,
                                 row.albumsort,
                                 row.artist,
                                 row.origyear,
                                 row.year,
                                 row.album,
                                 row.label,
                                 row.genre,
                                 row.upc,
                                 row.application,
                                 row.disc,
                                 row.tracks,
                                 dateformat(UTC.localize(row.utc_created).astimezone(LOCAL), TEMPLATE4),
                                 row.utc_modified))).items():
        fw.write("{0};{1}\n".format(k, v))
sys.exit(0)
