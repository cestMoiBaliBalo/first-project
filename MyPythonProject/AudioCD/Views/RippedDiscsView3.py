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

import jinja2
import yaml

from Applications.Tables.RippedDiscs.shared import selectlogs_fromkeywords, stringify
from Applications.parsers import database_parser
from Applications.shared import TemplatingEnvironment, UTF8, get_nearestmultiple, get_tabs, grouper, partitioner

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ==========
# Constants.
# ==========
TABSIZE = 3
LOGGERS = ["Applications.Tables.RippedDiscs", "MyPythonProject"]
HEADERS = {False: ["uid", "artistsort", "albumsort", "disc", "artist", "origyear", "year", "album", "ripped"],
           True: ["uid", "artistsort", "albumsort", "disc", "artist", "bootlegdate", "bootlegcity", "bootlegcountry", "bootlegtour", "ripped"]}
MAPPING = {True: "debug",
           False: "info"}

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
# Jinja2 template.
# ================
TEMPLATE = TemplatingEnvironment(loader=jinja2.FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "AudioCD", "Templates")))

# ================
# Initializations.
# ================
line_number, header, separator, tags, tags_length, tags_width, headers_length, content = 0, {}, {}, {}, {}, {}, {}, {}

# ===============
# Main algorithm.
# ===============

# 1. Grab arguments.
orderby = arguments.orderby
if not arguments.orderby:
    orderby = ["rowid"]

# 2. Get ripped discs lists.
reflist = list(selectlogs_fromkeywords(db=arguments.db, orderby=orderby))
defaultalbums, bootlegalbums = partitioner(reflist, predicate=lambda row: not row.bootleg)
defaultalbums = [tuple(map(stringify, (row.rowid, row.artistsort, row.albumsort, row.disc, row.artist, row.origyear, row.year, row.album, row.ripped))) for row in defaultalbums]
bootlegalbums = [tuple(map(stringify, (row.rowid, row.artistsort, row.albumsort, row.disc, row.artist, row.bootleg_date, row.bootleg_city, row.bootleg_country, row.bootleg_tour, row.ripped))) for row in
                 bootlegalbums]
logger.debug(defaultalbums)
logger.debug(bootlegalbums)

for albumtype, albumslist, isbootleg in [("defaultalbums", defaultalbums, False), ("bootlegalbums", bootlegalbums, True)]:

    # 3. Gather audio tags together per family into an ordered dictionary to preserve tags sequence.
    tags[albumtype] = OrderedDict(zip(HEADERS[isbootleg], zip(*albumslist)))

    # 4. Store header length into an ordered dictionary to preserve headers sequence.
    headers_length[albumtype] = OrderedDict((header, len(header)) for header in HEADERS[isbootleg])

    # 5. Compute both family maximum length and family maximum allowed width.
    tags_length[albumtype] = {key: max(len(item) for item in tags[albumtype][key]) for key in tags[albumtype].keys()}
    tags_width[albumtype] = {key: get_nearestmultiple(max(len(item) for item in tags[albumtype][key]), multiple=TABSIZE) + TABSIZE for key in tags[albumtype].keys()}

    # 6. Apply tabulations to each tag according to its family computed allowed width.
    tags[albumtype] = {key: ["{0}{1}".format(item, get_tabs(tags_width[albumtype][key] - len(item))).expandtabs(TABSIZE) for item in tags[albumtype][key]] for key in tags[albumtype].keys()}

    # 7. Prepare file header.
    template = ""
    for key in tags[albumtype].keys():
        template = "{0}{{h[{1}]:<{{w[{1}]}}}}".format(template, key)
    logger.debug(template)
    logger.debug(albumtype)
    header[albumtype] = template.format(h=OrderedDict((item, item.upper()) for item in HEADERS[isbootleg]), w=tags_width[albumtype])
    separator[albumtype] = template.format(h=OrderedDict((key, "-" * max(headers_length[albumtype][key], tags_length[albumtype][key])) for key in tags[albumtype].keys()), w=tags_width[albumtype])

for albumtype in ["defaultalbums", "bootlegalbums"]:
    try:
        content[albumtype] = [
            ("{0:<{w[uid]}}".format("{0:>{w[uid]}}".format(rowid.strip(), w=tags_length[albumtype]), w=tags_width[albumtype]), artistsort, albumsort, disc, artist, field1, field2, field3, field4, ripped)
            for rowid, artistsort, albumsort, disc, artist, field1, field2, field3, field4, ripped in zip(*[value for _, value in tags[albumtype].items()])
        ]
    except ValueError:
        content[albumtype] = [
            ("{0:<{w[uid]}}".format("{0:>{w[uid]}}".format(rowid.strip(), w=tags_length[albumtype]), w=tags_width[albumtype]), artistsort, albumsort, disc, artist, field1, field2, field3, ripped)
            for rowid, artistsort, albumsort, disc, artist, field1, field2, field3, ripped in zip(*[value for _, value in tags[albumtype].items()])
        ]

# 8.a. Write ripped discs into a plain text file. Then exit algorithm.
if not arguments.console:
    with open(os.path.join(os.path.expandvars("%TEMP%"), "rippeddiscs.txt"), "w", encoding=UTF8) as fw:
        for albumtype in ["defaultalbums", "bootlegalbums"]:
            fw.write(TEMPLATE.environment.get_template("T01").render(content=grouper(["".join(items) for items in content[albumtype]], 100), separator=separator[albumtype], header=header[albumtype]))
    sys.exit(0)

# 8.b. Print ripped discs into console. Then exit algorithm.
run("CLS", shell=True)
for albumtype in ["defaultalbums", "bootlegalbums"]:
    print(TEMPLATE.environment.get_template("T01").render(content=grouper(["".join(items) for items in content[albumtype]], 100), separator=separator[albumtype], header=header[albumtype]))
sys.exit(0)
