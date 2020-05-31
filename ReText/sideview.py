from PyQt5 import QtCore
from PyQt5.Qt import QDir, QListView, QStringListModel
from PyQt5.QtCore import QFile, QTextStream, QObject
from PyQt5.QtWidgets import QAbstractItemView


class DirListerFilenames:
    def listEntries(self, dir: QDir) -> [str]:
        dir.setNameFilters(["*.md"])
        nameList = []
        for fileInfo in dir.entryInfoList():
            nameList.append(fileInfo.completeBaseName())
        return nameList

class DirListerFolders:
    def listEntries(self, dir: QDir) -> [str]:
        dir.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)
        nameList = []
        for fileInfo in dir.entryInfoList():
            nameList.append(fileInfo.completeBaseName())
        return nameList

class SortingParser:
    def __init__(self, sortingFilePath : str):
        self.sortedEntries = []

        self.sortingFile = QFile(sortingFilePath)

        if not self.sortingFile.exists():
            self.sortingFile.open(QFile.WriteOnly | QFile.Text)

    def __getSortingFileEntries(self) -> [str]:
        if not self.sortingFile.open(QFile.ReadOnly | QFile.Text):
            return []

        sortingFileEntries = []

        inStream = QTextStream(self.sortingFile)
        while not inStream.atEnd():
            line = inStream.readLine()  # A QByteArray
            sortingFileEntries.append(line)

        self.sortingFile.close()

        return sortingFileEntries

    def __getDifference(self, actualContents : [str], eventuallyDifferentContents : [str]) -> [str]:
        result = []

        for item in actualContents:
            if not eventuallyDifferentContents.__contains__(item):
                result.append(item)

        return result

    def getSortedList(self, items : [str]) -> [str]:
        sortingFileEntries = self.__getSortingFileEntries()

        newItems = [x for x in items if x not in sortingFileEntries]

        sortingFileItemsWithNewContents = sortingFileEntries + newItems

        #remove all items which are not existing anymore
        sortedEntries = [x for x in sortingFileItemsWithNewContents if x in items]

        self.sortedEntries = sortedEntries

        if sortedEntries != sortingFileEntries:
            self.__saveSortingFile()

        return self.sortedEntries

    def __saveSortingFile(self):
        if not self.sortingFile.open(QFile.WriteOnly | QFile.Text):
            return

        s = QTextStream(self.sortingFile)
        for item in self.sortedEntries:
            s << item << '\n'

        self.sortingFile.close()


class SideView(QObject):
    def __init__(self, dirLister):
        self.listView = QListView()
        self.currentDir = None
        self.model = QStringListModel()
        self.directoryLister = dirLister
        self.sortingParser = None

        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView.setModel(self.model)

        self.listView.selectionModel().selectionChanged.connect(self.selectionChanged)

    def selectionChanged(self, selectedItem, unselectedItem):
        self.refreshListViewEntries()
        pass

    def setDirectory(self, dirPath: str):
        self.currentDir = QDir(dirPath)
        self.sortingParser = SortingParser(self.currentDir.filePath('.sorting'))
        self.refreshListViewEntries()


    def refreshListViewEntries(self):
        entries = self.directoryLister.listEntries(self.currentDir)
        sortedEntries = self.sortingParser.getSortedList(entries)
        
        self.model.setStringList(sortedEntries)