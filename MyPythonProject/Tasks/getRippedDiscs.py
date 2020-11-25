# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import itertools
import locale
import os
from functools import partial
from pathlib import Path

import pandas  # type: ignore

from Applications.Tables.RippedDiscs.shared import get_rippeddiscs
from Applications.shared import TEMPLATE6, UTF8, get_readabledate, localize_date

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent
_MYANCESTOR = _MYPARENT.parents[1]

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")

# ============
# Main script.
# ============
collection = [tuple(itertools.compress(item, [1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0])) for item in get_rippeddiscs()]
index, albumid, ripped_date, ripped_year, ripped_month, artist, albumsort, genre, application, disc, album, upc = zip(*collection)
series = {"Album ID": pandas.Series(albumid, index=index),
          "Artist": pandas.Series(artist, index=index),
          "Albumsort": pandas.Series(albumsort, index=index),
          "Disc": pandas.Series(disc, index=index),
          "Album": pandas.Series(album, index=index),
          "UPC": pandas.Series(upc, index=index),
          "Ripped Date": pandas.Series(map(partial(get_readabledate, template=TEMPLATE6), map(localize_date, ripped_date)), index=index),
          "Ripped Year": pandas.Series(ripped_year, index=index),
          "Ripped Month": pandas.Series(map(partial(get_readabledate, template="$month"), map(localize_date, ripped_date)), index=index),
          "Genre": pandas.Series(genre, index=index),
          "Application": pandas.Series(application, index=index)}
dataframe = pandas.DataFrame(series)
dataframe.index.name = "Record ID"
dataframe.to_csv(_MYANCESTOR / "rippeddiscs.csv", encoding=UTF8, sep="|")
