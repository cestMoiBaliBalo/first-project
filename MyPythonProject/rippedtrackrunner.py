# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import locale
import logging.config
import operator
import os
from contextlib import suppress
from functools import partial
from unittest import TestLoader, TestSuite, TextTestRunner

import yaml

from Applications.Unittests import module4
from Applications.decorators import attrgetter_
from Applications.shared import customfilter as cf

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# =================
# Define constants.
# =================
LOGGERS = ["Applications.shared", "Applications.AudioCD", "Applications.Tables.Albums", "MyPythonProject"]
MAPPING = {True: "debug", False: "info"}

# ================
# Parse arguments.
# ================
parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
parser.add_argument("-d", "--debug", action="store_true")
parser.add_argument("-c", "--console", nargs="*")
parser.add_argument("-v", "--verbosity", action="count")
arguments = vars(parser.parse_args())

# -----
locale.setlocale(locale.LC_ALL, "")

# -----
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    config = yaml.load(fp, Loader=yaml.FullLoader)

# -----
for item in LOGGERS:
    with suppress(KeyError):
        config["loggers"][item]["level"] = MAPPING[arguments.get("debug", False)].upper()

if all([arguments.get("debug", False), arguments.get("console", [])]):
    for item in LOGGERS:
        with suppress(KeyError):
            config["loggers"][item]["handlers"] = ["file", "console"]
    with suppress(KeyError):
        config["handlers"]["console"]["level"] = "DEBUG"
    config["handlers"]["console"]["func"] = partial(cf, attrgetter_("funcName")(partial(operator.contains, arguments.get("console", []))))

# -----
logging.config.dictConfig(config)
logger = logging.getLogger("MyPythonProject.{0}".format(os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0]))

# -----
verbosity = arguments.get("verbosity", 1)
if verbosity > 2:
    verbosity = 2
suite, loader, runner = TestSuite(), TestLoader(), TextTestRunner(verbosity=verbosity)
suite.addTests(loader.loadTestsFromTestCase(module4.TestRippedTrack))
runner.run(suite)
