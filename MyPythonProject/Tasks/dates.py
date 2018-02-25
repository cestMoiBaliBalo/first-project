# -*- coding: utf-8 -*-
import json
import logging
import os
import xml.etree.ElementTree as ET
from collections import namedtuple
from logging.config import dictConfig

import yaml

from Applications.Database.Tables.shared import selectfrom
from Applications.parsers import readtable
from Applications.shared import LOCAL, TEMPLATE4, UTC, UTF8, dateformat, now

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding=UTF8) as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Applications.Database.Tables")

# ================
# Initializations.
# ================
record, tasks = namedtuple("record", "uid utc_run"), namedtuple("tasks", "description uid")

# ==========
# Arguments.
# ==========
arguments = readtable.parse_args()

# ===============
# Main algorithm.
# ===============

# 1 --> Initializations.
logger.debug(arguments.db)
logger.debug(arguments.table)

# 2 --> Initializations.
with open(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Tasks", "Repository.json")) as fp:
    repo = {task.uid: task.description for task in [tasks._make(v) for k, v in json.load(fp).items()]}

# 3 --> Build XML file.
root = ET.Element("data", attrib=dict(table=arguments.table))
se = ET.SubElement(root, "updated")
se.text = now()
for row in map(record._make, selectfrom(arguments.table, db=arguments.db)):
    if row.uid in repo:
        se = ET.SubElement(root, "dates")
        uid = ET.SubElement(se, "task", attrib={"uid": str(row.uid)})
        uid.text = repo[row.uid]
        date = ET.SubElement(se, "lastrundate")
        date.text = dateformat(UTC.localize(row.utc_run).astimezone(LOCAL), TEMPLATE4)
ET.ElementTree(root).write(os.path.join(os.path.expandvars("%TEMP%"), "dates.xml"), encoding=UTF8, xml_declaration=True)
