# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import logging.config
import os
import sys
from collections import OrderedDict

import yaml

from Applications.Database.AudioCD.shared import selectlogs_fromuid
from Applications.parsers import database_parser
from Applications.shared import LOCAL, TEMPLATE4, UTC, dateformat, getnearestmultiple

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))


# ==========
# Functions.
# ==========
def clean_field(arg):
    if arg is None:
        return ""
    return arg


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser(parents=[database_parser])
parser.add_argument("uid", type=int)

# ==========
# Arguments.
# ==========
arguments = parser.parse_args()

# ================
# Initializations.
# ================
tags = ("ROWID",
        "Ripped",
        "Artistsort",
        "Albumsort",
        "Artist",
        "Origyear",
        "Year",
        "Album",
        "Genre",
        "Label",
        "UPC",
        "Disc",
        "Tracks",
        "Application",
        "UTC_Created",
        "UTC_Modified")

# ===============
# Main algorithm.
# ===============

# Get tags and values.
result = list(selectlogs_fromuid(arguments.uid, db=arguments.db))
if not result:
    sys.exit(1)

# Pretty print tags.
x = max([len(item) for item in tags])
y = getnearestmultiple(x, multiple=3)
tags = ["{0:<{width}}".format(item, width=y) for item in tags]

# Pretty print values.
row = result[0]
values = (str(row.rowid),
          dateformat(UTC.localize(row.ripped).astimezone(LOCAL), TEMPLATE4),
          row.artistsort,
          row.albumsort,
          row.artist,
          str(row.origyear),
          str(row.year),
          row.album,
          row.genre,
          clean_field(row.label),
          row.upc,
          str(row.disc),
          str(row.tracks),
          row.application,
          dateformat(UTC.localize(row.utc_created).astimezone(LOCAL), TEMPLATE4),
          clean_field(row.utc_modified))
x = max([len(item) for item in values])
y = getnearestmultiple(x, multiple=3) + 3
values = ["{0:<{width}}".format(item, width=y) for item in values]

# Write temporary output file.
with open(os.path.join(os.path.expandvars("%TEMP%"), "rippinglog_{0}.tmp".format(arguments.uid)), mode="w", encoding="ISO-8859-1") as fw:
    for k, v in OrderedDict(zip(tags, values)).items():
        fw.write("{0}: {1}\n".format(k, v))

# Exit algorithm.
sys.exit(0)
