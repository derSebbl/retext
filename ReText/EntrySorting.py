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
