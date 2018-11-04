# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import logging.config
import os
from unittest import TestLoader, TestSuite, TextTestRunner

import yaml

from Applications.Tests import module1, module2, module3, module4, module5

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))

# aaaaaaaaaaaaaaaaaaaaaa
suite = TestSuite()
loader = TestLoader()
runner = TextTestRunner(verbosity=3)
suite.addTests(loader.loadTestsFromModule(module1))
suite.addTests(loader.loadTestsFromModule(module2))
suite.addTests(loader.loadTestsFromModule(module3))
suite.addTests(loader.loadTestsFromModule(module4))
suite.addTests(loader.loadTestsFromModule(module5))
x = runner.run(suite)
