# -*- utf-8 -*-
import os
import yaml
import logging
from functools import partial
from logging.config import dictConfig
from Applications.shared import filesinfolder, IMAGES

__author__ = 'Xavier ROSSET'


# ================
# Initializations.
# ================
images = partial(filesinfolder, "jpg", folder=IMAGES, excluded=["Recover", "iPhone", "Recycle", "\$Recycle"])


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    # --> Logging.
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        dictConfig(yaml.load(fp))
    logger = logging.getLogger("Images.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    # --> Main algorithm.
    for image in images():
        logger.debug(image)
