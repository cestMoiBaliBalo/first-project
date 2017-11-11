# -*- coding: utf-8 -*-
"""
Log ripped audio CDs into a plain text file (`%TEMP%\rippedaudiocds.txt`).
"""
import logging.config
import os
import sys
from collections import OrderedDict

import yaml

from Applications.Database.AudioCD.shared import selectlogs
from Applications.parsers import database_parser
from Applications.shared import LOCAL, TEMPLATE4, UTF8, dateformat, getnearestmultiple, gettabs

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding=UTF8) as fp:
    logging.config.dictConfig(yaml.load(fp))
logger = logging.getLogger("Applications.Database.AudioCD")

# ================
# Input arguments.
# ================
database_parser.add_argument("--orderby", nargs="*")
database_parser.add_argument("--print", action="store_true")

# ==========
# Constants.
# ==========
TABSIZE = 3

# ================
# Initializations.
# ================
template, line_number, first, tags_length, tags_width, headers = "", 0, True, {}, {}, ["uid",
                                                                                       "artistsort",
                                                                                       "albumsort",
                                                                                       "artist",
                                                                                       "origyear",
                                                                                       "year",
                                                                                       "album",
                                                                                       "ripped"]

# ===============
# Main algorithm.
# ===============

# 1. Parse arguments.
arguments = database_parser.parse_args()

# 2. Grab arguments.
orderby = arguments.orderby
if not arguments.orderby:
    orderby = ["rowid"]

# 3. Get ripped CDs list.
reflist = [(str(row.rowid), row.artistsort, row.albumsort, row.artist, str(row.origyear), str(row.year), row.album, dateformat(LOCAL.localize(row.ripped), TEMPLATE4)) for row in
           selectlogs(arguments.db, orderby=orderby)]

# 4. Gather audio tags together per family into an ordered dictionary to preserve tags sequence.
tags = OrderedDict(zip(headers, zip(*reflist)))

# 5. Store header length into an ordered dictionary to preserve headers sequence.
headers_length = OrderedDict([(header, len(header)) for header in headers])

# 6. Compute both family maximum length and family maximum allowed width.
for key in tags.keys():
    tags_length[key] = max([len(item) for item in tags[key]])
    tags_width[key] = getnearestmultiple(max([len(item) for item in tags[key]]), multiple=TABSIZE) + TABSIZE

# 7. Apply tabulations to each tag according to its family computed allowed width.
for key in tags.keys():
    tags[key] = ["{0}{1}".format(item, gettabs(tags_width[key] - len(item))).expandtabs(TABSIZE) for item in tags[key]]

# 8. Prepare file header.
for key in tags.keys():
    template = "{0}{{h[{1}]:<{{w[{1}]}}}}".format(template, key)
header = template.format(h=OrderedDict([(header, header.upper()) for header in headers]), w=tags_width)
separator = template.format(h=OrderedDict([(key, "-" * max([headers_length[key], tags_length[key]])) for key in tags.keys()]), w=tags_width)

# 9.a. Display ripped CDs into a plain text file.
if not arguments.print:
    with open(os.path.join(os.path.expandvars("%TEMP%"), "rippedaudiocds.txt"), "w", encoding=UTF8) as fw:
        for rowid, artistsort, albumsort, artist, origyear, year, album, ripped in zip(*[item[1] for item in tags.items()]):
            rowid = "{0:<{w[uid]}}".format("{0:>{w[uid]}}".format(rowid.strip(), w=tags_length), w=tags_width)
            if first or line_number == 100:
                if not first:
                    fw.write("\n\n")
                fw.write("{0}\n".format(separator))
                fw.write("{0}\n".format(header))
                fw.write("{0}\n".format(separator))
                line_number = 0
                first = False
            fw.write("{0}{1}{2}{3}{4}{5}{6}{7}\n".format(rowid, artistsort, albumsort, artist, origyear, year, album, ripped))
            line_number += 1
    sys.exit(0)

# 9.b. Display ripped CDs into console.
for rowid, artistsort, albumsort, artist, origyear, year, album, ripped in zip(*[item[1] for item in tags.items()]):
    rowid = "{0:<{w[uid]}}".format("{0:>{w[uid]}}".format(rowid.strip(), w=tags_length), w=tags_width)
    if first or line_number == 100:
        print("\n\n")
        print("{0}".format(separator))
        print("{0}".format(header))
        print("{0}".format(separator))
        line_number = 0
        first = False
    print("{0}{1}{2}{3}{4}{5}{6}{7}".format(rowid, artistsort, albumsort, artist, origyear, year, album, ripped))
    line_number += 1
sys.exit(0)
