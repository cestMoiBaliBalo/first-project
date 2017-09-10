# -*- coding: ISO-8859-1 -*-
# pylint: disable=invalid-name
import argparse
import logging.config
import os
from contextlib import ExitStack

import yaml

from Applications.AudioCD.shared import RippedCD, digitalaudiobase, rippinglog
from Applications.shared import mainscript

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("file", help="tags file")
parser.add_argument("profile", help="ripping profile")
parser.add_argument("decorators", nargs="*", help="decorating profile(s)")
parser.add_argument("-t", "--test", action="store_true")

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))
logger = logging.getLogger("Applications.AudioCD.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

# ============
# Local names.
# ============
exists, join, expandvars = os.path.exists, os.path.join, os.path.expandvars

# ==========
# Variables.
# ==========
obj, arguments = [], parser.parse_args()

# ===============
# Main algorithm.
# ===============
logger.debug(mainscript(__file__))
stack = ExitStack()
try:
    rippedcd = stack.enter_context(RippedCD(arguments.profile, arguments.file, *arguments.decorators, test=arguments.test))
except ValueError as err:
    logger.debug(err)
else:
    with stack:
        if arguments.profile in ["default"]:

            #  --> 1. Digital audio files database.
            digitalaudiobase(rippedcd.new)

            #  --> 2. Ripped CD database.
            rippinglog(rippedcd.new)
