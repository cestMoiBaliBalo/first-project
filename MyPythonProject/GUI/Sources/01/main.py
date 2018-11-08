# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# Frame generated with wxFormBuilder (version Jun 17 2015)
# http://www.wxformbuilder.org/
import argparse
import fnmatch
import itertools
import os
import sys
from collections import OrderedDict
from functools import partial
from operator import itemgetter
from typing import List, Optional, Set, Tuple

import jinja2
import wx  # type: ignore
import yaml

from Applications.Tables.XReferences.shared import get_albums, get_artists
from Applications.shared import TemplatingEnvironment, find_files, get_dirname

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# ==========
# Functions.
# ==========
def exclude_allbut_checked_extensions(curdir: str, *files: str, extensions: Optional[List[str]] = None) -> Set[str]:
    """
    :param curdir:
    :param files:
    :param extensions:
    :return:
    """
    myset = set()  # type: Set[str]
    if extensions:
        myset = set(files) - set(itertools.chain.from_iterable(fnmatch.filter(files, f"*.{_extension}") for _extension in extensions))
    return myset


# ======
# Frame.
# ======
class MainFrame(wx.Frame):

    def __init__(self, parent, config) -> None:
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="Sync Audio Repository", pos=wx.DefaultPosition, size=wx.Size(-1, -1), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        # -----
        with open(config) as stream:
            self._configuration = yaml.load(stream)

        # -----
        self._init_interface()

        # -----
        self._init_variables()

        # -----
        self._sync = False  # type: bool
        self._synced = 0  # type: int
        self._arguments = []  # type: List

        # -----
        self._init_albums()
        self._init_artists()
        self._enable_checkall()
        self._enable_sync()
        self._enable_run()
        self._set_statusbar("Choose repository", "", "")

    def _init_interface(self) -> None:
        """

        :return:
        """
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetFont(wx.Font(9, 74, 90, 90, False, "Arial"))
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        wMainBox = wx.BoxSizer(wx.VERTICAL)
        wMainBox.SetMinSize(wx.Size(680, 350))

        # ----------------
        # Configure lists.
        # ----------------
        wBodyBox = wx.BoxSizer(wx.HORIZONTAL)

        # --> Repositories.
        self.m_repositories = wx.CheckListBox(self, 101, wx.DefaultPosition, wx.Size(220, -1), sorted(self._configuration["repositories"]), 0)
        wBodyBox.Add(self.m_repositories, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 5)

        # --> Artists.
        self.m_artists = wx.CheckListBox(self, 102, wx.DefaultPosition, wx.Size(220, -1), [], 0)
        wBodyBox.Add(self.m_artists, 0, wx.ALL | wx.EXPAND, 5)

        # --> Albums.
        self.m_albums = wx.CheckListBox(self, 103, wx.DefaultPosition, wx.Size(220, -1), [], 0)
        wBodyBox.Add(self.m_albums, 1, wx.BOTTOM | wx.EXPAND | wx.TOP, 5)

        # ------------------
        # Configure buttons.
        # ------------------
        wButtons = wx.GridSizer(1, 9, 0, 5)
        for index in range(1, 6):
            setattr(self, f"m_dummy{index}", wx.StaticText(self, 200 + index, wx.EmptyString, wx.Point(0, 1), wx.DefaultSize, 0))
            getattr(self, f"m_dummy{index}").Wrap(-1)
            wButtons.Add(getattr(self, f"m_dummy{index}"), 0, wx.ALL, 5)

        # Check all albums button.
        self.m_CheckAllButton = wx.ToggleButton(self, 301, "All Albums", wx.Point(0, 5), wx.Size(70, 30), 0)
        self.m_CheckAllButton.SetValue(False)
        self.m_CheckAllButton.Show(False)
        wButtons.Add(self.m_CheckAllButton, 0, 0, 0)

        # Run button.
        self.m_RunButton = wx.Button(self, 302, "Run", wx.Point(0, 6), wx.Size(70, 30), 0)
        wButtons.Add(self.m_RunButton, 0, 0, 0)

        # Sync button.
        self.m_SyncButton = wx.Button(self, 303, "Sync", wx.Point(0, 7), wx.Size(70, 30), 0)
        wButtons.Add(self.m_SyncButton, 0, 0, 0)

        # Close button.
        self.m_CloseButton = wx.Button(self, 304, "Close", wx.Point(0, 8), wx.Size(70, 30), 0)
        self.m_CloseButton.SetDefault()
        wButtons.Add(self.m_CloseButton, 0, 0, 0)

        # -----------------
        # Configure layout.
        # -----------------
        wMainBox.Add(wBodyBox, 1, wx.ALL | wx.EXPAND, 10)
        wMainBox.Add(wButtons, 0, wx.ALL, 10)
        self.SetSizer(wMainBox)
        self.Layout()
        wMainBox.Fit(self)
        self.wStatusBar = self.CreateStatusBar(3)
        self.Centre(wx.BOTH)

        # -----------------
        # Configure events.
        # -----------------
        self.m_repositories.Bind(wx.EVT_CHECKLISTBOX, self._check_repository)
        self.m_artists.Bind(wx.EVT_CHECKLISTBOX, self._check_artist)
        self.m_albums.Bind(wx.EVT_CHECKLISTBOX, self._check_album)
        self.m_CheckAllButton.Bind(wx.EVT_TOGGLEBUTTON, self._click_on_checkall)
        self.m_RunButton.Bind(wx.EVT_BUTTON, self._click_on_run)
        self.m_SyncButton.Bind(wx.EVT_BUTTON, self._click_on_sync)
        self.m_CloseButton.Bind(wx.EVT_BUTTON, self._click_on_close)

    def _init_variables(self):
        self._repositoryid, self._repository, self._extensions, self._destination = None, "", [], ""  # type: Optional[int], str, List, str
        self._artists, self._albums = OrderedDict(), OrderedDict()

    def _init_artists(self):
        self._artistid, self._total_artists = None, 0  # type: Optional[int], int
        self.m_artists.Set([])

    def _init_albums(self):
        self._total_albums = 0  # type: int
        self.m_albums.Set([])

    def _set_statusbar(self, *status):
        if len(status) > 0:
            for index in range(len(status)):
                self.wStatusBar.SetStatusText(status[index], index)

    def _check_repository(self, event) -> None:
        """

        :param event:
        :return:
        """
        if self._repositoryid is not None:
            self.m_repositories.Check(self._repositoryid, False)

        # Get box ID.
        chkb_id = event.GetInt()  # type: int
        self._repositoryid = chkb_id

        # Box has been checked: display artists respective to the repository.
        if self.m_repositories.IsChecked(chkb_id):

            # Get repository full path.
            self._repository = self._configuration["repositories"][self.m_repositories.GetString(chkb_id)]

            # Get compression type.
            compression = self._configuration["compression"][self._repository]  # type: str

            # Get allowed extensions.
            self._extensions = self._configuration["extensions"][compression]  # type: List[str]

            # Get artists with files matching allowed extensions.
            self._artists = OrderedDict(sorted(get_artists(*self._extensions), key=itemgetter(0)))
            self.m_artists.Set(list(self._artists))
            self._total_artists = self.m_artists.GetCount()

            # Set status bar.
            status2 = "Choose an artist"
            if self._synced:
                status2 = "Choose an artist or click Run button"
            self._set_statusbar(self._repository, status2, "")

        # Box has been unchecked.
        elif not self.m_repositories.IsChecked(chkb_id):

            # Reset lists.
            self._init_variables()
            self._init_albums()
            self._init_artists()

            # Set status bar.
            status = "Choose a repository"
            if self._synced:
                status = "Choose a repository or click Run button"
            self._set_statusbar(status, "", "")

        # Refresh layout.
        self._enable_checkall()
        self._enable_sync()
        self._enable_run()
        self.Layout()

    def _check_artist(self, event) -> None:
        """

        :param event:
        :return:
        """
        if self._artistid is not None:
            self.m_artists.Check(self._artistid, False)

        # Get box ID.
        chkb_id = event.GetInt()  # type: int
        self._artistid = chkb_id

        # Box has been checked: display albums respective to the artist.
        if self.m_artists.IsChecked(chkb_id):

            # Get artist full path.
            artist = self._artists[self.m_artists.GetString(chkb_id)]  # type: str
            self._destination = os.path.join(self._repository, os.path.splitdrive(artist)[1][1:])

            # Get albums with files matching extensions.
            self._albums = OrderedDict((album, (album_path, albumid)) for _, albumid, _, album, album_path in sorted(get_albums(artist, *self._extensions), key=itemgetter(2)))
            self.m_albums.Set(list(self._albums))
            self._total_albums = self.m_albums.GetCount()
            self._set_statusbar(self._repository, artist, f"{self._total_albums} album(s)")

        # Box has been unchecked.
        elif not self.m_artists.IsChecked(chkb_id):
            self._init_artists()
            self._set_statusbar(self._repository, "Choose an artist", "")

        # Refresh layout.
        self._enable_checkall()
        self._enable_sync()
        self._enable_run()
        self.Layout()

    def _check_album(self, event) -> None:
        """

        :param event:
        :return:
        """
        self._enable_checkall()
        self._enable_sync()
        self._enable_run()
        self.Layout()

    def _enable_checkall(self) -> None:
        """

        :return:
        """
        show = False  # type: bool
        if self._total_albums:
            show, value = True, False
            if all(self.m_albums.IsChecked(index) for index in range(self._total_albums)):
                value = True
            self.m_CheckAllButton.SetValue(value)
        self.m_CheckAllButton.Show(show)

    def _enable_sync(self) -> None:
        """

        :return:
        """
        show = False  # type: bool
        if self._total_albums:
            if any(self.m_albums.IsChecked(index) for index in range(self._total_albums)):
                show = True
        self.m_SyncButton.Enable(show)

    def _enable_run(self) -> None:
        """

        :return:
        """
        self.m_RunButton.Enable(self._synced)

    def _click_on_checkall(self, event) -> None:
        """

        :param event:
        :return:
        """
        self._toggle_allalbums(self.m_CheckAllButton.GetValue())
        self.m_CheckAllButton.SetValue(not self.m_CheckAllButton.GetValue())
        self._enable_checkall()
        self._enable_sync()
        self._enable_run()
        self.Layout()

    def _click_on_run(self, event) -> None:
        """

        :param event:
        :return:
        """
        self._sync = True
        self.Close(True)

    def _click_on_sync(self, event) -> None:
        """

        :param event:
        :return:
        """
        for index in range(self._total_albums):
            if self.m_albums.IsChecked(index):
                self._synced += 1
                album_path, albumid = self._albums[self.m_albums.GetString(index)]
                self._arguments.append((album_path, os.path.join(self._destination, albumid), self._extensions))
                self.m_albums.Check(index, check=False)
        self._init_albums()
        self.m_artists.Check(self._artistid, check=False)
        self._artistid = None
        self._repositoryid = None
        self._enable_checkall()
        self._enable_sync()
        self._enable_run()
        self._set_statusbar(self._repository, "Choose an artist or click Run button", "")
        self.Layout()

    def _click_on_close(self, event) -> None:
        """

        :param event:
        :return:
        """
        self.Close(True)

    def _toggle_allalbums(self, check) -> None:
        """

        :return:
        """
        for index in range(self._total_albums):
            self.m_albums.Check(index, check=check)

    @property
    def sync_audiofiles(self):
        return self._sync

    @property
    def sync_arguments(self):
        return self._arguments


# ============
# Main script.
# ============
if __name__ == '__main__':

    that_script = os.path.abspath(__file__)

    # Define variables.
    collection, level = [], 100  # type: List[Tuple[str, str]], int

    # Define template.
    template = TemplatingEnvironment(loader=jinja2.FileSystemLoader(get_dirname(that_script)))
    template.set_template(T1="T01")

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
    interface = MainFrame(None, os.path.join(get_dirname(that_script, level=2), "Resources", "resource1.yml"))
    interface.Show()
    app.MainLoop()
    if interface.sync_audiofiles:
        level = 0
        for source, destination, extensions in interface.sync_arguments:
            for dirname, dirnames, filenames in os.walk(source):
                if not dirnames:
                    if filenames:
                        for extension in extensions:
                            if set(find_files(dirname, excluded=partial(exclude_allbut_checked_extensions, extensions=[extension]))):
                                collection.append((os.path.join(dirname, f"*.{extension}"), destination))
        arguments.outfile.write(getattr(template, "T1").render(collection=collection))

    # Exit script.
    sys.exit(level)
