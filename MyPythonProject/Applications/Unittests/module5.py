# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import locale
import logging.config
import os
from pathlib import Path

import yaml

from Applications.shared import UTF8

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")

# ===========================
# Load logging configuration.
# ===========================
with open(_MYPARENT.parent / "Resources" / "logging.yml", encoding=UTF8) as fr:
    logging.config.dictConfig(yaml.load(fr, Loader=yaml.FullLoader))

