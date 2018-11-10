# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import logging.config
import os
from datetime import datetime
from itertools import compress
from operator import itemgetter
from typing import Iterable, Mapping, Tuple

import yaml

from Applications.Tables.RippedDiscs.shared import aggregate_rippeddiscs_by_genre, aggregate_rippeddiscs_by_month, get_rippeddiscs
from Applications.shared import DATABASE, LOCAL, UTC, format_date, format_collection, get_dataframe, print_collection

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))

boolean_to_string: Mapping[bool, str] = {False: "N", True: "Y"}


def get_collection(db: str = DATABASE):
    for disc in get_rippeddiscs(db=db):
        yield disc.artistsort, \
              disc.albumsort, \
              disc.album, \
              disc.disc, \
              disc.tracks, \
              disc.year_ripped, \
              disc.month_ripped, \
              format_date(UTC.localize(disc.ripped).astimezone(LOCAL)), \
              disc.genre, \
              boolean_to_string[disc.bootleg], \
              disc.ripped


def remove_rippeddate(iterable: Tuple[str, str, str, int, int, int, int, str, str, str, datetime]) -> Iterable[Tuple[str, str, str, int, int, int, int, str, str, str]]:
    for item in compress(iterable, [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0]):
        yield item


for item in print_collection(map(remove_rippeddate, sorted(get_collection(), key=itemgetter(10))), ["artistsort",
                                                                                                    "albumsort",
                                                                                                    "album",
                                                                                                    "disc",
                                                                                                    "tracks",
                                                                                                    "year",
                                                                                                    "month",
                                                                                                    "date",
                                                                                                    "genre",
                                                                                                    "bootleg"]):
    print(item)

print(get_dataframe(map(remove_rippeddate, sorted(get_collection(), key=itemgetter(10))), ["artistsort",
                                                                                           "albumsort",
                                                                                           "album",
                                                                                           "disc",
                                                                                           "tracks",
                                                                                           "year",
                                                                                           "month",
                                                                                           "date",
                                                                                           "genre",
                                                                                           "bootleg"]))

print(get_dataframe(sorted(sorted([(int(month[:4]), month[4:], total) for month, total in aggregate_rippeddiscs_by_month()], key=itemgetter(1)), key=itemgetter(0)), ["Year", "Month", "Total"]))
print(get_dataframe(sorted(sorted(aggregate_rippeddiscs_by_genre(), key=itemgetter(0)), key=itemgetter(1)), ["Genre", "Total"]))
print(get_dataframe(sorted(aggregate_rippeddiscs_by_genre(), key=itemgetter(0)), ["Genre", "Total"]))

for group in format_collection(map(remove_rippeddate, sorted(get_collection(), key=itemgetter(10)))):
    for item in filter(None, group):
        print("".join(item))

collection = get_dataframe(map(remove_rippeddate, sorted(get_collection(), key=itemgetter(10))), ["artistsort",
                                                                                                  "albumsort",
                                                                                                  "album",
                                                                                                  "disc",
                                                                                                  "tracks",
                                                                                                  "year",
                                                                                                  "month",
                                                                                                  "date",
                                                                                                  "genre",
                                                                                                  "bootleg"])
collection.to_csv(os.path.join(os.path.expandvars("%TEMP%"), "toto.csv"), sep="|", columns=["artistsort",
                                                                                            "albumsort",
                                                                                            "album",
                                                                                            "disc",
                                                                                            "tracks",
                                                                                            "year",
                                                                                            "month",
                                                                                            "date",
                                                                                            "genre",
                                                                                            "bootleg"])
