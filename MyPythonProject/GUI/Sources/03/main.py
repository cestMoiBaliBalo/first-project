# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# Frame generated with wxFormBuilder (version Jun 17 2015)
# http://www.wxformbuilder.org/
import logging.config
import os
from typing import Any, Mapping

import wx  # type: ignore
import yaml

from Applications.shared import get_dirname
from shared import ParentFrame

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

# ============
# Main script.
# ============
that_file = os.path.abspath(__file__)

# Logging.
with open(os.path.join(get_dirname(that_file, level=4), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))

# Interface global configuration.
with open(os.path.join(get_dirname(that_file, level=2), "Resources", "resource2.yml"), encoding="UTF_8") as fp:
    global_config = yaml.load(fp)  # type: Mapping[str, Any]

app = wx.App()
interface = ParentFrame(None, **global_config)
interface.Show()
app.MainLoop()
