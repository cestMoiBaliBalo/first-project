# -*- coding: utf-8 -*-
import logging.config
import os

import jinja2
import yaml

from Applications.parsers import foldercontent
from Applications.shared import TemplatingEnvironment

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))

# -----
template = TemplatingEnvironment(loader=jinja2.FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "AudioCD", "Tools")))

# -----
arguments = foldercontent.parse_args()

# -----
extensions = arguments.extensions
mode = "I"
pattern = "*"
if arguments.command == "3":
    mode = "E"

# -----
if arguments.command in ["1", "2"]:
    if len(arguments.extensions) == 1:
        pattern = "*.{0}".format(arguments.extensions[0])
        extensions = []

# -----
if not extensions:
    mode = "G"

# -----
with open(os.path.join(os.path.expandvars("%TEMP%"), "foldercontent.cmd"), mode="w", encoding="ISO-8859-1") as fw:
    fw.write(template.environment.get_template("T02").render(pattern=pattern, extensions=extensions, mode=mode))
