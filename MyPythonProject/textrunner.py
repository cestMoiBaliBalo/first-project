# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import locale
import logging.config
import sys
from contextlib import suppress
from unittest import TestLoader, TestSuite, TextTestRunner

import yaml

from Applications.Unittests import module1, module2, module3, module4, module5

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ==========
# Constants.
# ==========
LOGGERS = ["Applications.shared", "Applications.AudioCD", "MyPythonProject"]
MAPPING = {True: "debug", False: "info"}

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
parser.add_argument("--debug", action="store_true")
arguments = vars(parser.parse_args())

# ==========================
# Define French environment.
# ==========================
if sys.platform.startswith("win"):

    # -----
    import logging.config
    import os

    # -----
    locale.setlocale(locale.LC_ALL, "french")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources", "logging.yml"), encoding="UTF_8") as fp:
        config = yaml.load(fp)
    for item in LOGGERS:
        with suppress(KeyError):
            config["loggers"][item]["level"] = MAPPING[arguments.get("debug", False)].upper()
    logging.config.dictConfig(config)
    logger = logging.getLogger("MyPythonProject.{0}".format(os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0]))

if sys.platform.startswith("lin"):
    locale.setlocale(locale.LC_ALL, "fr_FR.utf8")

# ============
# Main script.
# ============
suite, loader, runner = TestSuite(), TestLoader(), TextTestRunner(verbosity=3)
suite.addTests(loader.loadTestsFromModule(module1))
suite.addTests(loader.loadTestsFromModule(module2))
suite.addTests(loader.loadTestsFromModule(module3))
suite.addTests(loader.loadTestsFromModule(module4))
suite.addTests(loader.loadTestsFromModule(module5))
runner.run(suite)
