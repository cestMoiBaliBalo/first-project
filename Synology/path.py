# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import sys

from Applications.shared import TEMPLATE4

from Modules.shared import SRC

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

for path in sys.path:
    print(path)

# Constant taken from MyPythonProject/Applications/shared.py
print(TEMPLATE4)

# Constant taken from Synology/Modules/shared.py
print(SRC)
