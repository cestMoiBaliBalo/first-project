# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# Frame generated with wxFormBuilder (version Jun 17 2015)
# http://www.wxformbuilder.org/
import datetime
import locale
import os
from collections import OrderedDict
from contextlib import ExitStack
from functools import partial
from itertools import compress, groupby, repeat
from operator import itemgetter
from typing import Any, Dict, List, Optional, Tuple

import wx

from Applications.Tables.Albums.shared import update_playeddisccount
from Applications.Tables.shared import DatabaseConnection
from Applications.shared import DATABASE, LOCAL, UTC, adjust_datetime

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


class DigitalAlbums(object):

    def __init__(self, db: str = DATABASE) -> None:
        self._mapping = OrderedDict()  # type: Dict[str, Tuple[str, int]]
        collection = set()  # type: Any
        with ExitStack() as stack:
            conn = stack.enter_context(DatabaseConnection(db=db))
            collection = set(conn.execute("SELECT artistsort, albumid, discid, album FROM albums_vw ORDER BY artistsort, albumid, discid"))
        for key, group in groupby(sorted(sorted(sorted(sorted(collection, key=itemgetter(3)), key=itemgetter(2)), key=itemgetter(1)), key=itemgetter(0)), key=lambda i: tuple(compress(i, [1, 1, 0, 1]))):
            _artistsort, _albumid, _album = key  # type: str, str, str
            _group = list(group)
            _totaldiscs = len(_group)  # type: int
            _albums = [f"{_artistsort} - {_album}"]  # type: List[str]
            _discs = [1]  # type: List[int]
            if _totaldiscs > 1:
                _albums = [f"{_artistsort} - {_album} - CD{discid}" for (discid,) in map(lambda i: tuple(compress(i, [0, 0, 1, 0])), _group)]
                _discs = [discid for (discid,) in map(lambda i: compress(i, [0, 0, 1, 0]), _group)]
            self._mapping.update(dict(zip(_albums, zip(repeat(_albumid), _discs))))

    @property
    def discs(self):
        for k, v in self._mapping.items():
            yield k, v


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
        self._init_interface()
        self._database = None  # type: Optional[str]
        self._total_albums = 0  # type: int

    def _init_interface(self) -> None:
        _now = UTC.localize(datetime.datetime.utcnow()).astimezone(LOCAL)  # type: datetime
        _year = _now.strftime("%Y")  # type: str
        _month = _now.strftime("%m")  # type: str
        _day = _now.strftime("%d")  # type: str
        _hour = _now.strftime("%H")  # type: str
        _minutes = _now.strftime("%M")  # type: str
        _seconds = _now.strftime("%S")  # type: str
        _years = range(int(_year) - 5, int(_year) + 1)
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
        albumsChoices = []
        self.albums = wx.CheckListBox(Sizer1.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(-1, -1), albumsChoices, 0)
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
        yearChoices = sorted(map(str, _years))
        self.year = wx.Choice(Sizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), yearChoices, wx.CB_SORT)
        self.year.SetSelection(yearChoices.index(_year))
        Sizer2a.Add(self.year, 0, wx.ALL, 5)

        # --> Month.
        monthChoices = self.MONTHS
        self.month = wx.Choice(Sizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), monthChoices, wx.CB_SORT)
        self.month.SetSelection(monthChoices.index(_month))
        Sizer2a.Add(self.month, 0, wx.ALL, 5)

        # --> Day.
        dayChoices = self.DAYS
        self.day = wx.Choice(Sizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), dayChoices, wx.CB_SORT)
        self.day.SetSelection(dayChoices.index(_day))
        Sizer2a.Add(self.day, 0, wx.ALL, 5)

        # --> Hours.
        hourChoices = self.HOURS
        self.hour = wx.Choice(Sizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), hourChoices, wx.CB_SORT)
        self.hour.SetSelection(hourChoices.index(_hour))
        Sizer2a.Add(self.hour, 0, wx.ALL, 5)

        # --> Minutes.
        minutesChoices = self.MINUTES
        self.minutes = wx.Choice(Sizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), minutesChoices, wx.CB_SORT)
        self.minutes.SetSelection(minutesChoices.index(_minutes))
        Sizer2a.Add(self.minutes, 0, wx.ALL, 5)

        # --> Seconds.
        secondsChoices = self.SECONDS
        self.seconds = wx.Choice(Sizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), secondsChoices, wx.CB_SORT)
        self.seconds.SetSelection(secondsChoices.index(_seconds))
        Sizer2a.Add(self.seconds, 0, wx.ALL, 5)

        # --> Time zone.
        self.zone = wx.Choice(Sizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), ["Local", "GMT"], 0)
        self.zone.SetSelection(0)
        Sizer2a.Add(self.zone, 0, wx.ALL, 5)

        # ------------------
        # Configure buttons.
        # ------------------
        Sizer3a = wx.BoxSizer(wx.HORIZONTAL)

        # --> OK.
        self.ok = wx.Button(self, wx.ID_ANY, "OK", wx.DefaultPosition, wx.Size(70, 30), 0)
        self.ok.Enable(False)
        self.ok.SetDefault()
        Sizer3a.Add(self.ok, 0, 0, 0)

        # --> Cancel.
        self.cancel = wx.Button(self, wx.ID_ANY, "Cancel", wx.DefaultPosition, wx.Size(70, 30), 0)
        Sizer3a.Add(self.cancel, 0, wx.LEFT, 5)

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
        self.Layout()
        self.Centre(wx.BOTH)

        # -----------------
        # Configure events.
        # -----------------
        self.database.Bind(wx.EVT_BUTTON, self._select_database)
        self.albums.Bind(wx.EVT_CHECKLISTBOX, self._check_album)
        self.ok.Bind(wx.EVT_BUTTON, self._click_on_ok)
        self.cancel.Bind(wx.EVT_BUTTON, self._click_on_cancel)

    def _select_database(self, event) -> None:
        """

        :param event:
        :return:
        """
        with wx.FileDialog(self, "Open database", wildcard="Database files (*.db)|*.db", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fd:
            if fd.ShowModal() == wx.ID_OK:
                self._database = fd.GetPath()
                self._discs = list(DigitalAlbums(self._database).discs)
                self._albums = [album_name for album_name, _ in self._discs]
                self.albums.Set(self._albums)
                self._total_albums = self.albums.GetCount()

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
        wx.MessageBox("{0:>3d} records updated".format(changes), "playeddiscs Table", style=wx.OK | wx.ICON_INFORMATION)
        for index in self.albums.GetCheckedItems():
            self.albums.Check(index, check=False)
        self._enable_ok()
        self.Layout()

    def _click_on_cancel(self, event) -> None:
        """

        :param event:
        :return:
        """
        self.Close()


# ============
# Main script.
# ============
if __name__ == '__main__':
    that_file = os.path.abspath(__file__)
    locale.setlocale(locale.LC_ALL, "french")
    app = wx.App()
    interface = MainFrame(None)
    interface.Show()
    app.MainLoop()
