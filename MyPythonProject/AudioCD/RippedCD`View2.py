# -*- coding: utf-8 -*-
"""
Log ripped audio CDs into an XML file (`%TEMP%\rippedaudiocds.xml`).
"""
import argparse
import logging.config
import os
import xml.etree.ElementTree as ET
from operator import itemgetter

import yaml

from Applications.Database.AudioCD.shared import selectlogs
from Applications.parsers import database_parser
from Applications.shared import LOCAL, TEMPLATE4, UTF8, dateformat
from Applications.xml import rippinglog_view1, rippinglog_view2

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding=UTF8) as fp:
    logging.config.dictConfig(yaml.load(fp))

# ================
# Input arguments.
# ================
parser = argparse.ArgumentParser(parents=[database_parser])
parser.add_argument("steps", nargs="*", type=int)

# ================
# Initializations.
# ================
output, reflist = os.path.join(os.path.expandvars("%TEMP%"), "rippedaudiocds.xml"), None

# ===============
# Main algorithm.
# ===============
arguments = parser.parse_args()
for step in arguments.steps:

    if step == 1:
        reflist = sorted(sorted([(row.rowid,
                                  (dateformat(LOCAL.localize(row.ripped), TEMPLATE4), int(LOCAL.localize(row.ripped).timestamp())),
                                  dateformat(LOCAL.localize(row.ripped), "$Y$m"),
                                  row.ripped,
                                  row.artist,
                                  row.year,
                                  row.album,
                                  row.upc,
                                  row.genre,
                                  row.application,
                                  row.albumsort,
                                  row.artistsort)
                                 for row in selectlogs(arguments.db)], key=itemgetter(3), reverse=True), key=itemgetter(2), reverse=True)
        if reflist:
            ET.ElementTree(rippinglog_view1(reflist)).write(output, encoding=UTF8, xml_declaration=True)

    elif step == 2:
        reflist = sorted([(row.rowid,
                           (dateformat(LOCAL.localize(row.ripped), TEMPLATE4), int(LOCAL.localize(row.ripped).timestamp())),
                           row.ripped,
                           row.artist,
                           row.year,
                           row.album,
                           row.upc,
                           row.genre,
                           row.application,
                           row.albumsort,
                           row.artistsort)
                          for row in selectlogs(arguments.db)], key=itemgetter(2))
        if reflist:
            ET.ElementTree(rippinglog_view2(reflist)).write(output, encoding=UTF8, xml_declaration=True)
