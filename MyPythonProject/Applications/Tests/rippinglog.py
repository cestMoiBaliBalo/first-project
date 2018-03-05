# -*- coding: utf-8 -*-
import logging.config
import os

import yaml

from ..AudioCD.shared import DefaultAudioCDTags, digitalaudiobase, rippinglog
from ..shared import TESTDATABASE

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    config = yaml.load(fp)
try:
    config["loggers"]["Applications.AudioCD"]["level"] = "DEBUG"
except KeyError:
    pass
logging.config.dictConfig(config)
logger = logging.getLogger("Applications.AudioCD")

# ===============
# Main algorithm.
# ===============
tags = {
    "_albumart_1_front album cover": "C:\\Users\\Xavier\\AppData\\Local\\Temp\\dbpA8B2.tmp\\11.bin",
    "album": "Dynasty",
    "albumartist": "Kiss",
    "albumartistsort": "Kiss",
    "albumsortcount": "1",
    "artist": "Kiss",
    "artistsort": "Kiss",
    "bootleg": "N",
    "disc": "1/1",
    "encoder": "Lame 3.99.5",
    "genre": "Rock",
    "incollection": "Y",
    "label": "Casablanca Records",
    "live": "N",
    "origyear": "1979",
    "profile": "Default",
    "source": "CD (Lossless)",
    "title": "2,000 Man",
    "titlelanguage": "English",
    "track": "2/9",
    "upc": "731453238824",
    "year": "1979"
}
rippinglog(DefaultAudioCDTags(**{k.lower(): v for k, v in tags.items()}), db=TESTDATABASE)
digitalaudiobase(DefaultAudioCDTags(**{k.lower(): v for k, v in tags.items()}), db=TESTDATABASE)
