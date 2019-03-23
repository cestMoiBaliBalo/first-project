# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import itertools
import locale
import logging.config
import os
from contextlib import ExitStack
from pathlib import PurePath

import yaml

from Applications.shared import TemplatingEnvironment, get_dirname

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

that_file = PurePath(os.path.abspath(__file__))

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "french")

# ===========================
# Load logging configuration.
# ===========================
with open(os.path.join(get_dirname(os.path.abspath(__file__), level=3), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))

# ==========
# Constants.
# ==========
COMPUTING = os.path.join(os.path.expandvars("%_COMPUTING%"))
RIPPEDTRACKS = "rippedtracks"

# ============
# Main script.
# ============

# Define template.
template = TemplatingEnvironment(path=that_file.parents[1] / "Templates")
template.set_template(template="T02")

# Set copy commands file.
with ExitStack() as stack:
    fr = stack.enter_context(open(os.path.join(COMPUTING, "Resources", f"{RIPPEDTRACKS}.txt"), encoding="UTF-8"))
    fw = stack.enter_context(open(os.path.join(COMPUTING, "Resources", f"{RIPPEDTRACKS}.cmd"), mode="w", encoding="UTF-8"))
    tracks = filter(None, itertools.chain.from_iterable([line.splitlines() for line in fr]))
    fw.write(getattr(template, "template").render(collection=(track.split("|") for track in tracks)))
