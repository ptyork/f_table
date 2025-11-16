"""Tests for none_text handling to ensure per-column ColDef.none_text takes precedence."""

from craftable import get_table, get_table_row, export_table, ColDefList
from io import StringIO
import unittest


class TestNoneTextPrecedence(unittest.TestCase):
    """Per-column none_text should override global none_text parameter."""

    def test_coldef_none_text_overrides_global_in_get_table(self):
        rows = [[None, None, None]]
        headers = ["Col1", "Col2", "Col3"]
        col_defs = ColDefList.parse(["10", "10", "10"])
        col_defs[0].none_text = "N/A"
        col_defs[1].none_text = "MISSING"
        result = get_table(
            rows,
            header_row=headers,
            col_defs=col_defs,
            none_text="(empty)",
        )
        self.assertIn("N/A", result)
        self.assertIn("MISSING", result)
        self.assertIn("(empty)", result)
        lines = result.split("\n")
        data_line = [line for line in lines if "N/A" in line or "MISSING" in line][0]
        self.assertIn("N/A", data_line)
        self.assertIn("MISSING", data_line)
        self.assertIn("(empty)", data_line)

    def test_coldef_none_text_overrides_global_in_get_table_row(self):
        row = [None, None, None]
        col_defs = ColDefList.parse(["10", "10", "10"])
        col_defs[0].none_text = "FIRST"
        col_defs[1].none_text = "SECOND"
        result = get_table_row(
            row,
            col_defs=col_defs,
            none_text="GLOBAL",
        )
        self.assertIn("FIRST", result)
        self.assertIn("SECOND", result)
        self.assertIn("GLOBAL", result)

    def test_coldef_none_text_overrides_global_in_export_table(self):
        rows = [[None, None]]
        headers = ["A", "B"]
        col_defs = ColDefList.parse(["10", "10"])
        col_defs[0].none_text = "COL_A"
        output = StringIO()
        export_table(
            rows,
            header_row=headers,
            col_defs=col_defs,
            none_text="GLOBAL_VAL",
            file=output,
        )
        result = output.getvalue()
        self.assertIn("COL_A", result)
        self.assertIn("GLOBAL_VAL", result)

    def test_global_none_text_used_when_coldef_none_text_empty(self):
        rows = [[None, None]]
        col_defs = ColDefList.parse(["10", "10"])
        result = get_table(
            rows,
            col_defs=col_defs,
            none_text="---",
        )
        self.assertEqual(result.count("---"), 2)

    def test_empty_coldef_none_text_uses_global(self):
        rows = [[None, None]]
        col_defs = ColDefList.parse(["10", "10"])
        col_defs[0].none_text = ""
        col_defs[1].none_text = "SECOND"
        result = get_table(
            rows,
            col_defs=col_defs,
            none_text="GLOBAL",
        )
        self.assertIn("SECOND", result)
        self.assertIn("GLOBAL", result)

    def test_mixed_none_and_values_with_coldef_none_text(self):
        rows = [
            [None, 42, None],
            ["Alice", None, "data"],
        ]
        headers = ["Name", "Age", "Info"]
        col_defs = ColDefList.parse(["10", "5", "10"])
        col_defs[0].none_text = "N/A"
        col_defs[1].none_text = "--"
        col_defs[2].none_text = "?"
        result = get_table(
            rows,
            header_row=headers,
            col_defs=col_defs,
            none_text="UNUSED",
        )
        self.assertIn("N/A", result)
        self.assertIn("--", result)
        self.assertIn("?", result)
        self.assertNotIn("UNUSED", result)
        self.assertIn("Alice", result)
        self.assertIn("42", result)
        self.assertIn("data", result)

    def test_coldef_parse_preserves_none_text_attribute(self):
        specs = ["10", ">8.2f", "^15"]
        col_defs = ColDefList.parse(specs)
        for cd in col_defs:
            self.assertTrue(hasattr(cd, "none_text"))
            self.assertEqual(cd.none_text, "")
        col_defs[0].none_text = "CUSTOM1"
        col_defs[1].none_text = "CUSTOM2"
        self.assertEqual(col_defs[0].none_text, "CUSTOM1")
        self.assertEqual(col_defs[1].none_text, "CUSTOM2")
        self.assertEqual(col_defs[2].none_text, "")


if __name__ == "__main__":
    unittest.main()
