from PyQt5.QtCore import QDir, QFile


class IEntryProvider:
    def isEntryValid(self, entry: str) -> bool:
        pass

    def addEntry(self, entry: str):
        pass

    def removeEntry(self, entry: str):
        pass

    def renameEnty(self, oldName: str, newName: str):
        pass


class EntryProviderParent(IEntryProvider):
    def __init__(self, invalidNewEntryName: str):
        self.invalidNewEntryName = invalidNewEntryName
        self.parentDir = QDir()

    def setDirectory(self, dirPath: str):
        self.parentDir = QDir(dirPath)

    def isEntryValid(self, entry: str) -> bool:
        # if already exists
        if entry in self.parentDir:
            return False
        if entry is self.invalidNewEntryName:
            return False
        return True

    def removeEntry(self, entry: str):
        self.parentDir.remove(entry)

    def renameEnty(self, oldName: str, newName: str):
        self.parentDir.rename(oldName, newName)


class EntryProviderDirectory(EntryProviderParent):
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
