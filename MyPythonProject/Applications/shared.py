# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import calendar
import csv
import locale
import logging.handlers
import operator
import os
import re
import sys
from abc import ABC, abstractmethod
from collections.abc import Sequence
from contextlib import ContextDecorator, ExitStack, suppress
from datetime import date, datetime, time, timedelta
from functools import singledispatch
from itertools import chain, dropwhile, filterfalse, groupby, repeat, tee, zip_longest
from pathlib import Path
from string import Template
from subprocess import PIPE, run
from typing import Any, Iterable, List, Optional, Tuple, Union

import jinja2
import yaml
from dateutil.parser import parserinfo
from pytz import timezone

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYPARENT = Path(os.path.abspath(__file__)).parent
locale.setlocale(locale.LC_ALL, "fr_FR")

# ==================
# Functions aliases.
# ==================
abspath, basename, dirname, exists, expandvars, isdir, join, normpath = os.path.abspath, os.path.basename, os.path.dirname, os.path.exists, os.path.expandvars, os.path.isdir, os.path.join, os.path.normpath

# ==========
# Constants.
# ==========
APPEND = "a"
COPYRIGHT = "\u00A9"
DFTENCODING = "UTF_8"
DFTTIMEZONE = "Europe/Paris"
LOCAL = timezone("Europe/Paris")
LOGPATTERN = "%(asctime)s - %(levelname)s - [%(name)s]: %(message)s"
UTC = timezone("UTC")
UTF8 = "UTF_8"
UTF16 = "UTF_16"
WRITE = "w"

# Resources.
ARECA = str(Path("C:/") / "Program Files" / "Areca" / "areca_cl.exe")
DATABASE = str(_MYPARENT.parent / "Resources" / "database.db")
TESTDATABASE = str(Path(os.path.expandvars("%TEMP%")) / "database.db")

# Regular expressions.
DFTDAYREGEX = r"0[1-9]|[12]\d|3[01]"
DFTMONTHREGEX = r"0[1-9]|1[0-2]"
DFTYEARREGEX = r"(?:20[0-2]|19[6-9])\d"
LOOKALBUMSORT = r"(?=[\d.]{12}$)(?=[12]\.\d{8}\.\d$)"
UPCREGEX = r"\d{12,13}"

# Templates for converting datetime objects to strings.
TEMPLATE1 = "$day $d/$m/$Y $H:$M:$S $Z (UTC$z)"
TEMPLATE2 = "$day $d $month $Y $H:$M:$S $Z (UTC$z)"
TEMPLATE3 = "$d/$m/$Y $H:$M:$S $Z (UTC$z)"
TEMPLATE4 = "$day $d $month $Y $H:$M:$S $Z (UTC$z)"
TEMPLATE5 = "$Y-$m-$d"
TEMPLATE6 = "$d/$m/$Y $H:$M:$S"
TEMPLATE7 = "$Y$m${d}_$H$M$S"

# Local drives.
MUSIC = Path("F:/")
TEMP = Path(os.path.expandvars("%TEMP%"))

# Miscellaneous containers.
GENRES = ["Alternative Rock",
          "Black Metal",
          "Doom Metal",
          "French Pop",
          "Hard Rock",
          "Heavy Metal",
          "Pop",
          "Progressive Rock",
          "Rock",
          "Trash Metal"]


# ===============
# Global classes.
# ===============
class CustomDialect(csv.Dialect):
    delimiter = "|"
    escapechar = "`"
    doublequote = False
    quoting = csv.QUOTE_NONE
    lineterminator = "\r\n"


class CustomFormatter(logging.Formatter):
    converter = datetime.fromtimestamp
    default_time_format = "%d/%m/%Y %H:%M:%S"
    default_localizedtime_format = "%Z (UTC%z)"
    default_format = "%s %s,%03d %s"

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created, tz=timezone(DFTTIMEZONE))
        s = self.default_format % (ct.strftime("%A"), ct.strftime(self.default_time_format), record.msecs, ct.strftime(self.default_localizedtime_format))
        if datefmt:
            s = ct.strftime(datefmt)
        return s


class CustomHandler(logging.StreamHandler):
    def __init__(self, arg, func):
        super(CustomHandler, self).__init__(stream=sys.stdout)
        if arg:
            self.addFilter(func)


class CustomTemplate(Template):
    delimiter = "@"
    idpattern = r"([a-z][a-z0-9]+)"
    flags = re.ASCII

    def __init__(self, template):
        super(CustomTemplate, self).__init__(template)


class ChangeLocalCurrentDirectory(ContextDecorator):
    """
    Context manager to change the current directory of a local system.
    """

    def __init__(self, directory):
        self._dir = str(directory)
        self._cwd = os.getcwd()

    def __enter__(self):
        os.chdir(self._dir)
        return self

    def __exit__(self, *exc):
        os.chdir(self._cwd)


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


class Files(Sequence):
    """
    Undocumented.
    """

    def __init__(self, path, *, excluded=None):

        if not path.exists():
            raise FileNotFoundError(f"No such file or directory: '{path}'")
        if not path.is_dir():
            raise NotADirectoryError(f"No such directory: '{path}'")

        collection = []  # type: List[Any]

        # [root1/file1.ext1, root1/file2.ext1, root1/file3.ext2], [root2/file1.ext1, root2/file2.ext1, root2/file3.ext2], ...
        if not excluded:
            collection = [[Path(root) / file for file in files] for root, _, files in os.walk(path) if files]

        # [root1/file1.ext1, root1/file2.ext1, root1/file3.ext2], [root2/file1.ext1, root2/file2.ext1, root2/file3.ext2], ...
        if excluded:
            for root, _, files in os.walk(path):
                if files:
                    files = set(Path(root) / file for file in files) - excluded(root, *set(files))
                    if files:
                        collection.append(list(files))

        # root1/file1.ext1, root1/file2.ext1, root1/file3.ext2, root2/file1.ext1, root2/file2.ext1, root2/file3.ext2, ...
        self._collection = sorted(chain.from_iterable(collection))  # type: List[Path]

    def __contains__(self, item):
        return item in self._collection

    def __getitem__(self, item):
        return self._collection[item]

    def __iter__(self):
        for item in self._collection:
            yield item

    def __len__(self):
        return len(self._collection)

    def __repr__(self):
        if not self:
            return "%s()" % (self.__class__.__name__,)
        return "%s(%r)" % (self.__class__.__name__, list(self))


class GetPath(argparse.Action):
    """
    Undocumented.
    """

    def __init__(self, option_strings, dest, **kwargs):
        super(GetPath, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, list(map(Path, values)))


class TitleCaseBaseConverter(ABC):
    """
    Undocumented.
    """

    # Define class-level configuration.
    with open(join(_MYPARENT / "Resources" / "resource1.yml"), encoding=UTF8) as fp:
        config = yaml.load(fp, Loader=yaml.FullLoader)

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

    def __init__(self):
        """
        Undocumented.
        """

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
    def convert(self, title):
        """
        Undocumented.

        """
        pass


class TitleCaseConverter(TitleCaseBaseConverter):
    """
    Undocumented.
    """
    _logger = logging.getLogger("{0}.TitleCaseConverter".format(__name__))

    def __init__(self):
        """
        Undocumented.
        """
        super(TitleCaseConverter, self).__init__()

    def convert(self, title):
        """
        Undocumented.
        """
        self._logger.debug(title)

        # A. General process.
        # A.1. Title is formatted with lowercase letters.
        # A.2. Words are capitalized --> `capitalize_words`.
        title = self.capitalize_words.sub(lambda match: match.group(1).capitalize(), title.lower().replace("[", "(").replace("]", ")"))
        self._logger.debug(title)

        # B. Exceptions process.
        # B.1. Words formatted only with lowercase letters --> `alw_lowercase`.
        # B.2. Words formatted only with a capital letter --> `alw_capital`.
        # B.3. Capital letter is mandatory for the first word of the title --> `capitalize_firstword`.
        # B.4. Capital letter is mandatory for the last word of the title --> `capitalize_lastword`.
        # B.5. Words formatted only with uppercase letters --> `alw_uppercase`.
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
        self._logger.debug(title)

        # C. Acronyms process.
        title = self.acronyms.sub(lambda match: match.group(1).upper(), title)
        self._logger.debug(title)

        # D. Apostrophes process.
        title = self.apostrophe_regex1.sub(lambda match: "{0}'{1}".format(match.group(1).capitalize(), match.group(2).lower()), title)
        title = self.apostrophe_regex2.sub(lambda match: "{0}'{1}".format(match.group(1).capitalize(), match.group(2).capitalize()), title)
        title = self.apostrophe_regex3.sub(lambda match: "{0}'".format(match.group(1).lower()), title)
        title = self.apostrophe_regex4.sub(" 'n' ", title)
        title = self.apostrophe_regex5.sub(" 'n' ", title)
        title = self.apostrophe_regex6.sub(" 'n' ", title)
        title = self.apostrophe_regex7.sub(" 'n' ", title)
        self._logger.debug(title)

        # E. Specific process.
        #    Capital letter is mandatory for the second word if the first one is defined between parenthesis --> `capitalize_secondword`.
        title = self.capitalize_secondword.sub(lambda match: "{0}{1}".format(match.group(1), match.group(2).capitalize()), title)
        self._logger.debug(title)

        # F. Roman numbers process.
        title = self.roman_numbers_regex1.sub(lambda match: match.group(0).upper(), title)
        title = self.roman_numbers_regex2.sub(lambda match: match.group(0).upper(), title)
        title = self.roman_numbers_regex3.sub(lambda match: match.group(0).upper(), title)
        self._logger.debug(title)

        # G. Punctuation process.
        title = self.punctuation.sub(lambda match: f"{match.group(1)}{match.group(2)}", title)

        # H. Return converted title.
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
        super(LocalParser, self).__init__(dayfirst, yearfirst)


class ToBoolean(object):

    def __init__(self, arg):
        self._bool = False
        if arg.lower() == "y":
            self._bool = True
        if arg.lower() == "yes":
            self._bool = True

    @property
    def boolean_value(self):
        return self._bool


# ===================
# Jinja2 environment.
# ===================
class TemplatingEnvironment(object):

    def __init__(self, path, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True, **kwargs):
        self._environment = jinja2.Environment(keep_trailing_newline=keep_trailing_newline, trim_blocks=trim_blocks, lstrip_blocks=lstrip_blocks, loader=jinja2.FileSystemLoader(str(path)))
        self.set_environment(**kwargs)

    def set_environment(self, **kwargs):
        globalvars = kwargs.get("globalvars", {})
        filters = kwargs.get("filters", {})
        for k, v in globalvars.items():
            self._environment.globals[k] = v
        for k, v in filters.items():
            self._environment.filters[k] = v

    def get_template(self, template):
        return self._environment.get_template(template)


# ======================
# Jinja2 custom filters.
# ======================
def ljustify(arg: str, width: int, *, char: str = "") -> str:
    """

    :param arg:
    :param width:
    :param char:
    :return:
    """
    return "{0:{char}<{width}}".format(arg, width=width, char=char)


def rjustify(arg: str, width: int, *, char: str = "") -> str:
    """

    :param arg:
    :param width:
    :param char:
    :return:
    """
    return "{0:{char}>{width}}".format(arg, width=width, char=char)


def rjustify_index(arg: int, width: int, *, char: str = "") -> str:
    """

    :param arg:
    :param width:
    :param char:
    :return:
    """
    return "{0:{char}>{width}d}".format(arg, width=width, char=char)


def normalize(arg: str) -> str:
    """

    :param arg:
    :return:
    """
    return arg.replace(", ", "_").replace(" ", "_")


def normalize2(arg: str) -> str:
    """

    :param arg:
    :return:
    """
    return arg.replace(" ", "%20").replace("&", "%26")


# ==========================
# Data validation functions.
# ==========================
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


def valid_path(path: str) -> str:
    """

    :param path:
    :return:
    """
    if not exists(path):
        raise FileNotFoundError(f"No such file or directory: '{path}'")
    if not isdir(path):
        raise NotADirectoryError(f"No such directory: '{path}'")
    if not os.access(path, os.R_OK):
        raise AttributeError(f"'{path}' is not readable")
    return path


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


# ========
# Filters.
# ========
def eq_string_(a: str, b: str, *, sensitive: bool = False) -> bool:
    if not sensitive:
        return operator.eq(b.lower(), a.lower())
    return operator.eq(b, a)


# ========================
# Miscellaneous functions.
# ========================
def mainscript(strg: str, align: str = "^", fill: str = "=", length: int = 140) -> str:
    """

    :param strg:
    :param align:
    :param fill:
    :param length:
    :return:
    """
    return "{0:{fill}{align}{length}}".format(" {0} ".format(strg), align=align, fill=fill, length=length)


def customfilehandler(maxbytes, backupcount, encoding=UTF8):
    """

    :param maxbytes:
    :param backupcount:
    :param encoding:
    :return:
    """
    return logging.handlers.RotatingFileHandler(str(_ME.parents[2] / "Log" / "pyscripts.log"), maxBytes=maxbytes, backupCount=backupcount, encoding=encoding)


def customfilter(func, record):
    """

    :param func:
    :param record:
    :return:
    """
    # record.pathname: "%_PYTHONPROJECT%\Applications\Tables\Albums\shared.py".
    # record.filename: "shared.py".
    # record.module  : "shared".
    # record.funcName: "_insert_albums".
    return func(record)


def customformatterfactory(pattern=LOGPATTERN):
    """

    :param pattern:
    :return:
    """
    return CustomFormatter(pattern)


def copy(src: str, dst: str, *, size: int = 16 * 1024) -> str:
    """

    :param src:
    :param dst:
    :param size:
    :return:
    """
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


def groupby_(iterable, index):
    """

    :param iterable:
    :param index:
    :return:
    """
    try:
        for key, group in iterable:
            yield key, list(groupby_(group, index))
    except ValueError:
        for key, group in groupby(iterable, key=operator.itemgetter(index)):
            yield key, list(group)


def nested_groupby_(iterable, *args):
    """

    :param iterable:
    :param args:
    :return:
    """
    try:
        items = iter(zip(*args))
    except TypeError:
        items = iter((arg,) for arg in args)
    for item in items:
        iterable = list(groupby_(iterable, *item))
    for key, group in iterable:
        yield key, group


def grouper(n, *iterables, fillvalue=None):
    """

    :param n:
    :param iterables:
    :param fillvalue:
    :return:
    """
    obj = [iter(iterables)] * n
    return zip_longest(*obj, fillvalue=fillvalue)


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
    _dirname = [os.path.abspath(path)]
    _dirname.extend([".."] * level)
    return os.path.abspath(os.path.join(*_dirname))


def get_readabledate(dt: datetime, *, template: str = TEMPLATE4, tz: Any = None) -> str:
    """
    Return a human readable datetime object respective to the local time zone.
    Datetime object can be naive and needs to be localized into the time zone got as keyword argument.

    :param dt: datetime object.
    :param template: template used to display the object representation.
    :param tz: object time zone.
    :return: object representation as a human readable string.
    """
    return _get_readabledate(dt, template, tz)


def get_utcreadabledate(dt: datetime, *, template: str = TEMPLATE4, tz: Any = timezone("Europe/Paris")) -> str:
    """
    Return a human readable UTC localized datetime object respective to a specific time zone got as keyword argument.

    :param dt: UTC localized datetime object.
    :param template: template used to display the object representation.
    :param tz: specific time zone.
    :return: object representation as a human readable string.
    """
    datobj = dt.astimezone(tz)
    with suppress(ValueError):
        datobj = UTC.localize(dt).astimezone(tz)
    return _format_date(datobj, template)


def now(*, template: str = TEMPLATE4) -> str:
    """

    :return:
    """
    return _get_readabledate(datetime.utcnow(), template, tz=UTC)


def format_date(dt: Union[date, datetime], *, template: str = TEMPLATE4) -> str:
    """
    Return a human readable datetime object.

    :param dt: datetime object.
    :param template: template used to display the object representation.
    :return: object representation as a human readable string.
    """
    return _format_date(dt, template)


def localize_date(dt: datetime, tz=UTC) -> datetime:
    """
    Return a datetime object localized into the local time zone from a time zone got as keyword argument.

    :param dt: datetime object.
    :param tz: datetime object time zone.
    :return: datetime object.
    """
    return _localize_date(dt, tz)


def convert_timestamp(utc_timestamp: int, tz: Any = UTC) -> datetime:
    """

    :param utc_timestamp:
    :param tz:
    :return:
    """
    return _convert_timestamp(utc_timestamp, tz)


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


def get_rippingapplication(*, timestamp: Optional[int] = None) -> Tuple[str, Optional[int]]:
    """
    Get ripping application respective to the facultative input local timestamp.

    :param timestamp: facultative input local timestamp.
    :return: ripping application.
    """
    application = {"1564610400": ("dBpoweramp Release 16.6", 2), "1553943600": ("dBpoweramp 16.5", None), "1388530800": ("dBpoweramp 15.1", None), "0": ("dBpoweramp 14.1", 1)}
    ts: Optional[int] = timestamp
    if timestamp is None:
        ts = int(UTC.localize(datetime.utcnow()).astimezone(LOCAL).timestamp())
    it = iter(dropwhile(lambda i: int(i) > ts, sorted(application, key=int, reverse=True)))  # type: ignore
    return application[next(it)]


def find_files(directory, *, excluded=None):
    """
    Return a generator object yielding files stored into `directory` argument.
    :param directory: Directory to walk through. Must be a string representing an existing path.
    :param excluded: Callable returning a set of files (as returned by os.listdir) to exclude.
                     Callable arguments are:
                        - root folder returned by os.walk.
                        - list of files present into the root folder.
    :return: generator object.
    """
    collection = []  # type: List[Any]
    if not excluded:
        collection.extend(map(os.path.join, repeat(root), files) for root, _, files in os.walk(directory) if files)
        collection = list(map(Path, collection))
    elif excluded:
        for root, _, files in os.walk(directory):
            if files:
                files = set(Path(root) / file for file in files) - excluded(root, *set(files))
                if files:
                    collection.extend(files)
    for file in sorted(collection):
        yield file


def get_drives():
    """

    :return:
    """
    regex = re.compile(r"^(E|[I-R]):$")
    process = run("wmic logicaldisk get name", shell=True, universal_newlines=True, stdout=PIPE)
    for drive in (drive.rstrip() for drive in process.stdout.splitlines() if regex.match(drive.rstrip())):
        yield drive


def pprint_sequence(*items, align="<", gap=0, char="", width=None):
    """
    Pretty print sequence by aligning items.
    Alignment is made respectively to the highest common width of all items.
    Or respectively to the value given by the keyword argument `width` if it is the highest value.

    :param items: sequence. Must be composed of strings or integers.
    :param align: alignment. Left is the default value.
    :param gap: number of whitespaces appended at the end of each aligned item.
    :param char: character used to fill the empty space created by the alignment. Whitespace is the default value.
    :param width: width used by the alignment. Can override the highest common width of all items.
    :return: iterator yielding aligned items.
    """
    _width = 0  # type: int
    with suppress(TypeError):
        _width = int(width)
    for item in _pprint_sequence(align, gap, char, _width, *map(stringify, items)):
        yield item


def pprint_mapping(*iterables, gap=0, char="", width=None):
    """
    Pretty print key-value pairs by left-aligning keys.
    Keys alignment is made respectively to the highest common width of all keys.

    :param iterables: key-value pairs.
    :param gap: number of whitespaces appended at the end of each aligned key.
    :param char: character used to fill the empty space created by the key alignment. Whitespace is the default value.
    :param width: width used by the key alignment. Can override the highest common width of all keys.
    :return: iterator yielding aligned key-value pairs.
    """
    keys, values = zip(*iterables)
    keys = list(map(stringify, keys))  # type: List[str]

    # -----
    _width = 0  # type: int
    with suppress(TypeError):
        _width = int(width)
    _width = max([max(map(len, keys)), _width])

    # -----
    for key, value in zip(_pprint_sequence("<", gap, char, _width, *keys), values):
        yield key, value


def pprint_count(*iterables, key_gap=0, key_width=None, char=("", "")):
    """
    Pretty print key-value pairs by left-aligning keys and right-aligned values.
    Keys alignment is made respectively to the highest common width of all keys.
    Values alignment is made respectively to the highest common width of all values.

    :param iterables: key-value pairs.
    :param key_gap: number of whitespaces appended at the end of each aligned key.
    :param key_width: width used by the key alignment. Can verride the highest common width of all keys.
    :param char: character used to fill the empty space created both by the key alignment and the value alignment. Whitespace is the default value.
    :return: iterator yielding aligned key-value pairs.
    """
    keys, values = zip(*iterables)
    keys = list(map(stringify, keys))  # type: List[str]

    # -----
    key_char, val_char = char

    # -----
    width = 0  # type: int
    with suppress(TypeError):
        width = int(key_width)
    _key_width = max([max(map(len, keys)), width])  # type: int
    _val_width = max(map(len, map(stringify, values)))  # type: int

    # -----
    for key, value in zip(_pprint_sequence("<", key_gap, key_char, _key_width, *keys), ["{:{fill}>{width}d}".format(value, fill=val_char, width=_val_width) for value in values]):
        yield key, value


def sort_by_insertion(*items: Any, reverse=False):
    """

    :param items:
    :param reverse:
    :return:
    """
    if not reverse:
        for item in _sort_by_insertion(*items):
            yield item
    elif reverse:
        for item in _sortreverse_by_insertion(*items):
            yield item


# ==========================
# Single dispatch functions.
# ==========================


#    ------------------------------------
# 1. Convert argument to a string object.
#    ------------------------------------
@singledispatch
def stringify(arg):
    return arg


@stringify.register(int)  # type: ignore
def _(arg: int) -> str:
    return str(arg)


@stringify.register  # type: ignore
def _(arg: datetime, *, template: str = TEMPLATE4, tz=UTC) -> str:
    return _format_date(tz.localize(arg).astimezone(LOCAL), template)


@stringify.register  # type: ignore
def _(arg: date, *, template: str = "%d/%m/%Y") -> str:
    return arg.strftime(template)


#    --------------------------------------
# 2. Convert argument to a datetime object.
#    --------------------------------------
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


#    -------------------------------------
# 3. Convert argument to a boolean object.
#    -------------------------------------
@singledispatch
def booleanify(arg):
    return arg


@booleanify.register(str)  # type: ignore
def _(arg: str):
    if arg.lower() in ["n", "y"]:
        return ToBoolean(arg).boolean_value
    return arg


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
    return tz.localize(dt).astimezone(LOCAL)


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


def _convert_timestamp(timestamp: int, tz: Any) -> datetime:
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


def _pprint_sequence(align: str, gap: int, char: str, width: int, *items: str) -> Iterable[str]:
    """
    Yield aligned sequence items.
    Alignment is made respectively to the highest common width of all items.
    Or respectively to the value given by the keyword argument `width`.

    :param align: alignment.
    :param gap: number of whitespaces appended at the end of each aligned item.
    :param char: character used to fill the empty space created by the alignment.
    :param width: width used by the alignment.
    :param items: sequence. Must be composed of strings or integers.
    :return: iterator yielding aligned items.
    """
    _width = max([max(map(len, items)), width])  # type: int
    _items = list(items)  # type: List[str]
    _items = ["{:{fill}{align}{width}}".format(item, fill=char, align=align, width=_width) for item in _items]
    _items = ["{:<{width}}".format(item, width=_width + gap) for item in _items]
    for item in _items:
        yield item


def _sort_by_insertion(*items: Any) -> Iterable[Any]:
    """

    :param items:
    :return:
    """
    sequence = list(items)
    length = len(sequence)
    for i in range(1, length):
        for j in range(i, 0, -1):
            if sequence[j - 1] > sequence[j]:
                sequence[j - 1], sequence[j] = sequence[j], sequence[j - 1]
    for item in sequence:
        yield item


def _sortreverse_by_insertion(*items: Any) -> Iterable[Any]:
    """

    :param items:
    :return:
    """
    sequence = list(items)
    length = len(sequence)
    for i in range(length - 2, -1, -1):
        for j in range(i, length - 1):
            if sequence[j + 1] > sequence[j]:
                sequence[j + 1], sequence[j] = sequence[j], sequence[j + 1]
    for item in sequence:
        yield item
