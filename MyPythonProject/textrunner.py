# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import locale
import sys
from unittest import TestLoader, TestSuite, TextTestRunner

from Applications.Unittests import module1, module2, module3, module4, module5

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ==========================
# Define French environment.
# ==========================
if sys.platform.startswith("win"):
    locale.setlocale(locale.LC_ALL, "french")
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
