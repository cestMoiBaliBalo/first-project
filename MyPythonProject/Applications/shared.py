# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import locale
import os
import re
import subprocess
from base64 import b85decode, b85encode
from collections import OrderedDict
from contextlib import ContextDecorator, ExitStack
from datetime import datetime
from itertools import dropwhile, filterfalse, islice, repeat, tee, zip_longest
from logging import Formatter, getLogger
from logging.handlers import RotatingFileHandler
from string import Template

import jinja2
import yaml
from dateutil.parser import parserinfo
from pytz import timezone

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")

# ==================
# Functions aliases.
# ==================
basename, exists, expandvars, isdir, join = os.path.basename, os.path.exists, os.path.expandvars, os.path.isdir, os.path.join

# ==========
# Constants.
# ==========
APPEND = "a"
WRITE = "w"
DATABASE = join(expandvars("%_COMPUTING%"), "Resources", "database.db")
TESTDATABASE = join(expandvars("%_PYTHONPROJECT%"), "Applications", "Tests", "database.db")
ARECA = join(r"C:\Program Files", "Areca", "areca_cl.exe")
DFTENCODING = "UTF_8"
DFTTIMEZONE = "Europe/Paris"
UTC = timezone("UTC")
LOCAL = timezone("Europe/Paris")
TEMPLATE1 = "$day $d/$m/$Y $H:$M:$S $Z (UTC$z)"
TEMPLATE2 = "$day $d $month $Y $H:$M:$S $Z (UTC$z)"
TEMPLATE3 = "$d/$m/$Y $H:$M:$S $Z (UTC$z)"
TEMPLATE4 = "$day $d $month $Y $H:$M:$S $Z (UTC$z)"
TEMPLATE5 = "$Y-$m-$d"
TEMPLATE6 = "$d/$m/$Y $H:$M:$S"
LOGPATTERN = "%(asctime)s [%(name)s]: %(message)s"
UTF8 = "UTF_8"
UTF16 = "UTF_16LE"
UTF16BOM = "\ufeff"
COPYRIGHT = "\u00a9"
DFTYEARREGEX = r"20[0-2]\d|19[6-9]\d"
DFTMONTHREGEX = r"0[1-9]|1[0-2]"
DFTDAYREGEX = r"0[1-9]|[12]\d|3[01]"
UPCREGEX = r"\d{12,13}"
ACCEPTEDANSWERS = ["N", "Y"]
MUSIC = "F:\\"
IMAGES = "H:\\"
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
EXTENSIONS = {"computing": ["py", "json", "yaml", "cmd", "css", "xsl"],
              "documents": ["doc", "txt", "pdf", "xav"],
              "music": ["ape", "mp3", "m4a", "flac", "ogg", "tak", "wv"],
              "lossless": ["ape", "flac", "tak", "wv"],
              "lossy": ["mp3", "m4a", "ogg"]}
ZONES = ["UTC",
         "US/Pacific",
         "US/Eastern",
         "Indian/Mayotte",
         "Asia/Tokyo",
         "Australia/Sydney"]


# ========
# Classes.
# ========
# class CustomFilter(Filter):
#     def filter(self, record):
#         # print(record.pathname)
#         # print(record.filename)
#         # print(record.module)
#         # print(record.funcName)
#         # if record.funcName.lower() in ["_selectlogs", "getalbumheader", "rippeddiscsview1"]:
#         #     return True
#         return False


class CustomFormatter(Formatter):
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


class StringFormatter(object):
    """

    """

    # 1. Class level regular expressions.
    _REX01 = re.compile(r"\b([a-z]+)\b", re.IGNORECASE)
    _REX02 = re.compile(r"\b((?:u\.?)(?:s\.?a\.?|k\.?))\b", re.IGNORECASE)
    _REX04 = re.compile(r"(\B\()([a-z]+)\b", re.IGNORECASE)  # Not used anymore!
    _REX05a = re.compile(r"\b([a-z]+)'([a-z]+)\b", re.IGNORECASE)
    _REX05b = re.compile(r"\b(o)'\b([a-z]+)\b", re.IGNORECASE)
    _REX05c = re.compile(r"\b(o)'\B", re.IGNORECASE)
    _REX05d = re.compile(r" \bn'\B ", re.IGNORECASE)
    _REX05e = re.compile(r" \B'n\b ", re.IGNORECASE)
    _REX05f = re.compile(r" \B'n'\B ", re.IGNORECASE)
    _REX05g = re.compile(r"\b'n'\b", re.IGNORECASE)
    _REX06 = re.compile(r"^(\([^)]+\) )\b([a-z]+)\b", re.IGNORECASE)

    # 2. Class level logger.
    _logger = getLogger("{0}.StringFormatter".format(__name__))

    # 3. Initialize instance.
    def __init__(self, somestring=None, config=join(expandvars("%_COMPUTING%"), "Resources", "stringformatter.yml")):

        # Initializations.
        self._inp_string, self._out_string = "", ""
        dict_config, self._rex09, self._rex10, self._rex11, self._rex12, self._rex13 = None, None, None, None, None, None
        if somestring:
            self.inp_string = somestring

        # Load configuration.
        with open(config, encoding=UTF8) as fp:
            dict_config = yaml.load(fp)
        lowercases = dict_config.get("lowercases", [])
        uppercases = dict_config.get("uppercases", [])
        capitalized = dict_config.get("capitalized", [])
        capitalize_first_word = dict_config.get("capitalize_first_word", False)
        capitalize_last_word = dict_config.get("capitalize_last_word", False)
        if lowercases:
            self._rex09 = re.compile(r"\b({0})\b".format("|".join(lowercases)), re.IGNORECASE)
        if uppercases:
            self._rex10 = re.compile(r"\b({0})\b".format("|".join(uppercases)), re.IGNORECASE)
        if capitalized:
            self._rex11 = re.compile(r"\b({0})\b".format("|".join(capitalized)), re.IGNORECASE)
        if capitalize_first_word:
            self._rex12 = re.compile(r"^([a-z]+)\b", re.IGNORECASE)
        if capitalize_last_word:
            self._rex13 = re.compile(r"\b([a-z]+)$", re.IGNORECASE)

        # Log regular expressions.
        self._logger.debug(self._rex09)
        self._logger.debug(self._rex10)
        self._logger.debug(self._rex11)

    def convert(self, somestring=None):
        if somestring:
            self.inp_string = somestring
        self._out_string = self._inp_string
        self._logger.debug(self._out_string)

        # ----------------
        # General process.
        # ----------------
        # 1. Title is formatted with lowercase letters.
        # 2. Words are capitalized --> _REX01.
        self._out_string = self._REX01.sub(lambda match: match.group(1).capitalize(), self._out_string.lower().replace("[", "(").replace("]", ")"))
        self._logger.debug(self._out_string)

        # -------------------
        # Exceptions process.
        # -------------------
        # 1. Words formatted only with lowercase letters --> _rex09.
        # 2. Words formatted only with a capital letter --> _rex11.
        # 3. Capital letter is mandatory for the first word of the title --> _rex12.
        # 4. Capital letter is mandatory for the last word of the title --> _rex13.
        # 5. Words formatted only with uppercase letters --> _rex10.
        if self._rex09:
            self._out_string = self._rex09.sub(lambda match: match.group(1).lower(), self._out_string)
        if self._rex11:
            self._out_string = self._rex11.sub(lambda match: " ".join(word.capitalize() for word in match.group(1).split()), self._out_string)
        if self._rex12:
            self._out_string = self._rex12.sub(lambda match: match.group(1).capitalize(), self._out_string)
        if self._rex13:
            self._out_string = self._rex13.sub(lambda match: match.group(1).capitalize(), self._out_string)
        if self._rex10:
            self._out_string = self._rex10.sub(lambda match: match.group(1).upper(), self._out_string)
        self._logger.debug(self._out_string)

        # -----------------
        # Acronyms process.
        # -----------------
        self._out_string = self._REX02.sub(lambda match: match.group(1).upper(), self._out_string)
        self._logger.debug(self._out_string)

        # --------------------
        # Apostrophes process.
        # --------------------
        self._out_string = self._REX05a.sub(lambda match: "{0}'{1}".format(match.group(1).capitalize(), match.group(2).lower()), self._out_string)
        self._out_string = self._REX05b.sub(lambda match: "{0}'{1}".format(match.group(1).capitalize(), match.group(2).capitalize()), self._out_string)
        self._out_string = self._REX05c.sub(lambda match: "{0}'".format(match.group(1).lower()), self._out_string)
        self._out_string = self._REX05d.sub(" 'n' ", self._out_string)
        self._out_string = self._REX05e.sub(" 'n' ", self._out_string)
        self._out_string = self._REX05f.sub(" 'n' ", self._out_string)
        self._out_string = self._REX05g.sub(" 'n' ", self._out_string)
        self._logger.debug(self._out_string)

        # -----------------
        # Specific process.
        # -----------------
        self._out_string = self._REX06.sub(lambda match: "{0}{1}".format(match.group(1), match.group(2).capitalize()), self._out_string)
        self._logger.debug(self._out_string)

        # ---------------------
        # Return output string.
        # ---------------------
        return self._out_string

    @property
    def inp_string(self):
        return self._inp_string

    @inp_string.setter
    def inp_string(self, arg):
        self._inp_string = arg


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


# ===========================
# Customized parsing actions.
# ===========================
class SetDatabase(argparse.Action):
    """

    """

    def __init__(self, option_strings, dest, **kwargs):
        super(SetDatabase, self).__init__(option_strings, dest, **kwargs)

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
        super(GetPath, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, self.destinations[values])


class GetExtensions(argparse.Action):
    """
    Set "files" attribute with a list of extensions.
    Set "extensions" attribute with a list of extensions to process.
    """

    def __init__(self, option_strings, dest, **kwargs):
        super(GetExtensions, self).__init__(option_strings, dest, **kwargs)

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
        super(ExcludeExtensions, self).__init__(option_strings, dest, **kwargs)

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
        super(KeepExtensions, self).__init__(option_strings, dest, **kwargs)

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
        super(IncludeExtensions, self).__init__(option_strings, dest, **kwargs)

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
        super(SetEndSeconds, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        if not values:
            setattr(namespace, self.dest, getattr(namespace, "beg"))


# ===================
# Jinja2 environment.
# ===================
class TemplatingEnvironment(object):
    def __init__(self, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True, **kwargs):
        self._environment = None
        self.environment = jinja2.Environment(keep_trailing_newline=keep_trailing_newline, trim_blocks=trim_blocks, lstrip_blocks=lstrip_blocks, loader=kwargs.get("loader"))

    def set_environment(self, **kwargs):
        for k, v in kwargs["globalvars"].items():
            self._environment.globals[k] = v
        for k, v in kwargs["filters"].items():
            self._environment.filters[k] = v

    def set_template(self, **templates):
        for k, v in templates.items():
            setattr(self, k, self._environment.get_template(v))

    @property
    def environment(self):
        return self._environment

    @environment.setter
    def environment(self, arg):
        self._environment = arg


# ==========================
# Data validation functions.
# ==========================
def valid_path(path):
    """

    :param path:
    :return:
    """
    if not exists(path):
        raise argparse.ArgumentTypeError('"{0}" doesn\'t exist.'.format(path))
    if not isdir(path):
        raise argparse.ArgumentTypeError('"{0}" is not a directory.'.format(path))
    if not os.access(path, os.R_OK):
        raise argparse.ArgumentTypeError('"{0}" is not a readable directory.'.format(path))
    return path


def valid_database(database):
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


def valid_discnumber(discnumber):
    """
    Check if string `discnumber` is a coherent disc number

    :param discnumber: disc number.
    :return: disc number converted to numeric characters.
    """
    msg = r"is not a valid disc number."
    try:
        _discnumber = int(discnumber)
    except (ValueError, TypeError):
        raise ValueError('"{0}" {1}'.format(discnumber, msg))
    if not _discnumber:
        raise ValueError('"{0}" {1}'.format(discnumber, msg))
    return _discnumber


def valid_tracks(tracks):
    """
    Check if string `tracks` is a coherent track number.

    :param tracks: track number.
    :return: track number converted to numeric characters.
    """
    msg = r"is not a valid total tracks number."
    try:
        _tracks = int(tracks)
    except TypeError:
        raise ValueError('"{0}" {1}'.format(tracks, msg))
    if not _tracks:
        raise ValueError('"{0}" {1}'.format(tracks, msg))
    return _tracks


def valid_albumid(albumid):
    """
    Check if string `albumid` is a coherent unique album ID.

    :param albumid: unique album ID.
    :return: unique album ID.
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


def valid_albumsort(albumsort):
    """
    Check if string `albumsort` is a coherent `albumsort` tag.

    :param albumsort: `albumsort` tag.
    :return: `albumsort` tag.
    """
    rex1 = re.compile(r"^(?=[\d.]+$)(?=.\.[^.]+\..$)(?=\d\.\d{{8}}\.\d$).\.({0})({1})({2})\..$".format(DFTYEARREGEX, DFTMONTHREGEX, DFTDAYREGEX))
    rex2 = re.compile(r"^(?=[\d.]+$)(?=.\.[^.]+\..$)(?=\d\.\d{{8}}\.\d$).\.({0})0000\..$".format(DFTYEARREGEX))
    msg = r"is not a valid albumsort."

    try:
        match1 = rex1.match(albumsort)
        match2 = rex2.match(albumsort)
    except TypeError:
        raise ValueError('"{0}" {1}'.format(albumsort, msg))
    if all([not match1, not match2]):
        raise ValueError('"{0}" {1}'.format(albumsort, msg))
    return albumsort


def valid_year(year):
    """
    Check if string `year` is a coherent year.

    :param year: year.
    :return: year converted to numeric characters.
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


def valid_productcode(productcode):
    """
    Check if string `productcode` is a coherent product code.

    :param productcode: product code.
    :return: product code.
    """
    regex, msg = re.compile(r"^{0}$".format(UPCREGEX)), r"is not a valid product code."

    try:
        productcode = str(productcode)
    except TypeError:
        raise ValueError('"{0}" {1}'.format(productcode, msg))
    if not regex.match(productcode):
        raise ValueError('"{0}" {1}'.format(productcode, msg))
    return productcode


def valid_genre(genre):
    """
    Check if string `genre` is a coherent audio genre.

    :param genre: audio genre.
    :return: audio genre.
    """
    msg = r"is not a valid genre."
    try:
        if genre.lower() not in (item.lower() for item in GENRES):
            raise ValueError('"{0}" {1}'.format(genre, msg))
    except AttributeError:
        raise ValueError('"{0}" {1}'.format(genre, msg))
    return genre


def valid_datetime(timestamp):
    """
    Check if string `timestamp` is a coherent Unix time or a coherent python datetime object.

    :param timestamp: Unix time or python datetime object.
    :return: (Unix time converted to a) python datetime naive object respective to the local system time zone.
    """
    error, msg = False, r"is not a valid Unix time."
    try:
        timestamp = int(timestamp)
    except (ValueError, TypeError):
        error = True

    if error:
        try:
            _struct = timestamp.timetuple()
        except (TypeError, AttributeError):
            raise ValueError('"{0}" {1}'.format(timestamp, msg))
        return int(timestamp.timestamp()), timestamp, _struct

    try:
        datobj = datetime.fromtimestamp(timestamp)
    except OSError:
        raise ValueError('"{0}" {1}'.format(timestamp, msg))
    else:
        _struct = datobj.timetuple()
    return timestamp, datobj, _struct


# ========================
# Miscellaneous functions.
# ========================
def copy(src, dst, *, size=16 * 1024):
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


def customformatterfactory(pattern=LOGPATTERN):
    return CustomFormatter(pattern)


def customfilehandler(maxbytes, backupcount, encoding=UTF8):
    return RotatingFileHandler(join(expandvars("%_COMPUTING%"), "Log", "pythonlog.log"), maxBytes=maxbytes, backupCount=backupcount, encoding=encoding)


def get_readabledate(dt, template, tz=None):
    """
    Return a local human readable (naive or aware) datetime object respective to the local system time zone.

    :param dt: datetime object. Naive or aware.
    :param template: template to make the object human readable.
    :param tz: datetime object original time zone.
    :return: human readable datetime object respective to the local system time zone.
    """
    datobj = dt
    if tz:
        datobj = tz.localize(dt).astimezone(LOCAL)
    return dateformat(datobj, template)


def now(template=TEMPLATE4):
    """

    :return:
    """
    return dateformat(UTC.localize(datetime.utcnow()).astimezone(LOCAL), template)


def dateformat(dt, template):
    """
    Return a human readable datetime aware object.

    :param dt: datetime object.
    :param template: template to make the object human readable.
    :return: human readable datetime object.
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


def get_tabs(length, *, tabsize=3):
    x = int(length / tabsize)
    y = length % tabsize
    if y:
        x += 1
    return x * "\t"


def get_nearestmultiple(length, *, multiple=3):
    x = int(length / multiple)
    y = length % multiple
    if y:
        x += 1
    return x * multiple


def get_rippingapplication(*, timestamp=None):
    """
    Get ripping application respective to the facultative input local timestamp.

    :param timestamp: facultative input local timestamp.
    :return: ripping application.
    """
    application = {"1512082800": "dBpoweramp 16.1", "1388530800": "dBpoweramp 15.1", "0": "dBpoweramp 14.1"}
    if not timestamp:
        timestamp = int(UTC.localize(datetime.utcnow()).astimezone(LOCAL).timestamp())
    return list(islice(dropwhile(lambda i: int(i[0]) > timestamp, sorted(application.items(), key=lambda i: int(i[0]), reverse=True)), 1))[0][1]


def find_files(directory, *, excluded=None):
    """
    Return a generator object yielding files stored in `directory`.
    :param directory: directory to walk through.
    :param excluded: callable returning a list composed of files to exclude as returned by os.listdir.
                     Callable input arguments must be:
                        :The root directory returned by os.walk.
                        :The list of files present into the root directory.
    :return: generator object.
    """
    collection = []
    for root, _, files in os.walk(directory):
        if not excluded:
            collection.extend(map(join, repeat(root), files))
        else:
            collection.extend(map(join, repeat(root), set(files) - excluded(root, *files)))
    for file in sorted(collection):
        yield file


def get_datefromseconds(beg, end, zone=DFTTIMEZONE):
    """
    Return a map object yielding human readable dates corresponding to a range of seconds since the epoch.
    :param beg: range start seconds.
    :param end: range stop seconds.
    :param zone: not mandatory time zone appended to the map object.
    :return: map object.
    """
    gap, width = 5, {}

    if beg > end:
        raise ValueError("Beginning Unix epoch time {0} must be lower than or equal to end Unix epoch time {1}".format(beg, end))
    zones = list(ZONES)
    zones.insert(0, zone)

    # Create N lists (1 list for 1 timestamp) composed of 7 timezones.
    mainlist = [[dateformat(timezone("UTC").localize(datetime.utcfromtimestamp(ts)).astimezone(timezone(tz)), TEMPLATE4) for tz in zones] for ts in range(beg, end + 1)]

    # Convert to 7 lists (1 list for 1 timezone) composed of N timestamps.

    # Associer dans un dictionnaire le fuseau avec l'ensemble de ses heures respectives.
    # La clé est le fuseau ("Europe/Paris" par exemple).
    # La valeur est la liste des heures respectives à chaque timestamp traité.
    # Un "OrderedDict" est utilisé pour conserver l'ordre des fuseaux.
    thatdict = OrderedDict(zip(zones, zip(*mainlist)))

    # Justifier à gauche les heures en tenant compte de la longueur maximale respective à chaque fuseau.
    # La longueur maximale respective à chaque fuseau est tout d'abord stockée dans un dictionnaire.
    for tz in thatdict.keys():
        width[tz] = max(len(item) for item in thatdict[tz]) + gap
    for tz in thatdict.keys():
        thatdict[tz] = ["{:<{w}}".format(item, w=width[tz]) for item in thatdict[tz]]

    # Convert to N lists (1 list for 1 timestamp) composed of 1 timestamp and 7 timezones and yield readable times.
    for ts, z1, z2, z3, z4, z5, z6, z7 in zip(range(beg, end + 1), *[v for k, v in thatdict.items()]):
        yield ts, z1, z2, z3, z4, z5, z6, z7


def mainscript(stg, align="^", fill="=", length=140):
    return "{0:{fill}{align}{length}}".format(" {0} ".format(stg), align=align, fill=fill, length=length)


def xsltransform(xml, xsl, html):
    process = subprocess.run(["java", "-cp", expandvars("%_SAXON%"), "net.sf.saxon.Transform",
                              "-s:{0}".format(xml),
                              "-xsl:{0}".format(xsl),
                              "-o:{0}".format(html)])
    return process.returncode


def prettyprint(*iterable, headers=(), char="=", tabsize=3, gap=3):
    """

    :param iterable:
    :param headers:
    :param char:
    :param tabsize:
    :param gap:
    :return:
    """
    sequence = [list(item) for item in iterable]

    # 1. Initializations.
    max_length, max_width, out_data, out_headers, separators = {}, {}, OrderedDict(), None, None

    # 2. Set input headers.
    inp_headers = list(headers)
    if not headers:
        inp_headers = ["header{0:>2d}".format(i) for i in range(len(sequence[0]))]

    # 3. Gather data per header.
    input_data = OrderedDict(zip(inp_headers, zip(*sequence)))

    # 4. Get data maximum length and maximum allowed width.
    for k, v in input_data.items():
        x = 0
        if headers:
            x = len(k)
        if any(bool(item) for item in v):
            x = max(len(str(item)) for item in v if item)
        if headers:
            if len(k) > x:
                x = len(k)
        max_length[k] = x
        max_width[k] = get_nearestmultiple(x, multiple=tabsize) + gap

    # 5. Justify data.
    for k, v in input_data.items():
        y = []
        for item in v:
            x = "{0}".format(get_tabs(max_width[k], tabsize=tabsize)).expandtabs(tabsize)
            if item:
                x = "{0}{1}".format(item, get_tabs(max_width[k] - len(str(item)), tabsize=tabsize)).expandtabs(tabsize)
            y.append(x)
        out_data[k] = y

    # 6. Set output headers.
    if headers:
        out_headers = tuple(["{0}{1}".format(header.upper(), get_tabs(max_width[header] - len(header), tabsize=tabsize)).expandtabs(tabsize) for header in input_data.keys()])
        separators = tuple(["{0}{1}".format(char * max_length[header], get_tabs(max_width[header] - max_length[header], tabsize=tabsize)).expandtabs(tabsize) for header in input_data.keys()])

    # 7. Set output data.
    out_data = zip(*[v for k, v in out_data.items()])

    # 8. Return output data as iterator objects.
    if headers:
        return [separators, out_headers, separators], out_data
    return None, out_data


def left_justify(iterable):
    """

    :param iterable:
    :return:
    """
    sequence = list(iterable)
    length = max(len(str(item)) for item in sequence)
    for item in ["{0:<{1}}".format(item, length) for item in sequence]:
        yield item


def base85_encode(stg, encoding="UTF-8"):
    return b85encode(stg.encode(encoding=encoding))


def base85_decode(bytobj, encoding="UTF-8"):
    return b85decode(bytobj).decode(encoding=encoding)


# ======================
# Jinja2 Custom filters.
# ======================
def integertostring(intg):
    return str(intg)


def cjustify(stg, width, char=""):
    return "{0:{2}^{1}}".format(stg, width, char)


def rjustify(stg, width, char=""):
    return "{0:{2}>{1}}".format(str(stg), width, char)


def ljustify(stg, width, char=""):
    return "{0:{2}<{1}}".format(stg, width, char)


def repeatelement(elem, n):
    for i in repeat(elem, n):
        yield i


def normalize(stg):
    return stg.replace(", ", "_").replace(" ", "_")


def normalize2(stg):
    return stg.replace(" ", "%20").replace("&", "%26")


def localize_date(dt, tz=None):
    """
    
    :param dt: 
    :param tz: 
    :return: 
    """
    datobj = dt
    if tz:
        datobj = tz.localize(dt).astimezone(LOCAL)
    return datobj
