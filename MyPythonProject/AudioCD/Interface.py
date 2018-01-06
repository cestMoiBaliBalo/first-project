# -*- coding: utf-8 -*-
"""
Interface.py: Command line application for tables maintenance.

Can be used as follow:

1. For displaying table record(s):
   select `table` --database "database_test.db"
   select `table`
   select `table` 250 251 252 --database "database_test.db"
   select `table` 250 251 252

2. For deleting table record(s):
   delete `table` 250 251 252 --database "database_test.db"
   delete `table` 250 251 252

3. For updating table record(s):
   update `table` 250 251 252 --artistsort "Artist, The" --albumsort "1.20170000.1" --database "database_test.db"
   update `table` 250 251 252 --artistsort "Artist, The" --albumsort "1.20170000.1"

"""
# pylint: disable=invalid-name

import argparse
import logging.config
import os
import re
import sys
from datetime import datetime
from functools import partial
from itertools import accumulate, repeat

import jinja2
import yaml
from dateutil.parser import parse
from pytz import timezone

from Applications.Database.AudioCD.shared import deletelog, insertfromargs, insertfromfile as insertlogsfromfile, selectlog, selectlogs, updatelog
from Applications.Database.DigitalAudioFiles.shared import deletealbum, deletealbumheader, deletetrack, getalbumdetail, getalbumheader, getalbumid, getrowid, insertfromfile as insertalbumsfromfile, \
    updatealbum, updatetrack
from Applications.Database.shared import Boolean
from Applications.parsers import database_parser, loglevel_parser
from Applications.shared import DATABASE, DFTMONTHREGEX, DFTYEARREGEX, LOCAL, LOCALMONTHS, LocalParser, StringFormatter, TEMPLATE4, TEMPLATE6, TemplatingEnvironment, UTC, dateformat, grouper, \
    prettyprint as pp, readable, rjustify, validalbumid, validalbumsort, validdiscnumber, validproductcode, validtimestamp, validtracks, validyear

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ==========
# Constants.
# ==========
GENRES = ["Rock", "Hard Rock", "Progressive Rock", "Alternative Rock", "Black Metal", "Doom Metal", "Heavy Metal", "Pop", "French Pop"]


# ========
# Classes.
# ========
class GetRowID(argparse.Action):
    """

    """

    def __init__(self, option_strings, dest, **kwargs):
        super(GetRowID, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        mylist = []
        for val in values:
            try:
                val = [int(val)]
            except ValueError:
                val = [item[0] for item in getrowid(val, db=getattr(namespace, "db"))]
            finally:
                mylist.extend(val)
        setattr(namespace, "rowid", mylist)


class FormatTitle(argparse.Action):
    """

    """

    def __init__(self, option_strings, dest, **kwargs):
        super(FormatTitle, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, "track_title", values)
        setattr(namespace, self.dest, StringFormatter(somestring=values).convert())


class DoNotFormatTitle(argparse.Action):
    """

    """

    def __init__(self, option_strings, dest, **kwargs):
        super(DoNotFormatTitle, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        if values:
            setattr(namespace, "title", getattr(namespace, "track_title"))


# ===========
# Decorators.
# ===========


#    --------------------------------
# 1. Decorators for SELECT functions.
#    --------------------------------
def deco1(func):
    def wrapper(*args, **kwargs):
        for row in getalbumheader(albumid=[item[1] for item in map(func, args, repeat(kwargs.get("db", DATABASE))) if item[1]], **kwargs):
            yield row

    return wrapper


def deco2(func):
    def wrapper(**kwargs):
        return [(row.track_rowid,
                 row.albumid,
                 row.discid,
                 row.trackid,
                 row.title,
                 row.album) for row in func(**kwargs)]

    return wrapper


def prettyprint(func):
    def wrapper(ns=None, **kwargs):
        thatlogger = logging.getLogger("Database.Interface.prettyprint")
        pairs = dict(kwargs)
        if ns:
            pairs = {k: v for k, v in vars(ns).items()}
        for k, v in sorted(pairs.items()):
            thatlogger.debug("{0}: {1}".format(k, v))
        table = pairs.get("table")
        if table:
            return PRETTYPRINT[table](func(**pairs))
        return []

    return wrapper


#    --------------------------------
# 2. Decorators for UPDATE functions.
#    --------------------------------
def deco3(func):
    def wrapper(*args, db, **kwargs):
        return [func(arg, db, **kwargs) for arg in args]  # [(A.Artist, The.1.20170000.1, 1, 1, 10), (A.Artist, The.1.20160000.1, 1, 1, 12)]

    return wrapper


def deco4(func):
    def wrapper(*args, db, **kwargs):
        return list(accumulate([func(arg, db, **kwargs) for arg in args]))[-1]  # type: int

    return wrapper


#    --------------------------------
# 3. Decorators for DELETE functions.
#    --------------------------------
def deco5(func):
    def wrapper(*args, db):
        return list(map(func, repeat(db), args))  # [(A.Artist, The.1.20170000.1, 1, 1, 10), (A.Artist, The.1.20160000.1, 1, 1, 12)]

    return wrapper


#    --------------------------------
# 4. Decorators for INSERT functions.
#    --------------------------------
def deco6(func):
    def wrapper(db, **kwargs):
        return func(*kwargs.get("file", []), db=db)  # type: int

    return wrapper


def deco7(func):
    def wrapper(db, **kwargs):
        return list(accumulate(func(*kwargs.get("file", []), db=db)))[-1]  # type: int

    return wrapper


#    -----------------
# 5. Other decorators.
#    -----------------
def dateprint_formatter(func):
    def wrapper(datobj, *, fromtz=timezone("UTC"), totz=timezone("Europe/Paris"), template=TEMPLATE6):
        if datobj:
            return func(fromtz.localize(datobj).astimezone(totz), template)
        return None

    return wrapper


dateformat = dateprint_formatter(dateformat)


# ==========
# Functions.
# ==========
def boolean(stg):
    return Boolean(stg)


def albumid(stg):
    """
    Check if a string match the albumsort pattern.

    :param stg: String.
    :return: Input string if match successes. Exception if match fails.
    """
    try:
        _albumid = validalbumid(stg)
    except ValueError as err:
        raise argparse.ArgumentTypeError(err)
    return _albumid


def albumsort(stg):
    """
    Check if a string match the albumsort pattern.

    :param stg: String.
    :return: Input string if match successes. Exception if match fails.
    """
    try:
        _albumsort = validalbumsort(stg)
    except ValueError as err:
        raise argparse.ArgumentTypeError(err)
    return _albumsort


def year(stg):
    """
    Check if a string match the year pattern.

    :param stg: String.
    :return: Input string converted to an integer if match successes. Exception if match fails.
    """
    try:
        _year = validyear(stg)
    except ValueError as err:
        raise argparse.ArgumentTypeError(err)
    return _year


def productcode(stg):
    """
    Check if a string match the product code pattern.

    :param stg: String.
    :return: Input string if match successes. Exception if match fails.
    """
    try:
        _productcode = validproductcode(stg)
    except ValueError as err:
        raise argparse.ArgumentTypeError(err)
    return _productcode


def unixepochtime(stg):
    """

    :param stg:
    :return:
    """
    try:
        _unixepochtime = validtimestamp(stg)
    except ValueError as err:
        raise argparse.ArgumentTypeError(err)
    return _unixepochtime


def discnumber(stg):
    """
    Check if a string match the albumsort pattern.

    :param stg: String.
    :return: Input string if match successes. Exception if match fails.
    """
    try:
        _discnumber = validdiscnumber(stg)
    except ValueError as err:
        raise argparse.ArgumentTypeError(err)
    return _discnumber


def tracks(stg):
    """
    Check if a string match the albumsort pattern.

    :param stg: String.
    :return: Input string if match successes. Exception if match fails.
    """
    try:
        _tracks = validtracks(stg)
    except ValueError as err:
        raise argparse.ArgumentTypeError(err)
    return _tracks


def validmonth(month):
    """

    :param month:
    :return:
    """
    rex1 = re.compile(r"^(?:{0})\b(?:-|/|\s)\b(?:{1})$".format(DFTYEARREGEX, DFTMONTHREGEX))
    rex2 = re.compile(r"^\b(\w+)\b\s\b(?:{0})$".format(DFTYEARREGEX), re.IGNORECASE)

    try:
        month = str(month)
    except TypeError:
        raise argparse.ArgumentTypeError('"{0}" is not a valid month format'.format(month))

    match = rex1.match(month)
    if match:
        return int(dateformat(LOCAL.localize(parse(month, default=datetime.utcnow(), parserinfo=LocalParser(dayfirst=True))), "$Y$m"))
    match = rex2.match(month)
    if match:
        if match.group(1) in LOCALMONTHS:
            return int(dateformat(LOCAL.localize(parse(month, default=datetime.utcnow(), parserinfo=LocalParser(dayfirst=True))), "$Y$m"))
    raise argparse.ArgumentTypeError('"{0}" is not a valid month format'.format(month))


def getfunction(table="default", statement="default", donotpropagate=True, row=True):
    table_dict = CONFIGURATION[table]
    statement_dict = table_dict[statement]
    propagation_dict = statement_dict[donotpropagate]
    return propagation_dict[row]


def gettemplate(args):
    """
    Get the appropriate Jinja2 template to display requested results.

    :param args: Namespace object holding parsed arguments as attributes.
    :return: Template. Or None if no template is required.
    """
    templates = {
        "rippinglog":
            {
                "select":
                    {
                        False: "T01",
                        True: "T01"
                    }
            },
        "albums":
            {
                "select":
                    {
                        False: "T01",
                        True: "T01"
                    },
                "delete":
                    {
                        False: "T03"
                    },
                "update":
                    {
                        False: "T03",
                        True: "T03"
                    }
            },
        "tracks":
            {
                "select":
                    {
                        False: "T01",
                        True: "T01"
                    }
            }
    }
    if args.table in templates:
        if args.statement in templates[args.table]:
            if args.donotpropagate in templates[args.table][args.statement]:
                return templates[args.table][args.statement][args.donotpropagate]
    return None


def insert_func(ns=None, **kwargs):
    """
    Run the appropriate `insert` function respective to the parsed table.

    :param ns: Namespace object holding parsed arguments as attributes.
    :param kwargs: Dictionary holding parsed arguments.
    :return: Inserted records count.
    """
    pairs = dict(kwargs)
    if ns:
        pairs = {k: v for k, v in vars(ns).items()}
    db = pairs.get("db")
    table = pairs.get("table")
    statement = pairs.get("statement")
    if all([db, table, statement]):
        kwargs = {key: val for key, val in pairs.items() if key not in ["db", "table", "statement", "function", "template"]}
        if kwargs:
            return CONFIGURATION[table][statement](db=db, **kwargs)
    return DEFAULT.get(table, DEFAULT["default"])


def select_func(ns=None, **kwargs):
    """
    Run the appropriate `select` function respective to the parsed table.

    :param ns: Namespace object holding parsed arguments as attributes.
    :param kwargs: Dictionary holding parsed arguments.
    :return: Selected records list.
    """
    pairs = dict(kwargs)
    if ns:
        pairs = {k: v for k, v in vars(ns).items()}
    db = pairs.get("db")
    table = pairs.get("table")
    statement = pairs.get("statement")
    donotpropagate = pairs.get("donotpropagate", False)
    rowid = pairs.get("rowid", [])
    if all([db, table, statement]):
        return list(getfunction(table, statement, donotpropagate, bool(rowid))(*rowid, **pairs))
    return []


def delete_func(ns=None, **kwargs):
    """
    Run the appropriate `delete` function respective to the parsed table.

    :param ns: Namespace object holding parsed arguments as attributes.
    :param kwargs: Dictionary holding parsed arguments.
    :return: Deleted records count.
    """
    pairs = dict(kwargs)
    if ns:
        pairs = {k: v for k, v in vars(ns).items()}
    db = pairs.get("db")
    table = pairs.get("table")
    statement = pairs.get("statement")
    donotpropagate = pairs.get("donotpropagate", False)
    rowid = pairs.get("rowid", [])
    if all([db, table, statement, rowid]):
        return getfunction(table, statement, donotpropagate, bool(rowid))(*rowid, db=db)
    return DEFAULT.get(table, DEFAULT["default"])


def update_func(ns=None, **kwargs):
    """
    Run the appropriate `update` function respective to the parsed table.

    :param ns: Namespace object holding parsed arguments as attributes.
    :param kwargs: Dictionary holding parsed arguments.
    :return: Updated records count.
    """
    pairs = dict(kwargs)
    if ns:
        pairs = {k: v for k, v in vars(ns).items()}
    db = pairs.get("db")
    table = pairs.get("table")
    statement = pairs.get("statement")
    donotpropagate = pairs.get("donotpropagate", False)
    rowid = pairs.get("rowid", [])
    if all([db, table, statement, rowid]):
        kwargs = {key: val for key, val in pairs.items() if key not in ["db", "donotformat", "donotpropagate", "function", "rowid", "statement", "table", "template", "test", "track_title"]}
        if kwargs:
            return getfunction(table, statement, donotpropagate, bool(rowid))(*rowid, db=db, **kwargs)
    return DEFAULT.get(table, DEFAULT["default"])


def print_rippinglog(iterable):
    """

    :param iterable:
    :return:
    """
    for item in print_formatter(*pp(*[(row.artistsort,
                                       row.albumsort,
                                       row.artist,
                                       "{0:>8d}".format(row.origyear),
                                       "{0:>4d}".format(row.year),
                                       row.album,
                                       row.label,
                                       row.genre,
                                       row.upc,
                                       "{0:>4d}".format(row.disc),
                                       "{0:>6d}".format(row.tracks),
                                       dateformat(row.ripped, fromtz=LOCAL),
                                       dateformat(row.utc_created),
                                       "{0:>5d}".format(row.rowid)) for row in iterable],
                                    headers=("artistsort", "albumsort", "artist", "origyear", "year", "album", "label", "genre", "upc", "disc", "tracks", "ripped", "created", "rowid"),
                                    tabsize=1,
                                    gap=2)):
        yield item


def print_albums(iterable):
    """

    :param iterable:
    :return:
    """
    for item in print_formatter(*pp(*[(row.albumid[2:-13],
                                       row.albumid[-12:],
                                       row.artist,
                                       "{0:>8d}".format(row.origyear),
                                       row.album,
                                       "{0:>5d}".format(row.discs),
                                       row.label,
                                       row.genre,
                                       row.upc,
                                       dateformat(row.utc_played),
                                       "{0:>5d}".format(row.played),
                                       dateformat(row.utc_modified),
                                       "{0:>4d}".format(row.year),
                                       "{0:>5d}".format(row.rowid)
                                       ) for row in iterable],
                                    headers=("artistsort", "albumsort", "artist", "origyear", "album", "discs", "label", "genre", "upc", "played", "count", "modified", "year", "rowid"),
                                    tabsize=1,
                                    gap=2)):
        yield item


def print_tracks(iterable):
    """

    :param iterable:
    :return:
    """
    for item in print_formatter(*pp(*[(row[1][2:-13],
                                       row[1][-12:],
                                       row[5],
                                       "{0:>6d}".format(row[2]),
                                       "{0:>7d}".format(row[3]),
                                       row[4],
                                       "{0:>5d}".format(row[0])) for row in iterable],
                                    headers=("artistsort", "albumsort", "album", "discid", "trackid", "title", "rowid"),
                                    tabsize=1,
                                    gap=2)):
        yield item


def print_formatter(header, body, *, itemspergroup=60):
    """

    :param header:
    :param body:
    :param itemspergroup:
    :return:
    """
    thatlogger = logging.getLogger("Database.Interface.print_formatter")
    thatlogger.debug(header)
    thatlogger.debug(body)

    # 1. Store header into a container object.
    if header:
        header = list(header)

    # 2. Group body by `itemspergroup` items and yield data.
    for item in grouper(body, itemspergroup):
        thatlogger.debug(item)
        yield "\n\n"
        if header:
            for head in header:
                yield "{0:>{1}}".format("".join(head), len("".join(head)) + 1)
        for sub_item in item:
            if sub_item:
                sub_item = "{0:>{1}}".format("".join(sub_item), len("".join(sub_item)) + 1)
                yield sub_item


# ==============================
# Maintenance functions mapping.
# ==============================
CONFIGURATION = {
    "rippinglog":
        {
            "select":
                {
                    True:
                        {
                            False: selectlogs,
                            True: selectlog
                        },
                    False:
                        {
                            False: selectlogs,
                            True: selectlog
                        }
                },
            "update":
                {
                    True:
                        {
                            True: updatelog
                        },
                    False:
                        {
                            True: updatelog
                        }
                },
            "delete":
                {
                    True:
                        {
                            True: deletelog
                        },
                    False:
                        {
                            True: deletelog
                        }
                },
            "insert": insertfromargs,
            "insertfromfile": deco6(insertlogsfromfile)
        },
    "albums":
        {
            "select":
                {
                    True:
                        {
                            False: getalbumheader,
                            True: deco1(getalbumid)
                        },
                    False:
                        {
                            False: getalbumheader,
                            True: deco1(getalbumid)
                        }
                },
            "delete":
                {
                    True:
                        {
                            True: deletealbumheader
                        },
                    False:
                        {
                            True: deco5(deletealbum)
                        }
                },
            "update":
                {
                    True:
                        {
                            True: deco3(updatealbum)
                        },
                    False:
                        {
                            True: deco3(updatealbum)
                        }
                },
            "insertfromfile": deco7(insertalbumsfromfile)

        },
    "tracks":
        {
            "select":
                {
                    True:
                        {
                            False: deco2(getalbumdetail),
                            True: deco2(getalbumdetail)
                        },
                    False:
                        {
                            False: deco2(getalbumdetail),
                            True: deco2(getalbumdetail)
                        }
                },
            "update":
                {
                    True:
                        {
                            True: deco4(updatetrack)
                        },
                    False:
                        {
                            True: deco4(updatetrack)
                        }
                },
            "delete":
                {
                    True:
                        {
                            True: deletetrack
                        },
                    False:
                        {
                            True: deletetrack
                        }
                }
        }
}
DEFAULT = {
    "default": 0,
    "albums": [(None, 0, 0, 0)]
}
ACTIONS = {
    "insert": "inserted",
    "insertfromfile": "inserted",
    "delete": "deleted",
    "update": "updated",
}
PRETTYPRINT = {
    "rippinglog": print_rippinglog,
    "albums": print_albums,
    "tracks": print_tracks
}

# ===============
# Parent parsers.
# ===============

#    -----------------
# 1. SELECT statement.
#    -----------------
select_parent = argparse.ArgumentParser(description="Shared parser for `select` subparsers.", add_help=False)
select_parent.set_defaults(donotpropagate=True)
select_parent.set_defaults(function=select_func)
select_parent.set_defaults(template=gettemplate)
select_parent.add_argument("rowid", nargs="*", type=int, help="List of ROWID to be selected. Optional.")

#    -----------------
# 2. DELETE statement.
#    -----------------
delete_parent = argparse.ArgumentParser(description="Shared parser for `delete` subparsers.", add_help=False)
delete_parent.set_defaults(function=delete_func)
delete_parent.set_defaults(template=gettemplate)
delete_parent.add_argument("keys", nargs="+", action=GetRowID, help="List of unique keys. ROWID or ALBUMID. Mandatory.")

#    -----------------
# 3. UPDATE statement.
#    -----------------
update_parent = argparse.ArgumentParser(description="Shared parser for `update` subparsers.", add_help=False, argument_default=argparse.SUPPRESS)
update_parent.set_defaults(function=update_func)
update_parent.set_defaults(template=gettemplate)
update_parent.set_defaults(donotpropagate=True)
update_parent.add_argument("keys", nargs="+", action=GetRowID, help="List of unique keys. ROWID or ALBUMID. Mandatory.")
update_parent.add_argument("--artist", help="Album artist. Optional.", metavar="The Artist")
update_parent.add_argument("--year", type=year, help="Album year. Optional. Only integers are allowed.")
update_parent.add_argument("--album", help="Album. Optional.", metavar="The Album")
update_parent.add_argument("--label", help="Album label. Optional.")
update_parent.add_argument("--genre", choices=GENRES, help="Album genre. Optional.")

#    ---------------
# 4. Subset results.
#    ---------------
subset_parser = argparse.ArgumentParser(description="Shared parser for subset results.", add_help=False, argument_default=argparse.SUPPRESS)
subset_parser.add_argument("--artistsort", nargs="*", help="Subset results by `artistsort`. Optional.")
subset_parser.add_argument("--albumsort", nargs="*", help="Subset results by `albumsort`. Optional.")
subset_parser.add_argument("--artist", nargs="*", help="Subset results by `artist`. Optional.")
subset_parser.add_argument("--year", nargs="*", type=year, help="Subset results by `year`. Optional.")
subset_parser.add_argument("--album", nargs="*", help="Subset results by `album`. Optional.")
subset_parser.add_argument("--genre", nargs="*", help="Subset results by `genre`. Optional.")

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser(usage="Command line application for tables maintenance.",
                                 description="Allow both `rippinglog` and `albums` maintenance thanks to a command line interface.",
                                 allow_abbrev=False,
                                 argument_default=argparse.SUPPRESS)
subparser = parser.add_subparsers(dest="table")

#     ------------------------------
#  1. Parser for `rippinglog` table.
#     ------------------------------
parser_log = subparser.add_parser("rippinglog",
                                  description="Subparser for `rippinglog` maintenance.")
subparser_log = parser_log.add_subparsers(dest="statement")

#  1.a. SELECT statement.
parser_log_select = subparser_log.add_parser("select",
                                             parents=[select_parent, database_parser, subset_parser, loglevel_parser],
                                             description="Subparser for selecting record(s) from `rippinglog` table.",
                                             argument_default=argparse.SUPPRESS)
parser_log_select.add_argument("--label", nargs="*", type=year, help="Subset results by `label`. Optional.")
parser_log_select.add_argument("--rippedyear", nargs="*", type=year, help="Subset results by `ripped year`. Optional.")
parser_log_select.add_argument("--rippedmonth", nargs="*", type=validmonth, help="Subset results by `ripped month`. Optional.")
parser_log_select.add_argument("--orderby", nargs="*", default=["rowid"])

#  1.b. DELETE statement.
parser_log_delete = subparser_log.add_parser("delete",
                                             parents=[delete_parent, database_parser, loglevel_parser],
                                             description="Subparser for deleting record(s) from `rippinglog` table.")
parser_log_delete.set_defaults(donotpropagate=True)

#  1.c. UPDATE statement.
parser_log_update = subparser_log.add_parser("update",
                                             parents=[update_parent, database_parser, loglevel_parser],
                                             description="Subparser for updating record(s) from `rippinglog` table.",
                                             argument_default=argparse.SUPPRESS)
parser_log_update.add_argument("--artistsort", help="Album artistsort key. Optional.", metavar="Artist, The")
parser_log_update.add_argument("--albumsort", type=albumsort, help="Album albumsort key. Optional.", metavar="1.20170000.1")
parser_log_update.add_argument("--origyear", type=year, help="Album original year. Optional.")
parser_log_update.add_argument("--disc", type=discnumber, help="Disc number. Optional.")
parser_log_update.add_argument("--tracks", type=tracks, help="Total tracks number. Optional.")
parser_log_update.add_argument("--upc", type=productcode, help="Album product code. Optional.")
parser_log_update.add_argument("--application", help="Ripping application. Optional.")
parser_log_update.add_argument("--ripped", type=unixepochtime, help="Ripping local Unix epoch time. Optional.", metavar="1500296048")

#  1.d. INSERT statement.
parser_log_insert = subparser_log.add_parser("insert",
                                             parents=[database_parser, loglevel_parser],
                                             description="Subparser for inserting record(s) into `rippinglog` table.",
                                             argument_default=argparse.SUPPRESS)
parser_log_insert.set_defaults(function=insert_func)
parser_log_insert.set_defaults(template=gettemplate)
parser_log_insert.set_defaults(donotpropagate=True)
parser_log_insert.add_argument("artistsort", help="Album artistsort. Mandatory.", metavar="Artist, The")
parser_log_insert.add_argument("albumsort", type=albumsort, help="Album albumsort. Mandatory.", metavar="1.20170000.1")
parser_log_insert.add_argument("artist", help="Album artist. Mandatory.", metavar="The Artist")
parser_log_insert.add_argument("origyear", help="Album original year. Mandatory. Only integers are allowed.")
parser_log_insert.add_argument("year", help="Album year. Mandatory. Only integers are allowed.")
parser_log_insert.add_argument("album", help="Album. Mandatory.", metavar="The Album")
parser_log_insert.add_argument("disc", type=discnumber, help="Disc number. Mandatory. Only integers are allowed.")
parser_log_insert.add_argument("tracks", type=tracks, help="Total tracks number. Mandatory. Only integers are allowed.")
parser_log_insert.add_argument("genre", choices=GENRES, help="Album genre. Mandatory.")
parser_log_insert.add_argument("upc", type=productcode, help="Album product code. Mandatory.")
parser_log_insert.add_argument("label", help="Album label. Mandatory.")
parser_log_insert.add_argument("--application", nargs="?", default="dBpoweramp 15.1", help="Ripping application. Optional.")
parser_log_insert.add_argument("--ripped", type=unixepochtime, help="Ripping local Unix epoch time. Optional.", metavar="1500296048")

#  1.e. INSERTFROMFILE statement.
parser_log_insertff = subparser_log.add_parser("insertfromfile",
                                               parents=[database_parser, loglevel_parser],
                                               description="Subparser for inserting record(s) into `rippinglog` table from file(s).")
parser_log_insertff.set_defaults(function=insert_func)
parser_log_insertff.set_defaults(template=gettemplate)
parser_log_insertff.set_defaults(donotpropagate=True)
parser_log_insertff.add_argument("file", nargs="+", type=argparse.FileType(mode="r", encoding="UTF_8"), help="Input file(s). UTF-8 encoded JSON or XML. Mandatory.")

#     --------------------------
#  2. Parser for `albums` table.
#     --------------------------
parser_alb = subparser.add_parser("albums",
                                  description="Subparser for `albums` maintenance.")
subparser_alb = parser_alb.add_subparsers(dest="statement")

#  2.a. SELECT statement.
parser_alb_select = subparser_alb.add_parser("select",
                                             parents=[select_parent, database_parser, subset_parser, loglevel_parser],
                                             description="Subparser for selecting record(s) from `albums` table.",
                                             argument_default=argparse.SUPPRESS)
parser_alb_select.add_argument("--label", nargs="*", type=year, help="Subset results by `label`. Optional.")
parser_alb_select.add_argument("--orderby", nargs="*", default=["albumid", "discid", "trackid"])

#  2.b. DELETE statement.
parser_alb_delete = subparser_alb.add_parser("delete",
                                             parents=[delete_parent, database_parser, loglevel_parser],
                                             description="Subparser for deleting record(s) from `albums` table.")
parser_alb_delete.add_argument("--donotpropagate", nargs="?", default=False, const=True)

#  2.c. UPDATE statement.
parser_alb_update = subparser_alb.add_parser("update",
                                             parents=[update_parent, database_parser, loglevel_parser],
                                             description="Subparser for updating record(s) from `albums` table.",
                                             argument_default=argparse.SUPPRESS)
alb_update_group = parser_alb_update.add_mutually_exclusive_group()
parser_alb_update.add_argument("--albumid", type=albumid, help="Album unique ID. Optional.", metavar="Artist, The.1.20170000.1")
parser_alb_update.add_argument("--live", type=boolean, help="Live album. Optional.")
parser_alb_update.add_argument("--bootleg", type=boolean, help="Bootleg album. Optional.")
parser_alb_update.add_argument("--incollection", type=boolean, help="Album in personal collection. Optional.")
parser_alb_update.add_argument("--upc", type=productcode, help="Album product code. Optional.")
parser_alb_update.add_argument("--utc_played", type=unixepochtime, help="Album last played UTC Unix epoch time. Optional.", metavar="1500296048")
alb_update_group.add_argument("--played", type=int, help="Album played counter. Optional.")
alb_update_group.add_argument("--icount", action="store_true", help="Increment played counter by 1. Optional.")
alb_update_group.add_argument("--dcount", action="store_true", help="Decrement played counter by 1. Optional.")

#  2.d. INSERTFROMFILE statement.
parser_alb_insertff = subparser_alb.add_parser("insertfromfile",
                                               parents=[database_parser, loglevel_parser], description="Subparser for inserting record(s) into `rippinglog` table from file(s).")
parser_alb_insertff.set_defaults(function=insert_func)
parser_alb_insertff.set_defaults(template=gettemplate)
parser_alb_insertff.set_defaults(donotpropagate=True)
parser_alb_insertff.add_argument("file", nargs="+", type=argparse.FileType(mode="r", encoding="UTF_8"), help="Input file(s). UTF-8 encoded JSON or XML. Mandatory.")

#     --------------------------
#  3. Parser for `tracks` table.
#     --------------------------
parser_trk = subparser.add_parser("tracks",
                                  description="Subparser for `tracks` maintenance.")
subparser_trk = parser_trk.add_subparsers(dest="statement")

#  3.a. SELECT statement.
parser_trk_select = subparser_trk.add_parser("select",
                                             parents=[select_parent, database_parser, loglevel_parser],
                                             description="Subparser for selecting record(s) from `tracks` table.",
                                             argument_default=argparse.SUPPRESS)
parser_trk_select.add_argument("--artistsort", nargs="*", help="Subset results by `artistsort`. Optional.")
parser_trk_select.add_argument("--albumsort", nargs="*", help="Subset results by `albumsort`. Optional.")
parser_trk_select.add_argument("--orderby", nargs="*", default=["albumid", "discid", "trackid"])

#  3.b. DELETE statement.
parser_trk_delete = subparser_trk.add_parser("delete",
                                             parents=[delete_parent, database_parser, loglevel_parser],
                                             description="Subparser for deleting record(s) from `tracks` table.")
parser_trk_delete.set_defaults(donotpropagate=True)

#  3.c. UPDATE statement.
parser_trk_update = subparser_trk.add_parser("update",
                                             parents=[update_parent, database_parser, loglevel_parser],
                                             description="Subparser for updating record(s) from `tracks` table.",
                                             argument_default=argparse.SUPPRESS)
parser_trk_update.add_argument("title", action=FormatTitle, help="Track title. Optional.")
parser_trk_update.add_argument("--donotformat", nargs="?", default=False, const=True, action=DoNotFormatTitle, help="Do not format track title. Optional.")

# ===============
# Main algorithm.
# ===============
if __name__ == '__main__':

    # -----
    TEMPLATE = TemplatingEnvironment(loader=jinja2.FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "AudioCD", "Tables")))
    TEMPLATE.set_environment(globalvars={"local": LOCAL,
                                         "utc": UTC},
                             filters={"readable": partial(readable, template=TEMPLATE4),
                                      "rjustify": rjustify})

    # -----
    arguments = parser.parse_args()

    # -----
    config = {}
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        config = yaml.load(fp)
    for logger in ["Applications.Database.AudioCD", "Applications.Database.DigitalAudioFiles", "Database"]:
        try:
            config["loggers"][logger]["level"] = arguments.loglevel.upper()
        except KeyError:
            pass
    logging.config.dictConfig(config)
    logger = logging.getLogger("Database.Interface")

    # -----
    for argument, value in sorted(vars(arguments).items()):
        logger.info("{0}: {1}".format(argument, value))

    # -----
    if arguments.template(arguments):
        if arguments.statement.lower() == "select":
            arguments.function = prettyprint(arguments.function)
        print(TEMPLATE.environment.get_template(arguments.template(arguments)).render(content=arguments.function(ns=arguments), mapping=ACTIONS.get(arguments.statement)))
        sys.exit(0)
    print("{0} record(s) {1}".format(arguments.function(ns=arguments), ACTIONS[arguments.statement]))
    sys.exit(0)
