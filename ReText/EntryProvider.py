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


from PyQt5.QtCore import QDir, QFile


class IEntryProvider:
    def setContext(self, context: str):
        pass

    def isEntryValid(self, entry: str) -> bool:
        pass

    def addEntry(self, entry: str):
        pass

    def removeEntry(self, entry: str):
        pass

    def renameEnty(self, oldName: str, newName: str):
        pass


class EntryProviderParent(IEntryProvider):
    def __init__(self):
        self.parentDir = QDir()

    def setContext(self, context: str):
        self.setDirectory(context)

    def setDirectory(self, dirPath: str):
        self.parentDir = QDir(dirPath)

    def isEntryValid(self, entry: str) -> bool:
        # if already exists
        if entry in self.parentDir:
            return False
        return True

    def removeEntry(self, entry: str):
        if not self.parentDir.remove(entry):
            raise Exception("Failed to remove entry")

    def renameEnty(self, oldName: str, newName: str):
        if not self.parentDir.rename(oldName, newName):
            raise Exception("Rename Failed")


class EntryProviderDirectory(EntryProviderParent):
    def removeEntry(self, entry: str):
        if not QDir(self.parentDir.filePath(entry)).removeRecursively():
            raise Exception("Failed to remove entry")

    def addEntry(self, entry: str):
        if not self.isEntryValid(entry):
            raise Exception(f"Error creating directory {entry}, invalid name")
        if not self.parentDir.mkdir(entry):
            raise Exception(f"Error creating directory {entry}")
        self.parentDir.refresh()


class EntryProviderFile(EntryProviderParent):
    def addEntry(self, entry: str):
        if not self.isEntryValid(entry):
            raise Exception(f"Error creating file: {entry}, invalid name")
        newFile = QFile(self.parentDir.filePath(entry))
        if not newFile.open(QFile.ReadWrite | QFile.Text):
            raise Exception(f"Error creating file: {entry}")
        self.parentDir.refresh()
