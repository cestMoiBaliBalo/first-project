# -*- coding: utf-8 -*-
"""
Display ripped audio CDs list in XML file ("%TEMP%\rippedcd.xml").
"""
from Applications.shared import dateformat, validdb, LOCAL, TEMPLATE4, UTF8
from Applications.Database.AudioCD.shared import select
from Applications.xml import rippinglog
from logging.config import dictConfig
import xml.etree.ElementTree as ET
from operator import itemgetter
import argparse
import logging
import yaml
import os

__author__ = 'Xavier ROSSET'


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding=UTF8) as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Applications.AudioCD.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("database", nargs="?", default=os.path.join(os.path.expandvars("%_COMPUTING%"), "database.db"), type=validdb)


# ===============
# Main algorithm.
# ===============
arguments = parser.parse_args()

#  1 --> Get data.
reflist = sorted(sorted([(item[0],
                          dateformat(LOCAL.localize(item[1]), TEMPLATE4),
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
                         for item in select(arguments.database)], key=itemgetter(3), reverse=True), key=itemgetter(2), reverse=True)

#  2 --> Build XML file.
ET.ElementTree(rippinglog(reflist)).write(os.path.join(os.path.expandvars("%TEMP%"), "rippedcd.xml"), encoding="UTF-8", xml_declaration=True)
