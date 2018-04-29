# -*- coding: utf-8 -*-
import datetime
import logging.config
import os
import sys

import yaml

from Applications.shared import LOCAL, UTC, validdatetime

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))


def some_function(ts):
    try:
        result = validrippeddate(validdatetime)(ts)
    except ValueError:
        raise
    else:
        return result


def validrippeddate(func):
    def wrapper(ts):
        try:
            result = func(ts)
        except ValueError:
            raise
        else:
            return result[0]

    return wrapper


print("# ========== #")
try:
    a, b, c = validdatetime(sys.argv[1])
except ValueError:
    print("Erreur!")
else:
    print(a)
    print(b)
    print(LOCAL.localize(b).astimezone(UTC))
    print(c)
    print(c.tm_year)

print("# ========== #")
try:
    a, b, c = validdatetime(datetime.datetime(2018, 3, 14, 5, 55, 23, tzinfo=UTC))
except ValueError:
    print("Erreur!")
else:
    print(a)
    print(b)
    print(b.astimezone(LOCAL))
    print(c.tm_year)

print("# ========== #")
try:
    a, b, c = validdatetime(datetime.datetime(2018, 3, 14, 6, 55, 23))
except ValueError:
    print("Erreur!")
else:
    print(a)
    print(b)
    print(LOCAL.localize(b).astimezone(UTC))
    print(c.tm_year)

print("# ========== #")
try:
    a, b, c = validdatetime(152100692312345)
except ValueError:
    print("Erreur!")
else:
    print(a)
    print(b)
    print(LOCAL.localize(b).astimezone(UTC))
    print(c.tm_year)

print("# ========== #")
try:
    result = some_function(1521149245)
except ValueError as err:
    print(err)
else:
    print(result)

print("# ========== #")
try:
    result = some_function("AAAAAAAAAA")
except ValueError as err:
    print(err)
else:
    print(result)
