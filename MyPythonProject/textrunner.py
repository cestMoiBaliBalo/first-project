# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import locale
import sys
from unittest import TestLoader, TestSuite, TextTestRunner

from Applications.Unittests import module1, module2, module3, module4, module5

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

# ==========================
# Define French environment.
# ==========================
if sys.platform.startswith("win"):

    # -----
    import logging.config
    import operator
    import os
    import yaml
    from contextlib import suppress
    from functools import partial
    from Applications.shared import attrgetter_, customfilter as cf

    # -----
    locale.setlocale(locale.LC_ALL, ("french", "fr_FR.ISO8859-1"))

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


elif sys.platform.startswith("lin"):
    locale.setlocale(locale.LC_ALL, "fr_FR.utf8")

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
runner.run(suite)
