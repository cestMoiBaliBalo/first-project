# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import operator
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterator

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent


# ================
# Local functions.
# ================
def timedelta_(datobj: date = date.today(), days: int = 0, kallable=operator.add) -> Iterator[Any]:
    result = kallable(datobj, timedelta(days=days))
    yield result
    yield result.isoformat()
    yield result.strftime("%A")
    yield result.isoweekday()
    yield result.isocalendar()[1]


# ============
# Main script.
# ============
if __name__ == "__main__":

    import argparse
    import locale
    from itertools import islice, tee

    import holidays  # type: ignore
    from dateutil.parser import parse  # type: ignore


    class SetDate(argparse.Action):
        """
        Undocumented.
        """

        def __init__(self, option_strings, dest, **kwargs):
            super(SetDate, self).__init__(option_strings, dest, **kwargs)

        def __call__(self, parsobj, namespace, values, option_string=None):
            setattr(namespace, self.dest, parse(values))


    locale.setlocale(locale.LC_ALL, "")

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today(), action=SetDate)
    parser.add_argument("days", type=int)
    subparsers = parser.add_subparsers(dest="operation")
    parser_add = subparsers.add_parser("add")
    parser_add.set_defaults(func=operator.add)
    parser_sub = subparsers.add_parser("sub")
    parser_sub.set_defaults(func=operator.sub)

    arguments = parser.parse_args()
    iterator = timedelta_(datobj=arguments.date, days=arguments.days, kallable=arguments.func)
    iter1, iter2, iter3 = tee(iterator, 3)
    for item in islice(iter1, 1):
        print(item.strftime("%A %d/%m/%Y"))
    for item in islice(iter2, 1, None):
        print(item)
    fr_holidays = holidays.France()
    (new_date,) = tuple(islice(iter3, 1))
    print(new_date in fr_holidays)
