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
parser.add_argument("track")
argument = parser.parse_args()
found, references = get_xreferences(argument.track)
if found:
    dump_xreferences(references)
