# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# Frame generated with wxFormBuilder (version Jun 17 2015)
# http://www.wxformbuilder.org/
import datetime
import locale
import os
from collections import OrderedDict
from collections.abc import MutableMapping
from contextlib import ExitStack
from functools import partial
from itertools import compress, groupby, repeat
from operator import itemgetter
from typing import Any, Iterable, List, Optional, Tuple

import wx  # type: ignore

from Applications.Tables.Albums.shared import update_playeddisccount
from Applications.Tables.shared import DatabaseConnection
from Applications.shared import DATABASE, LOCAL, UTC, adjust_datetime

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


class DigitalAlbums(MutableMapping):

    def __init__(self, db: str = DATABASE) -> None:
        self._mapping = OrderedDict()  # type: MutableMapping[str, Tuple[str, int]]
        with ExitStack() as stack:
            conn = stack.enter_context(DatabaseConnection(db=db))
            collection = set(conn.execute("SELECT artistsort, albumid, discid, album FROM albums_vw ORDER BY artistsort, albumid, discid"))  # type: Any
            collection = sorted(collection, key=itemgetter(3))
            collection = sorted(collection, key=itemgetter(2))
            collection = sorted(collection, key=itemgetter(1))
            collection = sorted(collection, key=itemgetter(0))
        for key, group in groupby(collection, key=partial(compress_, [1, 1, 0, 1])):
            _artistsort, _albumid, _album = key  # type: str, str, str
            _group = list(group)
            _totaldiscs = len(_group)  # type: int
            _albums = [f"{_artistsort} - {_album}"]  # type: List[str]
            _discs = [1]  # type: List[int]
            if _totaldiscs > 1:
                _albums = [f"{_artistsort} - {_album} - CD{discid}" for (discid,) in map(partial(compress_, [0, 0, 1, 0]), _group)]
                _discs = [discid for (discid,) in map(partial(compress_, [0, 0, 1, 0]), _group)]
            self._mapping.update(dict(zip(_albums, zip(repeat(_albumid), _discs))))

    def __delitem__(self, key):
        del self._mapping[key]

    def __getitem__(self, key):
        return self._mapping[key]

    def __iter__(self):
        return iter(self._mapping.items())

    def __len__(self):
        return len(self._mapping)

    def __setitem__(self, key, arg):
        self._mapping[key] = arg


def compress_(selectors, iterable):
    return tuple(compress(iterable, selectors))


# ======
# Frame.
# ======
class MainFrame(wx.Frame):
    MONTHS = sorted(item.zfill(2) for item in map(str, range(1, 13)))
    DAYS = sorted(item.zfill(2) for item in map(str, range(1, 32)))
    HOURS = sorted(item.zfill(2) for item in map(str, range(0, 24)))
    MINUTES = sorted(item.zfill(2) for item in map(str, range(0, 60)))
    SECONDS = sorted(item.zfill(2) for item in map(str, range(0, 60)))

    def __init__(self, parent) -> None:
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="Digital Albums", pos=wx.DefaultPosition, size=wx.Size(866, 519), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        self._database = None  # type: Optional[str]
        self._total_albums = 0  # type: int
        self._init_interface()
        self._reset_interface()
        self._set_statusbar("Choose database.", "")
        self.Layout()

    def _init_interface(self) -> None:
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetFont(wx.Font(9, 74, 90, 90, False, "Arial"))
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        MainSizer = wx.BoxSizer(wx.VERTICAL)

        # ---------
        # Database.
        # ---------
        self.database = wx.Button(self, wx.ID_ANY, "Database", wx.DefaultPosition, wx.Size(70, 30), 0)
        MainSizer.Add(self.database, 0, wx.BOTTOM | wx.LEFT | wx.TOP, 10)

        # -------
        # Albums.
        # -------
        Sizer1 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Discs"), wx.HORIZONTAL)
        self.albums = wx.CheckListBox(Sizer1.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(-1, -1), [], 0)
        Sizer1.Add(self.albums, 1, wx.ALL | wx.EXPAND, 5)

        # ------------
        # Played date.
        # ------------
        Sizer2 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Date"), wx.VERTICAL)
        Sizer2a = wx.FlexGridSizer(2, 7, 5, 5)
        Sizer2a.SetFlexibleDirection(wx.BOTH)
        Sizer2a.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        # --> Year header.
        self.m_staticText1 = wx.StaticText(Sizer2.GetStaticBox(), wx.ID_ANY, "Year", wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.m_staticText1.Wrap(-1)
        Sizer2a.Add(self.m_staticText1, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # --> Month header.
        self.m_staticText2 = wx.StaticText(Sizer2.GetStaticBox(), wx.ID_ANY, "Month", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText2.Wrap(-1)
        Sizer2a.Add(self.m_staticText2, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # --> Day header.
        self.m_staticText3 = wx.StaticText(Sizer2.GetStaticBox(), wx.ID_ANY, "Day", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText3.Wrap(-1)
        Sizer2a.Add(self.m_staticText3, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # --> Hours header.
        self.m_staticText4 = wx.StaticText(Sizer2.GetStaticBox(), wx.ID_ANY, "Hour", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText4.Wrap(-1)
        Sizer2a.Add(self.m_staticText4, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # --> Minutes header.
        self.m_staticText5 = wx.StaticText(Sizer2.GetStaticBox(), wx.ID_ANY, "Minutes", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText5.Wrap(-1)
        Sizer2a.Add(self.m_staticText5, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # --> Seconds header.
        self.m_staticText6 = wx.StaticText(Sizer2.GetStaticBox(), wx.ID_ANY, "Seconds", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText6.Wrap(-1)
        Sizer2a.Add(self.m_staticText6, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # --> Time zone header.
        self.m_staticText7 = wx.StaticText(Sizer2.GetStaticBox(), wx.ID_ANY, "Zone", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText7.Wrap(-1)
        Sizer2a.Add(self.m_staticText7, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # --> Year.
        self.year = wx.Choice(Sizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), sorted(map(str, self.now()[-1])), wx.CB_SORT)
        Sizer2a.Add(self.year, 0, wx.ALL, 5)

        # --> Month.
        self.month = wx.Choice(Sizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), self.MONTHS, wx.CB_SORT)
        Sizer2a.Add(self.month, 0, wx.ALL, 5)

        # --> Day.
        self.day = wx.Choice(Sizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), self.DAYS, wx.CB_SORT)
        Sizer2a.Add(self.day, 0, wx.ALL, 5)

        # --> Hours.
        self.hour = wx.Choice(Sizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), self.HOURS, wx.CB_SORT)
        Sizer2a.Add(self.hour, 0, wx.ALL, 5)

        # --> Minutes.
        self.minutes = wx.Choice(Sizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), self.MINUTES, wx.CB_SORT)
        Sizer2a.Add(self.minutes, 0, wx.ALL, 5)

        # --> Seconds.
        self.seconds = wx.Choice(Sizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), self.SECONDS, wx.CB_SORT)
        Sizer2a.Add(self.seconds, 0, wx.ALL, 5)

        # --> Time zone.
        self.zone = wx.Choice(Sizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), ["Local", "GMT"], 0)
        Sizer2a.Add(self.zone, 0, wx.ALL, 5)

        # ------------------
        # Configure buttons.
        # ------------------
        Sizer3a = wx.BoxSizer(wx.HORIZONTAL)

        # --> OK.
        self.ok = wx.Button(self, wx.ID_ANY, "OK", wx.DefaultPosition, wx.Size(70, 30), 0)
        Sizer3a.Add(self.ok, 0, 0, 0)

        # --> Close.
        self.cancel = wx.Button(self, wx.ID_ANY, "Close", wx.DefaultPosition, wx.Size(70, 30), 0)
        Sizer3a.Add(self.cancel, 0, wx.LEFT, 5)

        # --> Refresh.
        self.refresh = wx.Button(self, wx.ID_ANY, "Refresh", wx.DefaultPosition, wx.Size(70, 30), 0)
        Sizer3a.Add(self.refresh, 0, wx.LEFT, 5)

        # -----------------
        # Configure layout.
        # -----------------
        Sizer3 = wx.BoxSizer(wx.VERTICAL)
        Sizer3.Add(Sizer3a, 0, wx.LEFT, 10)
        Sizer2.Add(Sizer2a, 0, wx.ALL, 10)
        MainSizer.Add(Sizer1, 1, wx.ALL | wx.EXPAND, 10)
        MainSizer.Add(Sizer2, 0, wx.ALL | wx.EXPAND, 10)
        MainSizer.Add(Sizer3, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 10)
        self.SetSizer(MainSizer)
        self.wStatusBar = self.CreateStatusBar(2)
        self.Centre(wx.BOTH)

        # -----------------
        # Configure events.
        # -----------------
        self.database.Bind(wx.EVT_BUTTON, self._select_database)
        self.albums.Bind(wx.EVT_CHECKLISTBOX, self._check_album)
        self.ok.Bind(wx.EVT_BUTTON, self._click_on_ok)
        self.cancel.Bind(wx.EVT_BUTTON, self._click_on_cancel)
        self.refresh.Bind(wx.EVT_BUTTON, self._click_on_refresh)

    def _set_statusbar(self, *status):
        if len(status) > 0:
            for index in range(len(status)):
                self.wStatusBar.SetStatusText(status[index], index)

    def _reset_interface(self) -> None:
        """

        :return:
        """

        # ----- Uncheck all discs.
        for index in range(self.albums.GetCount()):
            self.albums.Check(index, check=False)

        # ----- Set current date and time
        _year, _month, _day, _hour, _minutes, _seconds, _years = self.now()
        self.year.SetSelection(sorted(map(str, _years)).index(_year))
        self.month.SetSelection(self.MONTHS.index(_month))
        self.day.SetSelection(self.DAYS.index(_day))
        self.hour.SetSelection(self.HOURS.index(_hour))
        self.minutes.SetSelection(self.MINUTES.index(_minutes))
        self.seconds.SetSelection(self.SECONDS.index(_seconds))
        self.zone.SetSelection(0)
        self.ok.Enable(False)
        self.ok.SetDefault()

        # ----- Disable OK button.
        self.ok.Enable(False)

    def _select_database(self, event) -> None:
        """

        :param event:
        :return:
        """
        with wx.FileDialog(self, "Open database", wildcard="Database files (*.db)|*.db", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fd:
            if fd.ShowModal() == wx.ID_OK:
                self._database = fd.GetPath()
                self._discs = list(DigitalAlbums(self._database))
                self._albums = [album_name for album_name, _ in self._discs]
                self.albums.Set(self._albums)
                self._total_albums = self.albums.GetCount()
                self._set_statusbar(self._database, "Check recently listened discs and set both date and time. Then click OK button.")

    def _check_album(self, event) -> None:
        """

        :param event:
        :return:
        """
        self._enable_ok()
        self.Layout()

    def _enable_ok(self) -> None:
        """

        :return:
        """
        enable = False  # type: bool
        if self._total_albums:
            if any(self.albums.IsChecked(index) for index in range(self._total_albums)):
                enable = True
        self.ok.Enable(enable)

    def _click_on_ok(self, event) -> None:
        """

        :param event:
        :return:
        """
        albums, discs = list(zip(*[self._discs[index][1] for index in self.albums.GetCheckedItems()]))
        datobj = adjust_datetime(int(self.year.GetString(self.year.GetSelection())), int(self.month.GetString(self.month.GetSelection())),
                                 int(self.day.GetString(self.day.GetSelection())),
                                 int(self.hour.GetString(self.hour.GetSelection())), int(self.minutes.GetString(self.minutes.GetSelection())),
                                 int(self.seconds.GetString(self.seconds.GetSelection())))
        playeddate = LOCAL.localize(datobj)
        if self.zone == "GMT":
            playeddate = UTC.localize(datobj).astimezone(LOCAL)
        update = partial(update_playeddisccount, db=self._database, local_played=playeddate)
        changes = sum([updated for _, updated in map(update, albums, map(int, discs))])
        wx.MessageBox("{0:>3d} record(s) updated".format(changes), "playeddiscs Table", style=wx.OK | wx.ICON_INFORMATION)
        self._reset_interface()
        self.Layout()

    def _click_on_cancel(self, event) -> None:
        """

        :param event:
        :return:
        """
        self.Close()

    def _click_on_refresh(self, event) -> None:
        """

        :param event:
        :return:
        """
        self._reset_interface()
        self.Layout()

    @staticmethod
    def now() -> Tuple[str, str, str, str, str, str, Iterable[int]]:
        _now = UTC.localize(datetime.datetime.utcnow()).astimezone(LOCAL)
        return _now.strftime("%Y"), _now.strftime("%m"), _now.strftime("%d"), _now.strftime("%H"), _now.strftime("%M"), _now.strftime("%S"), range(int(_now.strftime("%Y")) - 5, int(_now.strftime("%Y")) + 1)


# ============
# Main script.
# ============
if __name__ == '__main__':
    that_file = os.path.abspath(__file__)
    locale.setlocale(locale.LC_ALL, "")
    app = wx.App()
    interface = MainFrame(None)
    interface.Show()
    app.MainLoop()
