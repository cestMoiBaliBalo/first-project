# -*- coding: utf-8 -*-
import argparse
import io
import locale
import os
import re
import subprocess
import zipfile
from base64 import b85decode, b85encode
from collections import MutableMapping, OrderedDict
from contextlib import ContextDecorator
from datetime import datetime
from itertools import dropwhile, filterfalse, islice, repeat, tee, zip_longest
from logging import Formatter, getLogger
from logging.handlers import RotatingFileHandler
from string import Template

import jinja2
import yaml
from PIL import Image, TiffImagePlugin
from dateutil.parser import parse
from dateutil.parser import parserinfo
from dateutil.tz import gettz
from pytz import timezone

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")

# ==========
# Constants.
# ==========
APPEND = "a"
WRITE = "w"
DATABASE = os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "database.db")
TESTDATABASE = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tests", "database.db")
ARECA = os.path.join(os.path.expandvars("%PROGRAMFILES%"), "Areca", "areca_cl.exe")
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
              "music": ["ape", "mp3", "m4a", "flac", "ogg"]}
ZONES = ["UTC",
         "US/Pacific",
         "US/Eastern",
         "Indian/Mayotte",
         "Asia/Tokyo",
         "Australia/Sydney"]


# ========
# Classes.
# ========
class ImageError(OSError):
    def __init__(self, file, error):
        self.file = file
        self.error = error


class ExifError(ImageError):
    def __init__(self, file, error):
        super(ExifError, self).__init__(file, error)


class Files(MutableMapping):
    def __init__(self, fil):
        self._fil = None
        self.fil = fil
        self._metadata = {i: getattr(self, i) for i in ["ctime", "mtime", "dirname", "basename", "extension", "parts"]}

    def __getitem__(self, item):
        return self._metadata[item]

    def __setitem__(self, key, value):
        self._metadata[key] = value

    def __delitem__(self, key):
        del self._metadata[key]

    def __len__(self):
        return len(self._metadata)

    def __iter__(self):
        return iter(self._metadata)

    @property
    def fil(self):
        return self._fil

    @fil.setter
    def fil(self, value):
        if not os.path.exists(value):
            raise FileNotFoundError('Can\'t find "{0}". Please check both dirname and basename.'.format(value))
        self._fil = value

    @property
    def dirname(self):
        return os.path.dirname(self.fil)

    @property
    def basename(self):
        return os.path.splitext(os.path.basename(self.fil))[0]

    @property
    def extension(self):
        return os.path.splitext(self.fil)[1].strip(".")

    @property
    def parts(self):
        return os.path.dirname(self.fil).split("\\")

    @property
    def ctime(self):
        return int(os.path.getctime(self.fil))

    @property
    def mtime(self):
        return int(os.path.getmtime(self.fil))


class Images(Files):
    tzinfos = {"CEST": gettz("Europe/Paris"), "CET": gettz("Europe/Paris")}

    def __init__(self, img):
        super(Images, self).__init__(img)
        self._exif = None
        self.exif = img
        for i in ["localtimestamp", "originaldatetime", "originalyear", "originalmonth", "originalday", "originalhours", "originalminutes", "originalseconds", "dayoftheyear", "dayoftheweek", "defaultlocation",
                  "defaultprefix", "originalsubseconds"]:
            self._metadata[i] = getattr(self, i)

    @property
    def exif(self):
        return self._exif

    @exif.setter
    def exif(self, value):
        try:
            self._exif = self.getexif(Image.open(value))
        except ExifError:
            raise ExifError(value, "Can\'t grab exif tags from")
        except OSError:
            raise OSError('Can\'t identify "{0}" as an image file.'.format(value))
        else:
            if not self._exif:
                raise ExifError(value, "Can\'t grab metadata from")
            if 36867 not in self._exif:
                raise ExifError(value, "Can\'t grab timestamp from")

    @property
    def datetime(self):
        return parse("{0} CET".format(self.exif[36867].replace(":", "-", 2)), tzinfos=self.tzinfos)

    @property
    def localtimestamp(self):
        return int(self.datetime.timestamp())

    @property
    def originaldatetime(self):
        return self.datetime.strftime("%d/%m/%Y %H:%M:%S %Z%z")

    @property
    def originalyear(self):
        return self.datetime.strftime("%Y")

    @property
    def originalmonth(self):
        return self.datetime.strftime("%m")

    @property
    def originalday(self):
        return self.datetime.strftime("%d")

    @property
    def originalhours(self):
        return self.datetime.strftime("%H")

    @property
    def originalminutes(self):
        return self.datetime.strftime("%M")

    @property
    def originalseconds(self):
        return self.datetime.strftime("%S")

    @property
    def originalsubseconds(self):
        return self.exif.get(37521, 0)

    @property
    def dayoftheyear(self):
        return self.datetime.strftime("%j")

    @property
    def dayoftheweek(self):
        return self.datetime.strftime("%w")

    @property
    def defaultlocation(self):
        return self.defaultlocation(self.originalyear, self.originalmonth, self.originalday)

    @property
    def defaultprefix(self):
        return "{0}{1}".format(self.originalyear, str(self.originalmonth).zfill(2))

    @property
    def make(self):
        return self.exif.get(271, "")

    @property
    def model(self):
        return self.exif.get(272, "")

    @property
    def width(self):
        return self.exif.get(40962, 0)

    @property
    def height(self):
        return self.exif.get(40963, 0)

    @property
    def copyright(self):
        return self.exif.get(33432, "")

    @classmethod
    def getexif(cls, o):
        """
        :param o: image object.
        :return: metadata dictionary
        """
        d = {}
        try:
            data = o.info["exif"]
        except KeyError:
            raise ExifError
        file = io.BytesIO(data[6:])
        head = file.read(8)
        info = TiffImagePlugin.ImageFileDirectory(head)
        info.load(file)
        for key, value in info.items():
            d[key] = cls.fixup(value)
        try:
            file.seek(d[0x8769])
        except KeyError:
            pass
        else:
            info = TiffImagePlugin.ImageFileDirectory(head)
            info.load(file)
            for key, value in info.items():
                d[key] = cls.fixup(value)
        return d

    @staticmethod
    def fixup(v):
        if len(v) == 1:
            return v[0]
        return v

    @staticmethod
    def defaultlocation(year, month, day, drive=IMAGES):

        # Cas 1 : "H:\CCYY\MM\DD".
        if year in [2011, 2012]:
            return os.path.normpath(os.path.join(drive, str(year), str(month).zfill(2), str(day).zfill(2)))

        # Cas 2 : "H:\CCYY\MM.DD".
        if year == 2014:
            return os.path.normpath(os.path.join(drive, str(year), "{0}.{1}".format(str(month).zfill(2), str(day).zfill(2))))

        # Cas 3 : "H:\CCYYMM".
        return os.path.normpath(os.path.join(drive, "{0}{1}".format(year, str(month).zfill(2))))


class CustomFormatter(Formatter):
    converter = datetime.fromtimestamp
    default_time_format = "%d/%m/%Y %H:%M:%S"
    default_localizedtime_format = "%Z%z"
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


class GlobalInterface(object):
    def __init__(self, *inputs):
        self._answer = None
        self._inputs = inputs
        self._levels = len(inputs)
        self._input = inputs[0]
        self._level = 1
        self._index = 0
        self._step = 0

    def __iter__(self):
        return self

    def __next__(self):

        # Stop iteration once last level is exhausted.
        if self._level >= self._levels and self._index >= len(self._input):
            raise StopIteration

        # Load next level once previous level is exhausted.
        if self._level > 0 and self._index >= len(self._input):
            self._input = self._inputs[self._level].get(self._answer)
            if not self._input:
                raise StopIteration
            self._level += 1
            self._index = 0

        # Return expected input.
        self._index += 1
        self._step += 1
        return self._input[self._index - 1]

    @property
    def step(self):
        return self._step

    @property
    def answer(self):
        return self._answer

    @answer.setter
    def answer(self, value):
        self._answer = value


class StringFormatter(object):
    """

    """

    # --------------------
    # Regular expressions.
    # --------------------
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

    # -------
    # Logger.
    # -------
    _logger = getLogger("{0}.StringFormatter".format(__name__))

    # --------------------
    # Initialize instance.
    # --------------------
    def __init__(self, somestring=None, config=os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "stringformatter.yml")):

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
            self._out_string = self._rex11.sub(lambda match: " ".join([word.capitalize() for word in match.group(1).split()]), self._out_string)
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
        super(LocalParser, self).__init__(dayfirst, yearfirst)


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
    destinations = {"documents": os.path.expandvars("%_MYDOCUMENTS%"), "temp": os.path.expandvars("%TEMP%"), "backup": os.path.expandvars("%_BACKUP%")}

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


# class SetUID(argparse.Action):
#     """
#     Set "end" attribute.
#     Set "uid" attribute.
#     """
#
#     def __init__(self, option_strings, dest, **kwargs):
#         super(SetUID, self).__init__(option_strings, dest, **kwargs)
#
#     def __call__(self, parsobj, namespace, values, option_string=None):
#         setattr(namespace, self.dest, values)
#         setattr(namespace, "uid", list(range(getattr(namespace, "start"), values + 1)))


# ===================
# Jinja2 environment.
# ===================
class TemplatingEnvironment(object):
    def __init__(self, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True, **kwargs):
        self._environment = None
        self.environment = jinja2.Environment(keep_trailing_newline=keep_trailing_newline, trim_blocks=trim_blocks, lstrip_blocks=lstrip_blocks, loader=kwargs.get("loader"))

    def set_environment(self, **kwargs):
        for k, v in kwargs["globalvars"].items():
            self.environment.globals[k] = v
        for k, v in kwargs["filters"].items():
            self.environment.filters[k] = v

    def set_template(self, **templates):
        for k, v in templates.items():
            setattr(self, k, self.environment.get_template(v))

    @property
    def environment(self):
        return self._environment

    @environment.setter
    def environment(self, arg):
        self._environment = arg


# ==========================
# Data validation functions.
# ==========================
def validpath(path):
    """

    :param path:
    :return:
    """
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError('"{0}" doesn\'t exist.'.format(path))
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError('"{0}" is not a directory.'.format(path))
    if not os.access(path, os.R_OK):
        raise argparse.ArgumentTypeError('"{0}" is not a readable directory.'.format(path))
    return path


def validdb(db):
    """

    :param db:
    :return:
    """
    try:
        if not os.path.exists(db):
            raise ValueError('"{0}" doesn\'t exist.'.format(db))
    except TypeError:
        raise ValueError('"{0}" doesn\'t exist.'.format(db))
    return db


def validdiscnumber(discnumber):
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


def validtracks(tracks):
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


def validalbumid(albumid):
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
        _albumsort = validalbumsort(_albumsort)
    except TypeError:
        selectors[1] = False

    if not all(selectors):
        if not any(selectors):
            raise ValueError("Both `artistsort` and `albumsort` don\'t match the expected pattern.")
        raise ValueError("`artistsort` or `albumsort` doesn\'t match the expected pattern.")

    return "{0}{1}".format(_artistsort, _albumsort)


def validalbumsort(albumsort):
    """
    Check if string `albumsort` is a coherent `albumsort` tag.

    :param albumsort: `albumsort` tag.
    :return: `albumsort` tag.
    """
    rex1 = re.compile("^(?=[\d.]+$)(?=.\.[^.]+\..$)(?=\d\.\d{{8}}\.\d$).\.({0})({1})({2})\..$".format(DFTYEARREGEX, DFTMONTHREGEX, DFTDAYREGEX))
    rex2 = re.compile("^(?=[\d.]+$)(?=.\.[^.]+\..$)(?=\d\.\d{{8}}\.\d$).\.({0})0000\..$".format(DFTYEARREGEX))
    msg = r"is not a valid albumsort."

    try:
        match1 = rex1.match(albumsort)
        match2 = rex2.match(albumsort)
    except TypeError:
        raise ValueError('"{0}" {1}'.format(albumsort, msg))
    if all([not match1, not match2]):
        raise ValueError('"{0}" {1}'.format(albumsort, msg))
    return albumsort


def validyear(year):
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


def validproductcode(productcode):
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


def validgenre(genre):
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


def validtimestamp(ts):
    """
    Check if string `ts` is a coherent Unix time.

    :param ts: Unix time.
    :return: Unix time converted to numeric characters.
    """
    msg = r"is not a valid Unix time."
    try:
        ts = str(ts)
    except TypeError:
        raise ValueError('"{0}" {1}'.format(ts, msg))

    if not re.match(r"^\d{10}$", ts):
        raise ValueError('"{0}" {1}'.format(ts, msg))
    if not re.match(DFTYEARREGEX, dateformat(LOCAL.localize(datetime.fromtimestamp(int(ts))), "$Y")):
        raise ValueError('"{0}" {1}'.format(ts, msg))
    return int(ts)


def validdatetime(ts):
    """
    Check if string `ts` is a coherent Unix time or a coherent python datetime object.

    :param ts: Unix time or python datetime object.
    :return: (Unix time converted to a) python datetime naive object respective to the local system time zone.
    """
    error, msg = False, r"is not a valid Unix time."
    try:
        ts = int(ts)
    except (ValueError, TypeError):
        error = True

    if error:
        try:
            struct = ts.timetuple()
        except (TypeError, AttributeError):
            raise ValueError('"{0}" {1}'.format(ts, msg))
        return ts

    try:
        datobj = datetime.fromtimestamp(ts)
    except OSError:
        raise ValueError('"{0}" {1}'.format(ts, msg))
    return datobj


# ========================
# Miscellaneous functions.
# ========================
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
    return RotatingFileHandler(os.path.join(os.path.expandvars("%_COMPUTING%"), "Log", "pythonlog.log"), maxBytes=maxbytes, backupCount=backupcount, encoding=encoding)


def readable(dt, template, tz=None):
    """
    Return a human readable (naive or aware) datetime object respective to the local system time zone.

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


def gettabs(length, *, tabsize=3):
    x = int(length / tabsize)
    y = length % tabsize
    if y:
        x += 1
    return x * "\t"


def getnearestmultiple(length, *, multiple=3):
    x = int(length / multiple)
    y = length % multiple
    if y:
        x += 1
    return x * multiple


def getrippingapplication(*, timestamp=None):
    """
    Get ripping application respective to the facultative input local timestamp.

    :param timestamp: facultative input local timestamp.
    :return: ripping application.
    """
    application = {"1512082800": "dBpoweramp 16.1", "1388530800": "dBpoweramp 15.1", "0": "dBpoweramp 14.1"}
    if not timestamp:
        timestamp = int(UTC.localize(datetime.utcnow()).astimezone(LOCAL).timestamp())
    return list(islice(dropwhile(lambda i: int(i[0]) > timestamp, sorted(application.items(), key=lambda i: int(i[0]), reverse=True)), 1))[0][1]


def filesinfolder(*extensions, folder, excluded=None):
    """
    Return a generator object yielding files stored in "folder" having extension enumerated in "extensions".
    :param extensions: not mandatory list of extension(s) to filter files.
    :param folder: folder to walk through.
    :param excluded: list of folder(s) to exclude.
    :return: generator object.
    """
    # logger = getLogger("Default.{0}.filesinfolder".format(__name__))

    # --> Regular expression for folder(s) exclusion.
    regex1 = None
    if excluded:
        regex1 = re.compile(r"(?:{0})".format("|".join(map(os.path.normpath, map(os.path.join, repeat(folder), excluded))).replace("\\", r"\\").replace("$", r"\$")), re.IGNORECASE)

    # --> Walk through folder.
    for root, folders, files in os.walk(folder):

        # Regular expression for extension(s) inclusion.
        rex2 = r"\.[a-z0-9]{3,}$"
        if extensions:
            rex2 = r"\.(?:{0})$".format("|".join(extensions))
        regex2 = re.compile(rex2, re.IGNORECASE)

        # Yield file(s) if not excluded.
        for file in files:
            if regex1 and regex1.match(root):
                continue
            if not regex2.match(os.path.splitext(file)[1]):
                continue
            yield os.path.join(root, file)


def getdatefromseconds(beg, end, zone=DFTTIMEZONE):
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
        width[tz] = max([len(item) for item in thatdict[tz]]) + gap
    for tz in thatdict.keys():
        thatdict[tz] = ["{:<{w}}".format(item, w=width[tz]) for item in thatdict[tz]]

    # Convert to N lists (1 list for 1 timestamp) composed of 1 timestamp and 7 timezones and yield readable times.
    for ts, z1, z2, z3, z4, z5, z6, z7 in zip(range(beg, end + 1), *[v for k, v in thatdict.items()]):
        yield ts, z1, z2, z3, z4, z5, z6, z7


def interface(obj):
    for inp, dest in obj:
        while True:
            value = input("{0}. {1}: ".format(obj.step, inp))
            try:
                setattr(obj, dest, value)
                setattr(obj, "answer", value)
            except ValueError:
                continue
            break
    return obj


def zipfiles(archive, *files):
    logger = getLogger("{0}.zipfiles".format(__name__))
    if not os.path.exists(os.path.dirname(archive)):
        raise OSError('"{0}" doesn\'t exist. Please enter an existing directory.'.format(os.path.dirname(archive)))
    with zipfile.ZipFile(archive, "w") as thatzip:
        logger.info('"{0}" used as ZIP file.'.format(archive))
        for file in files:
            if os.path.exists(file):
                thatzip.write(file, arcname=os.path.basename(file))
                logger.info('"{0}" successfully written.'.format(file))
                continue
            logger.info('Failed to write "{0}".'.format(file))


def mainscript(stg, align="^", fill="=", length=140):
    return "{0:{fill}{align}{length}}".format(" {0} ".format(stg), align=align, fill=fill, length=length)


def xsltransform(xml, xsl, html):
    process = subprocess.run(["java", "-cp", os.path.expandvars("%_SAXON%"), "net.sf.saxon.Transform",
                              "-s:{0}".format(xml),
                              "-xsl:{0}".format(xsl),
                              "-o:{0}".format(html)])
    return process.returncode


def prettyprint(*tup, headers=(), char="=", tabsize=3, gap=3):
    """

    :param tup:
    :param headers:
    :param char:
    :param tabsize:
    :param gap:
    :return:
    """

    # 1. Initializations.
    max_length, max_width, out_data, out_headers, separators = {}, {}, OrderedDict(), None, None

    # 2. Set input headers.
    inp_headers = list(headers)
    if not headers:
        inp_headers = ["header{0:>2d}".format(i) for i in range(len(tup[0]))]

    # 3. Gather data per header.
    input_data = OrderedDict(zip(inp_headers, zip(*tup)))

    # 4. Get data maximum length and maximum allowed width.
    for k, v in input_data.items():
        x = 0
        if headers:
            x = len(k)
        if any([bool(item) for item in v]):
            x = max([len(item) for item in v if item])
        if headers:
            if len(k) > x:
                x = len(k)
        max_length[k] = x
        max_width[k] = getnearestmultiple(x, multiple=tabsize) + gap

    # 5. Justify data.
    for k, v in input_data.items():
        y = []
        for item in v:
            x = "{0}".format(gettabs(max_width[k], tabsize=tabsize)).expandtabs(tabsize)
            if item:
                x = "{0}{1}".format(item, gettabs(max_width[k] - len(item), tabsize=tabsize)).expandtabs(tabsize)
            y.append(x)
        out_data[k] = y

    # 6. Set output headers.
    if headers:
        out_headers = tuple(["{0}{1}".format(header.upper(), gettabs(max_width[header] - len(header), tabsize=tabsize)).expandtabs(tabsize) for header in input_data.keys()])
        separators = tuple(["{0}{1}".format(char * max_length[header], gettabs(max_width[header] - max_length[header], tabsize=tabsize)).expandtabs(tabsize) for header in input_data.keys()])

    # 7. Set output data.
    out_data = zip(*[v for k, v in out_data.items()])

    # 8. Return output data as iterator objects.
    if headers:
        return [separators, out_headers, separators], out_data
    return None, out_data


def base85_encode(strg, encoding="utf-8"):
    return b85encode(strg.encode(encoding=encoding))


def base85_decode(bytobj, encoding="utf-8"):
    return b85decode(bytobj).decode(encoding=encoding)


# ==========================
# Jinja2 Customized filters.
# ==========================
def integertostring(intg):
    return str(intg)


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
    datobj = dt
    if tz:
        datobj = tz.localize(dt).astimezone(LOCAL)
    return datobj
