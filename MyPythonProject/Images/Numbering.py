# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import fnmatch
import json
import logging.config
import os
import re
import sys
from collections import OrderedDict
from collections.abc import MutableSequence
from contextlib import suppress
from itertools import filterfalse, groupby, repeat, tee
from operator import itemgetter
from pathlib import PureWindowsPath
from subprocess import PIPE, run
from tempfile import TemporaryFile

import jinja2
import yaml

from Applications.shared import DFTMONTHREGEX, DFTYEARREGEX, IMAGES_COLLECTION, TEMPLATE7, TemplatingEnvironment, UTF8, WRITE, now

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ======================
# Functions local names.
# ======================
basename, dirname, exists, expandvars, join, listdir, normpath, rename, splitext = os.path.basename, os.path.dirname, os.path.exists, os.path.expandvars, os.path.join, os.listdir, os.path.normpath, \
                                                                                   os.rename, os.path.splitext


# ===============
# Global classes.
# ===============
class ImagesCollection(MutableSequence):
    """
    Class used to work with a local images collection.
    Main purposes are:
        - detect if some images aren't compliant with the storing convention.
        - detect if some images aren't compliant with the naming convention.
        - Move images.
        - Rename images.
    """
    logger = logging.getLogger("MyPythonProject.Images.{0}.ImagesCollection".format(str(PureWindowsPath(__file__).stem)))

    def __delitem__(self, key):
        del self._collection[key]

    def __getitem__(self, item):
        return self._collection[item]

    def __init__(self, *directories):
        self._collection, self._directories = [], ()
        self.directories = directories
        self.load()

        # Log processed directories.
        if self._directories:
            self.logger.debug(" ---------------------- ")
            self.logger.debug(" Processed directories. ")
            self.logger.debug(" ---------------------- ")
            for directory in self._directories:
                self.logger.debug("\t%s.".expandtabs(3), directory)

        # Log collected files.
        if self._collection:
            self.logger.debug(" ---------------- ")
            self.logger.debug(" Collected files. ")
            self.logger.debug(" ---------------- ")
            for path, _ in sorted(self._collection, key=itemgetter(0)):
                self.logger.debug("\t%s".expandtabs(3), normpath(path))
            with open(join(expandvars("%TEMP%"), "collection.yml"), mode=WRITE, encoding=UTF8) as stream:
                yaml.dump(self._collection, stream, indent=2, default_flow_style=False)

    def __len__(self):
        return len(self._collection)

    def __setitem__(self, key, value):
        self._collection[key] = value

    def display(self):
        """
        Log images collection. Images are grouped by image original month and sorted by image path.

        :return: None.
        """
        for month, images in groupby(sorted(sorted(self._collection, key=itemgetter(0)), key=itemgetter(1)), key=itemgetter(1)):
            self.logger.info("------")
            self.logger.info("%s", month)
            self.logger.info("------")
            for image in images:
                path, _ = image
                self.logger.info("\t%s".expandtabs(3), path)

    def insert(self, index, value):
        self._collection.insert(index, value)

    def load(self):
        """
        Load the images collection into a list object stored into the inner attribute `_collection`.

        :return: None.
        """
        self._collection = list(self.get_images(*self._directories))

    def move(self):
        """
        Move an image to the right directory in order to be compliant with the storing convention.
        Image original month is used to compute the right directory.

        :return: None.
        """
        for src, dst in ((normpath(path), normpath(join(IMAGES_COLLECTION, datetimeoriginal))) for path, datetimeoriginal in filter(self.filter, self._collection)):
            yield src, dst

    def rename(self):
        """
        Rename an image in order to be compliant with the naming convention.

        :return: None.
        """
        collection = []
        coll_true, coll_false = self.partition(self._collection, self.predicate)

        # Extract the five digits unique number from all images compliant with the naming convention.
        numbers = sorted(map(self.get_numbers, coll_true))

        # Extract all images non-compliant with the naming convention.
        coll_false = list(coll_false)

        # Compute expected numbers.
        _template = range(1, 1 + len(coll_false))
        end = 0
        if numbers:
            _template = range(1, 1 + len(numbers))
            end = numbers[-1]
        self.logger.debug(list(_template))
        self.logger.debug(end)
        for (path, datetimeoriginal), number in zip(coll_false, self.adjust_numbers(self.set_numbers(numbers, _template), len(coll_false), start=end + 1)):
            collection.append((normpath(path), basename(normpath(join(IMAGES_COLLECTION, str(datetimeoriginal), "{0}_{1:>05d}{2}".format(datetimeoriginal, number, splitext(path)[1].upper()))))))
        for image, new_name in collection:
            yield image, new_name

    @property
    def directories(self):
        return self._directories

    @directories.setter
    def directories(self, arg):
        self._directories = list(filter(exists, arg))

    @property
    def filestomove(self):
        """
        Return a list object composed of the images non-compliant with the storing convention.
        Those images are supposed to be moved to the right directory.

        :return: list object.
        """
        return list(filter(self.filter, self._collection))

    @classmethod
    def fromyear(cls, year):
        """
        Return an images collection from an input year.

        :param year: year as a four digits number. Integer or string object allowed.
        :return: ImagesCollection object.
        """
        return cls(*fnmatch.filter(map(join, repeat(IMAGES_COLLECTION), listdir(IMAGES_COLLECTION)), "{0}*".format(join(IMAGES_COLLECTION, str(year)))))

    @staticmethod
    def adjust_numbers(numbers, items, *, start=1):
        """

        :param numbers:
        :param items:
        :param start:
        :return: iterator object.
        """
        out = []
        numbers = list(numbers)
        length_numbers = len(numbers)
        if numbers:
            if items <= length_numbers:
                out = numbers[:items]
            elif items > length_numbers:
                out = numbers
                out.extend(range(start, start + items - length_numbers))
        elif not numbers:
            out = range(start, start + items)
        for number in out:
            yield number

    @staticmethod
    def filter(item):
        """
        Return a boolean value informing that the image dirname is compliant with the storing convention.
        Useful for detecting images stored into a wrong directory.

        :param item: tuple composed of both the image name and the image original month.
        :return: boolean value.
        """
        path, datetimeoriginal = item
        return not re.match(normpath(join(IMAGES_COLLECTION, str(datetimeoriginal))).replace("\\", "\\\\"), normpath(dirname(path)), re.IGNORECASE)

    @staticmethod
    def get_images(*directories):
        """
        Return an iterator object yielding an images collection taken from directories composing the `directories` argument.
        Exiftool application is run to get both image name and image original month.

        :param directories: list of directories scanned by Exiftool application.
        :return: iterator object.
        """
        in_logger = logging.getLogger("MyPythonProject.Images.{0}.get_images".format(str(PureWindowsPath(__file__).stem)))
        collection = OrderedDict()
        args = [str(PureWindowsPath(expandvars("%_RESOURCES%")) / "exiftool.exe"),
                "-r",
                "-d",
                "%Y%m%d%H%M%S",
                "-j",
                "-charset",
                "Latin1",
                "-DateTimeOriginal",
                "-fileOrder",
                "DateTimeOriginal",
                "-ext",
                "jpg"]
        if directories:
            args.extend(sorted(directories))
            with TemporaryFile(mode="r+", encoding="UTF_8") as stream:
                process = run(args, stdout=stream, stderr=PIPE, universal_newlines=True)
                in_logger.debug("Command    : %s.", process.args)
                in_logger.debug("Return code: %s.", process.returncode)
                if not process.returncode:
                    for line in process.stderr.splitlines():
                        in_logger.debug("%s.", line.lstrip())
                    stream.seek(0)
                    for item in json.load(stream):
                        in_logger.debug(item["DateTimeOriginal"])
                        in_logger.debug(item["SourceFile"])
                        with suppress(KeyError):
                            key = item["SourceFile"]
                            value = int(str(item["DateTimeOriginal"])[:6])
                            collection[key] = value
        for item in collection.items():
            yield item

    @staticmethod
    def get_numbers(item):
        """
        Return the five digits unique number composing an image name.

        :param item: tuple composed of both the image name and the image original month.
        :return: five digits unique number as an integer object.
        """
        path, _ = item
        return int(splitext(basename(path))[0].split("_")[1])

    @staticmethod
    def set_numbers(collection, template):
        """
        Return an iterator object yielding digits numbers present into `template` and absent from `collection`.
        Used to return available digits numbers when renaming images.

        :param collection:
        :param template:
        :return: iterator object.
        """
        col = set(collection)
        tmp = set(template)
        for number in sorted(tmp.difference(col)):
            yield number

    @staticmethod
    def partition(collection, predicate):
        """
        Return two iterator objects used to split `collection` depending on `predicate`.
        Useful to split the collection between images with a name compliant with the naming convention and images with a name non-compliant with the naming convention.

        :param collection: images collection.
        :param predicate: predicate used to filter images.
        :return: iterator objects gathered together into a tuple object.
        """
        it1, it2 = tee(collection)
        return filter(predicate, it1), filterfalse(predicate, it2)

    @staticmethod
    def predicate(item):
        """
        Return a boolean value informing that the image name is compliant with the naming convention.

        :param item: tuple composed of both the image name and the image original month.
        :return: boolean value.
        """
        path, _ = item
        return re.match(r"^(?:{0})(?:{1})_(\d{{5}})\.jpg$".format(DFTYEARREGEX, DFTMONTHREGEX), basename(path), re.IGNORECASE)


# =================
# Global functions.
# =================
def validyear(yea):
    """
    Check if a year is valid.

    :param yea: year as a four digits number. Must be a string object.
    :return: year as an integer object if argument is valid. Raise an argparse.ArgumentTypeError if argument isn't valid.
    """
    regex = re.compile(r"^(?=\d{4})20[0-2]\d$")
    if not regex.match(yea):
        raise argparse.ArgumentTypeError('"{0}" is not a valid year'.format(yea))
    return int(yea)


# ============
# Main script.
# ============
if __name__ == "__main__":

    THAT_SCRIPT = PureWindowsPath(os.path.abspath(__file__))

    # Local constants.
    LOGGERS = ["MyPythonProject"]
    MAPPING = {True: "debug", False: "info"}

    # Parse arguments.
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    parser.set_defaults(console=True)
    parser.add_argument("year", type=validyear)
    parser.add_argument("--debug", action="store_true")
    arguments = vars(parser.parse_args())

    # Logging.
    with open(THAT_SCRIPT.parents[1] / "Resources" / "logging.yml", encoding=UTF8) as fp:
        config = yaml.load(fp)

    # Template.
    template = TemplatingEnvironment(loader=jinja2.FileSystemLoader(str(PureWindowsPath(expandvars("%_PYTHONPROJECT%")) / "Images")))
    template.set_template(T1="T01", T2="T02")

    # -----
    for logger in LOGGERS:
        with suppress(KeyError):
            config["loggers"][logger]["level"] = MAPPING[arguments.get("debug", False)].upper()

    # -----
    # if arguments.get("console", False):
    #
    #     # Set up a specific stream handler.
    #     for logger in LOGGERS:
    #         with suppress(KeyError):
    #             config["loggers"][logger]["handlers"] = ["file", "console"]
    #     with suppress(KeyError):
    #         config["handlers"]["console"]["level"] = "DEBUG"
    #
    #     # Set up a specific filter for logging from "MyPythonProject.Images" only.
    #     localfilter = {"class": "logging.Filter", "name": "MyPythonProject.Images"}
    #     config["filters"]["localfilter"] = localfilter
    #     config["handlers"]["console"]["filters"] = ["localfilter"]

    # -----
    logging.config.dictConfig(config)

    # -----
    mycollection = ImagesCollection.fromyear(arguments.get("year"))

    # Move images if required.
    if mycollection.filestomove:
        _collection = list(mycollection.move())
        cmdfile = join(expandvars("%TEMP%"), "move_{0}.cmd".format(now(template=TEMPLATE7)))
        with open(cmdfile, WRITE, encoding="ISO-8859-1") as stream1:
            stream1.write(getattr(template, "T1").render(collection=_collection))
            with open(join(expandvars("%TEMP%"), "cmdfile.txt"), WRITE, encoding="ISO-8859-1") as stream2:
                stream2.write(f"{len(_collection)}|{cmdfile}\n")
        sys.exit(10)

    # Rename images.
    _collection = list(mycollection.rename())
    if _collection:
        cmdfile = join(expandvars("%TEMP%"), "rename_{0}.cmd".format(now(template=TEMPLATE7)))
        with open(cmdfile, WRITE, encoding="ISO-8859-1") as stream1:
            stream1.write(getattr(template, "T2").render(collection=_collection))
            with open(join(expandvars("%TEMP%"), "cmdfile.txt"), WRITE, encoding="ISO-8859-1") as stream2:
                stream2.write(f"{len(_collection)}|{cmdfile}\n")
        sys.exit(11)

    # No action required.
    sys.exit(0)
