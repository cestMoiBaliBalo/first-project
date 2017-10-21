# -*- coding: utf-8 -*-
"""
Log ripped audio CDs into an XML file (`%TEMP%\rippedcd.xml`).
"""
import logging
import os
import xml.etree.ElementTree as ET
from logging.config import dictConfig
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
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Applications.AudioCD.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

# ================
# Input arguments.
# ================
database_parser.add_argument("steps", nargs="*", type=int)

# ================
# Initializations.
# ================
output, reflist = os.path.join(os.path.expandvars("%TEMP%"), "rippedcd.xml"), None

# ===============
# Main algorithm.
# ===============
arguments = database_parser.parse_args()
for step in arguments.steps:

    if step == 1:
        reflist = sorted(sorted([(item[0],
                                  (dateformat(LOCAL.localize(item[1]), TEMPLATE4), int(LOCAL.localize(item[1]).timestamp())),
                                  dateformat(LOCAL.localize(item[1]), "$Y$m"),
                                  item[1],
                                  item[2],
                                  item[3],
                                  item[4],
                                  item[5],
                                  item[6],
                                  item[7],
                                  item[8],
                                  item[9])
                                 for item in selectlogs(arguments.db)], key=itemgetter(3), reverse=True), key=itemgetter(2), reverse=True)
        if reflist:
            ET.ElementTree(rippinglog_view1(reflist)).write(output, encoding="UTF-8", xml_declaration=True)

    elif step == 2:
        reflist = sorted([(item[0],
                           (dateformat(LOCAL.localize(item[1]), TEMPLATE4), int(LOCAL.localize(item[1]).timestamp())),
                           item[1],
                           item[2],
                           item[3],
                           item[4],
                           item[5],
                           item[6],
                           item[7],
                           item[8],
                           item[9])
                          for item in selectlogs(arguments.db)], key=itemgetter(2))
        if reflist:
            ET.ElementTree(rippinglog_view2(reflist)).write(output, encoding="UTF-8", xml_declaration=True)
