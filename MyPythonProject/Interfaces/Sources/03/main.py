# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# Frame generated with wxFormBuilder (version Jun 17 2015)
# http://www.wxformbuilder.org/
import locale
import logging.config
import os

import wx  # type: ignore
import yaml

from Applications.interfaces import ParentFrame
from Applications.shared import get_dirname

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ============
# Main script.
# ============
that_file = os.path.abspath(__file__)

# Define French environment.
locale.setlocale(locale.LC_ALL, "")

# Logging.
with open(os.path.join(get_dirname(that_file, level=4), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))

# Interface global configuration.
with open(os.path.join(get_dirname(that_file, level=2), "Resources", "tables_config.yml"), encoding="UTF_8") as fp:
    global_config = yaml.load(fp)

# Main interface.
app = wx.App()
interface = ParentFrame(None, **global_config)
interface.Show()
app.MainLoop()
