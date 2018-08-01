# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""
Log ripped audio CDs into a plain text file (`%TEMP%\rippeddiscs.txt`).
"""
import argparse
import logging.config
import os
import sys
from collections import OrderedDict
from contextlib import suppress
from subprocess import run

import yaml

from Applications.Tables.RippedDiscs.shared import selectlogs_fromkeywords, stringify
from Applications.parsers import database_parser
from Applications.shared import UTF8, get_nearestmultiple, get_tabs, partitioner

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ==========
# Constants.
# ==========
TABSIZE = 3
LOGGERS = ["Applications.Tables.RippedDiscs", "MyPythonProject"]
MAPPING = {True: "debug",
           False: "info"}
HEADERS = {False: ["uid", "artistsort", "albumsort", "disc", "artist", "origyear", "year", "album", "ripped"],
           True: ["uid", "artistsort", "albumsort", "disc", "artist", "bootlegdate", "bootlegcity", "bootlegcountry", "bootlegcountry", "ripped"]}

# ================
# Input arguments.
# ================
parser = argparse.ArgumentParser(parents=[database_parser])
parser.add_argument("--console", action="store_true")
parser.add_argument("--debug", action="store_true")
parser.add_argument("--orderby", nargs="*")
arguments = parser.parse_args()

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding=UTF8) as fp:
    config = yaml.load(fp)
for logger in LOGGERS:
    with suppress(KeyError):
        config["loggers"][logger]["level"] = MAPPING[arguments.debug].upper()
logging.config.dictConfig(config)
logger = logging.getLogger("MyPythonProject.AudioCD.Views.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

# ================
# Initializations.
# ================
line_number, first, header, separator, tags, tags_length, tags_width, headers_length = 0, True, {}, {}, {}, {}, {}, {}

# ===============
# Main algorithm.
# ===============

# 2. Grab arguments.
orderby = arguments.orderby
if not arguments.orderby:
    orderby = ["rowid"]

# 3. Get ripped discs lists.
reflist = list(selectlogs_fromkeywords(db=arguments.db, orderby=orderby))
defaultalbums, bootlegalbums = partitioner(reflist, predicate=lambda row: not row.bootleg)
defaultalbums = [tuple(map(stringify, (row.rowid, row.artistsort, row.albumsort, row.disc, row.artist, row.origyear, row.year, row.album, row.ripped))) for row in defaultalbums]
bootlegalbums = [tuple(map(stringify, (row.rowid, row.artistsort, row.albumsort, row.disc, row.artist, row.bootleg_date, row.bootleg_city, row.bootleg_country, row.bootleg_country, row.ripped))) for row in
                 bootlegalbums]
logger.debug(defaultalbums)
logger.debug(bootlegalbums)

for albumtype, albumslist, isbootleg in [("defaultalbums", defaultalbums, False), ("bootlegalbums", bootlegalbums, True)]:

    template = ""

    # 4. Gather audio tags together per family into an ordered dictionary to preserve tags sequence.
    tags[albumtype] = OrderedDict(zip(HEADERS[isbootleg], zip(*albumslist)))

    # 5. Store header length into an ordered dictionary to preserve headers sequence.
    headers_length[albumtype] = OrderedDict((header, len(header)) for header in HEADERS[isbootleg])

    # 6. Compute both family maximum length and family maximum allowed width.
    tags_length[albumtype], tags_width[albumtype] = {}, {}
    for key in tags[albumtype].keys():
        tags_length[albumtype][key] = max(len(item) for item in tags[albumtype][key])
        tags_width[albumtype][key] = get_nearestmultiple(max(len(item) for item in tags[albumtype][key]), multiple=TABSIZE) + TABSIZE

    # 7. Apply tabulations to each tag according to its family computed allowed width.
    for key in tags[albumtype].keys():
        tags[albumtype][key] = ["{0}{1}".format(item, get_tabs(tags_width[albumtype][key] - len(item))).expandtabs(TABSIZE) for item in tags[albumtype][key]]

    # 8. Prepare file header.
    for key in tags[albumtype].keys():
        template = "{0}{{h[{1}]:<{{w[{1}]}}}}".format(template, key)
    logger.debug(template)
    logger.debug(albumtype)
    header[albumtype] = template.format(h=OrderedDict((item, item.upper()) for item in HEADERS[isbootleg]), w=tags_width[albumtype])
    separator[albumtype] = template.format(h=OrderedDict((key, "-" * max(headers_length[albumtype][key], tags_length[albumtype][key])) for key in tags[albumtype].keys()), w=tags_width[albumtype])

# 9.a. Display ripped CDs into a plain text file. Then exit algorithm.
if not arguments.console:
    with open(os.path.join(os.path.expandvars("%TEMP%"), "rippeddiscs.txt"), "w", encoding=UTF8) as fw:
        for rowid, artistsort, albumsort, disc, artist, origyear, year, album, ripped in zip(*[item[1] for item in tags["defaultalbums"].items()]):
            rowid = "{0:<{w[uid]}}".format("{0:>{w[uid]}}".format(rowid.strip(), w=tags_length["defaultalbums"]), w=tags_width["defaultalbums"])
            if first or line_number == 100:
                if not first:
                    fw.write("\n\n")
                fw.write("{0}\n".format(separator["defaultalbums"]))
                fw.write("{0}\n".format(header["defaultalbums"]))
                fw.write("{0}\n".format(separator["defaultalbums"]))
                line_number = 0
                first = False
            fw.write("{0}{1}{2}{3}{4}{5}{6}{7}{8}\n".format(rowid, artistsort, albumsort, disc, artist, origyear, year, album, ripped))
            line_number += 1
    sys.exit(0)

# 9.b. Display ripped CDs into console. Then exit algorithm.
run("CLS", shell=True)
for rowid, artistsort, albumsort, disc, artist, origyear, year, album, ripped in zip(*[item[1] for item in tags["defaultalbums"].items()]):
    rowid = "{0:<{w[uid]}}".format("{0:>{w[uid]}}".format(rowid.strip(), w=tags_length["defaultalbums"]), w=tags_width["defaultalbums"])
    if first or line_number == 100:
        print("\n\n")
        print("{0}".format(separator["defaultalbums"]))
        print("{0}".format(header["defaultalbums"]))
        print("{0}".format(separator["defaultalbums"]))
        line_number = 0
        first = False
    print("{0}{1}{2}{3}{4}{5}{6}{7}{8}".format(rowid, artistsort, albumsort, disc, artist, origyear, year, album, ripped))
    line_number += 1
sys.exit(0)
