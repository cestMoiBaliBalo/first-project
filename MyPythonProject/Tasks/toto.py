# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import locale
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List

import iso8601
import yaml
from pytz import timezone

from Applications.shared import get_readabledate

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "french")


# ===============
# Action classes.
# ===============
class SetDelta(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super(SetDelta, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        try:
            value = int(values)
        except TypeError:
            raise ValueError(f'"{values}" is not a coherent delta argument')
        if value < 0:
            raise ValueError("Negative delta is not allowed")
        elif value > 10:
            raise ValueError("Delta can\'t exceed 10 days")
        setattr(namespace, self.dest, value)


# ==========
# Constants.
# ==========
TZ = timezone("Europe/Paris")
UTC = timezone("UTC")

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
parser.add_argument("config", type=argparse.FileType(mode="r+", encoding="UTF_8"))
parser.add_argument("key", choices=["my_documents"])
parser.add_argument("-u", "--update", dest="update", nargs="?", const="0", action=SetDelta)

# ================
# Parse arguments.
# ================
arguments = vars(parser.parse_args())
config_file = arguments["config"]

# ===============
# Main algorithm.
# ===============
now = UTC.localize(datetime.utcnow()).astimezone(TZ)
collections = yaml.load(config_file)  # type: Dict[str, List[str]]
collection = collections.get(arguments.get("key"), [])  # type: List[str]
last_run = None
if collection:
    last_run = iso8601.parse_date(collection[-1])  # type: datetime

# -----
# Read.
# -----
if arguments.get("update") is None:
    _exit = 1
    if collection:
        if now - last_run < timedelta(days=28):
            _exit = 0
    if last_run:
        with open(os.path.join(os.path.expandvars("%TEMP%"), "last_backup.txt"), mode="w", encoding="ISO-8859-1") as stream:
            stream.write(f"{get_readabledate(TZ.localize(last_run.replace(tzinfo=None)))}\n")
    sys.exit(_exit)

# -------
# Update.
# -------
current_run = UTC.localize(datetime.utcnow()).astimezone(TZ)  # type: datetime
if int(arguments.get("update")) > 0:
    current_run = UTC.localize(datetime.utcnow()).astimezone(TZ) - timedelta(days=28)
    if last_run:
        current_run = last_run
    current_run = current_run + timedelta(days=arguments.get("update"))
collection.append(current_run.isoformat())
collections[arguments.get("key")] = collection
config_file.seek(0)  # Set the file pointer at the beginning to replace configuration.
yaml.dump(collections, config_file, default_flow_style=False, indent=2)
sys.exit(0)
