import unittest
from craftable import get_table_row, BasicScreenStyle


class TestGetTableRow(unittest.TestCase):
    def test_simple_row(self):
        out = get_table_row(["Alice", 30, "Engineer"])
        self.assertIn("Engineer", out)

    def test_row_with_numeric_formatting(self):
        out = get_table_row([123.456, 789.012], col_defs=[".2f", ".1f"])
        self.assertIn("123.46", out)

    def test_row_lazy_end_true(self):
        out = get_table_row(["Alice", 30], lazy_end=True)
        self.assertEqual(out, out.rstrip())

    def test_row_lazy_end_false(self):
        out = get_table_row(["Alice", 30], lazy_end=False, style=BasicScreenStyle())
        self.assertIn("Alice", out)

    def test_row_multiline_value(self):
        out = get_table_row(["Line1\nLine2", "Normal"])
        self.assertIn("Line1", out)
        self.assertIn("Line2", out)

    def test_row_with_none_value(self):
        out = get_table_row([None, "Value"])
        self.assertIn("None", out)
