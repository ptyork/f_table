"""Unit tests for ColDefList creation, slicing, and mutation."""

import unittest
from craftable import ColDefList, ColDef


class TestColDefList(unittest.TestCase):
    """ColDefList API conformance and behaviors."""

    def test_create_and_slice(self):
        cds = ColDefList(["<10", ">15", "^20"])
        self.assertEqual(cds[0].width, 10)
        self.assertEqual(len(cds[0:2]), 2)

    def test_for_table(self):
        cds = ColDefList.for_table([["Short", "Medium"], ["A", "Longer text here"]])
        self.assertEqual(len(cds), 2)

    def test_append_string(self):
        cds = ColDefList()
        cds.append("<15")
        self.assertEqual(cds[0].width, 15)

    def test_append_coldef(self):
        cds = ColDefList()
        cds.append(ColDef(width=25))
        self.assertEqual(cds[0].width, 25)

    def test_getitem_and_setitem(self):
        cds = ColDefList(["<10", ">15"])
        self.assertEqual(cds[0].width, 10)
        cds[0] = "<20"
        self.assertEqual(cds[0].width, 20)
        cds[1] = ColDef(width=30)
        self.assertEqual(cds[1].width, 30)
