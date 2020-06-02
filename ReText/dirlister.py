from PyQt5.QtCore import QDir


class IDirLister:
    def listEntries(self, dir: QDir) -> [str]:
        pass

class DirListerFilenames(IDirLister):
    def listEntries(self, dir: QDir) -> [str]:
        dir.setNameFilters(["*.md"])
        fileNames = []
        for fileInfo in dir.entryInfoList():
            fileNames.append(fileInfo.completeBaseName())
        return fileNames


class DirListerFolders(IDirLister):
    def listEntries(self, dir: QDir) -> [str]:
        dir.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)
        folderNames = []
        for fileInfo in dir.entryInfoList():
            folderNames.append(fileInfo.fileName())
        return folderNames