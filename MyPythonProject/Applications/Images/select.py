# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import os
from pathlib import PurePath

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

that_file = PurePath(os.path.abspath(__file__))

# =============================
# Script if module run as main.
# =============================
if __name__ == "__main__":
    import argparse
    import sys
    import itertools
    from Applications.parsers import database_parser
    from .shared import select

    parser = argparse.ArgumentParser(parents=[database_parser])
    subparser = parser.add_subparsers()
    parser_select = subparser.add_parser("select")
    parser_select.add_argument("years", nargs="*", type=int)
    arguments = parser.parse_args()
    if not arguments.years:
        for a, b, c, d, e, f, g in select(arguments.db):
            print(a, b, c, d, e, f, g)
        sys.exit()
    for item in map(select, itertools.repeat(arguments.db), arguments.years):
        for a, b, c, d, e, f, g in item:
            print(a, b, c, d, e, f, g)
    sys.exit()
