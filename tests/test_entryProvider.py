import sys
import unittest

from PyQt5 import Qt
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QApplication

from ReText.EntryProvider import EntryProviderDirectory, EntryProviderFile

#QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
app = QApplication.instance() or QApplication(sys.argv)

class TestEntriesDir(unittest.TestCase):
    def setUp(self) -> None:
        self.newItemDefaultName = "New Notebook"
        self.itemProvider = EntryProviderDirectory(self.newItemDefaultName)
        dir = QDir('/tmp')
        dir.mkdir('retext_itemprovider_tests')
        dir.cd('retext_itemprovider_tests')
        self.testDir = dir
        self.itemProvider.setDirectory("/tmp/retext_itemprovider_tests")

    def tearDown(self) -> None:
        self.testDir.removeRecursively()

    def test_newEntry(self):
        self.itemProvider.addEntry("1")

    def test_newEntryTwice(self):
        self.itemProvider.addEntry("2")
        with self.assertRaises(Exception):
            self.itemProvider.addEntry("2")

    def test_renameEntry(self):
        self.itemProvider.addEntry("3")
        self.itemProvider.renameEnty("3", "3_renamed")

    def test_removeEntry(self):
        self.itemProvider.addEntry("4")
        self.itemProvider.removeEntry("4")

    def test_newItemDefaultName(self):
        with self.assertRaises(Exception):
            self.itemProvider.addEntry(self.newItemDefaultName)


class TestEntriesFiles(unittest.TestCase):
    def setUp(self) -> None:
        self.newItemDefaultName = "NewEntry.md"
        self.itemProvider = EntryProviderFile(self.newItemDefaultName)
        dir = QDir('/tmp')
        dir.mkdir('retext_itemprovider_tests')
        dir.cd('retext_itemprovider_tests')
        self.testDir = dir
        self.itemProvider.setDirectory("/tmp/retext_itemprovider_tests")

    def tearDown(self) -> None:
        self.testDir.removeRecursively()

    def test_newEntry(self):
        self.itemProvider.addEntry("1.md")

    def test_newEntryTwice(self):
        self.itemProvider.addEntry("2.md")
        with self.assertRaises(Exception):
            self.itemProvider.addEntry("2.md")

    def test_renameEntry(self):
        self.itemProvider.addEntry("3.md")
        self.itemProvider.renameEnty("3.md", "3_renamed.md")

    def test_removeEntry(self):
        self.itemProvider.addEntry("4.md")
        self.itemProvider.removeEntry("4.md")

    def test_newItemDefaultName(self):
        with self.assertRaises(Exception):
            self.itemProvider.addEntry(self.newItemDefaultName)