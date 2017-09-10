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
from functools import partial
from itertools import chain, groupby, repeat

import jinja2
import yaml

from Applications.Database.AudioCD.shared import deletelog, insertfromargs, selectlog, selectlogs, updatelog, validproductcode, validyear
from Applications.Database.DigitalAudioFiles.shared import deletealbum, \
    deletealbumheader, \
    getalbumdetail, \
    getalbumheader, \
    getalbumid, \
    updatealbum
from Applications.Database.shared import Boolean
from Applications.shared import DATABASE, \
    DFTDAYREGEX, \
    DFTMONTHREGEX, \
    DFTYEARREGEX, \
    LOCAL, \
    TEMPLATE4, \
    TemplatingEnvironment, \
    UTC, \
    readable, \
    validunixepochtime

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# ===========
# Decorators.
# ===========
def deco1(func):
    def wrapper(*args, db):
        albums = chain.from_iterable([[album.albumid for album in genobj] for genobj in map(func, args, repeat(db))])
        return list(chain.from_iterable([[row for row in genobj] for genobj in [getalbumheader(db=db, albumid=album) for album in albums]]))

    return wrapper


def deco2(func):
    def wrapper(*args, db):
        return list(map(func, repeat(db), args))

    return wrapper


def deco3(func):
    def wrapper(*rowid, db):
        def myfilter(item):
            return item.rowid in rowid

        mylist = filter(myfilter, func(db))
        return [(k, [(k, list(g)) for k, g in groupby(list(g), key=lambda i: i.discid)]) for k, g in groupby(mylist, key=lambda i: i.albumid)]

    return wrapper


def deco4(func):
    def wrapper(db):
        return [(k, [(k, list(g)) for k, g in groupby(list(g), key=lambda i: i.discid)]) for k, g in groupby(func(db), key=lambda i: i.albumid)]

    return wrapper


def deco5(func):
    def wrapper(*args, db, **kwargs):
        mylist = list()
        for arg in args:
            mylist.append(func(arg, db, **kwargs))
        return mylist

    return wrapper


# ==========
# Functions.
# ==========
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
                        False: "T04",
                        True: "T02"
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
            }
    }
    if args.table in templates:
        if args.statement in templates[args.table]:
            if args.donotpropagate in templates[args.table][args.statement]:
                return templates[args.table][args.statement][args.donotpropagate]
    return None


def albumsort(stg):
    """
    Check if a string match the albumsort pattern.

    :param stg: String.
    :return: Input string if match successes. Exception if match fails.
    """
    match1 = re.match(r"^[12]\.({0})({1})({2})\.\d$".format(DFTYEARREGEX, DFTMONTHREGEX, DFTDAYREGEX), stg)
    match2 = re.match(r"^[12]\.({0})0000\.\d$".format(DFTYEARREGEX), stg)
    if any([match1, match2]):
        return stg
    raise argparse.ArgumentTypeError('"{0}" isn\'t a correct albumsort tag.'.format(stg))


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
        del pairs["db"]
        del pairs["table"]
        del pairs["statement"]
        if "function" in pairs:
            del pairs["function"]
        if "template" in pairs:
            del pairs["template"]
        if pairs:
            return CONFIGURATION[table][statement](db=db, **pairs)
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
        return list(getfunction(table, statement, donotpropagate, bool(rowid))(*rowid, db=db))
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
    logger = logging.getLogger("Interface.update_func")
    pairs = dict(kwargs)
    if ns:
        pairs = {k: v for k, v in vars(ns).items()}
    db = pairs.get("db")
    table = pairs.get("table")
    statement = pairs.get("statement")
    donotpropagate = pairs.get("donotpropagate", False)
    rowid = pairs.get("rowid", [])
    if all([db, table, statement, rowid]):
        del pairs["db"]
        del pairs["table"]
        del pairs["statement"]
        del pairs["donotpropagate"]
        del pairs["rowid"]
        if "function" in pairs:
            del pairs["function"]
        if "template" in pairs:
            del pairs["template"]
        if pairs:
            logger.debug(pairs)
            return getfunction(table, statement, donotpropagate, bool(rowid))(*rowid, db=db, **pairs)
    return DEFAULT.get(table, DEFAULT["default"])


def boolean(stg):
    return Boolean(stg)


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
            "insert": insertfromargs
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
                            True: deco3(getalbumdetail),
                            False: deco4(getalbumdetail)
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
                            True: deco2(deletealbum)
                        }
                },
            "update":
                {
                    True:
                        {
                            True: deco5(updatealbum)
                        },
                    False:
                        {
                            True: deco5(updatealbum)
                        }
                }
        }
}
DEFAULT = {
    "default": 0,
    "albums": [("", 0, 0, 0)]
}
MAPPING = {
    "insert": "inserted",
    "delete": "deleted",
    "update": "updated",
}

# ===============
# Parent parsers.
# ===============

# -----
select_parent = argparse.ArgumentParser(description="Shared parser for `select` subparsers.", add_help=False)
select_parent.set_defaults(function=select_func)
select_parent.set_defaults(template=gettemplate)
select_parent.add_argument("rowid", nargs="*", type=int, help="List of rows IDs to be selected. Optional.")

# -----
delete_parent = argparse.ArgumentParser(description="Shared parser for `delete` subparsers.", add_help=False)
delete_parent.set_defaults(function=delete_func)
delete_parent.set_defaults(template=gettemplate)
delete_parent.add_argument("rowid", nargs="+", type=int, help="List of rows IDs to be deleted. Mandatory.")

# -----
update_parent = argparse.ArgumentParser(description="Shared parser for `update` subparsers.", add_help=False, argument_default=argparse.SUPPRESS)
update_parent.set_defaults(function=update_func)
update_parent.set_defaults(template=gettemplate)
update_parent.set_defaults(donotpropagate=True)
update_parent.add_argument("rowid", nargs="+", type=int, help="List of rows IDs to be updated. Mandatory.")
update_parent.add_argument("--artist", help="Album artist. Optional.", metavar="The Artist")
update_parent.add_argument("--year", type=validyear, help="Album year. Optional. Only integers are allowed.")
update_parent.add_argument("--album", help="Album. Optional.", metavar="The Album")
update_parent.add_argument("--genre", choices=["Rock", "Hard Rock", "Progressive Rock", "Alternative Rock", "Heavy Metal", "Black Metal", "French Pop"], help="Album genre. Optional.")

# -----
database = argparse.ArgumentParser(description="Shared parser for database argument.", add_help=False)
database.add_argument("--database", dest="db", default=DATABASE, help="Path to database storing maintained tables.")

# =================
# Arguments parser.
# =================

#     ------------
#  0. Main parser.
#     ------------
parser = argparse.ArgumentParser(usage="Command line application for tables maintenance.",
                                 description="Allow both `rippinglog` and `albums` maintenance thanks to a command line interface.",
                                 allow_abbrev=False,
                                 argument_default=argparse.SUPPRESS)
subparser = parser.add_subparsers(dest="table")

#     --------------------------------
#  1. Parser for `rippinglog` command.
#     --------------------------------
parser_log = subparser.add_parser("rippinglog", description="Subparser for `rippinglog` maintenance.")
subparser_log = parser_log.add_subparsers(dest="statement")

#  1.a. SELECT statement.
parser_log_select = subparser_log.add_parser("select", parents=[select_parent, database], description="Subparser for selecting record(s) from `rippinglog` table.")
parser_log_select.set_defaults(donotpropagate=True)

#  1.b. DELETE statement.
parser_log_delete = subparser_log.add_parser("delete", parents=[delete_parent, database], description="Subparser for deleting record(s) from `rippinglog` table.")
parser_log_delete.set_defaults(donotpropagate=True)

#  1.c. UPDATE statement.
parser_log_update = subparser_log.add_parser("update", parents=[update_parent, database], description="Subparser for updating record(s) from `rippinglog` table.", argument_default=argparse.SUPPRESS)
parser_log_update.add_argument("--artistsort", help="Album artistsort key. Optional.", metavar="Artist, The")
parser_log_update.add_argument("--albumsort", type=albumsort, help="Album albumsort key. Optional.", metavar="1.20170000.1")
parser_log_update.add_argument("--upc", type=validproductcode, help="Album product code. Optional.")
parser_log_update.add_argument("--application", help="Ripping application. Optional.")
parser_log_update.add_argument("--ripped", type=validunixepochtime, help="Ripping local Unix epoch time. Optional.", metavar="1500296048")

#  1.d. INSERT statement.
parser_log_insert = subparser_log.add_parser("insert", parents=[database], description="Subparser for inserting record(s) into `rippinglog` table.", argument_default=argparse.SUPPRESS)
parser_log_insert.set_defaults(function=insert_func)
parser_log_insert.set_defaults(template=gettemplate)
parser_log_insert.add_argument("artistsort", help="Album artistsort. Mandatory.", metavar="Artist, The")
parser_log_insert.add_argument("albumsort", type=albumsort, help="Album albumsort. Mandatory.", metavar="1.20170000.1")
parser_log_insert.add_argument("artist", help="Album artist. Mandatory.", metavar="The Artist")
parser_log_insert.add_argument("year", type=validyear, help="Album year. Mandatory. Only integers are allowed.")
parser_log_insert.add_argument("album", help="Album. Mandatory.", metavar="The Album")
parser_log_insert.add_argument("genre", choices=["Rock", "Hard Rock", "Progressive Rock", "Alternative Rock", "Heavy Metal", "Black Metal", "French Pop"], help="Album genre. Mandatory.")
parser_log_insert.add_argument("upc", type=validproductcode, help="Album product code. Mandatory.")
parser_log_insert.add_argument("--application", nargs="?", default="dBpoweramp 15.1", help="Ripping application. Optional.")
parser_log_insert.add_argument("--ripped", type=validunixepochtime, help="Ripping local Unix epoch time. Optional.", metavar="1500296048")

#     ----------------------------
#  2. Parser for `albums` command.
#     ----------------------------
parser_alb = subparser.add_parser("albums", description="Subparser for `albums` maintenance.")
subparser_alb = parser_alb.add_subparsers(dest="statement")

#  2.a. SELECT statement.
parser_alb_select = subparser_alb.add_parser("select", parents=[select_parent, database], description="Subparser for selecting record(s) from `albums` table.")
parser_alb_select.add_argument("--donotpropagate", nargs="?", default=False, const=True)

#  2.b. DELETE statement.
parser_alb_delete = subparser_alb.add_parser("delete", parents=[delete_parent, database], description="Subparser for deleting record(s) from `albums` table.")
parser_alb_delete.add_argument("--donotpropagate", nargs="?", default=False, const=True)

#  2.c. UPDATE statement.
parser_alb_update = subparser_alb.add_parser("update", parents=[update_parent, database], description="Subparser for updating record(s) from `albums` table.", argument_default=argparse.SUPPRESS)
alb_update_group = parser_alb_update.add_mutually_exclusive_group()
parser_alb_update.add_argument("--albumid", help="Album unique ID. Optional.", metavar="Artist, The.1.20170000.1")
parser_alb_update.add_argument("--live", type=boolean, help="Live album. Optional.")
parser_alb_update.add_argument("--bootleg", type=boolean, help="Bootleg album. Optional.")
parser_alb_update.add_argument("--incollection", type=boolean, help="Album in personal collection. Optional.")
parser_alb_update.add_argument("--upc", type=validproductcode, help="Album product code. Optional.")
parser_alb_update.add_argument("--played", type=validunixepochtime, help="Album last played UTC Unix epoch time. Optional.", metavar="1500296048")
alb_update_group.add_argument("--count", type=int, help="Album played counter. Optional.")
alb_update_group.add_argument("--icount", action="store_true", help="Increment played counter by 1. Optional.")
alb_update_group.add_argument("--dcount", action="store_true", help="Decrement played counter by 1. Optional.")

# ===============
# Main algorithm.
# ===============
if __name__ == '__main__':

    # -----
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        logging.config.dictConfig(yaml.load(fp))

    # -----
    TEMPLATE = TemplatingEnvironment(loader=jinja2.FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "AudioCD", "Tables")))
    TEMPLATE.set_environment(globalvars={"local": LOCAL,
                                         "utc": UTC},
                             filters={"readable": partial(readable, template=TEMPLATE4)})

    # -----
    arguments = parser.parse_args()

    # -----
    if arguments.template(arguments):
        print(TEMPLATE.environment.get_template(arguments.template(arguments)).render(content=arguments.function(ns=arguments), mapping=MAPPING.get(arguments.statement)))
        sys.exit(0)
    print("{0} record(s) {1}".format(arguments.function(**{key: val for key, val in vars(arguments).items() if val}), MAPPING[arguments.statement]))
    sys.exit(0)
