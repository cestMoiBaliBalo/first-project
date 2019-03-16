# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import calendar
import logging
import operator
import os
import re
from abc import ABC, abstractmethod
from base64 import b85decode, b85encode
from collections import OrderedDict
from contextlib import ContextDecorator, ExitStack, suppress
from datetime import date, datetime, time, timedelta
from functools import partial, singledispatch
from itertools import chain, dropwhile, filterfalse, groupby, repeat, tee, zip_longest
from logging import Formatter
from logging.handlers import RotatingFileHandler
from operator import itemgetter
from pathlib import PurePath, PureWindowsPath, WindowsPath
from string import Template
from subprocess import PIPE, run
from typing import Any, Iterable, Iterator, List, Optional, Tuple, Union

import jinja2
import yaml
from dateutil.parser import parserinfo
from pandas import DataFrame  # type: ignore
from pytz import timezone

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_THATFILE = PurePath(os.path.abspath(__file__))

# ==================
# Functions aliases.
# ==================
abspath, basename, dirname, exists, expandvars, isdir, join, normpath = os.path.abspath, os.path.basename, os.path.dirname, os.path.exists, os.path.expandvars, os.path.isdir, os.path.join, os.path.normpath

# ==========
# Constants.
# ==========
APPEND = "a"
COPYRIGHT = "\u00a9"
DFTENCODING = "UTF_8"
DFTTIMEZONE = "Europe/Paris"
LOCAL = timezone("Europe/Paris")
LOGPATTERN = "%(asctime)s [%(name)s]: %(message)s"
UTC = timezone("UTC")
UTF8 = "UTF_8"
UTF16 = "UTF_16LE"
UTF16BOM = "\ufeff"
WRITE = "w"

# Resources.
ARECA = str(PurePath("C:/Program Files", "Areca", "areca_cl.exe"))
DATABASE = str(_THATFILE.parents[1] / "Resources" / "database.db")
TESTDATABASE = str(_THATFILE.parent / "Unittests" / "Resources" / "database.db")
XREFERENCES = str(_THATFILE.parents[1] / "Resources" / "xreferences.db")

# Regular expressions.
BOOTLEGALBUM = r"((0[1-9]|1[0-2])\.(0[1-9]|[12]\d|3[01])(?:\.(\d))?(?: - ([^\\]+)))"
DEFAULTALBUM = r"(((?:20[0-2]|19[6-9])\d)(?:\.(\d))?(?: - ([^\\]+)))"
COMPRESSION = r"(?:([01])\.[^\\]+)"
DFTDAYREGEX = r"0[1-9]|[12]\d|3[01]"
DFTMONTHREGEX = r"0[1-9]|1[0-2]"
DFTYEARREGEX = r"(?:20[0-2]|19[6-9])\d"
DISC = r"(?:CD\d\\)?"
DRIVE = r"(?:[^\\]+)"
FOLDER = r"(?:\d\\)?"
LETTER = r"([A-Z])"
LOOKALBUMSORT = r"(?=[\d.]{12}$)(?=[12]\.\d{8}\.\d$)"
LOOKBOOTLEGALBUM = r"(?=(?:[^\\]+\\){7,8}[A-Za-z0-9.]+$)(?=(?:.+\.\w{3,4})$)"
LOOKDEFAULTALBUM = r"(?=(?:[^\\]+\\){5,7}[A-Za-z0-9.]+$)(?=(?:.+\.\w{3,4})$)"
UPCREGEX = r"\d{12,13}"

# Regular expressions templates.
ARTIST = "(?:(@{letter}[^\\\\]+))"
FILE = "(?:((([12])\\.\\b@{year}\\B(?:@{month}@{day})\\b\\.\\d)\\.\\b@{encoder}\\B\\d\\.D\\d\\.T\\d{2})\\.(\\w{3,4}))"
LOOKEXTENSIONS = r"(?=.+\.(?:@{extensions})$)"

# Templates for converting datetime objects to strings.
TEMPLATE1 = "$day $d/$m/$Y $H:$M:$S $Z (UTC$z)"
TEMPLATE2 = "$day $d $month $Y $H:$M:$S $Z (UTC$z)"
TEMPLATE3 = "$d/$m/$Y $H:$M:$S $Z (UTC$z)"
TEMPLATE4 = "$day $d $month $Y $H:$M:$S $Z (UTC$z)"
TEMPLATE5 = "$Y-$m-$d"
TEMPLATE6 = "$d/$m/$Y $H:$M:$S"
TEMPLATE7 = "$Y$m${d}_$H$M$S"

# Local drives.
IMAGES = PurePath("H:/")
MUSIC = PurePath("F:/")

# Distant directories.
IMAGES_COLLECTION = r"\\Diskstation\backup\Images\Collection"

# Miscellaneous containers.
ACCEPTEDANSWERS = ["N", "Y"]
EXTENSIONS = {"computing": ["py", "json", "yaml", "cmd", "css", "xsl"],
              "documents": ["doc", "txt", "pdf", "xav"],
              "music": ["ape", "dsf", "flac", "mp3", "m4a", "ogg", "tak", "wv"],
              "lossless": ["ape", "dsf", "flac", "tak", "wv"],
              "lossy": ["mp3", "m4a", "ogg"]}
GENRES = ["Rock",
          "Hard Rock",
          "Heavy Metal",
          "Trash Metal",
          "Black Metal",
          "Doom Metal",
          "Progressive Rock",
          "Alternative Rock",
          "Pop",
          "French Pop"]
LOCALMONTHS = ["Janvier",
               "Février",
               "Mars",
               "Avril",
               "Mai",
               "Juin",
               "Juillet",
               "Août",
               "Septembre",
               "Octobre",
               "Novembre",
               "Decembre"]


# ========
# Classes.
# ========
# class CustomFilter(Filter):
#     def filter(self, record):
#         # print(record.pathname)
#         # print(record.filename)
#         # print(record.module)
#         # print(record.funcName)
#         # if record.funcName.lower() in ["_selectlogs", "get_albumheader", "rippeddiscsview1"]:
#         #     return True
#         return False
class CustomTemplate(Template):
    delimiter = "@"
    idpattern = r"([a-z][a-z0-9]+)"
    flags = re.ASCII

    def __init__(self, template):
        super().__init__(template)


class CustomFormatter(Formatter):
    converter = datetime.fromtimestamp  # type: ignore
    default_time_format = "%d/%m/%Y %H:%M:%S"
    default_localizedtime_format = "%Z (UTC%z)"
    default_format = "%s %s,%03d %s"

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created, tz=timezone(DFTTIMEZONE))
        s = self.default_format % (ct.strftime("%A"), ct.strftime(self.default_time_format), record.msecs, ct.strftime(self.default_localizedtime_format))
        if datefmt:
            s = ct.strftime(datefmt)
        return s


class ChangeRemoteCurrentDirectory(ContextDecorator):
    """
    Context manager to change the current directory of a remote system.
    Use default FTPLIB library.
    """

    def __init__(self, ftpobj, directory):
        self._dir = directory
        self._ftpobj = ftpobj
        self._cwd = ftpobj.pwd()

    def __enter__(self):
        self._ftpobj.cwd(self._dir)
        return self

    def __exit__(self, *exc):
        self._ftpobj.cwd(self._cwd)


class AlternativeChangeRemoteCurrentDirectory(ContextDecorator):
    """
    Context manager to change the current directory of a remote system.
    Use FTPUTIL library.
    """

    def __init__(self, ftpobj, directory):
        self._dir = directory
        self._ftpobj = ftpobj
        self._cwd = ftpobj.getcwd()

    def __enter__(self):
        self._ftpobj.chdir(self._dir)
        return self

    def __exit__(self, *exc):
        self._ftpobj.chdir(self._cwd)


class ChangeLocalCurrentDirectory(ContextDecorator):
    """
    Context manager to change the current directory of a local system.
    """

    def __init__(self, directory):
        self._dir = directory
        self._cwd = os.getcwd()

    def __enter__(self):
        os.chdir(self._dir)
        return self

    def __exit__(self, *exc):
        os.chdir(self._cwd)


class TitleCaseBaseConverter(ABC):
    """
    
    """

    # Define class-level configuration.
    with open(join(_THATFILE.parent / "Resources" / "resource1.yml"), encoding=UTF8) as fp:
        config = yaml.load(fp)

    # Define class-level regular expressions.
    acronyms = re.compile(r"\b((?:u\.?)(?:s\.?a\.?|k\.?))\b", re.IGNORECASE)
    apostrophe_regex1 = re.compile(r"\b([a-z]+)'([a-z]+)\b", re.IGNORECASE)
    apostrophe_regex2 = re.compile(r"\b(o)'\b([a-z]+)\b", re.IGNORECASE)
    apostrophe_regex3 = re.compile(r"\b(o)'\B", re.IGNORECASE)
    apostrophe_regex4 = re.compile(r" \bn'\B ", re.IGNORECASE)
    apostrophe_regex5 = re.compile(r" \B'n\b ", re.IGNORECASE)
    apostrophe_regex6 = re.compile(r" \B'n'\B ", re.IGNORECASE)
    apostrophe_regex7 = re.compile(r"\b'n'\b", re.IGNORECASE)
    capitalize_secondword = re.compile(r"^(\([^)]+\) )\b([a-z]+)\b", re.IGNORECASE)
    capitalize_words = re.compile(r"\b([a-z]+)\b", re.IGNORECASE)
    punctuation = re.compile(r"(\w+\.\.\.) (\w+)")
    roman_numbers_regex1 = re.compile(r"(?i)\b(?:V|(X{1,3}|(?=[CL])C{,3}L?X{,3})V?)?I{,3}\b")
    roman_numbers_regex2 = re.compile(r"(?i)\b(?:(?=[CL])C{,3}L?X{,3}|X{1,3})?I[VX]\b")
    roman_numbers_regex3 = re.compile(r"(?i)\bC{,3}X[CL](?:V?I{,3}|I[VX])\b")

    def __init__(self) -> None:

        # Initializations.
        self.alw_lowercase, self.alw_uppercase, self.alw_capital, self.capitalize_firstword, self.capitalize_lastword = None, None, None, None, None

        # Load configuration.
        capitalized = self.config.get("capitalized", [])
        capitalize_firstword = self.config.get("capitalize_firstword", False)
        capitalize_lastword = self.config.get("capitalize_lastword", False)
        lowercases = self.config.get("lowercases", [])
        uppercases = self.config.get("uppercases", [])
        if lowercases:
            self.alw_lowercase = re.compile(r"\b({0})\b".format("|".join(lowercases)), re.IGNORECASE)
        if uppercases:
            self.alw_uppercase = re.compile(r"\b({0})\b".format("|".join(uppercases)), re.IGNORECASE)
        if capitalized:
            self.alw_capital = re.compile(r"\b({0})\b".format("|".join(capitalized)), re.IGNORECASE)
        if capitalize_firstword:
            self.capitalize_firstword = re.compile(r"^([a-z]+)\b", re.IGNORECASE)
        if capitalize_lastword:
            self.capitalize_lastword = re.compile(r"\b([a-z]+)$", re.IGNORECASE)

    @abstractmethod
    def convert(self, title: str) -> str:
        """

        :param title:
        :return:
        """
        pass


class TitleCaseConverter(TitleCaseBaseConverter):
    """

    """
    logger = logging.getLogger("{0}.TitleCaseConverter".format(__name__))

    def __init__(self) -> None:
        super().__init__()

    def convert(self, title: str):
        """
        
        :param title: 
        :return: 
        """
        self.logger.debug(title)

        # ----------------
        # General process.
        # ----------------
        # 1. Title is formatted with lowercase letters.
        # 2. Words are capitalized --> `capitalize_words`.
        title = self.capitalize_words.sub(lambda match: match.group(1).capitalize(), title.lower().replace("[", "(").replace("]", ")"))
        self.logger.debug(title)

        # -------------------
        # Exceptions process.
        # -------------------
        # 1. Words formatted only with lowercase letters --> `alw_lowercase`.
        # 2. Words formatted only with a capital letter --> `alw_capital`.
        # 3. Capital letter is mandatory for the first word of the title --> `capitalize_firstword`.
        # 4. Capital letter is mandatory for the last word of the title --> `capitalize_lastword`.
        # 5. Words formatted only with uppercase letters --> `alw_uppercase`.
        if self.alw_lowercase:
            title = self.alw_lowercase.sub(lambda match: match.group(1).lower(), title)
        if self.alw_capital:
            title = self.alw_capital.sub(lambda match: " ".join(word.capitalize() for word in match.group(1).split()), title)
        if self.capitalize_firstword:
            title = self.capitalize_firstword.sub(lambda match: match.group(1).capitalize(), title)
        if self.capitalize_lastword:
            title = self.capitalize_lastword.sub(lambda match: match.group(1).capitalize(), title)
        if self.alw_uppercase:
            title = self.alw_uppercase.sub(lambda match: match.group(1).upper(), title)
        self.logger.debug(title)

        # -----------------
        # Acronyms process.
        # -----------------
        title = self.acronyms.sub(lambda match: match.group(1).upper(), title)
        self.logger.debug(title)

        # --------------------
        # Apostrophes process.
        # --------------------
        title = self.apostrophe_regex1.sub(lambda match: "{0}'{1}".format(match.group(1).capitalize(), match.group(2).lower()), title)
        title = self.apostrophe_regex2.sub(lambda match: "{0}'{1}".format(match.group(1).capitalize(), match.group(2).capitalize()), title)
        title = self.apostrophe_regex3.sub(lambda match: "{0}'".format(match.group(1).lower()), title)
        title = self.apostrophe_regex4.sub(" 'n' ", title)
        title = self.apostrophe_regex5.sub(" 'n' ", title)
        title = self.apostrophe_regex6.sub(" 'n' ", title)
        title = self.apostrophe_regex7.sub(" 'n' ", title)
        self.logger.debug(title)

        # -----------------
        # Specific process.
        # -----------------
        # Capital letter is mandatory for the second word if the first one is defined between parenthesis --> `capitalize_secondword`.
        title = self.capitalize_secondword.sub(lambda match: "{0}{1}".format(match.group(1), match.group(2).capitalize()), title)
        self.logger.debug(title)

        # ----------------------
        # Roman numbers process.
        # ----------------------
        title = self.roman_numbers_regex1.sub(lambda match: match.group(0).upper(), title)
        title = self.roman_numbers_regex2.sub(lambda match: match.group(0).upper(), title)
        title = self.roman_numbers_regex3.sub(lambda match: match.group(0).upper(), title)
        self.logger.debug(title)

        # --------------------
        # Punctuation process.
        # --------------------
        title = self.punctuation.sub(lambda match: f"{match.group(1)}{match.group(2)}", title)

        # -----------------------
        # Return converted title.
        # -----------------------
        return title


class LocalParser(parserinfo):
    MONTHS = [('Janvier', 'January'),
              ('Février', 'February'),
              ('Mars', 'March'),
              ('Avril', 'April'),
              ('Mai', 'May'),
              ('Juin', 'June'),
              ('Juillet', 'July'),
              ('Août', 'August'),
              ('Septembre', 'September'),
              ('Octobre', 'October'),
              ('Novembre', 'November'),
              ('Decembre', 'December')]

    def __init__(self, dayfirst=False, yearfirst=False):
        super().__init__(dayfirst, yearfirst)


# ===========
# Decorators.
# ===========
def getitem_(index=0):
    def wrapper(f):
        def sub_wrapper1(arg):
            return f(arg[index])

        return sub_wrapper1

    return wrapper


def partial_(*args, **kwargs):
    def wrapper(f):
        def sub_wrapper2(arg):
            return partial(f, *args, **kwargs)(arg)

        return sub_wrapper2

    return wrapper


# ===========================
# Customized parsing actions.
# ===========================
class SetDatabase(argparse.Action):
    """

    """

    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        if values:
            setattr(namespace, "db", TESTDATABASE)


class GetPath(argparse.Action):
    """
    Set "destination" attribute with the full path corresponding to the "values".
    """
    destinations = {"documents": expandvars("%_MYDOCUMENTS%"),
                    "temp": expandvars("%TEMP%"),
                    "backup": expandvars("%_BACKUP%"),
                    "onedrive": join(expandvars("%USERPROFILE%"), "OneDrive")}

    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, self.destinations[values])


class GetExtensions(argparse.Action):
    """
    Set "files" attribute with a list of extensions.
    Set "extensions" attribute with a list of extensions to process.
    """

    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        lext = []
        for file in values:
            lext.extend(EXTENSIONS[file])
        setattr(namespace, "extensions", lext)


class ExcludeExtensions(argparse.Action):
    """
    Set "exclude" attribute with a list of extensions to exclude.
    Set "extensions" attribute with a list of extensions to process.
    """

    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        lext = []
        for ext in getattr(namespace, "extensions"):
            if ext not in values:
                lext.append(ext)
        setattr(namespace, "extensions", lext)


class KeepExtensions(argparse.Action):
    """
    Set "retain" attribute with a list of extensions to retain.
    Set "extensions" attribute with a list of extensions to process.
    """

    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        lext = []
        for ext in values:
            if ext in getattr(namespace, "extensions"):
                lext.append(ext)
        setattr(namespace, "extensions", lext)


class IncludeExtensions(argparse.Action):
    """
    Set "include" attribute with a list of extensions to include.
    Set "extensions" attribute with a list of extensions to process.
    """

    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        lext = getattr(namespace, "extensions")
        for ext in values:
            if ext not in lext:
                lext.append(ext)
        setattr(namespace, "extensions", lext)


class SetEndSeconds(argparse.Action):
    """
    Set "end" attribute.
    """

    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        if not values:
            setattr(namespace, self.dest, getattr(namespace, "beg"))


# ===================
# Jinja2 environment.
# ===================
class TemplatingEnvironment(object):
    def __init__(self, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True, **kwargs):
        self._environment = jinja2.Environment(keep_trailing_newline=keep_trailing_newline, trim_blocks=trim_blocks, lstrip_blocks=lstrip_blocks, loader=kwargs.get("loader"))

    def set_environment(self, **kwargs):
        globalvars = kwargs.get("globalvars", {})
        filters = kwargs.get("filters", {})
        for k, v in globalvars.items():
            self._environment.globals[k] = v
        for k, v in filters.items():
            self._environment.filters[k] = v

    def set_template(self, **templates):
        for k, v in templates.items():
            setattr(self, k, self._environment.get_template(v))

    @property
    def environment(self):
        return self._environment


# ==========================
# Data validation functions.
# ==========================
def valid_path(path: str) -> str:
    """

    :param path:
    :return:
    """
    if not exists(path):
        raise ValueError(f'"{path}" doesn\'t exist.')
    if not isdir(path):
        raise ValueError(f'"{path}" is not a directory.')
    if not os.access(path, os.R_OK):
        raise ValueError(f'"{path}" is not a readable directory.')
    return path


def valid_database(database: str) -> str:
    """

    :param database:
    :return:
    """
    try:
        if not exists(database):
            raise ValueError('"{0}" doesn\'t exist.'.format(database))
    except TypeError:
        raise ValueError('"{0}" doesn\'t exist.'.format(database))
    return database


def valid_discnumber(discnumber: Union[int, str]) -> int:
    """
    Check if string `discnumber` is a coherent disc number.
    Raise a ValueError if it is not coherent.

    :param discnumber: string.
    :return: input string converted to an integer number.
    """
    msg = r"is not a valid disc number."
    try:
        _discnumber = int(discnumber)
    except (ValueError, TypeError):
        raise ValueError('"{0}" {1}'.format(discnumber, msg))
    if not _discnumber:
        raise ValueError('"{0}" {1}'.format(discnumber, msg))
    return _discnumber


def valid_tracks(tracks: Union[int, str]) -> int:
    """
    Check if string `tracks` is a coherent track number.
    Raise a ValueError if it is not coherent.

    :param tracks: string.
    :return: input string converted to an integer number.
    """
    msg = r"is not a valid total tracks number."
    try:
        _tracks = int(tracks)
    except TypeError:
        raise ValueError('"{0}" {1}'.format(tracks, msg))
    if not _tracks:
        raise ValueError('"{0}" {1}'.format(tracks, msg))
    return _tracks


def valid_albumid(albumid: str) -> str:
    """
    Check if string `albumid` is a coherent unique album ID.
    Raise a ValueError if it is not coherent.

    :param albumid: string.
    :return: input string.
    """
    rex = re.compile(r"^([A-Z])\.\1[^.]+\.$")
    selectors = [True, True]
    try:
        _artistsort = albumid[:-12]
        _albumsort = albumid[-12:]
    except TypeError:
        raise ValueError('"{0}" is not a valid album ID.'.format(albumid))

    match = rex.match(_artistsort)
    if not match:
        selectors[0] = False

    try:
        _albumsort = valid_albumsort(_albumsort)
    except TypeError:
        selectors[1] = False

    if not all(selectors):
        if not any(selectors):
            raise ValueError("Both `artistsort` and `albumsort` don\'t match the expected pattern.")
        raise ValueError("`artistsort` or `albumsort` doesn\'t match the expected pattern.")

    return "{0}{1}".format(_artistsort, _albumsort)


def valid_albumsort(albumsort: str) -> str:
    """
    Check if string `albumsort` is a coherent albumsort audio tag.
    Raise a ValueError if it is not coherent.

    :param albumsort: string.
    :return: input string.
    """
    rex1 = re.compile(r"^{3}\d\.({0})({1})({2})\.\d$".format(DFTYEARREGEX, DFTMONTHREGEX, DFTDAYREGEX, LOOKALBUMSORT))
    rex2 = re.compile(r"^{1}\d\.({0})0000\.\d$".format(DFTYEARREGEX, LOOKALBUMSORT))
    msg = r"is not a valid albumsort."

    try:
        match1 = rex1.match(albumsort)
        match2 = rex2.match(albumsort)
    except TypeError:
        raise ValueError('"{0}" {1}'.format(albumsort, msg))
    if all([not match1, not match2]):
        raise ValueError('"{0}" {1}'.format(albumsort, msg))
    return albumsort


def valid_year(year: Union[int, str]) -> int:
    """
    Check if string `year` is a coherent year.
    Raise a ValueError if it is not coherent.

    :param year: string.
    :return: input string converted to an integer number.
    """
    regex, msg = re.compile("^({0})$".format(DFTYEARREGEX)), r"is not a valid year."

    # Argument is converted to a string.
    try:
        year = str(year)
    except TypeError:
        raise ValueError('"{0}" {1}'.format(year, msg))

    # Does the string match the year pattern?.
    try:
        if not regex.match(year):
            raise ValueError('"{0}" {1}'.format(year, msg))
    except TypeError:
        raise ValueError('"{0}" {1}'.format(year, msg))

    # Year is returned as an integer.
    return int(year)


def valid_productcode(productcode: str) -> str:
    """
    Check if string `productcode` is a coherent product code.
    Raise a ValueError if it is not coherent.

    :param productcode: string.
    :return: input string.
    """
    regex, msg = re.compile(f"^{UPCREGEX}$"), r"is not a valid product code."

    try:
        productcode = str(productcode)
    except TypeError:
        raise ValueError('"{0}" {1}'.format(productcode, msg))
    if not regex.match(productcode):
        raise ValueError('"{0}" {1}'.format(productcode, msg))
    return productcode


def valid_genre(genre: str) -> str:
    """
    Check if string `genre` is a coherent audio genre.
    Raise a ValueError if it is not coherent.

    :param genre: string.
    :return: input string.
    """
    msg = r"is not a valid genre."
    try:
        if genre.lower() not in (item.lower() for item in GENRES):
            raise ValueError('"{0}" {1}'.format(genre, msg))
    except AttributeError:
        raise ValueError('"{0}" {1}'.format(genre, msg))
    return genre


# ====================
# Filtering functions.
# ====================
def contains_(a, b) -> bool:
    return operator.contains(a, b)


def eq_integer(a: int, b: int) -> bool:
    return operator.eq(a, b)


def eq_string(a: str, b: str, sensitive: bool = False) -> bool:
    if not sensitive:
        return operator.eq(a.lower(), b.lower())
    return operator.eq(a, b)


def is_(a, b) -> bool:
    return operator.is_(a, b)


# ========================
# Miscellaneous functions.
# ========================
def customformatterfactory(pattern=LOGPATTERN):
    return CustomFormatter(pattern)


def customfilehandler(maxbytes, backupcount, encoding=UTF8):
    return RotatingFileHandler(join(_THATFILE.parents[2] / "Log" / "pythonlog.log"), maxBytes=maxbytes, backupCount=backupcount, encoding=encoding)


def copy(src: str, dst: str, *, size: int = 16 * 1024) -> str:
    if not isdir(dst):
        raise ValueError('"%s" is not a directory.' % dst)
    with ExitStack() as stack:
        fr = stack.enter_context(open(src, mode="rb"))
        fw = stack.enter_context(open(join(dst, basename(src)), mode="wb"))
        while True:
            _bytes = fr.read(size)
            if not _bytes:
                break
            fw.write(_bytes)
    return join(dst, basename(src))


def grouper(iterable, n, *, fillvalue=None):
    """

    :param iterable:
    :param n:
    :param fillvalue:
    :return:
    """
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def advanced_grouper(collection, *, key: Optional[int] = None, subkey: Optional[int] = None):
    if key is None:
        for item in collection:
            yield item
    elif key is not None:
        group_by = [(key, 0), (subkey, 1)]
        if subkey is None:
            group_by = [(key, 0)]
        group_by = iter(group_by)
        while True:
            try:
                key, index = next(group_by)
            except StopIteration:
                break
            if index == 0:
                collection = alternative_grouper(*collection, index=key)
            elif index > 0:
                templist1, templist2 = [], []
                for _key, _group in collection:
                    for _sub_key, _sub_group in alternative_grouper(*_group, index=key):
                        templist1.append((_sub_key, _sub_group))
                    templist2.append((_key, templist1))
                    templist1 = []
                collection = list(templist2)
        for item in collection:
            yield item


def alternative_grouper(*collection, index: int = 0):
    for k, group in groupby(collection, key=itemgetter(index)):
        yield k, list(group)


def partitioner(iterable, *, predicate=None):
    """

    :param iterable:
    :param predicate:
    :return:
    """
    if predicate is None:
        predicate = bool
    it1, it2 = tee(iterable)
    return filter(predicate, it1), filterfalse(predicate, it2)


def get_dirname(path: str, *, level: int = 1) -> str:
    """

    :param path:
    :param level:
    :return:
    """
    _dirname, _level = path, 1  # type: str, int
    while _level <= level:
        _dirname = dirname(_dirname)
        _level += 1
    return _dirname


def get_readabledate(dt: datetime, *, template: str = TEMPLATE4, tz=None) -> str:
    """
    Return a human readable (naive or aware) date respective to the local time zone.

    :param dt: datetime object.
    :param template: template used to display the date.
    :param tz: datetime object time zone.
    :return: string.
    """
    return _get_readabledate(dt, template, tz)


def now(*, template: str = TEMPLATE4) -> str:
    """

    :return:
    """
    return _get_readabledate(datetime.utcnow(), template, tz=UTC)


def format_date(dt: Union[date, datetime], *, template: str = TEMPLATE4) -> str:
    """
    Return a human readable datetime object.

    :param dt: datetime object.
    :param template: template used to display the date.
    :return: string.
    """
    return _format_date(dt, template)


def localize_date(dt: datetime, tz=UTC) -> datetime:
    """
    Return a datetime object localized into the local time zone from a different time zone.

    :param dt: datetime object.
    :param tz: datetime object time zone.
    :return: datetime object.
    """
    return _localize_date(dt, tz)


def convert_timestamp(timestamp: int, tz=UTC) -> datetime:
    """

    :param timestamp:
    :param tz:
    :return:
    """
    return _convert_timestamp(timestamp, tz)


def adjust_datetime(year: int, month: int, day: int, hour: int, minutes: int, seconds: int) -> Optional[datetime]:
    """

    :param year:
    :param month:
    :param day:
    :param hour:
    :param minutes:
    :param seconds:
    :return:
    """
    datobj = None  # type: Optional[datetime]
    try:
        datobj = datetime(year, month, day, hour, minutes, seconds)
    except ValueError as error:
        (message,) = error.args
    else:
        return datobj
    if message.lower() == "day is out of range for month":
        _, number_of_days = calendar.monthrange(year, month)  # type: int, int
        delta = day - number_of_days  # type: int
        return datetime.combine(date(year, month, number_of_days) + timedelta(days=delta), time(hour, minutes, seconds))
    raise ValueError(message)


def get_tabs(length: int, *, tabsize: int = 3) -> str:
    """

    :param length:
    :param tabsize:
    :return:
    """
    x = int(length / tabsize)
    y = length % tabsize
    if y:
        x += 1
    return x * "\t"


def get_nearestmultiple(length: int, *, multiple: int = 3) -> int:
    """

    :param length:
    :param multiple:
    :return:
    """
    x = int(length / multiple)
    y = length % multiple
    if y:
        x += 1
    return x * multiple


def get_rippingapplication(*, timestamp: Optional[int] = None) -> str:
    """
    Get ripping application respective to the facultative input local timestamp.

    :param timestamp: facultative input local timestamp.
    :return: ripping application.
    """
    application = {"1548975600": "dBpoweramp 16.5", "1388530800": "dBpoweramp 15.1", "0": "dBpoweramp 14.1"}
    ts: Optional[int] = timestamp
    if timestamp is None:
        ts = int(UTC.localize(datetime.utcnow()).astimezone(LOCAL).timestamp())
    it = iter(dropwhile(lambda i: int(i) > ts, sorted(application, key=int, reverse=True)))  # type: ignore
    return application[next(it)]


def find_files(directory: str, *, excluded=None):
    """
    Return a generator object yielding files stored into `directory` argument.
    :param directory: Directory to walk through. Must be a string representing an existing path.
    :param excluded: Callable returning a set of files (as returned by os.listdir) to exclude.
                     Callable arguments are:
                        - root folder returned by os.walk.
                        - list of files present into the root folder.
    :return: generator object.
    """
    collection = []  # type: List[Iterable[str]]
    if not excluded:
        collection.extend(map(os.path.join, repeat(root), files) for root, _, files in os.walk(directory) if files)
    elif excluded:
        for root, _, files in os.walk(directory):
            if files:
                files = set(files) - excluded(root, *set(files))
                if files:
                    collection.extend(map(os.path.join, repeat(root), files))
    for file in sorted(collection):
        yield file


def mainscript(strg: str, align: str = "^", fill: str = "=", length: int = 140) -> str:
    return "{0:{fill}{align}{length}}".format(" {0} ".format(strg), align=align, fill=fill, length=length)


# def xsltransform(xml, xsl, html):
#     process = subprocess.run(["java", "-cp", expandvars("%_SAXON%"), "net.sf.saxon.Transform",
#                               "-s:{0}".format(xml),
#                               "-xsl:{0}".format(xsl),
#                               "-o:{0}".format(html)])
#     return process.returncode


# def get_input(prompt, *, cls=True, template=None, **kwargs):
#     """
#
#     :param prompt:
#     :param cls:
#     :param template:
#     :param kwargs:
#     :return:
#     """
#     if cls:
#         run("CLS", shell=True)
#     if template:
#         print(template.render(**kwargs))
#     return input(prompt)


def get_drives() -> Iterable[str]:
    """

    :return:
    """
    regex = re.compile(r"^(E|[I-R]):$")
    process = run("wmic logicaldisk get name", shell=True, universal_newlines=True, stdout=PIPE)
    for drive in (drive.rstrip() for drive in process.stdout.splitlines() if regex.match(drive.rstrip())):
        yield drive


def format_collection(collection: Iterable[Tuple[Any, ...]], *, tabsize: int = 3, gap: int = 3, group: Optional[int] = 15) -> Iterable[Tuple[str, ...]]:
    """

    :param collection:
    :param tabsize:
    :param gap:
    :param group:
    :return:


    :how to use it:
    collection = list(format_collection(somecollection, group=15))
    template.render(collection=collection[somepage])
    """
    out_collection = []  # type: Iterable[Tuple[Any, ...]]
    _, _, in_collection = _set_collection(collection, None, tabsize=tabsize, gap=gap)
    if group:
        out_collection = zip_longest(*[in_collection] * group, fillvalue=None)
    for item in out_collection:
        yield item


def print_collection(collection: Iterable[Tuple[Any, ...]], headers: Optional[Iterable[str]], *, char: str = "=", tabsize: int = 3, gap: int = 3, group: Optional[int] = 50) -> Iterable[str]:
    """

    :param collection:
    :param headers:
    :param char:
    :param tabsize:
    :param gap:
    :param group:
    :return:

    :how to use it:
    for item in print_collection(somecollection, someheaders):
        print(item)
    """
    separators, headers, in_collection = _set_collection(collection, headers, char=char, tabsize=tabsize, gap=gap)
    if group:
        in_collection = zip_longest(*[in_collection] * group, fillvalue=None)
    out_collection: List[str]

    # Both headers and groups.
    if all([bool(headers), bool(group)]):
        out_collection = []
        for _group in in_collection:
            out_collection.extend(["", "", "".join(separators), "".join(headers), "".join(separators)])
            out_collection.extend("".join(item) for item in filter(None, _group))
        out_collection = out_collection[2:]

    # Headers only.
    elif headers and not group:
        out_collection = ["".join(separators), "".join(headers), "".join(separators)]
        out_collection.extend("".join(item) for item in in_collection)

    # Groups only.
    elif not headers and group:
        out_collection = []
        for _group in in_collection:
            out_collection.extend(["", ""])
            out_collection.extend("".join(item) for item in filter(None, _group))
        out_collection = out_collection[2:]

    # Neither headers nor groups.
    elif not any([bool(headers), bool(group)]):
        out_collection = ["".join(item) for item in in_collection]

    # Return formatted collection.
    for item in out_collection:
        yield item


def get_dataframe(collection: Iterable[Tuple[Any, ...]], headers: List[str]):
    """

    :param collection:
    :param headers:
    :return:
    """
    return DataFrame(dict(zip(headers, zip(*collection))))


def left_justify(iterable: Iterable[Any]) -> Iterable[str]:
    """

    :param iterable:
    :return:
    """
    sequence = list(iterable)  # type: List[Any]
    length = max(len(stringify(item)) for item in sequence)
    for item in ("{0:<{1}}".format(item, length) for item in sequence):
        yield item


def base85_encode(strg, encoding="UTF-8"):
    return b85encode(strg.encode(encoding=encoding))


def base85_decode(bytobj, encoding="UTF-8"):
    return b85decode(bytobj).decode(encoding=encoding)


# ============================
# Audio directories functions.
# ============================
def get_artists(directory: str = MUSIC) -> Iterable[Tuple[str, str]]:
    """
    Get artists composing the local music drive.
    Yield 2-items tuples composed of both artist's name and artist's folder path.

    :param directory: local music drive.
    :return: 2-items tuples composed of both artist's name and artist's folder path.
    """
    for _artist, _artist_path in chain.from_iterable(list(get_folders(letter_path)) for letter, letter_path in get_folders(directory)):
        yield _artist, _artist_path


def get_albums(directory: Union[PureWindowsPath, WindowsPath, str]) -> Iterable[Tuple[str, str, str, bool]]:
    """
    Get albums composing an artist folder.
    Yield 3-items tuples composed of album folder name, album folder path, album unique ID and is_bootleg boolean tag.

    :param directory: artist folder path.
    :return: 4-items tuples composed of album folder name, album folder path, album unique ID and is_bootleg boolean tag.
    """
    regex1 = re.compile(DEFAULTALBUM)
    regex2 = re.compile(r"\b\\([12])\\{0}".format(DEFAULTALBUM))
    regex3 = re.compile(r"^(?:{0})$".format(DFTYEARREGEX))
    regex4 = re.compile(BOOTLEGALBUM)
    regex5 = re.compile(r"\b\\([12])\\({0})\\{1}".format(DFTYEARREGEX, BOOTLEGALBUM))
    isbootleg = {"1": False, "2": True}
    for _name, _path in get_folders(os.fspath(directory)):
        if not os.path.isdir(_path):
            continue
        if _name in ["1", "2"]:
            for _album, _album_path, _albumsort, _isbootleg in get_albums(_path):
                yield _album, _album_path, _albumsort, _isbootleg
        else:
            match = regex1.match(_name)
            if match:
                category = "1"
                year, sort, album = match.group(2, 3, 4)
                match = regex2.search(_path)
                if match:
                    category = match.group(1)
                if not sort:
                    sort = "1"
                yield album, _path, f"{category}.{year}0000.{sort}", isbootleg.get(category, False)
            elif not match:
                match = regex3.match(_name)
                if match:
                    for _album, _album_path, _albumsort, _isbootleg in get_albums(_path):
                        yield _album, _album_path, _albumsort, _isbootleg
                elif not match:
                    match = regex4.match(_name)
                    if match:
                        match = regex5.search(_path)
                        if match:
                            category, year, month, day, sort = match.group(1, 2, 4, 5, 6)
                            if not sort:
                                sort = "1"
                            yield _name, _path, f"{category}.{year}{month}{day}.{sort}", isbootleg.get(category, False)


def get_folders(directory: str) -> Iterable[Tuple[str, str]]:
    """
    Get folders composing a directory.
    Yield a 2-item tuples composed of both folder name and folder path.

    :param directory: directory path.
    :return: 2-item tuples composed of both folder name and folder path.
    """
    _collection = []  # type: List[Tuple[str, str]]
    stack = ExitStack()
    try:
        stack.enter_context(ChangeLocalCurrentDirectory(directory))
    except PermissionError:
        pass
    else:
        with stack:
            _collection = [(name, os.path.join(os.getcwd(), name)) for name in os.listdir(".")]
    for name, path in _collection:
        yield name, path


# ==========================
# Single dispatch functions.
# ==========================
@singledispatch
def stringify(arg, **kwargs):
    return arg


@stringify.register(int)
def _(arg: int, **kwargs) -> str:
    return str(arg)


@stringify.register  # type: ignore
def _(arg: datetime, *, template: str = TEMPLATE4, tz=UTC) -> str:
    return _format_date(tz.localize(arg).astimezone(LOCAL), template)


@stringify.register  # type: ignore
def _(arg: date, *, template: str = "%d/%m/%Y") -> str:
    return arg.strftime(template)


@singledispatch
def valid_datetime(arg):
    """
    Check if input argument is a coherent (UTC) Unix time or a coherent python (local) datetime object.
    Raise a ValueError if not.
    :param arg: UTC Unix time (int or str allowed) or python datetime object.
    :return: Tuple composed of :
                   - Unix time.
                   - Datetime aware object respective to the local system time zone.
                   - time.struct_time object.
    """
    raise ValueError(f"Input argument is not a coherent argument.")


@valid_datetime.register(int)  # type: ignore
def _(arg: int) -> Tuple[int, datetime, Tuple[int, int, int, int, int, int, int, int, int, str, int]]:
    """

    :param arg: integer UTC Unix time.
    :return:
    """
    _msg = r"is not a valid Unix time."  # type: str
    try:
        _datobj = datetime.utcfromtimestamp(arg)  # type: datetime
    except OSError:
        raise ValueError(f'"{arg}" {_msg}')
    return arg, UTC.localize(_datobj).astimezone(LOCAL), UTC.localize(_datobj).astimezone(LOCAL).timetuple()


@valid_datetime.register(str)  # type: ignore
def _(arg: str) -> Tuple[int, datetime, Tuple[int, int, int, int, int, int, int, int, int, str, int]]:
    """

    :param arg: string UTC Unix time.
    :return:
    """
    _msg = r"is not a valid Unix time."  # type: str

    try:
        arg = int(arg)
    except (ValueError, TypeError) as err:
        raise ValueError(err)

    try:
        _datobj = datetime.utcfromtimestamp(arg)  # type: datetime
    except OSError:
        raise ValueError(f'"{arg}" {_msg}')

    return arg, UTC.localize(_datobj).astimezone(LOCAL), UTC.localize(_datobj).astimezone(LOCAL).timetuple()


@valid_datetime.register(datetime)  # type: ignore
def _(arg: datetime) -> Tuple[int, datetime, Tuple[int, int, int, int, int, int, int, int, int, str, int]]:
    """

    :param arg: local datetime object.
    :return:
    """
    _arg = arg
    with suppress(ValueError):
        _arg = LOCAL.localize(arg)
    _arg.astimezone(LOCAL)
    return int(_arg.timestamp()), _arg, _arg.timetuple()


# ======================
# Jinja2 Custom filters.
# ======================
def integer_to_string(intg: int) -> str:
    return str(intg)


def repeat_element(elem, n):
    for i in repeat(elem, n):
        yield i


def cjustify(strg: str, width: int, char: str = "") -> str:
    return "{0:{2}^{1}}".format(strg, width, char)


def rjustify(strg: str, width: int, char: str = "") -> str:
    return "{0:{2}>{1}}".format(str(strg), width, char)


def ljustify(strg: str, width: int, char: str = "") -> str:
    return "{0:{2}<{1}}".format(strg, width, char)


def normalize(strg: str) -> str:
    return strg.replace(", ", "_").replace(" ", "_")


def normalize2(strg: str) -> str:
    return strg.replace(" ", "%20").replace("&", "%26")


# =======================================================
# These interfaces mustn't be used from external scripts.
# =======================================================
def _localize_date(dt: datetime, tz) -> datetime:
    """
    Return a datetime object localized into the local time zone from a different time zone.

    :param dt: datetime object.
    :param tz: datetime object time zone.
    :return: datetime object.
    """
    return tz.localize(dt).astimezone(LOCAL)  # type: ignore


def _get_readabledate(dt: datetime, template: str, tz) -> str:
    """
    Return a human readable (naive or aware) date respective to the local time zone.

    :param dt: datetime object.
    :param template: template used to display the date.
    :param tz: datetime object time zone.
    :return: string.
    """
    datobj = dt
    if tz is not None:
        datobj = _localize_date(dt, tz)
    return _format_date(datobj, template)


def _convert_timestamp(timestamp: int, tz) -> datetime:
    return UTC.localize(datetime.utcfromtimestamp(timestamp)).astimezone(tz)


def _format_date(dt: Union[date, datetime], template: str) -> str:
    """
    Return a human readable date.

    :param dt: datetime object.
    :param template: template used to display the date.
    :return: string.
    """
    return Template(template).substitute(day=dt.strftime("%A").capitalize(),
                                         month=dt.strftime("%B").capitalize(),
                                         d=dt.strftime("%d"),
                                         j=dt.strftime("%j"),
                                         m=dt.strftime("%m"),
                                         y=dt.strftime("%y"),
                                         z=dt.strftime("%z"),
                                         H=dt.strftime("%H"),
                                         M=dt.strftime("%M"),
                                         S=dt.strftime("%S"),
                                         U=dt.strftime("%U"),
                                         W=dt.strftime("%W"),
                                         Y=dt.strftime("%Y"),
                                         Z=dt.strftime("%Z"))


def _set_collection(collection: Iterable[Tuple[Any, ...]], headers: Optional[Iterable[str]], *, char: str = "=", tabsize: int = 3, gap: int = 3) -> Tuple[List[str], List[str], Iterator[Tuple[str, ...]]]:
    """

    :param collection:
    :param headers:
    :param char:
    :param tabsize:
    :param gap:
    :return:
    """

    # 1. Initializations.
    max_length, max_width = {}, {}
    out_collection = OrderedDict()  # type: Any

    # 2. Gather data per header.
    in_collection = list(collection)  # type: Any
    length = len(in_collection)  # type: int
    in_collection = list(zip(*in_collection))
    _headers = None  # type: Any
    if headers is not None:
        _headers = iter(headers)
    elif headers is None:
        _headers = range(1, length + 1)
    in_collection = OrderedDict(zip(_headers, in_collection))

    # 3. Get data maximum length and maximum allowed width.
    for k, v in in_collection.items():
        key = stringify(k)
        _len = len(key)  # type: int
        if any(bool(item) for item in v):
            _len = max(len(stringify(item)) for item in v if item)
        if len(key) > _len:
            _len = len(key)
        max_length[k] = _len
        max_width[k] = get_nearestmultiple(_len, multiple=tabsize) + gap

    # 4. Justify data.
    for k, v in in_collection.items():
        y = []
        for item in v:
            _tabs = get_tabs(max_width[k], tabsize=tabsize).expandtabs(tabsize)
            if item:
                _tabs = "{0}{1}".format(item, get_tabs(max_width[k] - len(stringify(item)), tabsize=tabsize)).expandtabs(tabsize)
            y.append(_tabs)
        out_collection[k] = y

    # 5. Set separators.
    out_separators = ["{0}{1}".format(char * max_length[header], get_tabs(max_width[header] - max_length[header], tabsize=tabsize)).expandtabs(tabsize) for header in in_collection]

    # 6. Set output headers.
    out_headers = ["{0}{1}".format(stringify(header).upper(), get_tabs(max_width[header] - len(stringify(header)), tabsize=tabsize)).expandtabs(tabsize) for header in in_collection]

    # 7. Return output data.
    return out_separators, out_headers, iter(zip(*[v for _, v in out_collection.items()]))
