# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import calendar
import logging.config
import os
from datetime import date, datetime, time, timedelta
from typing import Optional

import yaml

from Applications.shared import LOCAL, UTC

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))


def toto(year: int, month: int, day: int, hour: int, minutes: int, seconds: int) -> Optional[datetime]:
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
        if message.lower() == "day is out of range for month":
            _, number_of_days = calendar.monthrange(year, month)  # type: int, int
            delta = day - number_of_days  # type: int
            return datetime.combine(date(year, month, number_of_days) + timedelta(days=delta), time(hour, minutes, seconds))
        else:
            raise
    else:
        return datobj


try:
    x = toto(2018, 2, 31, 22, 44, 15)
except ValueError as error:
    print(error)
else:
    print(LOCAL.localize(x).astimezone(UTC).replace(tzinfo=None))

# try:
#     x = toto(2018, 13, 31, 22, 44, 15)
# except ValueError as error:
#     print(error)
# else:
#     print(x)

# try:
#     x = toto(2018, 12, 31, 25, 44, 15)
# except ValueError as error:
#     print(error)
# else:
#     print(x)

try:
    x = toto(2018, 12, 31, 22, 44, 15)
except ValueError as error:
    print(error)
else:
    print(LOCAL.localize(x).astimezone(UTC).replace(tzinfo=None))

try:
    x = toto(2018, 12, 32, 22, 44, 15)
except ValueError as error:
    print(error)
else:
    print(LOCAL.localize(x).astimezone(UTC).replace(tzinfo=None))

try:
    x = toto(2018, 9, 31, 22, 44, 15)
except ValueError as error:
    print(error)
else:
    print(LOCAL.localize(x).astimezone(UTC).replace(tzinfo=None))
