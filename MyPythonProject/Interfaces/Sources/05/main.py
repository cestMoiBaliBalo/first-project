# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# Frame generated with wxFormBuilder (version Jun 17 2015)
# http://www.wxformbuilder.org/
import locale
import os
from collections import OrderedDict
from datetime import datetime
from functools import partial
from itertools import repeat
from typing import Any, Iterable, List, Optional, Tuple

import wx  # type: ignore
from pandas import DataFrame
from pytz import timezone

from Applications.shared import LOCAL, TEMPLATE4, UTC, adjust_datetime, convert_timestamp, get_readabledate

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# ======
# Frame.
# ======
class MainFrame(wx.Frame):
    PIPE = "|"
    SEMICOLON = ";"
    BACKAPOSTROPHE = "`"
    ZONES = ["US/Pacific",
             "US/Eastern",
             "UTC",
             "Indian/Mayotte",
             "Asia/Tokyo",
             "Australia/Sydney"]
    MONTHS = sorted(item.zfill(2) for item in map(str, range(1, 13)))
    DAYS = sorted(item.zfill(2) for item in map(str, range(1, 32)))
    HOURS = sorted(item.zfill(2) for item in map(str, range(0, 24)))
    MINUTES = sorted(item.zfill(2) for item in map(str, range(0, 60)))
    SECONDS = sorted(item.zfill(2) for item in map(str, range(0, 60)))

    def __init__(self, parent) -> None:
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition, size=wx.Size(775, 532), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        self._timezones = None  # type: Optional[List[str]]
        self._from_timestamp, self._to_timestamp = None, None  # type: Optional[int], Optional[int]
        self._data = None  # type: Optional[Any]
        self._pathname = None  # type: Optional[str]
        self._separator = None  # type: Optional[str]
        self._init_interface()
        self._reset_interface(caller="__init__")
        self.Layout()

    def _init_interface(self) -> None:
        """

        :return:
        """
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetFont(wx.Font(9, 74, 90, 90, False, "Arial"))
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))

        # ------------------------------
        # Configure date fields headers.
        # ------------------------------
        Sizer1 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Local dates"), wx.VERTICAL)
        Sizer1a = wx.FlexGridSizer(3, 7, 5, 5)
        Sizer1a.SetFlexibleDirection(wx.BOTH)
        Sizer1a.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        # -----
        self.m_staticText1 = wx.StaticText(Sizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText1.Wrap(-1)
        Sizer1a.Add(self.m_staticText1, 1, wx.ALIGN_CENTER | wx.ALL, 5)

        # -----
        self.m_staticText2 = wx.StaticText(Sizer1.GetStaticBox(), wx.ID_ANY, "Year", wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.m_staticText2.Wrap(-1)
        Sizer1a.Add(self.m_staticText2, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # -----
        self.m_staticText3 = wx.StaticText(Sizer1.GetStaticBox(), wx.ID_ANY, "Month", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText3.Wrap(-1)
        Sizer1a.Add(self.m_staticText3, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # -----
        self.m_staticText4 = wx.StaticText(Sizer1.GetStaticBox(), wx.ID_ANY, "Day", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText4.Wrap(-1)
        Sizer1a.Add(self.m_staticText4, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # -----
        self.m_staticText5 = wx.StaticText(Sizer1.GetStaticBox(), wx.ID_ANY, "Hour", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText5.Wrap(-1)
        Sizer1a.Add(self.m_staticText5, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # -----
        self.m_staticText6 = wx.StaticText(Sizer1.GetStaticBox(), wx.ID_ANY, "Minutes", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText6.Wrap(-1)
        Sizer1a.Add(self.m_staticText6, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # -----
        self.m_staticText7 = wx.StaticText(Sizer1.GetStaticBox(), wx.ID_ANY, "Seconds", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText7.Wrap(-1)
        Sizer1a.Add(self.m_staticText7, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # ----------------------
        # Configure date fields.
        # ----------------------

        # --> FROM date.
        self.m_staticText8 = wx.StaticText(Sizer1.GetStaticBox(), wx.ID_ANY, "From", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText8.Wrap(-1)
        Sizer1a.Add(self.m_staticText8, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.from_year = wx.Choice(Sizer1.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), sorted(map(str, self._now()[-1])), wx.CB_SORT)
        Sizer1a.Add(self.from_year, 0, wx.ALL, 5)

        self.from_month = wx.Choice(Sizer1.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), self.MONTHS, wx.CB_SORT)
        Sizer1a.Add(self.from_month, 0, wx.ALL, 5)

        self.from_day = wx.Choice(Sizer1.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), self.DAYS, wx.CB_SORT)
        Sizer1a.Add(self.from_day, 0, wx.ALL, 5)

        self.from_hour = wx.Choice(Sizer1.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), self.HOURS, wx.CB_SORT)
        Sizer1a.Add(self.from_hour, 0, wx.ALL, 5)

        self.from_minutes = wx.Choice(Sizer1.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), self.MINUTES, wx.CB_SORT)
        Sizer1a.Add(self.from_minutes, 0, wx.ALL, 5)

        self.from_seconds = wx.Choice(Sizer1.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), self.SECONDS, wx.CB_SORT)
        Sizer1a.Add(self.from_seconds, 0, wx.ALL, 5)

        # --> TO date.
        self.m_staticText9 = wx.StaticText(Sizer1.GetStaticBox(), wx.ID_ANY, "To", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText9.Wrap(-1)
        Sizer1a.Add(self.m_staticText9, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.to_year = wx.Choice(Sizer1.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), sorted(map(str, self._now()[-1])), wx.CB_SORT)
        Sizer1a.Add(self.to_year, 0, wx.ALL, 5)

        self.to_month = wx.Choice(Sizer1.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), self.MONTHS, wx.CB_SORT)
        Sizer1a.Add(self.to_month, 0, wx.ALL, 5)

        self.to_day = wx.Choice(Sizer1.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), self.DAYS, wx.CB_SORT)
        Sizer1a.Add(self.to_day, 0, wx.ALL, 5)

        self.to_hour = wx.Choice(Sizer1.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), self.HOURS, wx.CB_SORT)
        Sizer1a.Add(self.to_hour, 0, wx.ALL, 5)

        self.to_minutes = wx.Choice(Sizer1.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), self.MINUTES, wx.CB_SORT)
        Sizer1a.Add(self.to_minutes, 0, wx.ALL, 5)

        self.to_seconds = wx.Choice(Sizer1.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(100, -1), self.SECONDS, wx.CB_SORT)
        Sizer1a.Add(self.to_seconds, 0, wx.ALL, 5)

        # ---------------------
        # Configure time zones.
        # ---------------------
        Sizer2 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Additional time zones"), wx.VERTICAL)
        self.timezones = wx.CheckListBox(Sizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(180, 120), self.ZONES, 0)
        Sizer2.Add(self.timezones, 0, wx.ALL, 5)

        # ----------------------------
        # Configure output separators.
        # ----------------------------
        Sizer3 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Output file"), wx.HORIZONTAL)

        # -----
        self.csv = wx.CheckBox(Sizer3.GetStaticBox(), wx.ID_ANY, "CSV", wx.DefaultPosition, wx.DefaultSize, 0)
        Sizer3.Add(self.csv, 0, wx.BOTTOM | wx.LEFT | wx.TOP, 20)

        # -----
        self.select_button = wx.Button(Sizer3.GetStaticBox(), wx.ID_ANY, "Select", wx.DefaultPosition, wx.Size(70, 30), 0)
        Sizer3.Add(self.select_button, 0, wx.BOTTOM | wx.LEFT | wx.TOP, 12)

        # -----
        self.separator1 = wx.RadioButton(Sizer3.GetStaticBox(), wx.ID_ANY, "| (pipe)", wx.DefaultPosition, wx.DefaultSize, wx.RB_GROUP)
        Sizer3.Add(self.separator1, 0, wx.BOTTOM | wx.LEFT | wx.TOP, 20)

        # -----
        self.separator2 = wx.RadioButton(Sizer3.GetStaticBox(), wx.ID_ANY, "; (semicolon)", wx.DefaultPosition, wx.DefaultSize, 0)
        Sizer3.Add(self.separator2, 0, wx.BOTTOM | wx.LEFT | wx.TOP, 20)

        # -----
        self.separator3 = wx.RadioButton(Sizer3.GetStaticBox(), wx.ID_ANY, "` (back apostrophe)", wx.DefaultPosition, wx.DefaultSize, 0)
        Sizer3.Add(self.separator3, 0, wx.BOTTOM | wx.LEFT | wx.TOP, 20)

        # ------------------
        # Configure buttons.
        # ------------------
        Sizer4a = wx.BoxSizer(wx.HORIZONTAL)

        # --> OK.
        self.ok = wx.Button(self, wx.ID_ANY, "OK", wx.DefaultPosition, wx.Size(70, 30), 0)
        self.ok.SetDefault()
        Sizer4a.Add(self.ok, 0, 0, 0)

        # --> Close.
        self.close = wx.Button(self, wx.ID_ANY, "Close", wx.DefaultPosition, wx.Size(70, 30), 0)
        Sizer4a.Add(self.close, 0, wx.LEFT, 5)

        # --> Reset.
        self.reset = wx.Button(self, wx.ID_ANY, "Reset", wx.DefaultPosition, wx.Size(70, 30), 0)
        Sizer4a.Add(self.reset, 0, wx.LEFT, 5)

        # -----------------
        # Configure layout.
        # -----------------
        Sizer1.Add(Sizer1a, 0, wx.ALL, 10)
        Sizer4 = wx.BoxSizer(wx.VERTICAL)
        Sizer4.Add(Sizer4a, 0, wx.LEFT, 10)
        MainSizer = wx.BoxSizer(wx.VERTICAL)
        MainSizer.Add(Sizer1, 0, wx.ALL | wx.EXPAND, 10)
        MainSizer.Add(Sizer2, 0, wx.ALL | wx.EXPAND, 10)
        MainSizer.Add(Sizer3, 0, wx.ALL | wx.EXPAND, 10)
        MainSizer.Add(Sizer4, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 10)
        self.SetSizer(MainSizer)
        self.Centre(wx.BOTH)

        # -----------------
        # Configure events.
        # -----------------
        self.reset.Bind(wx.EVT_BUTTON, self._reset_clicked)
        self.close.Bind(wx.EVT_BUTTON, self._cancel_clicked)
        self.ok.Bind(wx.EVT_BUTTON, self._ok_clicked)
        self.select_button.Bind(wx.EVT_BUTTON, self._select_clicked)
        self.csv.Bind(wx.EVT_CHECKBOX, self._csv_checked)
        self.separator1.Bind(wx.EVT_RADIOBUTTON, self._pipe_selected)
        self.separator2.Bind(wx.EVT_RADIOBUTTON, self._semicolon_selected)
        self.separator3.Bind(wx.EVT_RADIOBUTTON, self._backapostrophe_selected)

    def _reset_interface(self, *, caller):
        _year, _month, _day, _hour, _minutes, _seconds, _years = self._now()
        self._timezones = ["Europe/Paris"]
        self._from_timestamp, self._to_timestamp = 0, 0
        self._data = None
        self._pathname = os.path.join(os.path.expandvars("%TEMP%"), "timezones.csv")
        self.csv.SetValue(False)
        self.select_button.Enable(False)
        self.separator1.SetValue(True)
        self.separator1.Enable(False)
        self.separator2.Enable(False)
        self.separator3.Enable(False)
        self._separator = self.PIPE
        self.from_year.SetSelection(sorted(map(str, _years)).index(_year))
        self.to_year.SetSelection(sorted(map(str, _years)).index(_year))
        self.from_month.SetSelection(self.MONTHS.index(_month))
        self.to_month.SetSelection(self.MONTHS.index(_month))
        self.from_day.SetSelection(self.DAYS.index(_day))
        self.to_day.SetSelection(self.DAYS.index(_day))
        self.from_hour.SetSelection(self.HOURS.index(_hour))
        self.to_hour.SetSelection(self.HOURS.index(_hour))
        self.from_minutes.SetSelection(self.MINUTES.index(_minutes))
        self.to_minutes.SetSelection(self.MINUTES.index(_minutes))
        self.from_seconds.SetSelection(self.SECONDS.index(_seconds))
        self.to_seconds.SetSelection(self.SECONDS.index(_seconds))
        for index in range(self.timezones.GetCount()):
            self.timezones.Check(index, check=False)

    def _reset_clicked(self, event) -> None:
        """

        :param event:
        :return:
        """
        self._reset_interface(caller="_reset_clicked")

    def _cancel_clicked(self, event) -> None:
        """
        
        :param event: 
        :return: 
        """
        self.Close()

    def _ok_clicked(self, event) -> None:
        """
        
        :param event: 
        :return: 
        """
        self._from_timestamp = int(adjust_datetime(int(self.from_year.GetString(self.from_year.GetSelection())), int(self.from_month.GetString(self.from_month.GetSelection())),
                                                   int(self.from_day.GetString(self.from_day.GetSelection())),
                                                   int(self.from_hour.GetString(self.from_hour.GetSelection())), int(self.from_minutes.GetString(self.from_minutes.GetSelection())),
                                                   int(self.from_seconds.GetString(self.from_seconds.GetSelection()))).timestamp())
        self._to_timestamp = int(adjust_datetime(int(self.to_year.GetString(self.to_year.GetSelection())), int(self.to_month.GetString(self.to_month.GetSelection())),
                                                 int(self.to_day.GetString(self.to_day.GetSelection())),
                                                 int(self.to_hour.GetString(self.to_hour.GetSelection())), int(self.to_minutes.GetString(self.to_minutes.GetSelection())),
                                                 int(self.to_seconds.GetString(self.to_seconds.GetSelection()))).timestamp())
        for index in self.timezones.GetCheckedItems():
            self._timezones.append(self.timezones.GetString(index))
        self._data = OrderedDict((tz, list(map(get_readabledate, map(convert_timestamp, range(self._from_timestamp, self._to_timestamp + 1), repeat(timezone(tz)))))) for tz in sorted(set(self._timezones)))
        self._headers = list(self._data)

        # Results are displayed into a child frame.
        if not self.csv.IsChecked():
            window = ChildFrame(parent=self)
            window.Show()
            self.Hide()

        # Results are displayed into a plain text file with separator.
        elif self.csv.IsChecked():
            DataFrame(self._data).to_csv(self._pathname, sep=self._separator, columns=self._headers)
            wx.MessageBox("CSV file created successfully", "", style=wx.OK | wx.ICON_INFORMATION)

        # Reset interface to default values.
        self._reset_interface(caller="_ok_clicked")

    def _select_clicked(self, event) -> None:
        """

        :param event:
        :return:
        """
        with wx.FileDialog(self, "Save CSV file", wildcard="CSV files (*.csv)|*.csv", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_OK:
                self._pathname = fileDialog.GetPath()

    def _csv_checked(self, event) -> None:
        """

        :param event:
        :return:
        """
        self.select_button.Enable(False)
        self.separator1.Enable(False)
        self.separator2.Enable(False)
        self.separator3.Enable(False)
        if self.csv.IsChecked():
            self.select_button.Enable(True)
            self.separator1.Enable(True)
            self.separator2.Enable(True)
            self.separator3.Enable(True)

    def _pipe_selected(self, event) -> None:
        """

        :param event:
        :return:
        """
        self._separator = self.PIPE

    def _semicolon_selected(self, event) -> None:
        """

        :param event:
        :return:
        """
        self._separator = self.SEMICOLON

    def _backapostrophe_selected(self, event) -> None:
        """

        :param event:
        :return:
        """
        self._separator = self.BACKAPOSTROPHE

    @staticmethod
    def _now() -> Tuple[str, str, str, str, str, str, Iterable[int]]:
        now = UTC.localize(datetime.utcnow()).astimezone(LOCAL)  # type: datetime
        return now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"), now.strftime("%H"), now.strftime("%M"), now.strftime("%S"), range(int(now.strftime("%Y")) - 5, int(now.strftime("%Y")) + 1)

    @property
    def data(self):
        return self._data

    @property
    def headers(self):
        return self._headers


class ChildFrame(wx.Frame):
    """

    """

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition, size=wx.Size(1168, 789), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        self._parent = parent
        self._data = VirtualList(self, parent.headers, *[value for key, value in parent.data.items()])
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetFont(wx.Font(9, 74, 90, 90, False, "Arial"))
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        MainSizer = wx.BoxSizer(wx.VERTICAL)

        # -----
        MainSizer.Add(self._data, 1, wx.ALL | wx.EXPAND, 5)

        # -----
        Sizer1 = wx.BoxSizer(wx.VERTICAL)
        self.ok = wx.Button(self, wx.ID_ANY, "Close", wx.DefaultPosition, wx.Size(70, 30), 0)
        self.ok.SetDefault()
        Sizer1.Add(self.ok, 0, wx.ALIGN_LEFT, 0)

        # -----
        MainSizer.Add(Sizer1, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(MainSizer)
        self.Layout()
        self.Centre(wx.BOTH)

        # -----
        self.ok.Bind(wx.EVT_BUTTON, self._ok_clicked)

    def _ok_clicked(self, event) -> None:
        """

        :param event:
        :return:
        """
        self._parent.Show()
        self.Destroy()


class VirtualList(wx.ListCtrl):
    """

    """

    def __init__(self, parent, headers, *data):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.LC_REPORT | wx.LC_VIRTUAL)
        self._data = list(data)
        self.SetItemCount(max(set(len(item) for item in self._data)))
        for index, header in enumerate(headers):
            self.InsertColumn(index, header)
            self.SetColumnWidth(0, 225)

    def OnGetItemText(self, item, col):
        return self._data[col][item]


# ============
# Main script.
# ============
if __name__ == '__main__':
    that_file = os.path.abspath(__file__)
    locale.setlocale(locale.LC_ALL, "french")
    get_readabledate = partial(get_readabledate, template=TEMPLATE4)
    app = wx.App()
    interface = MainFrame(None)
    interface.Show()
    app.MainLoop()
