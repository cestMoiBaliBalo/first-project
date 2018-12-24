# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# Frame generated with wxFormBuilder (version Jun 17 2015)
# http://www.wxformbuilder.org/
import argparse
import os
import sys
from itertools import filterfalse, repeat
from pathlib import PurePath
from typing import List, Tuple

import jinja2
import wx  # type: ignore
import yaml

from Applications.shared import TemplatingEnvironment, get_drives

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# ======
# Frame.
# ======
class MainFrame(wx.Frame):

    def __init__(self, parent, **kwargs) -> None:
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="Sync Mobile Devices", pos=wx.DefaultPosition, size=wx.Size(-1, -1), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        self._configuration = dict(kwargs)
        self._init_interface(*sorted(self._configuration.get("repositories")))
        self._init_variables()
        self._copy_audiofiles, self._collection = False, []  # type: bool, List[Tuple[str, str, str]]

    def _init_interface(self, *collection) -> None:
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetFont(wx.Font(9, 74, 90, 90, False, "Arial"))
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))

        # ---------------------
        # Configure checkboxes.
        # ---------------------

        # --> Repositories.
        SzRepositories = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Repositories"), wx.VERTICAL)
        SzRepositories.SetMinSize(wx.Size(-1, 180))
        repositories: int = 0
        for repository in collection:
            repositories += 1
            checkbox = wx.CheckBox(SzRepositories.GetStaticBox(), repositories, repository, wx.DefaultPosition, wx.DefaultSize, 0)
            setattr(self, f"checkbox{repositories}", checkbox)
            SzRepositories.Add(getattr(self, f"checkbox{repositories}"), 0, wx.ALL, 5)
        self._repositories: int = repositories

        # --> Drives.
        SzDrives = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Drives"), wx.VERTICAL)
        SzDrives.SetMinSize(wx.Size(-1, 180))
        drives: int = repositories
        for drive in map(lambda i: i[:-1], get_drives()):
            drives += 1
            checkbox = wx.CheckBox(SzDrives.GetStaticBox(), drives, drive, wx.DefaultPosition, wx.DefaultSize, 0)
            setattr(self, f"checkbox{drives}", checkbox)
            SzDrives.Add(getattr(self, f"checkbox{drives}"), 0, wx.ALL, 5)
        self._drives: int = drives

        # --> Additional boxes.

        # °°° MP3 audio files.
        self.checkbox_mp3 = wx.CheckBox(SzRepositories.GetStaticBox(), drives + 1, r"*.mp3", wx.DefaultPosition, wx.DefaultSize, 0)
        self.checkbox_mp3.Hide()
        SzRepositories.Add(self.checkbox_mp3, 0, wx.ALL, 5)

        # °°° M4A audio files.
        self.checkbox_m4a = wx.CheckBox(SzRepositories.GetStaticBox(), drives + 2, r"*.m4a", wx.DefaultPosition, wx.DefaultSize, 0)
        self.checkbox_m4a.Hide()
        SzRepositories.Add(self.checkbox_m4a, 0, wx.ALL, 5)

        # ------------------
        # Configure buttons.
        # ------------------
        SzButtons = wx.BoxSizer(wx.HORIZONTAL)

        # --> "Run" button.
        self.run = wx.Button(self, wx.ID_ANY, "Run", wx.DefaultPosition, wx.Size(70, 30), 0)
        SzButtons.Add(self.run, 0, wx.BOTTOM | wx.RIGHT, 5)

        # --> "Sync" button.
        self.sync = wx.Button(self, wx.ID_ANY, "Sync", wx.DefaultPosition, wx.Size(70, 30), 0)
        SzButtons.Add(self.sync, 0, wx.BOTTOM | wx.RIGHT, 5)

        # --> "Close" button.
        self.close = wx.Button(self, wx.ID_ANY, "Close", wx.DefaultPosition, wx.Size(70, 30), 0)
        self.close.SetDefault()
        SzButtons.Add(self.close, 0, wx.BOTTOM, 5)

        # -----------------
        # Configure layout.
        # -----------------
        Sizer2 = wx.BoxSizer(wx.VERTICAL)
        Sizer2.Add(SzButtons, 1, wx.ALIGN_LEFT, 5)
        Sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        Sizer1.Add(SzRepositories, 1, wx.RIGHT, 15)
        Sizer1.Add(SzDrives, 1, 0, 0)
        MainSizer = wx.BoxSizer(wx.VERTICAL)
        MainSizer.Add(Sizer1, 1, wx.ALL, 15)
        MainSizer.Add(Sizer2, 0, wx.LEFT, 15)
        self.SetSizer(MainSizer)
        self.Layout()
        MainSizer.Fit(self)
        self.Centre(wx.BOTH)

        # -----------------
        # Configure events.
        # -----------------
        for index in range(1, repositories + 1):
            getattr(self, f"checkbox{index}").Bind(wx.EVT_CHECKBOX, self._check_repository)
        for index in range(repositories + 1, drives + 1):
            getattr(self, f"checkbox{index}").Bind(wx.EVT_CHECKBOX, self._check_drive)
        self.checkbox_m4a.Bind(wx.EVT_CHECKBOX, self._check_m4a_audiofiles)
        self.run.Bind(wx.EVT_BUTTON, self._click_on_run)
        self.sync.Bind(wx.EVT_BUTTON, self._click_on_sync)
        self.close.Bind(wx.EVT_BUTTON, self._click_on_close)

    def _init_variables(self):
        """

        :return:
        """
        self._is_repository_checked, self._is_drive_checked, self._m4a_audiofiles = False, False, False  # type: bool, bool, bool
        self._repository, self._compression, self._drive = "", "", ""  # type: str, str, str
        for index in range(1, self._drives + 1):
            getattr(self, f"checkbox{index}").SetValue(False)
            getattr(self, f"checkbox{index}").Enable(True)
        self.checkbox_mp3.Show(False)
        self.checkbox_m4a.Show(False)
        self.sync.Enable(False)
        self.run.Enable(False)

    def _check_repository(self, event) -> None:
        """

        :param event:
        :return:
        """

        # Get repository label.
        chkb = event.GetEventObject()
        self._is_repository_checked = chkb.GetValue()

        # Repository has been checked.
        # Disable all repositories but the checked one.
        # Enable additional boxes.
        # Enable "sync" button if both repository and drive have been checked.
        if chkb.GetValue():
            self._toggle_checkboxes(1, self._repositories + 1)
            chkb.Enable(True)
            self._repository = self._configuration["repositories"][chkb.GetLabel()]
            self._compression = self._configuration["compression"][self._repository]
            self.sync.Enable(self._is_drive_checked)
            if self._compression.lower() == "lossy":
                self.checkbox_mp3.Show(True)
                self.checkbox_mp3.SetValue(True)
                self.checkbox_mp3.Enable(False)
                self.checkbox_m4a.Show(True)
                self.checkbox_m4a.SetValue(False)

        # Repository has been unchecked.
        # Enable all repositories and disable "sync" button.
        # Disable additional boxes.
        elif not chkb.GetValue():
            self._toggle_checkboxes(1, self._repositories + 1, enable=True)
            self.checkbox_mp3.Show(False)
            self.checkbox_m4a.Show(False)
            self.sync.Enable(False)

        # Apply new layout.
        self.Layout()

    def _check_drive(self, event) -> None:
        """

        :param event:
        :return:
        """

        # Get drive value.
        chkb = event.GetEventObject()
        self._is_drive_checked = chkb.GetValue()

        # Drive has been checked.
        # Disable all drives but the checked one.
        # Enable "sync" button if both repository and drive have been checked.
        if chkb.GetValue():
            self._toggle_checkboxes(self._repositories + 1, self._drives + 1)
            chkb.Enable(True)
            self._drive = chkb.GetLabel()
            self.sync.Enable(self._is_repository_checked)

        # Drive has been unchecked.
        # Enable all drives and disable "sync" button.
        elif not chkb.GetValue():
            self._toggle_checkboxes(self._repositories + 1, self._drives + 1, enable=True)
            self.sync.Enable(False)

        # Apply new layout.
        self.Layout()

    def _check_m4a_audiofiles(self, event) -> None:
        """

        :param event:
        :return:
        """
        self._m4a_audiofiles = self.checkbox_m4a.GetValue()

    def _click_on_run(self, event) -> None:
        """

        :param event:
        :return:
        """
        self._copy_audiofiles = True
        self.Close(True)

    def _click_on_sync(self, event) -> None:
        """

        :param event:
        :return:
        """
        extensions = self._configuration["patterns"][self._compression]  # type: List[str]
        extensions.extend(self._configuration["m4a_audiofiles"].get(self._m4a_audiofiles, []))
        extensions = list(filterfalse(lambda i: i is None, extensions))
        self._collection.extend(list(zip(repeat(self._repository), extensions, repeat(f"{self._drive.upper()}:"))))
        self._init_variables()
        self.run.Enable(True)
        self.Layout()

    def _click_on_close(self, event) -> None:
        """

        :param event:
        :return:
        """
        self.Close(True)

    def _toggle_checkboxes(self, start: int, stop: int, *, enable: bool = False) -> None:
        """

        :param start:
        :param stop:
        :param enable:
        :return:
        """
        for index in range(start, stop):
            getattr(self, f"checkbox{index}").Enable(enable)

    @property
    def copy_audiofiles(self):
        return self._copy_audiofiles

    @property
    def collection(self):
        return self._collection


# ============
# Main script.
# ============
if __name__ == '__main__':

    _THATFILE = PurePath(os.path.abspath(__file__))

    # Define variables.
    level = 100  # type: int

    # Define template.
    template = TemplatingEnvironment(loader=jinja2.FileSystemLoader(str(_THATFILE.parent)))
    template.set_template(T1="T01")

    # Parse input arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("outfile",
                        type=argparse.FileType("w", encoding="ISO-8859-1"),
                        nargs="?",
                        default=os.path.join(os.path.expandvars("%TEMP%"), "xxcopy.cmd"),
                        help="XXCOPY commands file")
    arguments = parser.parse_args()

    # Load configuration.
    with open(_THATFILE.parents[1] / "Resources" / "resource1.yml") as stream:
        configuration = yaml.load(stream)

    # Run interface.
    app = wx.App()
    interface = MainFrame(None, **configuration)
    interface.Show()
    app.MainLoop()
    if interface.copy_audiofiles:
        level = 0
        arguments.outfile.write(getattr(template, "T1").render(collection=iter(interface.collection)))

    # Exit script.
    sys.exit(level)
