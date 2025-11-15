import unittest
from craftable import get_table
from craftable import BasicScreenStyle, RoundedBorderScreenStyle, MarkdownStyle


class TestEdgeCases(unittest.TestCase):
    def test_table_with_very_long_row(self):
        data = [list(range(50))]
        result = get_table(data, table_width=500)
        self.assertIn("49", result)

    def test_table_with_many_rows(self):
        data = [[i, f"Row{i}"] for i in range(100)]
        result = get_table(data)
        self.assertIn("Row99", result)

    def test_table_with_tabs_in_values(self):
        result = get_table([["Value\twith\ttabs", "Normal"]])
        self.assertIsNotNone(result)

    def test_table_with_carriage_returns(self):
        result = get_table([["Value\rwith\rCR", "Normal"]])
        self.assertIsNotNone(result)

    def test_jagged_rows_various_lengths(self):
        data = [["A", "B"], ["C", "D", "E"], ["F"], ["G", "H", "I", "J"]]
        out = get_table(data)
        self.assertIn("A", out)

    def test_header_row_mismatch(self):
        data = [["A", "B"], ["C", "D"]]
        header = ["Col1", "Col2", "Col3"]
        out = get_table(data, header_row=header)
        self.assertIn("Col1", out)

    def test_col_defs_mismatch(self):
        data = [["A", "B", "C"], ["D", "E", "F"]]
        out = get_table(data, col_defs=["<10", ">10"])  # fewer than columns
        self.assertIn("A", out)

    def test_scientific_notation_values(self):
        data = [[1e10, 1e-10], [2.5e6, 3.7e-5]]
        out = get_table(data)
        self.assertIsNotNone(out)

    def test_zero_width_columns_auto_size(self):
        data = [["A", "B"], ["C", "D"]]
        out = get_table(data, col_defs=["<0", "<0"])  # width 0 means auto-size
        self.assertIn("A", out)
        self.assertIn("D", out)

    def test_very_wide_columns(self):
        data = [["A", "B"], ["C", "D"]]
        out = get_table(data, col_defs=["<100", "<100"])
        self.assertTrue(any(len(line) > 100 for line in out.split("\n")))

    def test_table_with_special_characters(self):
        data = [["Hello 世界", "Café"], ["Über", "Naïve"]]
        result = get_table(data)
        self.assertIn("世界", result)
        self.assertIn("Café", result)

    def test_table_preserves_row_order(self):
        data = [["First"], ["Second"], ["Third"]]
        result = get_table(data)
        first_idx = result.find("First")
        second_idx = result.find("Second")
        third_idx = result.find("Third")
        self.assertLess(first_idx, second_idx)
        self.assertLess(second_idx, third_idx)

    def test_table_with_header_and_no_data(self):
        header = ["Col1", "Col2"]
        result = get_table([], header_row=header)
        self.assertIn("No data to display", result)

    def test_table_multiple_rows_same_values(self):
        data = [["A", "B"], ["A", "B"], ["A", "B"]]
        result = get_table(data)
        self.assertGreaterEqual(result.count("A"), 3)

    def test_table_with_negative_numbers(self):
        data = [[-10, -20.5], [30, -40.123]]
        result = get_table(data)
        self.assertIn("-10", result)
        self.assertIn("-20.5", result)

    def test_table_with_empty_string_col_defs(self):
        data = [["Short", "Medium text", "X"], ["A", "B", "C"]]
        col_defs = ["", "^", ">"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("Short", result)
        self.assertIn("Medium text", result)

    def test_table_with_mixed_col_def_formats(self):
        data = [["abc", "123", "123 123 123"], ["abc", "123 123", "123 123 123 123"]]
        col_defs = ["10", "^10T", ">30"]
        result = get_table(data, col_defs=col_defs, style=BasicScreenStyle())
        self.assertIn("abc", result)

    def test_table_with_embedded_newlines_and_style(self):
        data = [["Line", "Text with\nnewlines\nin it"]]
        result = get_table(data, style=RoundedBorderScreenStyle())
        self.assertIn("Text with", result)

    def test_table_markdown_with_col_and_header_defs(self):
        data = [["A", "B", "C"], ["D", "E", "F"]]
        header = ["Col1", "Col2", "Col3"]
        col_defs = ["", "^", ""]
        header_defs = ["", "", "<"]
        result = get_table(data, header_row=header, style=MarkdownStyle(), col_defs=col_defs, header_defs=header_defs)
        self.assertIn("|", result)
        self.assertIn("Col1", result)

    def test_table_with_long_text_varying_lengths(self):
        data = [["abc", "123", "123 123 123"], ["abc", "123 123", "123 123 123 123"], ["abc", "123", "123 123 123 123 123"], ["abc", "123 123", "123 123"]]
        result = get_table(data)
        self.assertIn("abc", result)
        self.assertIn("123 123 123 123 123", result)
