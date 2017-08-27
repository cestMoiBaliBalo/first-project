# -*- coding: utf-8 -*-
import os
import yaml
import ftplib
import logging
from base64 import b85decode
from contextlib import ExitStack
from logging.config import dictConfig
from Images.CollectionLocal import images
from Applications.shared import NAS, PASSWORD
from Images.CollectionRemote import remotedirectorycontent

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========
@contextmanager
def decorator(obj, s):
    sep = "".join(list(repeat("-", len(s))))
    obj.info(sep)
    yield
    obj.info(sep)


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    remote, local = [], None

    # --> Logging.
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        dictConfig(yaml.load(fp))
    logger = logging.getLogger("Images.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    # --> Main algorithm.
    stack1 = ExitStack()
    try:
        ftp = stack1.enter_context(ftplib.FTP(NAS, timeout=30))
    except TimeoutError as err:
        logger.exception(err)
    else:
        with stack1:
            ftp.login(user="admin", passwd=b85decode(PASSWORD).decode())
            logger.debug(ftp.getwelcome())
            refdirectory = "/pictures"
            try:
                ftp.cwd(refdirectory)
            except ftplib.error_perm as err:
                logger.exception(err)
            else:
                remote.extend([os.path.basename(image) for image in remotedirectorycontent("jpg", ftpobject=ftp, currentdir=refdirectory, excluded=["#recycle"])])

                # --> Remote collection.
                remote_collection = set(remote)

                # --> Local collection.
                local_images = ((os.path.dirname(image), os.path.basename(image)) for image in images())  # Generator expression.
                local_collection = set(map(os.path.basename, images()))

                difference = sorted(local_collection - remote_collection)
                if difference:
                    with decorator(logger, "differences"):
                        logger.info("differences".upper())
                    logger.info("Differences: {0}".format(len(difference)))
                    for file in (os.path.join(dirname, basename) for dirname, basename in local_images if basename in difference):
                        logger.info(file)

                common = sorted(local_collection & remote_collection)
                if common:
                    logger.debug("-----------")
                    logger.debug("common".upper())
                    logger.debug("-----------")
                    logger.debug("Common: {0}".format(len(common)))
                    for file in (os.path.join(dirname, basename) for dirname, basename in local_images if basename in common):
                        logger.debug(file)
