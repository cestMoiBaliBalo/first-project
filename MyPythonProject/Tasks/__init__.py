# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'

import logging
from .. import shared
from logging import handlers

# Create Logger.
parent_logger = logging.getLogger(__package__)
parent_logger.setLevel(logging.DEBUG)

# Create handler.
handler = logging.handlers.RotatingFileHandler(shared.LOG, backupCount=5, maxBytes=500000)
handler.setLevel(logging.DEBUG)

# Create Formatter.
formatter = shared.CustomFormatter(shared.LOGPATTERN)

# Add formatter to handler
handler.setFormatter(formatter)

# Add handler to logger.
parent_logger.addHandler(handler)
