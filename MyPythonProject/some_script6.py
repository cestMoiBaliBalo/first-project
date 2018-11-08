# -*- coding: utf-8 -*-
from contextlib import ExitStack
from itertools import compress, groupby, repeat
from operator import itemgetter
from typing import Any, Dict, Iterable, List, Tuple

from Applications.Tables.shared import DatabaseConnection
from Applications.shared import DATABASE


def get_albums(db: str = DATABASE) -> Iterable[Tuple[str, Tuple[str, int]]]:
    """

    :return:
    """
    collection, mapping = set(), {}  # type: Any, Dict[str, Tuple[str, int]]
    with ExitStack() as stack:
        conn = stack.enter_context(DatabaseConnection(db=db))
        collection = set(conn.execute("SELECT artistsort, albumid, discid, album FROM albums_vw ORDER BY artistsort, albumid, discid"))
    collection = sorted(sorted(sorted(sorted(collection, key=itemgetter(3)), key=itemgetter(2)), key=itemgetter(1)), key=itemgetter(0))

    for key, group in groupby(collection, key=lambda i: tuple(compress(i, [1, 1, 0, 1]))):
        _artistsort, _albumid, _album = key  # type: str, str, str
        _group = list(group)
        _totaldiscs = len(_group)  # type: int
        _albums = [f"{_artistsort} - {_album}"]  # type: List[str]
        _discs = [1]  # type: List[int]
        if _totaldiscs > 1:
            _albums = [f"{_artistsort} - {_album} - CD{discid}" for (discid,) in map(lambda i: tuple(compress(i, [0, 0, 1, 0])), _group)]
            _discs = [discid for (discid,) in map(lambda i: compress(i, [0, 0, 1, 0]), _group)]
        mapping.update(dict(zip(_albums, zip(repeat(_albumid), _discs))))

    for k, v in mapping.items():
        yield k, v


albums = dict(get_albums())
for album in sorted(albums):
    print(album)
for album in sorted(albums):
    print(album)
    print(albums[album])
