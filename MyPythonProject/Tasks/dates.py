# -*- coding: utf-8 -*-
import os
import yaml
import json
import logging
from collections import namedtuple
import xml.etree.ElementTree as ET
from logging.config import dictConfig
from Applications.parsers import readtable
from Applications.Database.Tables.shared import select
from Applications.shared import dateformat, mainscript, now, LOCAL, UTC, UTF8, TEMPLATE4

__author__ = 'Xavier ROSSET'


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding=UTF8) as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Applications.Database.Tables")


# ================
# Initializations.
# ================
record, tasks = namedtuple("record", "uid rundate"), namedtuple("tasks", "task uid")


# ==========
# Arguments.
# ==========
arguments = readtable.parse_args()


# ===============
# Main algorithm.
# ===============

#  1 --> Initializations.
logger.debug(mainscript(__file__))
with open(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Tasks", "Repository.json")) as fp:
    repo = {task.uid: task.task for task in [tasks._make(v) for k, v in json.load(fp).items()]}

#  2 --> Build XML file.
root = ET.Element("Data", attrib=dict(css="firstcss.css", table=arguments.table))
se = ET.SubElement(root, "Updated")
se.text = now()
for row in map(record._make, select(arguments.table, db=arguments.database)):
    se = ET.SubElement(root, "Dates")
    uid = ET.SubElement(se, "Task", attrib={"uid": str(row.uid)})
    uid.text = repo[row.uid]
    date = ET.SubElement(se, "LastRunDate")
    date.text = dateformat(UTC.localize(row.rundate).astimezone(LOCAL), TEMPLATE4)
ET.ElementTree(root).write(os.path.join(os.path.expandvars("%TEMP%"), "toto.xml"), encoding=UTF8, xml_declaration=True)
