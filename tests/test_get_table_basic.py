import unittest
from craftable import get_table, ColDef, ColDefList
from craftable.styles.basic_screen_style import BasicScreenStyle
from craftable.styles.rounded_border_screen_style import RoundedBorderScreenStyle
from craftable.styles.markdown_style import MarkdownStyle
from craftable.styles.ascii_style import ASCIIStyle
from craftable.styles.no_border_screen_style import NoBorderScreenStyle


class TestGetTable(unittest.TestCase):
    def test_empty_table_shows_no_data_message(self):
        result = get_table([])
        self.assertIn("No data to display", result)

    def test_simple_table_no_header(self):
        data = [["Alice", 30], ["Bob", 25]]
        result = get_table(data)
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)

    def test_simple_table_with_header(self):
        data = [["Alice", 30], ["Bob", 25]]
        header = ["Name", "Age"]
        result = get_table(data, header_row=header)
        self.assertIn("Name", result)
        self.assertIn("Age", result)
        self.assertIn("Alice", result)

    def test_single_row_table(self):
        data = [["Single", "Row", "Data"]]
        result = get_table(data)
        self.assertIn("Single", result)

    def test_single_column_table(self):
        data = [["Item1"], ["Item2"], ["Item3"]]
        result = get_table(data)
        self.assertIn("Item3", result)

    def test_mixed_data_types(self):
        data = [["Alice", 30, 5.5, True], ["Bob", 25, 6.2, False]]
        result = get_table(data)
        self.assertIn("5.5", result)
        self.assertIn("True", result)

    def test_none_values(self):
        data = [["Alice", None], [None, 25]]
        result = get_table(data)
        self.assertIn("None", result)

    def test_multiline_values(self):
        data = [["Line1\nLine2", "Normal"], ["SingleLine", "Multi\nLine\nValue"]]
        result = get_table(data)
        self.assertIn("Line2", result)

    def test_table_with_col_defs_string(self):
        data = [["Alice", 30], ["Bob", 25]]
        result = get_table(data, col_defs=["<20", ">10"])
        self.assertIn("Alice", result)

    def test_table_with_col_defs_objects(self):
        data = [["Alice", 30], ["Bob", 25]]
        col_defs = [ColDef(width=15, align="<"), ColDef(width=10, align=">")]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("Alice", result)

    def test_table_with_col_def_list(self):
        data = [["Alice", 30], ["Bob", 25]]
        col_defs = ColDefList(["<15", ">10"])
        result = get_table(data, col_defs=col_defs)
        self.assertIn("Bob", result)

    def test_table_with_header_defs(self):
        data = [["Alice", 30], ["Bob", 25]]
        header = ["Name", "Age"]
        result = get_table(data, header_row=header, header_defs=[">20", "^10"])
        self.assertIn("Name", result)

    def test_table_with_basic_screen_style(self):
        data = [["Alice", 30], ["Bob", 25]]
        result = get_table(data, style=BasicScreenStyle())
        self.assertTrue(any(c in result for c in ["│", "─", "┌", "└", "╭", "╰"]))

    def test_table_with_rounded_border_style(self):
        data = [["Alice", 30], ["Bob", 25]]
        result = get_table(data, style=RoundedBorderScreenStyle())
        self.assertIn("Alice", result)

    def test_table_with_markdown_style(self):
        data = [["Alice", 30], ["Bob", 25]]
        header = ["Name", "Age"]
        result = get_table(data, header_row=header, style=MarkdownStyle())
        self.assertIn("|", result)

    def test_table_with_ascii_style(self):
        data = [["Alice", 30], ["Bob", 25]]
        header = ["Name", "Age"]
        result = get_table(data, header_row=header, style=ASCIIStyle())
        self.assertIn("Alice", result)

    def test_table_with_no_border_style(self):
        data = [["Alice", 30], ["Bob", 25]]
        result = get_table(data, style=NoBorderScreenStyle())
        self.assertIn("Bob", result)

    def test_table_with_fixed_width(self):
        data = [["Alice", 30], ["Bob", 25]]
        result = get_table(data, table_width=50)
        self.assertIn("Alice", result)

    def test_table_with_lazy_end_true(self):
        data = [["Alice", 30], ["Bob", 25]]
        result = get_table(data, lazy_end=True, style=BasicScreenStyle())
        self.assertTrue(all(line == line.rstrip() for line in result.split("\n") if line))

    def test_table_with_lazy_end_false(self):
        data = [["Alice", 30], ["Bob", 25]]
        result = get_table(data, lazy_end=False, style=BasicScreenStyle())
        self.assertIn("│", result)

    def test_table_with_separate_rows_true(self):
        data = [["Alice", 30], ["Bob", 25], ["Charlie", 35]]
        result = get_table(data, separate_rows=True, style=BasicScreenStyle())
        self.assertGreater(len(result.split("\n")), 3)

    def test_table_with_long_text_wrapping(self):
        long_text = "This is a very long piece of text that should wrap"
        result = get_table([[long_text, "Short"]], table_width=40)
        self.assertGreater(len(result.split("\n")), 1)

    def test_table_with_truncation(self):
        data = [["VeryLongTextThatShouldBeTruncated", "Short"]]
        result = get_table(data, col_defs=["<10T", "<10"])
        self.assertIn("…", result)

    def test_table_with_auto_fill_column(self):
        data = [["Short", "Text"], ["X", "Y"]]
        result = get_table(data, col_defs=["<5A", "<5"], table_width=50)
        self.assertTrue(any(len(line) >= 40 for line in result.split("\n")))

    def test_table_with_numeric_formatting(self):
        data = [[123.456, 789.012], [0.123, 999.999]]
        result = get_table(data, col_defs=[".2f", ".1f"])
        self.assertIn("123.46", result)

    def test_table_with_percentage_formatting(self):
        data = [[0.123, 0.456], [0.789, 0.012]]
        result = get_table(data, col_defs=[".1%", ".0%"])
        self.assertIn("12.3%", result)

    def test_table_with_integer_formatting(self):
        data = [[1234, 5678], [90, 12345]]
        result = get_table(data, col_defs=["d", "d"])
        self.assertIn("1234", result)
