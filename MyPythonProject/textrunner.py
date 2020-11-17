# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import locale
import logging.config
import operator
import os
import sys
from contextlib import suppress
from functools import partial
from pathlib import Path
from unittest import TestLoader, TestSuite, TextTestRunner

import yaml

from Applications.Unittests import module1, module2, module3, module4, module5
from Applications.decorators import attrgetter_
from Applications.shared import customfilter as cf

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent

# =================
# Define constants.
# =================
LOGGERS = ["Applications.shared", "Applications.AudioCD", "Applications.Tables.Albums", "MyPythonProject"]
EXIT = {False: 1, True: 0}

# ================
# Parse arguments.
# ================
parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
parser.add_argument("-d", "--debug", action="store_true")
parser.add_argument("-c", "--console", action="store_true")
parser.add_argument("-v", "--verbosity", action="count")
arguments = vars(parser.parse_args())

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "fr_FR")

# ===========================
# Load logging configuration.
# ===========================
if arguments.get("debug", False):

    # -----
    with open(_MYPARENT / "Resources" / "logging.yml", encoding="UTF_8") as fp:
        config = yaml.load(fp, Loader=yaml.FullLoader)

    # -----
    for item in LOGGERS:
        with suppress(KeyError):
            config["loggers"][item]["level"] = "DEBUG"

    # -----
    if arguments.get("console", False):
        for item in LOGGERS:
            with suppress(KeyError):
                config["loggers"][item]["handlers"] = ["file", "console"]
        with suppress(KeyError):
            config["handlers"]["console"]["level"] = "DEBUG"
        config["handlers"]["console"]["func"] = partial(cf, attrgetter_("funcName")(partial(operator.contains, arguments.get("console", []))))

    # -----
    logging.config.dictConfig(config)
    logger = logging.getLogger("MyPythonProject.{0}".format(os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0]))

# ================
# Run main script.
# ================
verbosity = arguments.get("verbosity", 1)
if verbosity > 2:
    verbosity = 2
suite, loader, runner = TestSuite(), TestLoader(), TextTestRunner(verbosity=verbosity)
suite.addTests(loader.loadTestsFromModule(module1))
suite.addTests(loader.loadTestsFromModule(module2))
suite.addTests(loader.loadTestsFromModule(module3))
suite.addTests(loader.loadTestsFromModule(module4))
suite.addTests(loader.loadTestsFromModule(module5))
result = runner.run(suite)
sys.exit(EXIT[result.wasSuccessful()])
