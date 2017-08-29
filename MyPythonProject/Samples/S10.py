# -*- coding: utf-8 -*-
import json
import logging
import os
from logging.config import dictConfig

import yaml

from Applications.parsers import epochconverterparser
from Applications.shared import UTF8, WRITE, getdatefromseconds, now

__author__ = 'Xavier ROSSET'

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Default.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

# ================
# Initializations.
# ================
arguments = epochconverterparser.parse_args()

# ===============
# Main algorithm.
# ===============
try:
    mylist = list(getdatefromseconds(arguments.start, arguments.end, arguments.zone))
except ValueError as err:
    logger.exception(err)
else:
    if mylist:
        with open(os.path.join(os.path.expandvars("%TEMP%"), "toto.json"), mode=WRITE, encoding=UTF8) as fp:
            json.dump([now(), mylist], fp, indent=4, ensure_ascii=False)
