# -*- coding: utf-8 -*-
import argparse
import logging.config
import os
import re
import sys

import yaml

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))

parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)

parser.add_argument("choice")
parser.add_argument("max", type=int)
parser.add_argument("--min", default="1", type=int)

arguments = parser.parse_args()

if not re.match(r"^\d+$", arguments.choice):
    sys.exit(2)
_choice = int(arguments.choice)
if _choice < arguments.min or _choice > arguments.max:
    sys.exit(1)
sys.exit(0)
