# -*- coding: utf-8 -*-
import os
import re
import sys
from contextlib import suppress
from datetime import datetime

from jinja2 import FileSystemLoader
from pytz import timezone

from Applications.AudioCD.shared import DFTPATTERN, filcontents
from Applications.shared import DFTTIMEZONE, TEMPLATE3, TemplatingEnvironment, UTF16, WRITE, dateformat, validalbumsort

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# =========
# Template.
# =========
_template = TemplatingEnvironment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "AudioCD", "RippedCD"))).environment.get_template("Tags")

# ==========
# Constants.
# ==========
_CODEC = {"AAC": "02",
          "LAME": "01"}
_REGEX = re.compile(DFTPATTERN, re.IGNORECASE)

# ==========
# Variables.
# ==========
_tags = {}

# ============
# Main script.
# ============

# Get tags from dBpoweramp Batch Converter.
with open(sys.argv[1], encoding=UTF16) as fr:
    for line in filcontents(fr):
        _match = _REGEX.match(line)
        if _match:
            _tags[_match.group(1).rstrip().lower()] = _match.group(2)

# Change tags.
_tags["encodedby"] = "dBpoweramp Batch Converter on {0} from original nugs.net FLAC file".format(dateformat(datetime.now(tz=timezone(DFTTIMEZONE)), TEMPLATE3))
_tags["encodingtime"] = int(datetime.now(tz=timezone(DFTTIMEZONE)).timestamp())
_tags["encodingyear"] = datetime.now(tz=timezone(DFTTIMEZONE)).strftime("%Y")
_tags["taggingtime"] = dateformat(datetime.now(tz=timezone(DFTTIMEZONE)), TEMPLATE3)
_albumsort = _tags.get("albumsort")
if _albumsort:
    try:
        _albumsort = validalbumsort(_albumsort[:-3])
    except ValueError:
        pass
    else:
        with suppress("KeyError"):
            _tags["albumsort"] = "{0}.{1}".format(_albumsort, _CODEC[sys.argv[2]])

# Remove tags.
with suppress("KeyError"):
    del _tags["copyright"]
with suppress("KeyError"):
    del _tags["description"]
with suppress("KeyError"):
    del _tags["mediaprovider"]
with suppress("KeyError"):
    del _tags["purchasedate"]

# Get back tags to dBpoweramp Batch Converter.
with open(sys.argv[1], mode=WRITE, encoding=UTF16) as fw:
    fw.write(_template.render(tags=_tags))
