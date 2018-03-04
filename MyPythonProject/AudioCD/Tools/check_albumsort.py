# -*- coding: utf-8 -*-
import argparse
import sys

from Applications.shared import validalbumsort

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

#    -------
# 1. Parser.
#    -------
parser = argparse.ArgumentParser()
parser.add_argument("albumsort")

#    ---------------
# 2. Input argument.
#    ---------------
arguments = parser.parse_args()

#    ---------------
# 3. Main algorithm.
#    ---------------
try:
    validalbumsort(arguments.albumsort)
except ValueError:
    sys.exit(1)
sys.exit(0)
