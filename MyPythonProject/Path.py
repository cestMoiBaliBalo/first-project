# -*- coding: utf-8 -*-
import argparse
import logging.config
import os
import sys
from contextlib import suppress

import yaml

from Applications.shared import TEMPLATE4, UTF8

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ==========
# Constants.
# ==========
LOGGERS = ["MyPythonProject"]
DEBUG = "DEBUG"

# =======
# Parser.
# =======
parser = argparse.ArgumentParser()
parser.add_argument("--console", action="store_true")
arguments = parser.parse_args()

# ========
# Logging.
# ========

# 1. Load logging configuration and adapt logger(s) level(s).
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding=UTF8) as fp:
    config = yaml.load(fp)
for logger in LOGGERS:
    with suppress(KeyError):
        config["loggers"][logger]["level"] = DEBUG

# 2. Set up a specific stream handler if required.
if arguments.console:
    for logger in LOGGERS:
        with suppress(KeyError):
            config["loggers"][logger]["handlers"] = ["file", "console"]
    with suppress(KeyError):
        config["handlers"]["console"]["level"] = DEBUG

# 3. Declare logging configuration.
logging.config.dictConfig(config)

# ===============
# Main algorithm.
# ===============
logger = logging.getLogger("MyPythonProject.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))
for path in sys.path:
    logger.debug(path)
logger.debug(TEMPLATE4)
