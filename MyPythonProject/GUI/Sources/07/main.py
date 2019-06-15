# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# Frame generated with wxFormBuilder (version Jun 17 2015)
# http://www.wxformbuilder.org/
import locale
import os
from contextlib import suppress
from functools import partial
from operator import itemgetter
from typing import Any, Iterable, List, Optional, Tuple, Union

import wx  # type: ignore

from Applications.Tables.RippedDiscs.shared import get_rippeddiscs
from Applications.shared import DATABASE, advanced_grouper

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# ======
# Frame.
# ======
class MainFrame(wx.Frame):

    def __init__(self, parent, *args: str) -> None:
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="Digital Albums", pos=wx.DefaultPosition, size=wx.Size(933, 524), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        # -----
        self._fields, self._indexes, self._pathname = None, None, None  # type: Optional[List[str]], Optional[List[int]], Optional[str]
        self._centralindex, self._rightindex = None, None  # type: Optional[int], Optional[int]
        self._args = args  # type: Tuple[str, ...]

        # -----
        self._init_interface()

        # -----
        self._reset_interface()

    def _init_interface(self) -> None:
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetFont(wx.Font(9, 74, 90, 90, False, "Arial"))
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))

        # -----------------------
        # Browse output XML file.
        # -----------------------
        self._xml = wx.Button(self, wx.ID_ANY, "XML File", wx.DefaultPosition, wx.Size(70, 30), 0)

        # ----------------
        # Configure lists.
        # ----------------
        Sizer1 = wx.BoxSizer(wx.HORIZONTAL)

        # Available fields.
        Sizer1a = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Fields"), wx.VERTICAL)
        self._leftpane = wx.ListCtrl(Sizer1a.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(150, 100), wx.LC_REPORT)
        self._leftpane.InsertColumn(0, "Name")
        self._leftpane.SetColumnWidth(0, 100)
        Sizer1a.Add(self._leftpane, 1, wx.EXPAND, 0)

        # Picked up  fields for sorting.
        Sizer1b = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Order by"), wx.VERTICAL)
        self._centralpane = wx.ListCtrl(Sizer1b.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(150, 100), wx.LC_REPORT | wx.LC_VRULES)
        self._centralpane.SetDropTarget(CentralDropTarget(self, self._centralpane))
        Sizer1b.Add(self._centralpane, 1, wx.EXPAND, 0)

        # Picked up field for grouping.
        Sizer1c = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Group by"), wx.VERTICAL)
        self._rightpane = wx.ListCtrl(Sizer1c.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(150, 100), wx.LC_REPORT)
        self._rightpane.SetDropTarget(RightDropTarget(self, self._rightpane))
        Sizer1c.Add(self._rightpane, 1, wx.EXPAND, 0)

        # ------------------
        # Configure buttons.
        # ------------------
        Sizer2a = wx.BoxSizer(wx.HORIZONTAL)

        # --> OK.
        self._ok = wx.Button(self, wx.ID_ANY, "OK", wx.DefaultPosition, wx.Size(70, 30), 0)
        Sizer2a.Add(self._ok, 0, wx.ALL, 5)

        # --> Cancel.
        self._cancel = wx.Button(self, wx.ID_ANY, "Cancel", wx.DefaultPosition, wx.Size(70, 30), 0)
        Sizer2a.Add(self._cancel, 0, wx.ALL, 5)

        # --> Reset.
        self._reset = wx.Button(self, wx.ID_ANY, "Reset", wx.DefaultPosition, wx.Size(70, 30), 0)
        Sizer2a.Add(self._reset, 0, wx.ALL, 5)

        # -----------------
        # Configure layout.
        # -----------------
        Sizer2 = wx.BoxSizer(wx.VERTICAL)
        Sizer2.Add(Sizer2a, 0, wx.ALL | wx.EXPAND, 5)
        Sizer1.Add(Sizer1a, 1, wx.ALL | wx.EXPAND, 5)
        Sizer1.Add(Sizer1b, 1, wx.ALL | wx.EXPAND, 5)
        Sizer1.Add(Sizer1c, 1, wx.ALL | wx.EXPAND, 5)
        MainSizer = wx.BoxSizer(wx.VERTICAL)
        MainSizer.Add(self._xml, 0, wx.ALL, 10)
        MainSizer.Add(Sizer1, 1, wx.ALL | wx.EXPAND, 5)
        MainSizer.Add(Sizer2, 0, 0, 5)
        self.SetSizer(MainSizer)
        self.Layout()
        self.Centre(wx.BOTH)

        # -----------------
        # Configure events.
        # -----------------
        self._xml.Bind(wx.EVT_BUTTON, self._on_xml_clicked)
        self._ok.Bind(wx.EVT_BUTTON, self._on_ok_clicked)
        self._cancel.Bind(wx.EVT_BUTTON, self._on_cancel_clicked)
        self._reset.Bind(wx.EVT_BUTTON, self._on_reset_clicked)
        self._leftpane.Bind(wx.EVT_LIST_BEGIN_DRAG, self._on_dragged_from_leftpane)
        self._leftpane.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_leftpane_dblclicked)
        self._centralpane.Bind(wx.EVT_LIST_BEGIN_DRAG, self._on_dragged_from_centralpane)
        self._centralpane.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_centralpane_dblclicked)

    def _reset_interface(self) -> None:
        self._ok.Enable(False)
        self._fields = list(self._args)
        self._rightpane.DeleteAllItems()
        self._centralpane.DeleteAllItems()
        self._leftpane.DeleteAllItems()
        self._centralindex = 0
        self._rightindex = 0
        for index, field in enumerate(self._fields):
            self._leftpane.InsertItem(index, field)

    def _on_xml_clicked(self, event) -> None:
        """

        :param event:
        :return:
        """
        with wx.FileDialog(self, "Save XML file", wildcard="XML files (*.xml)|*.xml", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_OK:
                self._pathname = fileDialog.GetPath()
                self._ok.Enable(True)

    def _on_dragged_from_leftpane(self, event) -> None:
        """

        :param event:
        :return:
        """
        index = self._leftpane.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)  # type: int
        text = self._leftpane.GetItemText(index)  # type: str
        dragged_text = wx.TextDataObject(text)
        src = wx.DropSource(self._leftpane)
        src.SetData(dragged_text)
        if src.DoDragDrop(True) == wx.DragMove:
            self._update_leftpane(text)

    def _on_dragged_from_centralpane(self, event) -> None:
        """

        :param event:
        :return:
        """
        index = self._centralpane.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)  # type: int
        text = self._centralpane.GetItemText(index)  # type: str
        dragged_text = wx.TextDataObject(text)
        src = wx.DropSource(self._centralpane)
        src.SetData(dragged_text)
        src.DoDragDrop(True)

    def _on_leftpane_dblclicked(self, event):
        """

        :param event:
        :return:
        """
        index = self._leftpane.GetNextItem(-1, geometry=wx.LIST_NEXT_ALL, state=wx.LIST_STATE_SELECTED)  # type: int
        text = self._leftpane.GetItemText(index, 0)  # type: str

        # Insert data into central pane.
        self._centralpane.InsertItem(self._centralindex, text)
        self._centralpane.SetItem(self._centralindex, 1, "False")
        self._centralindex += 1

        # Remove data from left pane.
        self._update_leftpane(text)

    def _on_centralpane_dblclicked(self, event) -> None:
        """

        :param event:
        :return:
        """
        index = self._centralpane.GetNextItem(-1, geometry=wx.LIST_NEXT_ALL, state=wx.LIST_STATE_SELECTED)  # type: int
        value = self._centralpane.GetItemText(index, 1)  # type: str
        if value.lower() == "false":
            self._centralpane.SetItem(index, 1, "True")
        elif value.lower() == "true":
            self._centralpane.SetItem(index, 1, "False")

    def _on_ok_clicked(self, event) -> None:
        """

        :param event:
        :return:
        """
        get_list_indexes = partial(self._get_list_indexes, iterable=self._args)

        # -----
        items = ((self._centralpane.GetItemText(index, 0), self._centralpane.GetItemText(index, 1)) for index in self._get_listctrl_indexes(self._centralpane))
        orderby = list(map(get_list_indexes, map(self._convert_string_to_boolean, items)))
        orderby.reverse()
        orderby = iter(orderby)

        # -----
        items = ((self._rightpane.GetItemText(index, 0), index) for index in self._get_listctrl_indexes(self._rightpane))
        groupby = iter(map(get_list_indexes, items))

        # ----- Get collection.
        collection = [(disc.artistsort,
                       disc.albumsort,
                       disc.disc,
                       disc.ripped_year,
                       disc.ripped_month,
                       disc.ripped,
                       disc.genre,
                       "{0}{1:0>2d}".format(disc.ripped_year, disc.ripped_month),
                       disc.album,
                       disc.origyear,
                       disc.year,
                       disc.upc,
                       disc.tracks,
                       disc.bootleg)
                      for disc in get_rippeddiscs(db=DATABASE)]  # type: Any

        # ----- Sort collection.
        while True:
            try:
                list_index, reverse = next(orderby)  # type: int, bool
            except StopIteration:
                break
            collection = sorted(collection, key=itemgetter(list_index), reverse=reverse)

        # ----- Group collection (at most two groupby fields).
        key, _ = next(groupby)  # type: int, int
        subkey = None  # type: Optional[int]
        with suppress(StopIteration):
            subkey, _ = next(groupby)
        collection = list(advanced_grouper(collection, key=key, subkey=subkey))

        # -----
        print(collection)
        # ET.ElementTree(rippeddiscs(collection=groupby(collection, key=itemgetter(2)))).write(os.path.join(os.path.expandvars("%TEMP%"), "rippeddiscs.xml"), encoding=UTF8, xml_declaration=True)
        wx.MessageBox("XML output created", "some title", style=wx.OK | wx.ICON_INFORMATION)
        self._reset_interface()

    def _on_cancel_clicked(self, event) -> None:
        """

        :param event:
        :return:
        """
        self.Close()

    def _on_reset_clicked(self, event) -> None:
        """

        :param event:
        :return:
        """
        self._reset_interface()

    def _update_leftpane(self, arg) -> None:
        if self._leftpane.DeleteAllItems():
            self._fields.pop(self._fields.index(arg))
            for index, field in enumerate(self._fields):
                self._leftpane.InsertItem(index, field)

    @staticmethod
    def _get_listctrl_indexes(panel, geometry=wx.LIST_NEXT_ALL, state=wx.LIST_STATE_DONTCARE) -> Iterable[int]:
        index = -1
        while True:
            index = panel.GetNextItem(index, geometry, state)
            if index == -1:
                break
            yield index

    @staticmethod
    def _get_list_indexes(two_item_tuple, iterable) -> Tuple[int, bool]:
        field, bool_string = two_item_tuple
        return iterable.index(field), bool_string

    @staticmethod
    def _convert_string_to_boolean(two_item_tuple) -> Tuple[str, Union[bool, str]]:
        field, bool_string = two_item_tuple
        if bool_string.lower() == "false":
            return field, False
        elif bool_string.lower() == "true":
            return field, True
        return field, bool_string

    @property
    def centralindex(self) -> int:
        return self._centralindex

    @centralindex.setter
    def centralindex(self, arg) -> None:
        self._centralindex = arg  # type: int

    @property
    def rightindex(self) -> int:
        return self._centralindex

    @rightindex.setter
    def rightindex(self, arg) -> None:
        self._rightindex = arg  # type: int

    @property
    def indexes(self) -> List[int]:
        return self._indexes

    @indexes.setter
    def indexes(self, arg) -> None:
        pane, geometry, state = arg
        if geometry is None:
            geometry = wx.LIST_NEXT_ALL
        if state is None:
            state = wx.LIST_STATE_DONTCARE
        self._indexes = list(self._get_listctrl_indexes(pane, geometry, state))  # type: List[int]

    @property
    def centralpane(self):
        return self._centralpane

    @property
    def rightpane(self):
        return self._rightpane

    @property
    def ok_button(self):
        return self._ok


class DropTarget(wx.TextDropTarget):
    def __init__(self, parent, pane):
        wx.TextDropTarget.__init__(self)
        self._parent = parent
        self._pane = pane


class CentralDropTarget(DropTarget):
    def __init__(self, parent, pane):
        DropTarget.__init__(self, parent, pane)
        self._pane.InsertColumn(0, "Field")
        self._pane.SetColumnWidth(0, 100)
        self._pane.InsertColumn(1, "Reverse")
        self._pane.SetColumnWidth(1, 100)

    def OnDropText(self, x, y, data):
        self._pane.InsertItem(self._parent.centralindex, data)
        self._pane.SetItem(self._parent.centralindex, 1, "False")
        self._parent.centralindex += 1
        return True


class RightDropTarget(DropTarget):
    def __init__(self, parent, pane):
        DropTarget.__init__(self, parent, pane)
        self._pane.InsertColumn(0, "Field")
        self._pane.SetColumnWidth(0, 100)

    def OnDropText(self, x, y, data):

        # -----
        if self._pane.GetItemCount() == 2:
            wx.MessageBox("Can't append any additional groupby field.", "An error occured", style=wx.OK | wx.ICON_EXCLAMATION)
            return False

        # -----
        self._parent.indexes = (self._parent.centralpane, None, None)
        orderby = [self._parent.centralpane.GetItemText(index, 0) for index in self._parent.indexes]
        self._parent.indexes = (self._pane, None, None)
        groupby = [self._pane.GetItemText(index, 0) for index in self._parent.indexes]
        groupby.append(data)
        if not set(groupby).issubset(set(orderby)):
            wx.MessageBox(f"Can't append '{data}' as groupby field. Limit reached.", "An error occured", style=wx.OK | wx.ICON_EXCLAMATION)
            return False

        # -----
        self._pane.InsertItem(self._parent.rightindex, data)
        self._parent.rightindex += 1
        return True


# ============
# Main script.
# ============
if __name__ == '__main__':
    that_file = os.path.abspath(__file__)
    locale.setlocale(locale.LC_ALL, "french")
    app = wx.App()
    interface = MainFrame(None, "artistsort", "albumsort", "discid", "ripped_year", "ripped_month", "rippde_date", "genre")
    interface.Show()
    app.MainLoop()
