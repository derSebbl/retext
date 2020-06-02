from PyQt5.QtCore import QFile, QTextStream


class IEntrySorting:
    def getSortedList(self, items: [str]) -> [str]:
        pass

    def addEntry(self, entry: str):
        pass

class EntrySortingFile:
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
            if item not in eventuallyDifferentContents:
                result.append(item)

        return result

    def getSortedList(self, items: [str]) -> [str]:
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

    def addEntry(self, entry):
        self.sortedEntries.append(entry)
        self.__saveSortingFile()
