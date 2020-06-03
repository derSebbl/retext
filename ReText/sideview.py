# This file is part of ReText
# Copyright: 2020 Sebastian Michel
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys

from PyQt5 import QtGui
from PyQt5.Qt import QDir, QListView, QStringListModel
from PyQt5.QtCore import QFileInfo, Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import QAbstractItemView, QLineEdit, QAction, QMenu

from ReText.EntryProvider import IEntryProvider, EntryProviderDirectory, EntryProviderFile
from ReText.EntrySorting import EntrySortingFile, IEntrySorting
from ReText.dirlister import DirListerFilenames, DirListerFolders


class IItemNameNormalizer:
    def normalizeName(self, name) -> str:
        pass


class ItemNameNormalizerDefault(IItemNameNormalizer):
    def normalizeName(self, name) -> str:
        return name


class ItemNameNormalizerPage(IItemNameNormalizer):
    def normalizeName(self, name) -> str:
        fileInfo = QFileInfo(name)
        if fileInfo.suffix() == "md":
            return name
        else:
            return name + '.md'


class SideView(QObject):
    onBeforeItemDeletion = pyqtSignal(str)
    onEntrySelected = pyqtSignal(str)
    onDirectoryChanged = pyqtSignal(str)
    onRemoveRequested = pyqtSignal(str)

    def __init__(self, dirLister, entryProvider: IEntryProvider, newEntryText: str,
                 itemNameNormalizer: IItemNameNormalizer):
        super().__init__()

        def initListView():
            self.listView = QListView()
            self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.listView.setModel(self.model)
            self.listView.setMinimumWidth(200)

            actionRemove = QAction("Remove", None)
            self.listView.addAction(actionRemove)

            self.listView.selectionModel().currentChanged.connect(
                lambda selectedItem, unselectedItem:
                self.onEntrySelected.emit(
                    self.itemNameNormalizer.normalizeName(self.currentDir.filePath(selectedItem.data())))
            )

            def contextMenu(position):
                menu = QMenu()
                index = self.listView.indexAt(position)
                entry = self.model.data(index, Qt.DisplayRole)

                deleteAction = None
                renameAction = None

                addAction = menu.addAction("Add")

                if entry is not None:
                    deleteAction = menu.addAction("Delete")
                    renameAction = menu.addAction("Rename")

                refreshAction = menu.addAction("Refresh")

                chosenAction = menu.exec_(self.listView.mapToGlobal(position))

                if chosenAction is None:
                    return

                if chosenAction == deleteAction:
                    self.onRemoveRequested.emit(entry)
                elif chosenAction == renameAction:
                    self.renameEntry(index,entry)
                elif chosenAction == addAction:
                    self.onCreateNewEntry()
                elif chosenAction == refreshAction:
                    self.refreshListViewEntries()

            self.listView.customContextMenuRequested.connect(contextMenu)
            self.listView.setContextMenuPolicy(Qt.CustomContextMenu)

        self.currentDir: QDir = None
        self.model = QStringListModel()
        self.directoryLister = dirLister
        self.entryProvider = entryProvider
        self.newEntryText = newEntryText
        self.itemNameNormalizer = itemNameNormalizer
        self.sortingParser: IEntrySorting
        initListView()

    def renameEntry(self, index, oldName):
        def onNewEntryCommited(editedLine: QLineEdit):
            self.listView.itemDelegate().commitData.disconnect(onNewEntryCommited)
            try:
                newName = editedLine.text()
                normalizedNameOld = self.itemNameNormalizer.normalizeName(oldName)
                normalizedNameNew = self.itemNameNormalizer.normalizeName(newName)

                self.emitOnItemDeletion(normalizedNameOld)

                self.entryProvider.renameEnty(normalizedNameOld, normalizedNameNew)
                self.sortingParser.rename(oldName, newName)
                self.refreshListViewEntries()
            except Exception:
                pass

        self.listView.itemDelegate().commitData.connect(onNewEntryCommited)
        self.listView.edit(index)

    def emitOnItemDeletion(self, normalizedName):
        self.onBeforeItemDeletion.emit(self.currentDir.filePath(normalizedName))

    def removeEntry(self, entry):
        normalizedName = self.itemNameNormalizer.normalizeName(entry)
        self.emitOnItemDeletion(normalizedName)

        self.entryProvider.removeEntry(normalizedName)
        self.refreshListViewEntries()

    def setDirectory(self, dirPath: str):
        self.currentDir = QDir(dirPath)
        self.sortingParser = EntrySortingFile(self.currentDir.filePath('.sorting'))
        self.entryProvider.setContext(dirPath)
        self.refreshListViewEntries()

        self.onDirectoryChanged.emit(self.currentDir.absolutePath())

    def refreshListViewEntries(self):
        if self.currentDir is None:
            return
        entries = self.directoryLister.listEntries(self.currentDir)
        sortedEntries = self.sortingParser.getSortedList(entries)
        
        self.model.setStringList(sortedEntries)

    def onCreateNewEntry(self):
        def onNewEntryCommited(editedLine: QLineEdit):
            self.listView.itemDelegate().commitData.disconnect(onNewEntryCommited)
            try:
                if editedLine.text() == self.newEntryText:
                    raise Exception()

                normalizedName = self.itemNameNormalizer.normalizeName(editedLine.text())
                self.entryProvider.addEntry(normalizedName)
                self.refreshListViewEntries()
                self.listView.setCurrentIndex(index)
            except Exception:
                print(f"Error adding entry {editedLine.text()}", file=sys.stderr)
                self.model.removeRow(self.model.rowCount() -1)

        if not self.model.insertRow(self.model.rowCount()):
            return

        self.listView.itemDelegate().commitData.connect(onNewEntryCommited)
        index = self.model.index(self.model.rowCount() - 1, 0)
        self.model.setData(index, self.newEntryText)
        self.listView.edit(index)
        pass


class SideViewFactory:
    @staticmethod
    def createPagesSideView() -> SideView:
        newPageText = 'New Page'
        return SideView(
            DirListerFilenames(),
            EntryProviderFile(),
            newPageText,
            ItemNameNormalizerPage()
        )

    @staticmethod
    def createNotebooksSideView() -> SideView:
        newNotebookText = 'New Notebook'
        return SideView(
            DirListerFolders(),
            EntryProviderDirectory(),
            newNotebookText,
            ItemNameNormalizerDefault()
        )
