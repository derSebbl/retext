import sys

from PyQt5 import QtGui
from PyQt5.Qt import QDir, QListView, QStringListModel
from PyQt5.QtCore import QFileInfo, Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import QAbstractItemView, QLineEdit, QAction, QMenu

from ReText.EntryProvider import IEntryProvider, EntryProviderDirectory, EntryProviderFile
from ReText.EntrySorting import EntrySortingFile
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

    def __init__(self, dirLister, entryProvider: IEntryProvider, newEntryText: str,
                 itemNameNormalizer: IItemNameNormalizer, onItemSelectedCallback):
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
                onItemSelectedCallback(
                    self.itemNameNormalizer.normalizeName(self.currentDir.filePath(selectedItem.data())))
            )

            def contextMenu(position):
                menu = QMenu()
                deleteAction = menu.addAction("Delete")
                chosenAction = menu.exec_(self.listView.mapToGlobal(position))
                if chosenAction == deleteAction:
                    index = self.listView.indexAt(position)
                    entry = self.model.data(index, Qt.DisplayRole)
                    self.removeEntry(index, entry)

            self.listView.customContextMenuRequested.connect(contextMenu)
            self.listView.setContextMenuPolicy(Qt.CustomContextMenu)

        self.currentDir: QDir
        self.model = QStringListModel()
        self.directoryLister = dirLister
        self.entryProvider = entryProvider
        self.newEntryText = newEntryText
        self.itemNameNormalizer = itemNameNormalizer
        self.sortingParser = None
        initListView()

    def removeEntry(self, index, entry):
        normalizedName = self.itemNameNormalizer.normalizeName(entry)

        self.onBeforeItemDeletion.emit(self.currentDir.filePath(normalizedName))

        self.entryProvider.removeEntry(normalizedName)
        self.refreshListViewEntries()

    def setDirectory(self, dirPath: str):
        self.currentDir = QDir(dirPath)
        self.sortingParser = EntrySortingFile(self.currentDir.filePath('.sorting'))
        self.entryProvider.setContext(dirPath)
        self.refreshListViewEntries()

    def refreshListViewEntries(self):
        entries = self.directoryLister.listEntries(self.currentDir)
        sortedEntries = self.sortingParser.getSortedList(entries)
        
        self.model.setStringList(sortedEntries)

    def createNewEntryTriggered(self):
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
    def createPagesSideView(openItemAction) -> SideView:
        newPageText = 'New Page'
        return SideView(
            DirListerFilenames(),
            EntryProviderFile(),
            newPageText,
            ItemNameNormalizerPage(),
            openItemAction
        )

    @staticmethod
    def createNotebooksSideView(sideViewPages: SideView) -> SideView:
        newNotebookText = 'New Notebook'
        return SideView(
            DirListerFolders(),
            EntryProviderDirectory(),
            newNotebookText,
            ItemNameNormalizerDefault(),
            lambda selectedItem: sideViewPages.setDirectory(selectedItem)
        )
