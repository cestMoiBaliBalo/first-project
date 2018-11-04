# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# Frame generated with wxFormBuilder (version Jun 17 2015)
# http://www.wxformbuilder.org/
import argparse
import os
import sys
from typing import List, Optional

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

    def __init__(self, parent, config) -> None:
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="Sync Mobile Devices", pos=wx.DefaultPosition, size=wx.Size(-1, -1), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        with open(config) as stream:
            self._configuration = yaml.load(stream)
        self._init_interface(*sorted(self._configuration.get("repositories")))
        self._init_variables()
        self._copy_audiofiles, self._command1, self._command2 = False, [], []  # type: bool, list, list

    def _init_interface(self, *collection):

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetFont(wx.Font(9, 74, 90, 90, False, "Arial"))
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        m_MainBox = wx.BoxSizer(wx.VERTICAL)

        # ---------------------
        # Configure checkboxes.
        # ---------------------
        m_CheckBoxes = wx.BoxSizer(wx.HORIZONTAL)

        # --> Repositories.
        m_Repositories = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Repositories"), wx.VERTICAL)
        m_Repositories.SetMinSize(wx.Size(-1, 160))
        repositories: int = 0
        for repository in collection:
            repositories += 1
            checkbox = wx.CheckBox(m_Repositories.GetStaticBox(), repositories, repository, wx.DefaultPosition, wx.DefaultSize, 0)
            setattr(self, f"m_checkBox{repositories}", checkbox)
            m_Repositories.Add(getattr(self, f"m_checkBox{repositories}"), 0, wx.ALL, 5)
        self._repositories: int = repositories

        # --> Drives.
        m_Drives = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Drives"), wx.VERTICAL)
        m_Drives.SetMinSize(wx.Size(-1, 160))
        drives: int = repositories
        for drive in map(lambda i: i[:-1], get_drives()):
            drives += 1
            checkbox = wx.CheckBox(m_Drives.GetStaticBox(), drives, drive, wx.DefaultPosition, wx.DefaultSize, 0)
            setattr(self, f"m_checkBox{drives}", checkbox)
            m_Drives.Add(getattr(self, f"m_checkBox{drives}"), 0, wx.ALL, 5)
        self._drives: int = drives

        # --> Additional boxes.

        # °°° MP3 audio files.
        self.m_checkBox_mp3 = wx.CheckBox(m_Repositories.GetStaticBox(), drives + 1, r"*.mp3", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_checkBox_mp3.Hide()
        m_Repositories.Add(self.m_checkBox_mp3, 0, wx.ALL, 5)

        # °°° M4A audio files.
        self.m_checkbox_m4a = wx.CheckBox(m_Repositories.GetStaticBox(), drives + 2, r"*.m4a", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_checkbox_m4a.Hide()
        m_Repositories.Add(self.m_checkbox_m4a, 0, wx.ALL, 5)

        # ------------------
        # Configure buttons.
        # ------------------
        m_Buttons = wx.BoxSizer(wx.HORIZONTAL)

        # --> "Run" button.
        self.m_runbutton = wx.Button(self, wx.ID_ANY, "Run", wx.DefaultPosition, wx.Size(70, 30), 0)
        m_Buttons.Add(self.m_runbutton, 0, wx.BOTTOM, 5)

        # --> "Sync" button.
        self.m_syncbutton = wx.Button(self, wx.ID_ANY, "Sync", wx.DefaultPosition, wx.Size(70, 30), 0)
        m_Buttons.Add(self.m_syncbutton, 0, wx.BOTTOM | wx.LEFT, 5)

        # --> "Close" button.
        self.m_closebutton = wx.Button(self, wx.ID_ANY, "Close", wx.DefaultPosition, wx.Size(70, 30), 0)
        self.m_closebutton.SetDefault()
        m_Buttons.Add(self.m_closebutton, 0, wx.BOTTOM | wx.LEFT, 5)

        # -----------------
        # Configure layout.
        # -----------------
        m_CheckBoxes.Add(m_Repositories, 1, wx.BOTTOM | wx.EXPAND, 20)
        m_CheckBoxes.Add(m_Drives, 1, wx.BOTTOM | wx.EXPAND, 20)
        m_MainBox.Add(m_CheckBoxes, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)
        m_MainBox.Add(m_Buttons, 0, wx.ALIGN_RIGHT | wx.RIGHT, 20)
        self.SetSizer(m_MainBox)
        self.Layout()
        m_MainBox.Fit(self)
        self.Centre(wx.BOTH)

        # -----------------
        # Configure events.
        # -----------------
        for index in range(1, repositories + 1):
            getattr(self, f"m_checkBox{index}").Bind(wx.EVT_CHECKBOX, self._check_repository)
        for index in range(repositories + 1, drives + 1):
            getattr(self, f"m_checkBox{index}").Bind(wx.EVT_CHECKBOX, self._check_drive)
        self.m_checkbox_m4a.Bind(wx.EVT_CHECKBOX, self._check_m4a_audiofiles)
        self.m_runbutton.Bind(wx.EVT_BUTTON, self._click_on_run)
        self.m_syncbutton.Bind(wx.EVT_BUTTON, self._click_on_sync)
        self.m_closebutton.Bind(wx.EVT_BUTTON, self._click_on_close)

    def _init_variables(self):
        """

        :return:
        """
        self._is_repository_checked, self._is_drive_checked, self._m4a_audiofiles = False, False, False  # type: bool, bool, bool
        self._repository, self._compression, self._drive = "", "", ""  # type: str, str, str
        for index in range(1, self._drives + 1):
            getattr(self, f"m_checkBox{index}").SetValue(False)
            getattr(self, f"m_checkBox{index}").Enable(True)
        self.m_checkBox_mp3.Show(False)
        self.m_checkbox_m4a.Show(False)
        self.m_syncbutton.Enable(False)
        self.m_runbutton.Enable(False)

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
            self.m_syncbutton.Enable(self._is_drive_checked)
            if self._compression.lower() == "lossy":
                self.m_checkBox_mp3.Show(True)
                self.m_checkBox_mp3.SetValue(True)
                self.m_checkBox_mp3.Enable(False)
                self.m_checkbox_m4a.Show(True)
                self.m_checkbox_m4a.SetValue(False)

        # Repository has been unchecked.
        # Enable all repositories and disable "sync" button.
        # Disable additional boxes.
        elif not chkb.GetValue():
            self._toggle_checkboxes(1, self._repositories + 1, enable=True)
            self.m_checkBox_mp3.Show(False)
            self.m_checkbox_m4a.Show(False)
            self.m_syncbutton.Enable(False)

        # Apply new layout.
        self.Layout()

    def _check_drive(self, event) -> None:
        """

        :param event:
        :return:
        """

        # Get drive label.
        chkb = event.GetEventObject()
        self._is_drive_checked = chkb.GetValue()

        # Drive has been checked.
        # Disable all drives but the checked one.
        # Enable "sync" button if both repository and drive have been checked.
        if chkb.GetValue():
            self._toggle_checkboxes(self._repositories + 1, self._drives + 1)
            chkb.Enable(True)
            self._drive = chkb.GetLabel()
            self.m_syncbutton.Enable(self._is_repository_checked)

        # Drive has been unchecked.
        # Enable all drives and disable "sync" button.
        elif not chkb.GetValue():
            self._toggle_checkboxes(self._repositories + 1, self._drives + 1, enable=True)
            self.m_syncbutton.Enable(False)

        # Apply new layout.
        self.Layout()

    def _check_m4a_audiofiles(self, event) -> None:
        """

        :param event:
        :return:
        """
        self._m4a_audiofiles = self.m_checkbox_m4a.GetValue()

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
        patterns: List = self._configuration["patterns"][self._compression]
        extra_patterns: Optional[List] = self._configuration["extra_patterns"].get(self._compression)
        if self._m4a_audiofiles:
            patterns.extend(extra_patterns)
        self._command1.extend((self._repository, pattern, f"{self._drive.upper()}:") for pattern in patterns)
        self._command2.append((f"{self._drive.upper()}:", self._repository))
        self._init_variables()
        self.m_runbutton.Enable(True)
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
            getattr(self, f"m_checkBox{index}").Enable(enable)

    @property
    def copy_audiofiles(self):
        return self._copy_audiofiles

    @property
    def command1(self):
        return self._command1

    @property
    def command2(self):
        return self._command2


# ============
# Main script.
# ============
if __name__ == '__main__':

    # Define variables.
    level = 100  # type: int

    # Define template.
    template = TemplatingEnvironment(loader=jinja2.FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "GUI", "Sources", "02")))
    # template.set_environment(globalvars={},
    #                          filters={})
    template.set_template(T1="T01")
    # T1 = template.environment.get_template("T01")

    # Parse input arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("outfile",
                        type=argparse.FileType("w", encoding="ISO-8859-1"),
                        nargs="?",
                        default=os.path.join(os.path.expandvars("%TEMP%"), "xxcopy.cmd"),
                        help="DOS commands file running XXCOPY statements.")
    arguments = parser.parse_args()

    # Run interface.
    app = wx.App()
    interface = MainFrame(None, os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Tasks", "Resources", "Configuration.yml"))
    interface.Show()
    app.MainLoop()
    if interface.copy_audiofiles:
        level = 0
        arguments.outfile.write(getattr(template, "T1").render(command1=interface.command1, command2=interface.command2))

    # Exit script.
    sys.exit(level)
