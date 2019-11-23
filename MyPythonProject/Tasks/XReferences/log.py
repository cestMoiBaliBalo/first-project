# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import locale
import logging.config
import os
from contextlib import suppress
from typing import Set, Tuple

import yaml

from Applications.Tables.XReferences.shared import get_drive_albums
from Applications.shared import UTF8, get_dirname

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# -----
locale.setlocale(locale.LC_ALL, "")

# -----
with open(os.path.join(get_dirname(os.path.abspath(__file__), level=3), "Resources", "logging.yml"), encoding=UTF8) as stream:
    log_config = yaml.load(stream, Loader=yaml.FullLoader)
with suppress(KeyError):
    log_config["loggers"]["Applications.Tables.XReferences"]["level"] = "DEBUG"
logging.config.dictConfig(log_config)
logger = logging.getLogger("MyPythonProject.Tables.XReferences")

# -----
albums_drive = set(get_drive_albums())  # type: Set[Tuple[str, str, str, str, str, bool, str, str]]
