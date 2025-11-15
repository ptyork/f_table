import unittest
from f_table import get_table_header
from f_table.styles.basic_screen_style import BasicScreenStyle


class TestGetTableHeader(unittest.TestCase):
    def test_simple_header(self):
        out = get_table_header(["Name", "Age", "City"])
        self.assertIn("City", out)

    def test_header_with_style(self):
        out = get_table_header(["Name", "Age"], style=BasicScreenStyle())
        self.assertTrue("─" in out or "-" in out)

    def test_header_with_header_defs(self):
        out = get_table_header(["Name", "Age"], header_defs=[">20", "^10"])
        self.assertIn("Name", out)
        self.assertIn("Age", out)

    def test_header_with_col_defs_alignment(self):
        out = get_table_header(["Name", "Age"], col_defs=["<20", ">10"])
        self.assertIn("Name", out)

    def test_header_multiline_lines_count(self):
        out = get_table_header(["Name", "Age"], style=BasicScreenStyle())
        self.assertGreaterEqual(len(out.split("\n")), 3)

    def test_header_lazy_end_true(self):
        out = get_table_header(["Col1", "Col2"], lazy_end=True)
        self.assertTrue(all(line == line.rstrip() for line in out.split("\n") if line))

    def test_header_lazy_end_false(self):
        out = get_table_header(["Col1", "Col2"], lazy_end=False, style=BasicScreenStyle())
        self.assertIn("Col1", out)
