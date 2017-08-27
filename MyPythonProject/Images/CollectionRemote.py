# -*- coding: utf-8 -*-
import os
import re
import yaml
import ftplib
import logging
from base64 import b85decode
from contextlib import ExitStack
from logging.config import dictConfig
from Applications.shared import NAS, PASSWORD, ChangeRemoteCurrentDirectory

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========
def remotedirectorycontent(*extensions, ftpobject, currentdir, logobject=None, excluded=None):

    # Define regular expression for folder(s) exclusion.
    regex = None
    if excluded:
        regex = re.compile(r"{0}/(?:{1})".format(currentdir, "|".join(excluded)), re.IGNORECASE)

    # Loop over sub-folders.
    for item in ftpobject.nlst():
        wdir = "{0}/{1}".format(currentdir, item)

        # 1 --> Log variables.  
        if logobject:
            logobject.debug(currentdir)
            logobject.debug(item)
            logobject.debug(wdir)

        # 2 --> Sub-folder "wdir" match the regular expression: it is excluded.
        if regex and regex.match(wdir):
            continue

        # 3 --> Sub-folder "wdir" is set as current directory.    
        #       If an exception occurs sub-folder "wdir" is assumed to be a file and yielded as a consequence.
        #       If any exception doesn't occur sub-folder "wdir" is walked through.
        stack2 = ExitStack()
        try:
            stack2.enter_context(ChangeRemoteCurrentDirectory(ftpobject, wdir))
        except ftplib.error_perm:
            if not extensions or (extensions and os.path.splitext(wdir)[1][1:].lower() in (extension.lower() for extension in extensions)):
                yield wdir
        else:
            with stack2:
                for content in remotedirectorycontent(*extensions, ftpobject=ftpobject, currentdir=wdir, logobject=logobject, excluded=excluded):
                    yield content


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    # --> Logging.
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        dictConfig(yaml.load(fp))
    logger = logging.getLogger("Images.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    # --> Main alogrithm.
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
                for file in remotedirectorycontent("jpg", ftpobject=ftp, currentdir=refdirectory, excluded=["#recycle"]):
                    logger.debug(file)
