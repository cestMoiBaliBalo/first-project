# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import logging.config
import os
from collections import OrderedDict
from functools import partial
from itertools import repeat

import yaml
from pandas import DataFrame
from pytz import timezone

from Applications.shared import TEMPLATE4, convert_timestamp, get_readabledate

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))

ZONES = ["US/Pacific",
         "US/Eastern",
         "UTC",
         "Europe/Paris",
         "Indian/Mayotte",
         "Asia/Tokyo",
         "Australia/Sydney"]

beg = 1537599800
end = 1537599895
get_readabledate = partial(get_readabledate, template=TEMPLATE4)

df = DataFrame(OrderedDict((tz, list(map(get_readabledate, map(convert_timestamp, range(beg, end + 1), repeat(timezone(tz)))))) for tz in ZONES))
df.to_csv(os.path.join(os.path.expandvars("%TEMP%"), "toto.csv"), sep="|", columns=ZONES)
