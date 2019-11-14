# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse

from Applications.AudioCD.shared import dump_xreferences, get_xreferences

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ============
# Main script.
# ============
parser = argparse.ArgumentParser()
parser.add_argument("path", help="String representing an audio file. Both path and name.")
argument = parser.parse_args()
found, references = get_xreferences(argument.path)
if found:
    dump_xreferences(references)
