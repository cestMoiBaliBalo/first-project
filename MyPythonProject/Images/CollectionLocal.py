# -*- coding: utf-8 -*-
import logging
import os
from functools import partial
from logging.config import dictConfig

import yaml

from Applications.shared import IMAGES, filesinfolder

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ================
# Initializations.
# ================
images = partial(filesinfolder, "jpg", folder=IMAGES, excluded=["Recover", "iPhone", "Recycle", "\$Recycle"])

# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    # --> Logging.
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
        dictConfig(yaml.load(fp))
    logger = logging.getLogger("MyPythonProject.Images.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    # --> Main algorithm.
    for image in images():
        logger.info(image)
