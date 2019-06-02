# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# Frame generated with wxFormBuilder (version Jun 17 2015)
# http://www.wxformbuilder.org/
import functools
import logging
from collections import OrderedDict, defaultdict, deque
from datetime import date, datetime
from itertools import compress
from operator import itemgetter
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, Union

import wx  # type: ignore

from Applications.Tables.Albums.shared import bootlegalbums, defaultalbums
from Applications.Tables.RippedDiscs.shared import get_rippeddiscs
from Applications.shared import UTC, get_readabledate, localize_date, stringify, valid_datetime

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ==========
# Variables.
# ==========
boolean_to_string: Mapping[bool, str] = {False: "N", True: "Y"}


# ==========
# Functions.
# ==========
def adapt_ifnone(arg: Optional[str]) -> str:
    if arg is None:
        return ""
    return arg


def get_datetime(func):
    @functools.wraps
    def wrapper(timestamp: str) -> datetime:
        try:
            _, datobj, _ = func(timestamp)
        except ValueError:
            return UTC.localize(datetime.utcnow()).replace(microsecond=0, tzinfo=None)
        return datobj.astimezone(UTC).replace(microsecond=0, tzinfo=None)

    return wrapper


# ===========
# Decorators.
# ===========
# Allow `valid_datetime` function to return a single datetime objet localized into the UTC timezone.
adapt_timestamp = get_datetime(valid_datetime)


# ======
# Frame.
# ======
class ParentFrame(wx.Frame):
    _logger = logging.getLogger("{0}.ParentFrame".format(__name__))

    def __init__(self, parent, **kwargs) -> None:
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="Display tables content", pos=wx.DefaultPosition, size=wx.Size(1077, 541), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        # -----
        self._init_interface()

        # -----
        self._callables = kwargs["_CALLABLES"]
        self._classes = kwargs["_CLASSES"]
        self._dftsortfields = kwargs["_DFTSORTFIELDS"]
        self._displayedfields = kwargs["_DISPLAYEDFIELDS"]
        self._enabledfields = kwargs["_ENABLEDFIELDS"]
        self._fields = kwargs["_FIELDS"]
        self._headers = kwargs["_HEADERS"]
        self._mappings = kwargs["_MAPPINGS"]
        self._selectors = kwargs["_SELECTORS"]
        self._sizes = kwargs["_SIZES"]
        self._sortfields = kwargs["_SORTFIELDS"]
        self._tables = kwargs["_TABLES"]

        # -----
        self._database, self._path, self._table = None, None, None  # type: Optional[str], Optional[str], Optional[str]
        self._collections = {}
        self._collection = []
        self._record = OrderedDict()
        self._clicked = None  # type: Optional[int]
        self._clicks = defaultdict(int)  # type: Dict[int, int]
        self._column, self._columns, self._reverse = None, None, False  # type: Optional[int], Optional[List[int]], bool

    def _init_interface(self) -> None:
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        MainSizer = wx.BoxSizer(wx.VERTICAL)

        # --------------------------
        # Configure database picker.
        # --------------------------
        self.m_database = wx.Button(self, wx.ID_ANY, "Database", wx.DefaultPosition, wx.Size(70, 30), 0)
        self.m_database.SetMinSize(wx.Size(70, 30))
        MainSizer.Add(self.m_database, 0, wx.ALL, 5)

        # ----------------
        # Configure lists.
        # ----------------
        Sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.m_tables = wx.ListBox(self, wx.ID_ANY, wx.Point(-1, -1), wx.Size(200, -1), [], wx.LB_SINGLE)
        Sizer1.Add(self.m_tables, 0, wx.ALL | wx.EXPAND, 5)
        self.m_data = wx.ListCtrl(self, wx.ID_ANY, wx.Point(-1, -1), wx.DefaultSize, wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VRULES)
        Sizer1.Add(self.m_data, 1, wx.BOTTOM | wx.EXPAND | wx.RIGHT | wx.TOP, 5)

        # ------------------
        # Configure buttons.
        # ------------------
        Sizer2a = wx.BoxSizer(wx.HORIZONTAL)

        # --> CSV File.
        self.m_csv = wx.Button(self, wx.ID_ANY, "CSV File", wx.DefaultPosition, wx.Size(70, 30), 0)
        self.m_csv.Enable(False)
        Sizer2a.Add(self.m_csv, 0, wx.ALL, 5)

        # --> Refresh.
        self.m_refresh = wx.Button(self, wx.ID_ANY, "Refresh", wx.Point(-1, -1), wx.Size(70, 30), 0)
        self.m_refresh.Enable(False)
        Sizer2a.Add(self.m_refresh, 0, wx.ALL, 5)

        # --> Close.
        self.m_close = wx.Button(self, wx.ID_ANY, "Close", wx.Point(-1, -1), wx.Size(70, 30), 0)
        Sizer2a.Add(self.m_close, 0, wx.ALL, 5)

        # ------------------
        # Initialize layout.
        # ------------------
        Sizer2 = wx.BoxSizer(wx.VERTICAL)
        Sizer2.Add(Sizer2a, 0, wx.ALIGN_RIGHT, 5)
        MainSizer.Add(Sizer1, 1, wx.EXPAND, 0)
        MainSizer.Add(Sizer2, 0, wx.EXPAND, 5)
        self.SetSizer(MainSizer)
        self.Layout()
        self.Centre(wx.BOTH)

        # -----------------
        # Configure events.
        # -----------------
        self.m_database.Bind(wx.EVT_BUTTON, self._database)
        self.m_tables.Bind(wx.EVT_LISTBOX, self._table)
        self.m_data.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._record)
        self.m_refresh.Bind(wx.EVT_BUTTON, self._click_on_refresh)
        self.m_close.Bind(wx.EVT_BUTTON, self._click_on_close)
        self.m_csv.Bind(wx.EVT_BUTTON, self._click_on_csv)
        self.Bind(wx.EVT_LIST_COL_CLICK, self._header_onclick, self.m_data)

    def _load_collection(self, collection) -> None:
        """

        :return:
        """
        index = 0  # type: int
        collection = iter(collection)
        for item in collection:
            item = list(compress(item, self._selectors[self._table.lower()]))
            self.m_data.InsertItem(index, item[0])
            for column in range(1, self._number_of_fields):
                self.m_data.SetItem(index, column, adapt_ifnone(stringify(item[column])))
            index += 1

    def _set_clicks(self, column: int) -> bool:
        """

        :param column:
        :return:
        """
        reverse = False  # type: bool
        if self._clicked is not None:
            if self._clicked != column:
                for key in self._clicks:
                    self._clicks[key] = 0
        self._clicked = column
        self._clicks[column] += 1
        if self._clicks[column] == 2:
            reverse = True
            self._clicks[column] = 0
        return reverse

    def _database(self, event) -> None:
        """

        :param event:
        :return:
        """
        with wx.FileDialog(self, "Open database", wildcard="Database files (*.db)|*.db", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fd:
            if fd.ShowModal() == wx.ID_OK:
                self._path = fd.GetPath()
                self.m_data.DeleteAllItems()
                self.m_data.DeleteAllColumns()
                self.m_tables.Set([])
                self.m_tables.Set(self._tables.get(self._path, self._tables["default"]))
                self.m_csv.Enable(False)
                self.m_refresh.Enable(False)

    def _table(self, event) -> None:
        """

        :param event:
        :return:
        """
        self.m_data.DeleteAllItems()
        self.m_data.DeleteAllColumns()

        # Load configuration.
        self._table = self.m_tables.GetString(self.m_tables.GetSelection())
        self._number_of_fields = self._fields.get(self._table.lower(), 0)

        # Load headers.
        _headers = self._headers.get(self._table.lower(), [])  # type: List[str]
        for header in range(len(_headers)):
            self.m_data.InsertColumn(header, _headers[header])

        # Load data.
        column, columns = self._dftsortfields[self._table.lower()]  # type: int, List[int]
        collection = self._collections.get(self._table.lower(), [])
        if not collection:
            collection = list(self._get_collection(self._path, self._table.lower()))
        self._collections[self._table.lower()] = collection
        self._collection = list(self._sort_collection(collection, column, *columns))
        self._load_collection(self._collection)
        self._column, self._columns = column, columns

        # Enable buttons.
        self.m_csv.Enable(True)
        self.m_refresh.Enable(True)

    def _record(self, event) -> None:
        """

        :param event:
        :return:
        """
        _headers = deque(self._headers.get(self._table.lower(), []))
        _headers.appendleft("RowID")
        _headers.append("AlbumID")
        if self._table.lower() in ["rippeddiscs"]:
            _headers.append("DiscID")
        self._record = OrderedDict(zip(_headers, self._collection[self.m_data.GetNextSelected(-1)]))
        window = self._classes[self._table.lower()](parent=self)
        window.Show()
        self.Hide()

    def _click_on_close(self, event) -> None:
        """

        :param event:
        :return:
        """
        self.Close(True)

    def _click_on_refresh(self, event) -> None:
        """

        :param event:
        :return:
        """
        self.Close(True)

    def _click_on_csv(self, event) -> None:
        """

        :param event:
        :return:
        """
        self.Close(True)

    def _header_onclick(self, event) -> None:
        """

        :param event:
        :return:
        """
        column = event.GetColumn() + 1  # type: int

        # -----
        self._logger.debug(self._sortfields)
        self._logger.debug(self._table.lower())
        self._logger.debug(column)

        # -----
        columns = self._sortfields[self._table.lower()].get(str(column), self._sortfields[self._table.lower()]["default"])  # type: List[int]
        reverse = self._set_clicks(column)
        self.m_data.DeleteAllItems()
        self._collection = list(self._sort_collection(self._collection, column, *columns, reverse=reverse))
        self._load_collection(self._collection)
        self._column, self._columns, self._reverse = column, columns, reverse

    @staticmethod
    def _get_collection(database: str, table: str) -> Iterable[Tuple[Union[int, str], ...]]:
        """

        :param database:
        :param table:
        :return:
        """
        collection, table = set(), table.lower()
        if table == "albums":
            pass
        elif table == "defaultalbums":
            collection = set((album.album_rowid,
                              album.artistsort,
                              album.albumsort,
                              album.origyear,
                              album.year,
                              album.album,
                              album.label,
                              album.upc,
                              int(localize_date(album.created_date).timestamp()),
                              get_readabledate(album.created_date, tz=UTC),
                              album.genre,
                              album.support,
                              boolean_to_string[album.is_bootleg],
                              album.discid,
                              album.discs,
                              boolean_to_string[album.is_disc_live],
                              album.tracks,
                              album.albumid) for album in defaultalbums(db=database))
        elif table == "bootlegalbums":
            collection = set((album.album_rowid,
                              album.artistsort,
                              album.albumsort,
                              album.bootlegtrack_date,
                              album.bootlegtrack_city,
                              album.bootlegtrack_tour,
                              album.bootlegtrack_country,
                              int(localize_date(album.created_date).timestamp()),
                              get_readabledate(album.created_date, tz=UTC),
                              album.album,
                              album.genre,
                              album.support,
                              boolean_to_string[album.is_bootleg],
                              album.discid,
                              album.discs,
                              boolean_to_string[album.is_disc_live],
                              album.tracks,
                              album.albumid) for album in bootlegalbums(db=database))
        elif table == "rippeddiscs":
            collection = set((disc.rowid,
                              disc.artistsort,
                              disc.albumsort,
                              disc.disc,
                              int(localize_date(disc.ripped).timestamp()),
                              get_readabledate(disc.ripped, tz=UTC),
                              disc.ripped_year,
                              disc.ripped_month,
                              disc.album,
                              disc.genre,
                              boolean_to_string[disc.bootleg],
                              disc.tracks,
                              disc.albumid,
                              f"{disc.albumid}.D{disc.disc}") for disc in get_rippeddiscs(db=database))
        elif table == "playeddiscs":
            pass
        for item in collection:
            yield item

    @staticmethod
    def _sort_collection(collection, column: int, *columns: int, reverse: bool = False) -> Iterable[Tuple[Union[int, str], ...]]:
        """

        :param collection:
        :param column:
        :param columns:
        :param reverse:
        :return:
        """
        collection = iter(collection)
        for index in reversed(columns):
            collection = sorted(collection, key=itemgetter(index))
        collection = sorted(collection, key=itemgetter(column), reverse=reverse)
        for item in collection:
            yield item

    @property
    def database(self):
        return self._path

    @property
    def table(self):
        return self._table

    @property
    def collection(self):
        return self._collection

    @collection.setter
    def collection(self, arg):
        database, table, column, columns, reverse = arg
        collection = list(self._get_collection(database, table))
        self._collections[table.lower()] = collection
        self._collection = list(self._sort_collection(collection, column, *columns, reverse=reverse))

    @property
    def listctrl(self):
        return self.m_data

    @listctrl.setter
    def listctrl(self, arg):
        self._load_collection(arg)

    @property
    def column(self):
        return self._column

    @property
    def columns(self):
        return self._columns

    @property
    def record(self):
        return self._record

    @property
    def reverse(self):
        return self._reverse

    @property
    def callables(self):
        return self._callables

    @property
    def displayedfields(self):
        return self._displayedfields

    @property
    def enabledfields(self):
        return self._enabledfields

    @property
    def mappings(self):
        return self._mappings

    @property
    def sizes(self):
        return self._sizes


class Record(object):

    def __init__(self, parent):
        """

        :param parent: `ParentFrame` instance.
        """
        self.m_refresh = None
        self.m_delete = None
        self.m_update = None
        self.m_close = None

        # Get attributes from parent interface.
        self._parent = parent
        self._database = parent.database
        self._table = parent.table
        self._record = parent.record
        table = parent.table.lower()

        # Get configuration attributes.
        self._callable = parent.callables[table]
        self._displayedfields = parent.displayedfields[table]
        self._enabledfields = parent.enabledfields.get(table, {})
        self._mappings = parent.mappings.get(table, {})
        self._sizes = parent.sizes[table]

        # Set other attributes.
        self._albumid = parent.record["AlbumID"]
        self._discid = parent.record.get("DiscID")
        self._rowid = int(parent.record["RowID"])
        self._differences = set()  # type: Any
        self._data_before, self._data_after = {k.lower(): v for k, v in parent.record.items()}, {k.lower(): v for k, v in parent.record.items()}

    def _control_onchange(self, event):
        ctrl = event.GetEventObject()

        # TextCtrl control.
        try:
            value = ctrl.GetValue()

        # Choice control.
        except AttributeError:
            value = ctrl.GetString(ctrl.GetSelection())

        self._data_after[self._displayedfields[ctrl.GetId()]] = value
        enable = False
        self._differences = set(self._data_after.items()).difference(set(self._data_before.items()))
        if self._differences:
            enable = True
        self.m_update.Enable(enable)

    @staticmethod
    def _toto(field, **fields):
        if fields:
            return fields.get(field, False)
        return False

    @property
    def albumid(self):
        if self._discid is None:
            return self._albumid
        return self._discid

    @property
    def callable(self):
        return self._callable

    @property
    def data_after(self):
        return self._data_after

    @property
    def data_before(self):
        return self._data_before

    @property
    def database(self):
        return self._database

    @property
    def differences(self):
        return dict(self._differences)

    @property
    def displayedfields(self):
        return self._displayedfields

    @property
    def mappings(self):
        return self._mappings

    @property
    def parent(self):
        return self._parent

    @property
    def table(self):
        return self._table


class DefaultAlbumRecord(wx.Frame, Record):

    def __init__(self, parent) -> None:
        """

        :param parent: ParentFrame instance.
        """
        Record.__init__(self, parent)
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=f"{self._table}: record {self._rowid}", pos=wx.DefaultPosition, size=wx.Size(450, 496), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        self._init_interface(**self._record)

    def _init_interface(self, **data):
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetFont(wx.Font(9, 74, 90, 90, False, "Arial"))
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        MainSizer = wx.BoxSizer(wx.VERTICAL)
        bSizer1 = wx.FlexGridSizer(*self._sizes)
        bSizer1.AddGrowableCol(1)
        bSizer1.SetFlexibleDirection(wx.BOTH)
        bSizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        # ----------------------------------
        # Configure both texts and controls.
        # ----------------------------------

        # Artistsort
        self.m_artistsort = wx.StaticText(self, wx.ID_ANY, "ArtistSort", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_artistsort.Wrap(-1)
        bSizer1.Add(self.m_artistsort, 0, wx.ALL, 5)
        self.t_artistsort = wx.TextCtrl(self, 0, adapt_ifnone(stringify(data["ArtistSort"])), wx.DefaultPosition, wx.DefaultSize, 0)
        self.t_artistsort.Enable(self._toto("artistsort", **self._enabledfields))
        self.t_artistsort.Bind(wx.EVT_TEXT, self._control_onchange)
        bSizer1.Add(self.t_artistsort, 0, wx.ALL | wx.EXPAND, 5)

        # Albumsort
        self.m_albumsort = wx.StaticText(self, wx.ID_ANY, "AlbumSort", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_albumsort.Wrap(-1)
        bSizer1.Add(self.m_albumsort, 0, wx.ALL, 5)
        self.t_albumsort = wx.TextCtrl(self, 1, adapt_ifnone(stringify(data["AlbumSort"])), wx.DefaultPosition, wx.DefaultSize, 0)
        self.t_albumsort.Enable(self._toto("albumsort", **self._enabledfields))
        self.t_albumsort.Bind(wx.EVT_TEXT, self._control_onchange)
        bSizer1.Add(self.t_albumsort, 0, wx.ALL | wx.EXPAND, 5)

        # Origyear.
        self.m_origyear = wx.StaticText(self, wx.ID_ANY, "OrigYear", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_origyear.Wrap(-1)
        bSizer1.Add(self.m_origyear, 0, wx.ALL, 5)
        t_origyearChoices = list(map(str, range(1961, int(date.today().strftime("%Y")) + 1)))
        self.t_origyear = wx.Choice(self, 2, wx.DefaultPosition, wx.DefaultSize, t_origyearChoices, 0)
        self.t_origyear.SetSelection(t_origyearChoices.index(adapt_ifnone(stringify(data["OrigYear"]))))
        self.t_origyear.Enable(self._toto("origyear", **self._enabledfields))
        self.t_origyear.Bind(wx.EVT_CHOICE, self._control_onchange)
        bSizer1.Add(self.t_origyear, 0, wx.ALL | wx.EXPAND, 5)

        # Year.
        self.m_year = wx.StaticText(self, wx.ID_ANY, "Year", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_year.Wrap(-1)
        bSizer1.Add(self.m_year, 0, wx.ALL, 5)
        t_yearChoices = list(map(str, range(1961, int(date.today().strftime("%Y")) + 1)))
        self.t_year = wx.Choice(self, 3, wx.DefaultPosition, wx.DefaultSize, t_yearChoices, 0)
        self.t_year.SetSelection(t_yearChoices.index(adapt_ifnone(stringify(data["Year"]))))
        self.t_year.Enable(self._toto("year", **self._enabledfields))
        self.t_year.Bind(wx.EVT_CHOICE, self._control_onchange)
        bSizer1.Add(self.t_year, 0, wx.ALL | wx.EXPAND, 5)

        # Album.
        self.m_album = wx.StaticText(self, wx.ID_ANY, "Album", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_album.Wrap(-1)
        bSizer1.Add(self.m_album, 0, wx.ALL, 5)
        self.t_album = wx.TextCtrl(self, 4, adapt_ifnone(stringify(data["Album"])), wx.DefaultPosition, wx.DefaultSize, 0)
        self.t_album.Enable(self._toto("album", **self._enabledfields))
        self.t_album.Bind(wx.EVT_TEXT, self._control_onchange)
        bSizer1.Add(self.t_album, 0, wx.ALL | wx.EXPAND, 5)

        # Label.
        self.m_label = wx.StaticText(self, wx.ID_ANY, "Label", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_label.Wrap(-1)
        bSizer1.Add(self.m_label, 0, wx.ALL, 5)
        self.t_label = wx.TextCtrl(self, 5, adapt_ifnone(stringify(data["Label"])), wx.DefaultPosition, wx.DefaultSize, 0)
        self.t_artistsort.Enable(self._toto("label", **self._enabledfields))
        self.t_label.Bind(wx.EVT_TEXT, self._control_onchange)
        bSizer1.Add(self.t_label, 0, wx.ALL | wx.EXPAND, 5)

        # UPC.
        self.m_upc = wx.StaticText(self, wx.ID_ANY, "UPC", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_upc.Wrap(-1)
        bSizer1.Add(self.m_upc, 0, wx.ALL, 5)
        self.t_upc = wx.TextCtrl(self, 6, adapt_ifnone(stringify(data["UPC"])), wx.DefaultPosition, wx.DefaultSize, 0)
        self.t_upc.Enable(self._toto("upc", **self._enabledfields))
        self.t_upc.Bind(wx.EVT_TEXT, self._control_onchange)
        bSizer1.Add(self.t_upc, 0, wx.ALL | wx.EXPAND, 5)

        # Genre.
        self.m_genre = wx.StaticText(self, wx.ID_ANY, "Genre", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_genre.Wrap(-1)
        bSizer1.Add(self.m_genre, 0, wx.ALL, 5)
        self.t_genre = wx.TextCtrl(self, 7, adapt_ifnone(stringify(data["Genre"])), wx.DefaultPosition, wx.DefaultSize, 0)
        self.t_genre.Enable(self._toto("genre", **self._enabledfields))
        self.t_genre.Bind(wx.EVT_TEXT, self._control_onchange)
        bSizer1.Add(self.t_genre, 0, wx.ALL | wx.EXPAND, 5)

        # Discs.
        self.m_discs = wx.StaticText(self, wx.ID_ANY, "Discs", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_discs.Wrap(-1)
        bSizer1.Add(self.m_discs, 0, wx.ALL, 5)
        self.t_discs = wx.TextCtrl(self, 8, adapt_ifnone(stringify(data["Discs"])), wx.DefaultPosition, wx.DefaultSize, 0)
        self.t_discs.Enable(self._toto("discs", **self._enabledfields))
        self.t_discs.Bind(wx.EVT_TEXT, self._control_onchange)
        bSizer1.Add(self.t_discs, 0, wx.ALL | wx.EXPAND, 5)

        # ----------------------------------
        # Configure both buttons and events.
        # ----------------------------------
        # Common to all tables.
        bSizer3 = wx.BoxSizer(wx.HORIZONTAL)
        Buttons(parent=self, sizer=bSizer3)

        # ------------------
        # Initialize layout.
        # ------------------
        MainSizer.Add(bSizer1, 1, wx.ALL | wx.EXPAND, 15)
        bSizer2 = wx.BoxSizer(wx.VERTICAL)
        bSizer2.Add(bSizer3, 0, wx.ALIGN_RIGHT | wx.RIGHT, 15)
        MainSizer.Add(bSizer2, 0, wx.EXPAND | wx.TOP, 15)
        self.SetSizer(MainSizer)
        self.Layout()
        self.Centre(wx.BOTH)


class RippedDiscRecord(wx.Frame, Record):

    def __init__(self, parent) -> None:
        """

        :param parent: `ParentFrame` instance.
        """
        Record.__init__(self, parent)
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=f"{self._table}: record {self._rowid}", pos=wx.DefaultPosition, size=wx.Size(450, 496), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        self._init_interface(**self._record)

    def _init_interface(self, **data):
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetFont(wx.Font(9, 74, 90, 90, False, "Arial"))
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        MainSizer = wx.BoxSizer(wx.VERTICAL)
        bSizer1 = wx.FlexGridSizer(*self._sizes)
        bSizer1.AddGrowableCol(1)
        bSizer1.SetFlexibleDirection(wx.BOTH)
        bSizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        # ----------------------------------
        # Configure both texts and controls.
        # ----------------------------------
        index = 0  # type: int
        for k, v in data.items():
            if k.lower() in self._displayedfields:
                setattr(self, f"m_{k.lower()}", wx.StaticText(self, wx.ID_ANY, k, wx.DefaultPosition, wx.DefaultSize, 0))
                getattr(self, f"m_{k.lower()}").Wrap(-1)
                bSizer1.Add(getattr(self, f"m_{k.lower()}"), 0, wx.ALL, 5)
                setattr(self, f"t_{k.lower()}", wx.TextCtrl(self, index, adapt_ifnone(stringify(v)), wx.DefaultPosition, wx.DefaultSize, 0))
                getattr(self, f"t_{k.lower()}").Enable(self._toto(k.lower(), **self._enabledfields))
                getattr(self, f"t_{k.lower()}").Bind(wx.EVT_TEXT, self._control_onchange)
                bSizer1.Add(getattr(self, f"t_{k.lower()}"), 0, wx.ALL | wx.EXPAND, 5)
                index += 1

        # ----------------------------------
        # Configure both buttons and events.
        # ----------------------------------
        # Common to all tables.
        bSizer3 = wx.BoxSizer(wx.HORIZONTAL)
        Buttons(parent=self, sizer=bSizer3)

        # ------------------
        # Initialize layout.
        # ------------------
        MainSizer.Add(bSizer1, 1, wx.ALL | wx.EXPAND, 15)
        bSizer2 = wx.BoxSizer(wx.VERTICAL)
        bSizer2.Add(bSizer3, 0, wx.ALIGN_RIGHT | wx.RIGHT, 15)
        MainSizer.Add(bSizer2, 0, wx.EXPAND | wx.TOP, 15)
        self.SetSizer(MainSizer)
        self.Layout()
        self.Centre(wx.BOTH)


class Buttons(object):

    def __init__(self, parent, sizer):
        """

        :param parent: `DefaultAlbumRecord` or `RippedDiscRecord` instance.
        :param sizer: Sizer instance.
        """
        parent.m_refresh = wx.Button(parent, wx.ID_ANY, "Refresh", wx.DefaultPosition, wx.Size(70, 30), 0)
        sizer.Add(parent.m_refresh, 0, wx.BOTTOM | wx.LEFT | wx.TOP, 5)
        parent.m_refresh.Bind(wx.EVT_BUTTON, self._refreshbutton_onclick)

        parent.m_delete = wx.Button(parent, wx.ID_ANY, "Delete", wx.DefaultPosition, wx.Size(70, 30), 0)
        sizer.Add(parent.m_delete, 0, wx.BOTTOM | wx.LEFT | wx.TOP, 5)
        parent.m_delete.Bind(wx.EVT_BUTTON, self._deletebutton_onclick)

        parent.m_update = wx.Button(parent, wx.ID_ANY, "Update", wx.DefaultPosition, wx.Size(70, 30), 0)
        parent.m_update.Enable(False)
        sizer.Add(parent.m_update, 0, wx.BOTTOM | wx.LEFT | wx.TOP, 5)
        parent.m_update.Bind(wx.EVT_BUTTON, self._updatebutton_onclick)

        parent.m_close = wx.Button(parent, wx.ID_ANY, "Close", wx.DefaultPosition, wx.Size(70, 30), 0)
        parent.m_close.SetDefault()
        sizer.Add(parent.m_close, 0, wx.ALL, 5)
        parent.m_close.Bind(wx.EVT_BUTTON, self._click_on_close)

        self._parent = parent

    def _click_on_close(self, event):
        self._parent.parent.Show()
        self._parent.Destroy()

    def _deletebutton_onclick(self, event):
        self._parent.parent.Show()
        self._parent.Destroy()

    def _updatebutton_onclick(self, event):
        if self._parent.callable(self._parent.albumid, db=self._parent.database, **self._adapt_key()):
            self._parent.parent.collection = (self._parent.database, self._parent.table.lower(), self._parent.parent.column, self._parent.parent.columns, self._parent.parent.reverse)
        self._parent.parent.listctrl.DeleteAllItems()
        self._parent.parent.listctrl = self._parent.parent.collection
        self._parent.parent.Show()
        self._parent.Destroy()

    def _refreshbutton_onclick(self, event):
        for item in self._parent.displayedfields:
            item = item.lower()
            getattr(self._parent, f"t_{item}").SetValue(adapt_ifnone(stringify(self._parent.data_before[item])))
        self._parent.m_update.Enable(False)

    def _adapt_key(self):
        data_after = {}  # Dict[str, Any]
        for k, v in self._parent.differences.items():  # {unixtimestamp: "1234567890", origyear: "1985"}
            if k in self._parent.mappings:
                k, func = self._parent.mappings[k]
                v = func(v)
            data_after[k] = v
        return data_after


class Interface04(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition, size=wx.Size(426, 403), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        self._init_interface()
        self._insert, self._debug, self._console = False, True, True
        self._tags, self._database = None, None
        self._profile = "default"
        self._albums, self._bootlegs, self._run_clicked = True, False, False

    def _init_interface(self):
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetFont(wx.Font(9, 74, 90, 90, False, "Arial"))
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        MainBoxSizer = wx.BoxSizer(wx.VERTICAL)

        # -------------------
        # Configure controls.
        # -------------------
        Sizer1 = wx.FlexGridSizer(7, 2, 9, 25)
        Sizer1.AddGrowableCol(0)
        Sizer1.AddGrowableCol(1)
        Sizer1.SetFlexibleDirection(wx.BOTH)
        Sizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        # Audio tags file picker.
        self.m_AudioTags_Label = wx.StaticText(self, wx.ID_ANY, "Audio Tags File", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_AudioTags_Label.Wrap(-1)
        Sizer1.Add(self.m_AudioTags_Label, 0, wx.TOP, 15)
        self.m_AudioTags = wx.FilePickerCtrl(self, wx.ID_ANY, wx.EmptyString, "Select an audio tags JSON file", "*.json", wx.Point(-1, -1), wx.DefaultSize,
                                             wx.FLP_DEFAULT_STYLE | wx.FLP_FILE_MUST_EXIST | wx.FLP_OPEN)
        Sizer1.Add(self.m_AudioTags, 0, wx.TOP, 10)

        # Database picker.
        self.m_Database_Label = wx.StaticText(self, wx.ID_ANY, "Database", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_Database_Label.Wrap(-1)
        Sizer1.Add(self.m_Database_Label, 0, wx.TOP, 15)
        self.m_Database = wx.FilePickerCtrl(self, wx.ID_ANY, wx.EmptyString, "Select a database", "*.db", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE | wx.FLP_FILE_MUST_EXIST | wx.FLP_OPEN)
        Sizer1.Add(self.m_Database, 0, wx.TOP, 10)

        # Ripping profile choice box.
        self.m_Profile_Label = wx.StaticText(self, wx.ID_ANY, "Profile", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_Profile_Label.Wrap(-1)
        Sizer1.Add(self.m_Profile_Label, 0, wx.TOP, 15)
        m_ProfileChoices = ["default", "bootleg"]
        self.m_Profile = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_ProfileChoices, 0)
        self.m_Profile.SetSelection(0)
        Sizer1.Add(self.m_Profile, 0, wx.TOP, 10)

        # Albums radio button.
        self.m_Albums = wx.RadioButton(self, wx.ID_ANY, "Albums", wx.DefaultPosition, wx.DefaultSize, wx.RB_GROUP)
        Sizer1.Add(self.m_Albums, 0, wx.TOP, 10)

        # Bootlegs radio button.
        self.m_Bootlegs = wx.RadioButton(self, wx.ID_ANY, "Bootlegs", wx.DefaultPosition, wx.DefaultSize, 0)
        Sizer1.Add(self.m_Bootlegs, 0, wx.TOP, 10)

        # Debug checkbox.
        self.m_Debug = wx.CheckBox(self, wx.ID_ANY, "Debug", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_Debug.SetValue(True)
        Sizer1.Add(self.m_Debug, 0, wx.TOP, 10)

        # Console checkbox.
        self.m_Console = wx.CheckBox(self, wx.ID_ANY, "Console", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_Console.SetValue(True)
        Sizer1.Add(self.m_Console, 0, wx.TOP, 10)

        # Insert checkbox.
        self.m_Insert = wx.CheckBox(self, wx.ID_ANY, "Insert", wx.DefaultPosition, wx.DefaultSize, 0)
        Sizer1.Add(self.m_Insert, 0, wx.TOP, 10)
        self.m_Dummy = wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_Dummy.Wrap(-1)
        Sizer1.Add(self.m_Dummy, 0, wx.TOP, 10)

        # ------------------
        # Configure buttons.
        # ------------------
        Sizer3 = wx.BoxSizer(wx.HORIZONTAL)

        # Run.
        self.m_Run = wx.Button(self, wx.ID_ANY, "Run", wx.DefaultPosition, wx.Size(70, 30), 0)
        self.m_Run.SetDefault()
        Sizer3.Add(self.m_Run, 0, wx.RIGHT, 5)

        # Cancel.
        self.m_Cancel = wx.Button(self, wx.ID_ANY, "Cancel", wx.DefaultPosition, wx.Size(70, 30), 0)
        Sizer3.Add(self.m_Cancel, 0, wx.RIGHT, 5)

        # -----------------
        # Configure layout.
        # -----------------
        MainBoxSizer.Add(Sizer1, 1, wx.ALL | wx.EXPAND, 10)
        Sizer2 = wx.BoxSizer(wx.VERTICAL)
        Sizer2.Add(Sizer3, 0, wx.ALIGN_RIGHT | wx.BOTTOM, 15)
        MainBoxSizer.Add(Sizer2, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(MainBoxSizer)
        self.Layout()
        self.Centre(wx.BOTH)

        # -----------------
        # Configure events.
        # -----------------
        self.m_AudioTags.Bind(wx.EVT_FILEPICKER_CHANGED, self._audiotags_onchange)
        self.m_Database.Bind(wx.EVT_FILEPICKER_CHANGED, self._database)
        self.m_Profile.Bind(wx.EVT_CHOICE, self._profile_onchoice)
        self.m_Albums.Bind(wx.EVT_RADIOBUTTON, self._radio_oncheck)
        self.m_Bootlegs.Bind(wx.EVT_RADIOBUTTON, self._radio_oncheck)
        self.m_Insert.Bind(wx.EVT_CHECKBOX, self._box_oncheck)
        self.m_Debug.Bind(wx.EVT_CHECKBOX, self._box_oncheck)
        self.m_Console.Bind(wx.EVT_CHECKBOX, self._box_oncheck)
        self.m_Run.Bind(wx.EVT_BUTTON, self._run_onclick)
        self.m_Cancel.Bind(wx.EVT_BUTTON, self._cancel_onclick)

    def _audiotags_onchange(self, event):
        """

        :param event:
        :return:
        """
        self._tags = self.m_AudioTags.GetPath()

    def _database(self, event):
        """

        :param event:
        :return:
        """
        self._database = self.m_Database.GetPath()

    def _profile_onchoice(self, event):
        self._profile = self.m_Profile.GetString(self.m_Profile.GetCurrentSelection())

    def _radio_oncheck(self, event):
        """

        :param event:
        :return:
        """
        radio = event.GetEventObject()
        setattr(self, f"_{radio.GetLabel().lower()}", radio.GetValue())

    def _box_oncheck(self, event):
        """

        :param event:
        :return:
        """
        chkb = event.GetEventObject()
        setattr(self, f"_{chkb.GetLabel().lower()}", chkb.GetValue())

    def _run_onclick(self, event):
        """

        :param event:
        :return:
        """
        self._run_clicked = True
        self.Close(True)

    def _cancel_onclick(self, event):
        """

        :param event:
        :return:
        """
        self.Close(True)

    @property
    def albums(self):
        return self._albums

    @property
    def audiotags(self):
        return self._tags

    @property
    def bootlegs(self):
        return self._bootlegs

    @property
    def console(self):
        return self._console

    @property
    def database(self):
        return self._database

    @property
    def debug(self):
        return self._debug

    @property
    def insert(self):
        return self._insert

    @property
    def profile(self):
        return self._profile

    @property
    def run_clicked(self):
        return self._run_clicked
