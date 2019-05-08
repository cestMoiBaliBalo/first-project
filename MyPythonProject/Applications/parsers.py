# -*- coding: utf-8 -*-
import argparse
import operator

from . import shared

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# =================
# Global Functions.
# =================
def unixtime(timestamp) -> int:
    """

    :param timestamp:
    :return:
    """
    try:
        _unixtime = shared.valid_datetime(timestamp)
    except ValueError as err:
        raise argparse.ArgumentTypeError(err)
    return _unixtime[0]


def database(db: str) -> str:
    """

    :param db:
    :return:
    """
    try:
        _database = shared.valid_database(db)
    except ValueError as err:
        raise argparse.ArgumentTypeError(err)
    return _database


#     =========
#  1. PARSER 1.
#     =========
zipfile = argparse.ArgumentParser()
zipfile.add_argument("source", type=shared.valid_path)
zipfile.add_argument("destination", choices=["documents", "backup", "temp", "onedrive"], action=shared.GetPath)
subparsers = zipfile.add_subparsers()

# Singled extensions.
parser1_s = subparsers.add_parser("singled")
parser1_s.add_argument("extensions", nargs="+")

# Grouped extensions.
parser1_g = subparsers.add_parser("grouped")
parser1_g.add_argument("group", nargs="+", choices=["documents", "computing"], action=shared.GetExtensions)
group = parser1_g.add_mutually_exclusive_group()
group.add_argument("-e", "--excl", dest="exclude", nargs="*", action=shared.ExcludeExtensions, help="exclude enumerated extension(s)")
group.add_argument("-k", "--keep", nargs="*", action=shared.KeepExtensions, help="exclude all extensions but enumerated extension(s)")
parser1_g.add_argument("-i", "--incl", dest="include", nargs="*", action=shared.IncludeExtensions, help="include enumerated extension(s)")

#     =========
#  2. PARSER 2.
#     =========
epochconverter = argparse.ArgumentParser()
epochconverter.add_argument("beg", help="Beginning epoch", type=unixtime)
epochconverter.add_argument("end", help="End epoch", type=unixtime, nargs="?", action=shared.SetEndSeconds)
epochconverter.add_argument("-z", "--zone", help="Time zone", default=shared.DFTTIMEZONE)

#     =========
#  3. PARSER 3.
#     =========
database_parser = argparse.ArgumentParser(description="Shared parser for database arguments.", add_help=False)
group = database_parser.add_mutually_exclusive_group()
group.add_argument("--database", nargs="?", default=shared.DATABASE, help="Path to database storing digital albums.", type=database, dest="db")
group.add_argument("-t", "--test", nargs="?", default=False, const=True, action=shared.SetDatabase, help="Use test database.")

#     =========
#  5. PARSER 5.
#     =========
loglevel_parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS, add_help=False)
loglevel_parser.add_argument("--loglevel", help="Log level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])

#     =========
#  6. PARSER 6.
#     =========
subset_parser = argparse.ArgumentParser(parents=[database_parser], argument_default=argparse.SUPPRESS)
subset_parser.add_argument("--artistsort", nargs="*", help="Subset digital albums by artistsort.")
subset_parser.add_argument("--albumsort", nargs="*", help="Subset digital albums by albumsort.")
subset_parser.add_argument("--artist", nargs="*", help="Subset digital albums by artist.")

#     =========
#  7. PARSER 7.
#     =========
tasks_parser = argparse.ArgumentParser()
tasks_parser.set_defaults(table="tasks")
tasks_parser.set_defaults(debug=True)
tasks_parser.add_argument("taskid", type=int)
subparser1 = tasks_parser.add_subparsers(dest="action")
parser_check = subparser1.add_parser("check", argument_default=argparse.SUPPRESS, parents=[database_parser])
parser_check.add_argument("--delta", default="10", type=int)
parser_update = subparser1.add_parser("update", argument_default=argparse.SUPPRESS, parents=[database_parser])
group = parser_update.add_mutually_exclusive_group()
group.add_argument("--timestamp", type=int)
group.add_argument("--datstring")
subparser2 = parser_update.add_subparsers(dest="operation")
parser_add = subparser2.add_parser("add", argument_default=argparse.SUPPRESS)
parser_add.set_defaults(func=operator.add)
parser_add.add_argument("days", type=int)
parser_sub = subparser2.add_parser("sub", argument_default=argparse.SUPPRESS)
parser_sub.set_defaults(func=operator.sub)
parser_sub.add_argument("days", type=int)

#     =========
#  8. PARSER 8.
#     =========

# --------------
# Parent parser.
# --------------
# images_pparser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS, add_help=False)
# images_pparser.add_argument("files", nargs="+", help="Source directories or images")
# images_pparser.add_argument("--ext", nargs="*", dest="extensions", default=["jpg"])
# images_pparser.add_argument("--test", action="store_true")

# -------------
# Child parser.
# -------------
# images_cparser = argparse.ArgumentParser()
# subparser = images_cparser.add_subparsers(dest="script")

# --> Rename images.
# images_rename = subparser.add_parser("rename", argument_default=argparse.SUPPRESS, parents=[images_pparser, loglevel_parser])
# images_rename.add_argument("--index", default="1", type=int, help="Starting index")

# --> Write tags.
# images_write = subparser.add_parser("write", argument_default=argparse.SUPPRESS, parents=[images_pparser, loglevel_parser])
# images_write.add_argument("--city")
# images_write.add_argument("--location")
# images_write.add_argument("--keywords", nargs="*")
# images_write.add_argument("--copyright", action="store_true")

# --> Read tags.
# images_read = subparser.add_parser("read", argument_default=argparse.SUPPRESS, parents=[images_pparser, loglevel_parser])

#     =========
#  9. PARSER 9.
#     =========
# foldercontent = argparse.ArgumentParser()
# subparser = foldercontent.add_subparsers(dest="command")

# -----
# parser1 = subparser.add_parser("1")
# parser1.add_argument("extensions", nargs="*", help="only given extensions. Facultative", default=[])

# -----
# parser2 = subparser.add_parser("2")
# parser2.add_argument("group", nargs="+", choices=["computing", "documents", "lossless", "lossy", "music"], action=shared.GetExtensions)
# group = parser2.add_mutually_exclusive_group()
# group.add_argument("-e", "--excl", dest="exclude", nargs="*", action=shared.ExcludeExtensions, help="exclude enumerated extension(s)")
# group.add_argument("-k", "--keep", nargs="*", action=shared.KeepExtensions, help="exclude all extensions but enumerated extension(s)")
# parser2.add_argument("-i", "--incl", dest="include", nargs="*", action=shared.IncludeExtensions, help="include enumerated extension(s)")

# -----
# parser3 = subparser.add_parser("3")
# parser3.add_argument("extensions", nargs="+", help="excluded extensions. Mandatory.")

#     ==========
# 10. PARSER 10.
#     ==========
tags_grabber = argparse.ArgumentParser()
tags_grabber.add_argument("source", help="UTF-16-LE encoded TXT audio tags file", type=argparse.FileType(mode="r+", encoding="UTF_16LE"))
tags_grabber.add_argument("profile", help="ripping profile", choices=["default", "bootleg"])
tags_grabber.add_argument("decorators", nargs="*", help="decorating profile(s)")
tags_grabber.add_argument("--tags_processing", nargs="?", default="no_tags_processing", help="audio tags processing profile")
