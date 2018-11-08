# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
from unittest import TestLoader, TestSuite, TextTestRunner

from Applications.Unittests import module1, module2, module3, module4, module5

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

suite = TestSuite()
loader = TestLoader()
runner = TextTestRunner(verbosity=3)
suite.addTests(loader.loadTestsFromModule(module1))
suite.addTests(loader.loadTestsFromModule(module2))
suite.addTests(loader.loadTestsFromModule(module3))
suite.addTests(loader.loadTestsFromModule(module4))
suite.addTests(loader.loadTestsFromModule(module5))
runner.run(suite)
