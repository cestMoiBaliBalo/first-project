# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import locale
import sys
from unittest import TestLoader, TestResult, TestSuite

from Applications.Unittests import module1, module2, module3, module4

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ==========================
# Define French environment.
# ==========================
if sys.platform.startswith("win"):
    locale.setlocale(locale.LC_ALL, ("french", "fr_FR.ISO8859-1"))
elif sys.platform.startswith("lin"):
    locale.setlocale(locale.LC_ALL, "fr_FR.utf8")

# ============
# Main script.
# ============
exit_code = {False: 1, True: 0}
suite, loader, result = TestSuite(), TestLoader(), TestResult()
suite.addTests(loader.loadTestsFromModule(module1))
suite.addTests(loader.loadTestsFromModule(module2))
suite.addTests(loader.loadTestsFromModule(module3))
suite.addTests(loader.loadTestsFromModule(module4))
if sys.platform.startswith("win"):
    from Applications.Unittests import module5
    suite.addTests(loader.loadTestsFromModule(module5))
suite.run(result)
sys.exit(exit_code[result.wasSuccessful()])
