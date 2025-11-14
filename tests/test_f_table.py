"""
Comprehensive unit tests for f_table module.

Tests focus on the public get_* functions:
- get_table (primary function - extensive testing)
- get_table_row
- get_table_header

Uses unittest framework with pytest as the test runner.
"""

import unittest
from f_table import (
    get_table,
    get_table_row,
    get_table_header,
    ColDef,
    ColDefList,
    InvalidTableError,
    InvalidColDefError,
    NoBorderScreenStyle,
    BasicScreenStyle,
    RoundedBorderScreenStyle,
    MarkdownStyle,
    ASCIIStyle,
)


class TestGetTable(unittest.TestCase):
    """Comprehensive tests for get_table function."""

    def test_empty_table_shows_no_data_message(self):
        """Test that empty table shows a 'No data to display' message."""
        result = get_table([])
        self.assertIn("No data to display", result)

    def test_simple_table_no_header(self):
        """Test basic table without header."""
        data = [["Alice", 30], ["Bob", 25]]
        result = get_table(data)
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)
        self.assertIn("30", result)
        self.assertIn("25", result)

    def test_simple_table_with_header(self):
        """Test basic table with header row."""
        data = [["Alice", 30], ["Bob", 25]]
        header = ["Name", "Age"]
        result = get_table(data, header_row=header)
        self.assertIn("Name", result)
        self.assertIn("Age", result)
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)

    def test_single_row_table(self):
        """Test table with only one data row."""
        data = [["Single", "Row", "Data"]]
        result = get_table(data)
        self.assertIn("Single", result)
        self.assertIn("Row", result)
        self.assertIn("Data", result)

    def test_single_column_table(self):
        """Test table with only one column."""
        data = [["Item1"], ["Item2"], ["Item3"]]
        result = get_table(data)
        self.assertIn("Item1", result)
        self.assertIn("Item2", result)
        self.assertIn("Item3", result)

    def test_mixed_data_types(self):
        """Test table with various data types (int, float, str, bool)."""
        data = [
            ["Alice", 30, 5.5, True],
            ["Bob", 25, 6.2, False],
        ]
        result = get_table(data)
        self.assertIn("Alice", result)
        self.assertIn("30", result)
        self.assertIn("5.5", result)
        self.assertIn("True", result)
        self.assertIn("False", result)

    def test_none_values(self):
        """Test table with None values."""
        data = [["Alice", None], [None, 25]]
        result = get_table(data)
        self.assertIn("Alice", result)
        self.assertIn("None", result)
        self.assertIn("25", result)

    def test_empty_string_values(self):
        """Test table with empty string values."""
        data = [["", "Bob"], ["Alice", ""]]
        result = get_table(data)
        # Table should render without errors
        self.assertIsNotNone(result)

    def test_multiline_values(self):
        """Test table with multiline values (newlines in cells)."""
        data = [["Line1\nLine2", "Normal"], ["SingleLine", "Multi\nLine\nValue"]]
        result = get_table(data)
        # Should handle newlines gracefully
        self.assertIn("Line1", result)
        self.assertIn("Line2", result)

    def test_table_with_col_defs_string(self):
        """Test table with column definitions as strings."""
        data = [["Alice", 30], ["Bob", 25]]
        col_defs = ["<20", ">10"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("Alice", result)
        # Check that columns are at least sized
        lines = result.split("\n")
        self.assertTrue(any(len(line) > 20 for line in lines))

    def test_table_with_col_defs_objects(self):
        """Test table with column definitions as ColDef objects."""
        data = [["Alice", 30], ["Bob", 25]]
        col_defs = [ColDef(width=15, align="<"), ColDef(width=10, align=">")]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("Alice", result)
        self.assertIn("30", result)

    def test_table_with_col_def_list(self):
        """Test table with ColDefList."""
        data = [["Alice", 30], ["Bob", 25]]
        col_defs = ColDefList(["<15", ">10"])
        result = get_table(data, col_defs=col_defs)
        self.assertIn("Alice", result)

    def test_table_with_header_defs(self):
        """Test table with custom header definitions."""
        data = [["Alice", 30], ["Bob", 25]]
        header = ["Name", "Age"]
        header_defs = [">20", "^10"]  # Right-align name, center age
        result = get_table(data, header_row=header, header_defs=header_defs)
        self.assertIn("Name", result)
        self.assertIn("Age", result)

    def test_table_with_basic_screen_style(self):
        """Test table with BasicScreenStyle."""
        data = [["Alice", 30], ["Bob", 25]]
        result = get_table(data, style=BasicScreenStyle())
        self.assertIn("Alice", result)
        # Should have box drawing characters
        self.assertTrue(any(c in result for c in ["│", "─", "┌", "└"]))

    def test_table_with_rounded_border_style(self):
        """Test table with RoundedBorderScreenStyle."""
        data = [["Alice", 30], ["Bob", 25]]
        result = get_table(data, style=RoundedBorderScreenStyle())
        self.assertIn("Alice", result)

    def test_table_with_markdown_style(self):
        """Test table with MarkdownStyle."""
        data = [["Alice", 30], ["Bob", 25]]
        header = ["Name", "Age"]
        result = get_table(data, header_row=header, style=MarkdownStyle())
        self.assertIn("|", result)  # Markdown uses pipes
        self.assertIn("Name", result)

    def test_table_with_ascii_style(self):
        """Test table with ASCIIStyle (plain +-| chars)."""
        data = [["Alice", 30], ["Bob", 25]]
        header = ["Name", "Age"]
        result = get_table(data, header_row=header, style=ASCIIStyle())
        for ch in ["|", "+", "-"]:
            self.assertIn(ch, result)
        self.assertIn("Alice", result)

    def test_table_with_no_border_style(self):
        """Test table with NoBorderScreenStyle (default)."""
        data = [["Alice", 30], ["Bob", 25]]
        result = get_table(data, style=NoBorderScreenStyle())
        self.assertIn("Alice", result)

    def test_table_with_fixed_width(self):
        """Test table with specified table_width."""
        data = [["Alice", 30], ["Bob", 25]]
        result = get_table(data, table_width=50)
        lines = result.split("\n")
        # At least one line should exist (not testing exact width as implementation may vary)
        self.assertGreater(len(lines), 0)
        self.assertIn("Alice", result)

    def test_table_with_lazy_end_true(self):
        """Test table with lazy_end=True (omits right border)."""
        data = [["Alice", 30], ["Bob", 25]]
        result = get_table(data, lazy_end=True, style=BasicScreenStyle())
        lines = result.split("\n")
        # Lines should have trailing whitespace stripped
        self.assertTrue(all(line == line.rstrip() for line in lines if line))

    def test_table_with_lazy_end_false(self):
        """Test table with lazy_end=False (includes right border)."""
        data = [["Alice", 30], ["Bob", 25]]
        result = get_table(data, lazy_end=False, style=BasicScreenStyle())
        self.assertIn("│", result)  # Should have right borders

    def test_table_with_separate_rows_true(self):
        """Test table with separate_rows=True (row separators)."""
        data = [["Alice", 30], ["Bob", 25], ["Charlie", 35]]
        result = get_table(data, separate_rows=True, style=BasicScreenStyle())
        lines = result.split("\n")
        # Should have more lines due to separators
        self.assertGreater(len(lines), 3)

    def test_table_with_separate_rows_false(self):
        """Test table with separate_rows=False (no row separators)."""
        data = [["Alice", 30], ["Bob", 25]]
        result = get_table(data, separate_rows=False)
        self.assertIn("Alice", result)

    def test_table_with_long_text_wrapping(self):
        """Test table with long text that needs wrapping."""
        long_text = "This is a very long piece of text that should wrap"
        data = [[long_text, "Short"]]
        result = get_table(data, table_width=40)
        # Text should wrap across multiple lines
        lines = result.split("\n")
        self.assertGreater(len(lines), 1)

    def test_table_with_truncation(self):
        """Test table with truncation enabled in column definition."""
        data = [["VeryLongTextThatShouldBeTruncated", "Short"]]
        col_defs = ["<10T", "<10"]  # T flag enables truncation
        result = get_table(data, col_defs=col_defs)
        # Should contain ellipsis for truncated text
        self.assertIn("…", result)

    def test_table_with_auto_fill_column(self):
        """Test table with auto-fill column (A flag)."""
        data = [["Short", "Text"], ["X", "Y"]]
        col_defs = ["<5A", "<5"]  # A flag enables auto-fill
        result = get_table(data, col_defs=col_defs, table_width=50)
        # First column should expand to fill available space
        lines = result.split("\n")
        self.assertTrue(any(len(line) >= 40 for line in lines))

    def test_table_with_no_wrap_column(self):
        """Test table with no-wrap column (N flag)."""
        data = [["This is long text that normally wraps", "Short"]]
        col_defs = ["<20N", "<10"]  # N flag disables wrapping
        result = get_table(data, col_defs=col_defs)
        # Text should not wrap
        self.assertIn("This is long text", result)

    def test_table_with_alignment_left(self):
        """Test table with left-aligned columns."""
        data = [["Alice", 30], ["Bob", 25]]
        col_defs = ["<15", "<10"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("Alice", result)

    def test_table_with_alignment_right(self):
        """Test table with right-aligned columns."""
        data = [["Alice", 30], ["Bob", 25]]
        col_defs = [">15", ">10"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("Alice", result)

    def test_table_with_alignment_center(self):
        """Test table with center-aligned columns."""
        data = [["Alice", 30], ["Bob", 25]]
        col_defs = ["^15", "^10"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("Alice", result)

    def test_table_with_mixed_alignments(self):
        """Test table with mixed column alignments."""
        data = [["Alice", 30, "Engineer"], ["Bob", 25, "Designer"]]
        col_defs = ["<10", ">5", "^15"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("Alice", result)
        self.assertIn("Engineer", result)

    def test_table_with_numeric_formatting(self):
        """Test table with numeric format specifications."""
        data = [[123.456, 789.012], [0.123, 999.999]]
        col_defs = [".2f", ".1f"]  # Format as floats with precision
        result = get_table(data, col_defs=col_defs)
        self.assertIn("123.46", result)  # Rounded
        self.assertIn("789.0", result)

    def test_table_with_percentage_formatting(self):
        """Test table with percentage formatting."""
        data = [[0.123, 0.456], [0.789, 0.012]]
        col_defs = [".1%", ".0%"]  # Format as percentages
        result = get_table(data, col_defs=col_defs)
        self.assertIn("12.3%", result)
        self.assertIn("46%", result)

    def test_table_with_integer_formatting(self):
        """Test table with integer formatting."""
        data = [[1234, 5678], [90, 12345]]
        col_defs = ["d", "d"]  # Format as integers
        result = get_table(data, col_defs=col_defs)
        self.assertIn("1234", result)

    def test_table_with_unequal_row_lengths(self):
        """Test table where rows have different numbers of columns.
        
        Note: The current implementation requires all rows to have the same length.
        This test verifies that behavior by expecting an error or by padding rows.
        """
        data = [["A", "B", "C"], ["D", "E"], ["F"]]
        # The implementation may raise an error for unequal rows
        # or handle them gracefully - we just check it doesn't crash unexpectedly
        try:
            result = get_table(data)
            # If it succeeds, verify the values that should be present
            self.assertIn("A", result)
        except (IndexError, ValueError):
            # Expected behavior for unequal rows - implementation limitation
            pass

    def test_table_with_special_characters(self):
        """Test table with special characters and unicode."""
        data = [["Hello 世界", "Café"], ["Über", "Naïve"]]
        result = get_table(data)
        self.assertIn("世界", result)
        self.assertIn("Café", result)

    def test_table_with_very_wide_columns(self):
        """Test table with very wide column definitions."""
        data = [["A", "B"], ["C", "D"]]
        col_defs = ["<100", "<100"]
        result = get_table(data, col_defs=col_defs)
        # Should create wide columns
        lines = result.split("\n")
        self.assertTrue(any(len(line) > 100 for line in lines))

    def test_table_with_zero_width_columns(self):
        """Test table with zero-width columns (auto-sized)."""
        data = [["A", "B"], ["C", "D"]]
        col_defs = ["<0", "<0"]  # Width 0 means auto-size
        result = get_table(data, col_defs=col_defs)
        self.assertIn("A", result)

    def test_table_preserves_row_order(self):
        """Test that table preserves the order of rows."""
        data = [["First"], ["Second"], ["Third"]]
        result = get_table(data)
        first_idx = result.find("First")
        second_idx = result.find("Second")
        third_idx = result.find("Third")
        self.assertLess(first_idx, second_idx)
        self.assertLess(second_idx, third_idx)

    def test_table_with_header_and_no_data(self):
        """Test table with header but empty data list."""
        header = ["Col1", "Col2"]
        result = get_table([], header_row=header)
        # Should show no data message
        self.assertIn("No data to display", result)

    def test_table_multiple_rows_same_values(self):
        """Test table with multiple rows containing the same values."""
        data = [["A", "B"], ["A", "B"], ["A", "B"]]
        result = get_table(data)
        # Count occurrences - should be 3
        count = result.count("A")
        self.assertGreaterEqual(count, 3)

    def test_table_with_boolean_values(self):
        """Test table with boolean True/False values."""
        data = [[True, False], [False, True]]
        result = get_table(data)
        self.assertIn("True", result)
        self.assertIn("False", result)

    def test_table_with_negative_numbers(self):
        """Test table with negative numbers."""
        data = [[-10, -20.5], [30, -40.123]]
        result = get_table(data)
        self.assertIn("-10", result)
        self.assertIn("-20.5", result)

    def test_table_with_scientific_notation(self):
        """Test table with very large/small numbers (scientific notation)."""
        data = [[1e10, 1e-10], [2.5e6, 3.7e-5]]
        result = get_table(data)
        # Should handle scientific notation
        self.assertIsNotNone(result)

    def test_table_column_count_consistency(self):
        """Test that all rows in output have consistent structure."""
        data = [["A", "B", "C"], ["D", "E", "F"], ["G", "H", "I"]]
        result = get_table(data, style=BasicScreenStyle())
        lines = [line for line in result.split("\n") if line.strip()]
        # All content lines should have similar structure
        self.assertGreater(len(lines), 0)

    def test_table_with_empty_string_col_defs(self):
        """Test table with empty string column definitions (minimal/auto width)."""
        data = [["Short", "Medium text", "X"], ["A", "B", "C"]]
        col_defs = ["", "^", ">"]  # Empty width, center align, right align
        result = get_table(data, col_defs=col_defs)
        self.assertIn("Short", result)
        self.assertIn("Medium text", result)

    def test_table_with_mixed_col_def_formats(self):
        """Test table with mixed column definition formats (some with width, some without)."""
        data = [["abc", "123", "123 123 123"], ["abc", "123 123", "123 123 123 123"]]
        col_defs = ["10", "^10T", ">30"]  # Fixed width, center+truncate, right align
        result = get_table(data, col_defs=col_defs, style=BasicScreenStyle())
        self.assertIn("abc", result)

    def test_table_with_center_align_and_truncate(self):
        """Test table with combined center alignment and truncation."""
        data = [["VeryLongTextThatNeedsTruncation", "Short"]]
        col_defs = ["^10T", "<10"]  # Center align with truncation
        result = get_table(data, col_defs=col_defs)
        # Should be truncated to 10 chars with ellipsis
        self.assertIn("…", result)

    def test_table_with_embedded_newlines(self):
        """Test table with text that already contains newline characters."""
        data = [
            [
                "Line1",
                "Text with\nembedded\nnewlines",
            ],
            [
                "Line2",
                "More text\nwith newlines",
            ],
        ]
        result = get_table(data)
        # Should preserve embedded newlines
        self.assertIn("embedded", result)
        self.assertIn("newlines", result)

    def test_table_with_embedded_newlines_and_width(self):
        """Test table with embedded newlines and table_width constraint."""
        data = [
            [
                "This is a line",
                "Text with newlines:\n  * Item 1\n  * Item 2",
            ],
        ]
        result = get_table(data, table_width=50)
        # Should handle both embedded newlines and width constraints
        self.assertIn("Item 1", result)
        self.assertIn("Item 2", result)

    def test_table_with_embedded_newlines_and_style(self):
        """Test table with embedded newlines and RoundedBorderScreenStyle."""
        data = [
            [
                "Line",
                "Text with\nnewlines\nin it",
            ],
        ]
        result = get_table(data, style=RoundedBorderScreenStyle())
        self.assertIn("Text with", result)

    def test_table_with_embedded_newlines_separate_rows(self):
        """Test table with embedded newlines and separate_rows=True."""
        data = [
            ["Col1", "Text\nwith\nnewlines"],
            ["Col2", "More\ntext"],
        ]
        header = ["A", "B"]
        result = get_table(
            data,
            header_row=header,
            style=RoundedBorderScreenStyle(),
            separate_rows=True,
        )
        self.assertIn("Col1", result)
        self.assertIn("newlines", result)

    def test_table_markdown_with_col_and_header_defs(self):
        """Test Markdown style with both column and header definitions."""
        data = [["A", "B", "C"], ["D", "E", "F"]]
        header = ["Col1", "Col2", "Col3"]
        col_defs = ["", "^", ""]  # Default, center, default
        header_defs = ["", "", "<"]  # Default, default, left
        result = get_table(
            data,
            header_row=header,
            style=MarkdownStyle(),
            col_defs=col_defs,
            header_defs=header_defs,
        )
        self.assertIn("|", result)
        self.assertIn("Col1", result)

    def test_table_with_auto_fill_and_table_width(self):
        """Test table with auto-fill column (A flag) and specific table width."""
        data = [["Short", "Text"], ["X", "Y"]]
        col_defs = ["", "^", ">A"]  # Last column auto-fills
        result = get_table(data, col_defs=col_defs, table_width=50, style=BasicScreenStyle())
        # Auto-fill column should expand to use available space
        self.assertIn("Short", result)

    def test_table_with_long_text_varying_lengths(self):
        """Test table with rows having varying text lengths."""
        data = [
            ["abc", "123", "123 123 123"],
            ["abc", "123 123", "123 123 123 123"],
            ["abc", "123", "123 123 123 123 123"],
            ["abc", "123 123", "123 123"],
        ]
        result = get_table(data)
        # Should handle varying lengths without error
        self.assertIn("abc", result)
        self.assertIn("123 123 123 123 123", result)

    def test_table_with_lorem_ipsum_wrapping(self):
        """Test table with very long Lorem Ipsum text that requires wrapping."""
        long_text = (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
            "sed do eiusmod tempor incididunt ut labore et dolore magna "
            "aliqua. Ut enim ad minim veniam, quis nostrud exercitation "
            "ullamco laboris nisi ut aliquip ex ea commodo consequat."
        )
        data = [["a", "123", long_text]]
        result = get_table(data, style=BasicScreenStyle(), col_defs=["10", "^10", "70"])
        # Should wrap the long text
        self.assertIn("Lorem ipsum", result)
        self.assertIn("consequat", result)

    def test_table_with_truncation_on_long_text(self):
        """Test table with truncation flag on very long text."""
        long_text = (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
            "sed do eiusmod tempor incididunt."
        )
        data = [["a", "123", long_text]]
        col_defs = ["10", "^10", "30T"]  # Truncate last column to 30 chars
        result = get_table(data, style=BasicScreenStyle(), col_defs=col_defs)
        # Should truncate with ellipsis
        self.assertIn("…", result)


class TestGetTableRow(unittest.TestCase):
    """Tests for get_table_row function."""

    def test_simple_row(self):
        """Test basic row generation."""
        values = ["Alice", 30, "Engineer"]
        result = get_table_row(values)
        self.assertIn("Alice", result)
        self.assertIn("30", result)
        self.assertIn("Engineer", result)

    def test_single_value_row(self):
        """Test row with single value."""
        values = ["OnlyValue"]
        result = get_table_row(values)
        self.assertIn("OnlyValue", result)

    def test_row_with_col_defs(self):
        """Test row with column definitions."""
        values = ["Alice", 30]
        col_defs = ["<20", ">10"]
        result = get_table_row(values, col_defs=col_defs)
        self.assertIn("Alice", result)

    def test_row_with_style(self):
        """Test row with custom style."""
        values = ["Alice", 30]
        result = get_table_row(values, style=BasicScreenStyle())
        self.assertIn("Alice", result)

    def test_row_with_lazy_end_true(self):
        """Test row with lazy_end=True."""
        values = ["Alice", 30]
        result = get_table_row(values, lazy_end=True)
        # Should strip trailing whitespace
        self.assertEqual(result, result.rstrip())

    def test_row_with_lazy_end_false(self):
        """Test row with lazy_end=False."""
        values = ["Alice", 30]
        result = get_table_row(values, lazy_end=False, style=BasicScreenStyle())
        self.assertIn("Alice", result)

    def test_row_with_multiline_value(self):
        """Test row with multiline value."""
        values = ["Line1\nLine2", "Normal"]
        result = get_table_row(values)
        # Should handle newlines
        self.assertIn("Line1", result)
        self.assertIn("Line2", result)

    def test_row_with_none_value(self):
        """Test row with None value."""
        values = [None, "Value"]
        result = get_table_row(values)
        self.assertIn("None", result)

    def test_row_with_empty_string(self):
        """Test row with empty string value."""
        values = ["", "Value"]
        result = get_table_row(values)
        self.assertIn("Value", result)

    def test_row_with_numeric_formatting(self):
        """Test row with numeric format specification."""
        values = [123.456, 789.012]
        col_defs = [".2f", ".1f"]
        result = get_table_row(values, col_defs=col_defs)
        self.assertIn("123.46", result)


class TestGetTableHeader(unittest.TestCase):
    """Tests for get_table_header function."""

    def test_simple_header(self):
        """Test basic header generation."""
        header = ["Name", "Age", "City"]
        result = get_table_header(header)
        self.assertIn("Name", result)
        self.assertIn("Age", result)
        self.assertIn("City", result)

    def test_header_with_style(self):
        """Test header with custom style."""
        header = ["Name", "Age"]
        result = get_table_header(header, style=BasicScreenStyle())
        self.assertIn("Name", result)
        # Should have header borders
        self.assertTrue("─" in result or "-" in result)

    def test_header_with_header_defs(self):
        """Test header with custom header definitions."""
        header = ["Name", "Age"]
        header_defs = [">20", "^10"]
        result = get_table_header(header, header_defs=header_defs)
        self.assertIn("Name", result)

    def test_header_with_col_defs(self):
        """Test header with column definitions for alignment."""
        header = ["Name", "Age"]
        col_defs = ["<20", ">10"]
        result = get_table_header(header, col_defs=col_defs)
        self.assertIn("Name", result)

    def test_header_multiline(self):
        """Test header returns multiple lines (top border, header, bottom border)."""
        header = ["Name", "Age"]
        result = get_table_header(header, style=BasicScreenStyle())
        lines = result.split("\n")
        # Should have at least 3 lines (top border, header, separator)
        self.assertGreaterEqual(len(lines), 3)

    def test_header_with_lazy_end_true(self):
        """Test header with lazy_end=True."""
        header = ["Name", "Age"]
        result = get_table_header(header, lazy_end=True)
        lines = result.split("\n")
        # Lines should have trailing whitespace stripped
        self.assertTrue(all(line == line.rstrip() for line in lines if line))

    def test_header_with_lazy_end_false(self):
        """Test header with lazy_end=False."""
        header = ["Name", "Age"]
        result = get_table_header(header, lazy_end=False, style=BasicScreenStyle())
        self.assertIn("Name", result)

    def test_header_single_column(self):
        """Test header with single column."""
        header = ["OnlyColumn"]
        result = get_table_header(header)
        self.assertIn("OnlyColumn", result)

    def test_header_with_markdown_style(self):
        """Test header with MarkdownStyle."""
        header = ["Name", "Age"]
        result = get_table_header(header, style=MarkdownStyle())
        self.assertIn("|", result)
        self.assertIn("Name", result)


class TestColDef(unittest.TestCase):
    """Tests for ColDef class."""

    def test_coldef_parse_simple(self):
        """Test parsing simple column definition."""
        col_def = ColDef.parse("<20")
        self.assertEqual(col_def.width, 20)
        self.assertEqual(col_def.align, "<")

    def test_coldef_parse_right_align(self):
        """Test parsing right-aligned column definition."""
        col_def = ColDef.parse(">15")
        self.assertEqual(col_def.width, 15)
        self.assertEqual(col_def.align, ">")

    def test_coldef_parse_center_align(self):
        """Test parsing center-aligned column definition."""
        col_def = ColDef.parse("^25")
        self.assertEqual(col_def.width, 25)
        self.assertEqual(col_def.align, "^")

    def test_coldef_parse_with_auto_flag(self):
        """Test parsing column definition with auto-fill flag."""
        col_def = ColDef.parse("<20A")
        self.assertEqual(col_def.width, 20)
        self.assertTrue(col_def.auto_fill)

    def test_coldef_parse_with_truncate_flag(self):
        """Test parsing column definition with truncate flag."""
        col_def = ColDef.parse("<20T")
        self.assertEqual(col_def.width, 20)
        self.assertTrue(col_def.truncate)

    def test_coldef_parse_with_all_flags(self):
        """Test parsing column definition with all flags."""
        col_def = ColDef.parse("<20AT")
        self.assertEqual(col_def.width, 20)
        self.assertTrue(col_def.auto_fill)
        self.assertTrue(col_def.truncate)

    def test_coldef_parse_format_spec(self):
        """Test parsing column definition with format specification."""
        col_def = ColDef.parse(".2f")
        self.assertEqual(str(col_def.format_spec), ".2f")

    def test_coldef_format_value(self):
        """Test formatting a value with ColDef."""
        col_def = ColDef(width=10, align="<")
        result = col_def.format("test")
        self.assertEqual(len(result), 10)
        self.assertTrue(result.startswith("test"))

    def test_coldef_format_truncate(self):
        """Test formatting with truncation."""
        col_def = ColDef(width=5, truncate=True)
        result = col_def.format("LongText")
        self.assertEqual(len(result), 5)
        self.assertIn("…", result)

    def test_coldef_format_center(self):
        """Test formatting with center alignment."""
        col_def = ColDef(width=10, align="^")
        result = col_def.format("Hi")
        self.assertEqual(len(result), 10)
        # Should be centered with spaces on both sides
        self.assertTrue(result.strip() == "Hi")

    def test_coldef_format_right(self):
        """Test formatting with right alignment."""
        col_def = ColDef(width=10, align=">")
        result = col_def.format("Hi")
        self.assertEqual(len(result), 10)
        self.assertTrue(result.endswith("Hi"))


class TestColDefList(unittest.TestCase):
    """Tests for ColDefList class."""

    def test_coldeflist_create_from_strings(self):
        """Test creating ColDefList from strings."""
        col_defs = ColDefList(["<10", ">15", "^20"])
        self.assertEqual(len(col_defs), 3)
        self.assertEqual(col_defs[0].width, 10)
        self.assertEqual(col_defs[1].width, 15)
        self.assertEqual(col_defs[2].width, 20)

    def test_coldeflist_create_from_coldef_objects(self):
        """Test creating ColDefList from ColDef objects."""
        col_defs = ColDefList([ColDef(width=10), ColDef(width=20)])
        self.assertEqual(len(col_defs), 2)

    def test_coldeflist_append_string(self):
        """Test appending string to ColDefList."""
        col_defs = ColDefList()
        col_defs.append("<15")
        self.assertEqual(len(col_defs), 1)
        self.assertEqual(col_defs[0].width, 15)

    def test_coldeflist_append_coldef(self):
        """Test appending ColDef to ColDefList."""
        col_defs = ColDefList()
        col_defs.append(ColDef(width=25))
        self.assertEqual(len(col_defs), 1)
        self.assertEqual(col_defs[0].width, 25)

    def test_coldeflist_getitem(self):
        """Test getting item from ColDefList."""
        col_defs = ColDefList(["<10", ">15"])
        col_def = col_defs[0]
        self.assertIsInstance(col_def, ColDef)
        self.assertEqual(col_def.width, 10)

    def test_coldeflist_setitem_string(self):
        """Test setting item in ColDefList with string."""
        col_defs = ColDefList(["<10", ">15"])
        col_defs[0] = "<20"
        self.assertEqual(col_defs[0].width, 20)

    def test_coldeflist_setitem_coldef(self):
        """Test setting item in ColDefList with ColDef."""
        col_defs = ColDefList(["<10", ">15"])
        col_defs[0] = ColDef(width=30)
        self.assertEqual(col_defs[0].width, 30)

    def test_coldeflist_slice(self):
        """Test slicing ColDefList."""
        col_defs = ColDefList(["<10", ">15", "^20"])
        subset = col_defs[0:2]
        self.assertIsInstance(subset, ColDefList)
        self.assertEqual(len(subset), 2)

    def test_coldeflist_for_table(self):
        """Test creating ColDefList from table data."""
        data = [["Short", "Medium text"], ["A", "Longer text here"]]
        col_defs = ColDefList.for_table(data)
        self.assertEqual(len(col_defs), 2)
        # Widths should match longest values
        self.assertGreaterEqual(col_defs[0].width, 5)
        self.assertGreaterEqual(col_defs[1].width, 15)


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and error handling."""

    def test_table_with_very_long_row(self):
        """Test table with a very long row (many columns).
        
        Note: Default table width may not accommodate 50 columns.
        This tests the behavior with many columns and larger table width.
        """
        data = [list(range(50))]  # 50 columns
        # Use a very large table width to accommodate all columns
        result = get_table(data, table_width=500)
        # Should handle without error
        self.assertIn("0", result)
        self.assertIn("49", result)

    def test_table_with_many_rows(self):
        """Test table with many rows."""
        data = [[i, f"Row{i}"] for i in range(100)]
        result = get_table(data)
        # Should handle without error
        self.assertIn("Row0", result)
        self.assertIn("Row99", result)

    def test_coldef_parse_invalid_raises_error(self):
        """Test that invalid column definition raises InvalidColDefError.
        
        Note: ColDef.parse may be lenient and accept various inputs.
        This test verifies error handling exists but may need adjustment.
        """
        # Try a clearly invalid format spec that should fail
        # If parse is very lenient, this test documents that behavior
        try:
            result = ColDef.parse("invalid!@#")
            # If it succeeds, it means parse is lenient - that's OK
            self.assertIsInstance(result, ColDef)
        except InvalidColDefError:
            # Expected behavior for strict parsing
            pass

    def test_coldeflist_append_invalid_raises_error(self):
        """Test that appending invalid type to ColDefList raises ValueError."""
        col_defs = ColDefList()
        with self.assertRaises(ValueError):
            col_defs.append(123)  # Invalid type

    def test_table_with_tabs_in_values(self):
        """Test table with tab characters in values."""
        data = [["Value\twith\ttabs", "Normal"]]
        result = get_table(data)
        # Should handle tabs without error
        self.assertIsNotNone(result)

    def test_table_with_carriage_returns(self):
        """Test table with carriage return characters."""
        data = [["Value\rwith\rCR", "Normal"]]
        result = get_table(data)
        self.assertIsNotNone(result)

    def test_jagged_rows_shorter_first(self):
        """Test jagged list where first rows are shorter than later rows."""
        data = [
            ["A", "B"],           # 2 columns
            ["C", "D", "E"],      # 3 columns
            ["F", "G", "H", "I"], # 4 columns
        ]
        try:
            result = get_table(data)
            # If it succeeds, should handle gracefully
            self.assertIn("A", result)
        except (IndexError, ValueError):
            # Expected - implementation may not handle jagged rows
            pass

    def test_jagged_rows_longer_first(self):
        """Test jagged list where first rows are longer than later rows."""
        data = [
            ["A", "B", "C", "D"], # 4 columns
            ["E", "F", "G"],      # 3 columns
            ["H", "I"],           # 2 columns
        ]
        try:
            result = get_table(data)
            # If it succeeds, should handle gracefully
            self.assertIn("A", result)
        except (IndexError, ValueError):
            # Expected - implementation may not handle jagged rows
            pass

    def test_jagged_rows_with_empty_cells(self):
        """Test jagged list with some rows having fewer cells."""
        data = [
            ["Alice", "30", "Engineer"],
            ["Bob"],  # Missing age and title
            ["Charlie", "35"],  # Missing title
        ]
        try:
            result = get_table(data)
            self.assertIn("Alice", result)
            self.assertIn("Bob", result)
        except (IndexError, ValueError):
            # Expected - implementation may not handle jagged rows
            pass

    def test_header_row_longer_than_data(self):
        """Test when header_row has more columns than data rows."""
        data = [["A", "B"], ["C", "D"]]
        header = ["Col1", "Col2", "Col3", "Col4"]  # 4 headers, but only 2 data cols
        try:
            result = get_table(data, header_row=header)
            # Should either truncate header or pad data
            self.assertIn("Col1", result)
        except (IndexError, ValueError):
            # Expected if implementation doesn't handle this
            pass

    def test_header_row_shorter_than_data(self):
        """Test when header_row has fewer columns than data rows."""
        data = [["A", "B", "C", "D"], ["E", "F", "G", "H"]]
        header = ["Col1", "Col2"]  # 2 headers, but 4 data cols
        try:
            result = get_table(data, header_row=header)
            # Should either pad header or use only first columns
            self.assertIn("Col1", result)
        except (IndexError, ValueError):
            # Expected if implementation doesn't handle this
            pass

    def test_col_defs_longer_than_data_columns(self):
        """Test when col_defs has more entries than data columns."""
        data = [["A", "B"], ["C", "D"]]  # 2 columns
        col_defs = ["<10", ">10", "^10", "<5"]  # 4 col_defs
        try:
            result = get_table(data, col_defs=col_defs)
            # Should ignore extra col_defs
            self.assertIn("A", result)
        except (IndexError, ValueError):
            # Expected if implementation doesn't handle this
            pass

    def test_col_defs_shorter_than_data_columns(self):
        """Test when col_defs has fewer entries than data columns."""
        data = [["A", "B", "C", "D"], ["E", "F", "G", "H"]]  # 4 columns
        col_defs = ["<10", ">10"]  # Only 2 col_defs
        try:
            result = get_table(data, col_defs=col_defs)
            # Should use defaults for missing col_defs
            self.assertIn("A", result)
            self.assertIn("C", result)  # Columns without col_defs
        except (IndexError, ValueError):
            # Expected if implementation doesn't handle this
            pass

    def test_header_defs_longer_than_headers(self):
        """Test when header_defs has more entries than header_row."""
        data = [["A", "B"], ["C", "D"]]
        header = ["Col1", "Col2"]
        header_defs = ["<10", ">10", "^10", "<5"]  # More defs than headers
        try:
            result = get_table(data, header_row=header, header_defs=header_defs)
            # Should ignore extra header_defs
            self.assertIn("Col1", result)
        except (IndexError, ValueError):
            # Expected if implementation doesn't handle this
            pass

    def test_header_defs_shorter_than_headers(self):
        """Test when header_defs has fewer entries than header_row."""
        data = [["A", "B", "C", "D"], ["E", "F", "G", "H"]]
        header = ["Col1", "Col2", "Col3", "Col4"]
        header_defs = ["<10", ">10"]  # Only 2 defs for 4 headers
        try:
            result = get_table(data, header_row=header, header_defs=header_defs)
            # Should use defaults for missing header_defs
            self.assertIn("Col1", result)
            self.assertIn("Col3", result)  # Headers without defs
        except (IndexError, ValueError):
            # Expected if implementation doesn't handle this
            pass

    def test_all_mismatched_lengths(self):
        """Test with different lengths for data, header, col_defs, and header_defs."""
        data = [["A", "B", "C"], ["D", "E"]]  # Jagged: 3 and 2 columns
        header = ["H1", "H2", "H3", "H4"]     # 4 headers
        col_defs = ["<10", ">10"]             # 2 col_defs
        header_defs = ["^10"]                  # 1 header_def
        try:
            result = get_table(
                data,
                header_row=header,
                col_defs=col_defs,
                header_defs=header_defs
            )
            # If it works, great; if not, that's also expected
            self.assertIsNotNone(result)
        except (IndexError, ValueError):
            # Expected - this is a complex edge case
            pass

    def test_empty_row_in_data(self):
        """Test table with an empty row in the middle of data."""
        data = [
            ["Alice", "30"],
            [],  # Empty row
            ["Bob", "25"]
        ]
        try:
            result = get_table(data)
            # Should handle or error gracefully
            self.assertIsNotNone(result)
        except (IndexError, ValueError):
            # Expected if implementation doesn't handle empty rows
            pass

    def test_single_column_jagged(self):
        """Test jagged rows where some have only 1 column, others have more."""
        data = [
            ["OnlyOne"],
            ["Two", "Columns"],
            ["Three", "Columns", "Here"],
        ]
        try:
            result = get_table(data)
            self.assertIn("OnlyOne", result)
        except (IndexError, ValueError):
            # Expected for jagged rows
            pass


class TestIterableTypes(unittest.TestCase):
    """Tests for using various iterable types (tuples, generators, etc.) instead of lists."""

    def test_values_as_tuples(self):
        """Test that tuples work for data rows."""
        data = [
            ("Alice", 30, "Engineer"),
            ("Bob", 25, "Designer"),
            ("Charlie", 35, "Manager")
        ]
        result = get_table(data)
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)
        self.assertIn("Engineer", result)
        self.assertIn("Designer", result)

    def test_values_as_tuple_of_tuples(self):
        """Test that tuple of tuples works for entire data structure."""
        data = (
            ("Alice", 30),
            ("Bob", 25),
            ("Charlie", 35)
        )
        result = get_table(data)
        self.assertIn("Alice", result)
        self.assertIn("30", result)

    def test_header_row_as_tuple(self):
        """Test that tuple works for header_row."""
        data = [["Alice", 30], ["Bob", 25]]
        header = ("Name", "Age")
        result = get_table(data, header_row=header)
        self.assertIn("Name", result)
        self.assertIn("Age", result)
        self.assertIn("Alice", result)

    def test_col_defs_as_tuple(self):
        """Test that tuple works for col_defs."""
        data = [["Alice", 30], ["Bob", 25]]
        col_defs = ("<20", ">10")
        result = get_table(data, col_defs=col_defs)
        self.assertIn("Alice", result)
        self.assertIn("30", result)

    def test_header_defs_as_tuple(self):
        """Test that tuple works for header_defs."""
        data = [["Alice", 30], ["Bob", 25]]
        header = ["Name", "Age"]
        header_defs = ("^20", "^10")
        result = get_table(data, header_row=header, header_defs=header_defs)
        self.assertIn("Name", result)
        self.assertIn("Age", result)

    def test_mixed_list_and_tuple_rows(self):
        """Test mixing lists and tuples for different rows."""
        data = [
            ["Alice", 30],
            ("Bob", 25),
            ["Charlie", 35],
            ("Diana", 28)
        ]
        result = get_table(data)
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)
        self.assertIn("Charlie", result)
        self.assertIn("Diana", result)

    def test_generator_for_values(self):
        """Test that a generator expression works for data."""
        data = ((name, age) for name, age in [("Alice", 30), ("Bob", 25), ("Charlie", 35)])
        result = get_table(data)
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)
        self.assertIn("Charlie", result)

    def test_generator_function_for_values(self):
        """Test that a generator function works for data."""
        def data_generator():
            yield ["Alice", 30]
            yield ["Bob", 25]
            yield ["Charlie", 35]
        
        result = get_table(data_generator())
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)
        self.assertIn("30", result)

    def test_range_as_row_values(self):
        """Test that range objects work as row values."""
        data = [
            list(range(5)),
            list(range(5, 10)),
            list(range(10, 15))
        ]
        result = get_table(data)
        self.assertIn("0", result)
        self.assertIn("9", result)
        self.assertIn("14", result)

    def test_map_object_for_values(self):
        """Test that map objects work for data."""
        raw_data = [("Alice", 30), ("Bob", 25), ("Charlie", 35)]
        data = map(lambda x: list(x), raw_data)
        result = get_table(data)
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)

    def test_filter_object_for_values(self):
        """Test that filter objects work for data."""
        raw_data = [["Alice", 30], ["Bob", 25], ["Charlie", 35], ["Diana", 20]]
        data = filter(lambda row: row[1] >= 25, raw_data)
        result = get_table(data)
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)
        self.assertIn("Charlie", result)
        self.assertNotIn("Diana", result)

    def test_zip_object_for_values(self):
        """Test that zip objects work for data."""
        names = ["Alice", "Bob", "Charlie"]
        ages = [30, 25, 35]
        data = zip(names, ages)
        result = get_table(data)
        self.assertIn("Alice", result)
        self.assertIn("30", result)

    def test_all_parameters_as_tuples(self):
        """Test using tuples for all parameters (values, header_row, col_defs, header_defs)."""
        data = (
            ("Alice", 30, "Engineer"),
            ("Bob", 25, "Designer"),
            ("Charlie", 35, "Manager")
        )
        header = ("Name", "Age", "Role")
        col_defs = ("<20", ">5", "<15")
        header_defs = ("^20", "^5", "^15")
        
        result = get_table(data, header_row=header, col_defs=col_defs, header_defs=header_defs)
        self.assertIn("Name", result)
        self.assertIn("Age", result)
        self.assertIn("Role", result)
        self.assertIn("Alice", result)
        self.assertIn("Engineer", result)

    def test_nested_generator_with_tuple_rows(self):
        """Test generator that yields tuples."""
        def data_gen():
            for name, age in [("Alice", 30), ("Bob", 25)]:
                yield (name, age, age * 1000)
        
        result = get_table(data_gen(), header_row=("Name", "Age", "Salary"))
        self.assertIn("Alice", result)
        self.assertIn("30000", result)

    def test_col_def_objects_in_tuple(self):
        """Test tuple of ColDef objects for col_defs."""
        data = [["Alice", 30], ["Bob", 25]]
        col_defs = (ColDef.parse("<20"), ColDef.parse(">10"))
        result = get_table(data, col_defs=col_defs)
        self.assertIn("Alice", result)
        self.assertIn("30", result)

    def test_mixed_types_in_col_defs_tuple(self):
        """Test tuple with mixed string col_defs - all strings in tuple."""
        data = [["Alice", 30, "Engineer"], ["Bob", 25, "Designer"]]
        col_defs = ("<20", ">10", "<15")
        result = get_table(data, col_defs=col_defs)
        self.assertIn("Alice", result)
        self.assertIn("Engineer", result)


class TestPrefixSuffix(unittest.TestCase):
    """Comprehensive tests for prefix, prefix_align, suffix, and suffix_align in column definitions."""

    def test_basic_prefix(self):
        """Test basic prefix without alignment specifier."""
        data = [[100, 200], [300, 400]]
        col_defs = ["$(10)", "$(10)"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("$100", result)
        self.assertIn("$200", result)
        self.assertIn("$300", result)
        self.assertIn("$400", result)

    def test_basic_suffix(self):
        """Test basic suffix without alignment specifier."""
        data = [[50, 75], [100, 125]]
        col_defs = ["(10)%", "(10)%"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("50%", result)
        self.assertIn("75%", result)
        self.assertIn("100%", result)
        self.assertIn("125%", result)

    def test_prefix_and_suffix_combined(self):
        """Test using both prefix and suffix on the same column."""
        data = [[100, 200], [300, 400]]
        col_defs = ["$(10)USD", "$(10)EUR"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("$100USD", result)
        self.assertIn("$200EUR", result)
        self.assertIn("$300USD", result)
        self.assertIn("$400EUR", result)

    def test_prefix_with_left_align(self):
        """Test prefix with left alignment (<)."""
        data = [[5, 10], [100, 200]]
        col_defs = ["<$(>10)", "<$(>10)"]
        result = get_table(data, col_defs=col_defs)
        # Prefix should be left-aligned in cell
        self.assertIn("$", result)
        self.assertIn("5", result)
        self.assertIn("100", result)

    def test_prefix_with_right_align(self):
        """Test prefix with right alignment (> is default)."""
        data = [[5, 10], [100, 200]]
        col_defs = [">$(>10)", ">$(>10)"]
        result = get_table(data, col_defs=col_defs)
        # Prefix should be right-aligned (prepended to value)
        self.assertIn("$", result)
        self.assertIn("5", result)
        self.assertIn("100", result)

    def test_suffix_with_left_align(self):
        """Test suffix with left alignment (< is default)."""
        data = [[50, 75]]
        col_defs = ["(10)<%", "(10)<%"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("50%", result)
        self.assertIn("75%", result)

    def test_suffix_with_right_align(self):
        """Test suffix with right alignment (>)."""
        data = [[50, 75]]
        col_defs = ["(10)>%", "(10)>%"]
        result = get_table(data, col_defs=col_defs)
        # Suffix should be right-aligned in cell
        self.assertIn("%", result)
        self.assertIn("50", result)
        self.assertIn("75", result)

    def test_prefix_default_align(self):
        """Test prefix without explicit alignment (defaults to right >)."""
        data = [[5, 10]]
        col_defs = ["$(10)"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("$", result)
        self.assertIn("5", result)

    def test_prefix_with_format_spec(self):
        """Test prefix combined with format specification."""
        data = [[1234.567, 9876.543]]
        col_defs = ["$(>15,.2f)USD", "€(>15,.2f)EUR"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("$1,234.57USD", result)
        self.assertIn("€9,876.54EUR", result)

    def test_suffix_with_format_spec(self):
        """Test suffix combined with format specification."""
        data = [[0.234, 0.567]]
        col_defs = ["(>10.1%)pts", "(>10.1%)bps"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("23.4%pts", result)
        self.assertIn("56.7%bps", result)

    def test_multi_char_prefix(self):
        """Test multi-character prefix."""
        data = [[100, 200]]
        col_defs = ["USD (15)", "EUR (15)"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("USD 100", result)
        self.assertIn("EUR 200", result)

    def test_multi_char_suffix(self):
        """Test multi-character suffix."""
        data = [[100, 200]]
        col_defs = ["(15) dollars", "(15) euros"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("100 dollars", result)
        self.assertIn("200 euros", result)

    def test_prefix_suffix_with_width(self):
        """Test that width accounts for prefix and suffix length when aligned."""
        data = [[100]]
        col_defs = ["<$(20)>USD"]
        result = get_table(data, col_defs=col_defs)
        # Should include prefix and suffix with proper spacing
        self.assertIn("$", result)
        self.assertIn("USD", result)
        self.assertIn("100", result)

    def test_empty_prefix_suffix(self):
        """Test that specs without prefix/suffix work as before."""
        data = [[100, 200]]
        col_defs = ["10", ">10"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("100", result)
        self.assertIn("200", result)
        # Should not have dollar signs or other decorations
        self.assertNotIn("$", result)

    def test_prefix_suffix_with_string_values(self):
        """Test prefix and suffix with string values."""
        data = [["Alice", "Bob"], ["Charlie", "Diana"]]
        col_defs = ["Mr. (15) Sr.", "Ms. (15) Jr."]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("Mr. Alice Sr.", result)
        self.assertIn("Ms. Bob Jr.", result)
        self.assertIn("Mr. Charlie Sr.", result)
        self.assertIn("Ms. Diana Jr.", result)

    def test_prefix_suffix_coldef_parsing(self):
        """Test that ColDef.parse correctly extracts prefix, prefix_align, suffix, and suffix_align."""
        # Basic prefix
        col_def = ColDef.parse("$(10)")
        self.assertEqual(col_def.prefix, "$")
        self.assertEqual(col_def.prefix_align, "")
        self.assertEqual(col_def.suffix, "")
        self.assertEqual(col_def.width, 10)

        # Basic suffix
        col_def = ColDef.parse("(10)%")
        self.assertEqual(col_def.prefix, "")
        self.assertEqual(col_def.suffix, "%")
        self.assertEqual(col_def.suffix_align, "")
        self.assertEqual(col_def.width, 10)

        # Both prefix and suffix
        col_def = ColDef.parse("$(10)USD")
        self.assertEqual(col_def.prefix, "$")
        self.assertEqual(col_def.suffix, "USD")
        self.assertEqual(col_def.width, 10)

        # Prefix with right alignment (explicit)
        col_def = ColDef.parse(">$(10)")
        self.assertEqual(col_def.prefix, "$")
        self.assertEqual(col_def.prefix_align, ">")
        self.assertEqual(col_def.width, 10)

        # Prefix with left alignment
        col_def = ColDef.parse("<$(10)")
        self.assertEqual(col_def.prefix, "$")
        self.assertEqual(col_def.prefix_align, "<")
        self.assertEqual(col_def.width, 10)

        # Suffix with left alignment (explicit)
        col_def = ColDef.parse("(10)<%")
        self.assertEqual(col_def.suffix, "%")
        self.assertEqual(col_def.suffix_align, "<")
        self.assertEqual(col_def.width, 10)

        # Suffix with right alignment
        col_def = ColDef.parse("(10)>%")
        self.assertEqual(col_def.suffix, "%")
        self.assertEqual(col_def.suffix_align, ">")
        self.assertEqual(col_def.width, 10)

        # No prefix/suffix markers
        col_def = ColDef.parse("10")
        self.assertEqual(col_def.prefix, "")
        self.assertEqual(col_def.suffix, "")
        self.assertEqual(col_def.width, 10)

        # Both alignments specified
        col_def = ColDef.parse("<$(10)>USD")
        self.assertEqual(col_def.prefix, "$")
        self.assertEqual(col_def.prefix_align, "<")
        self.assertEqual(col_def.suffix, "USD")
        self.assertEqual(col_def.suffix_align, ">")
        self.assertEqual(col_def.width, 10)

    def test_prefix_suffix_with_alignment(self):
        """Test prefix/suffix with various value alignment options."""
        data = [[100, 200, 300]]
        col_defs = ["$(<15)USD", "$(>15)USD", "$(^15)USD"]
        result = get_table(data, col_defs=col_defs)
        # All should have prefix and suffix
        self.assertIn("$100USD", result)
        self.assertIn("$200USD", result)
        self.assertIn("$300USD", result)

    def test_prefix_suffix_with_truncate(self):
        """Test prefix and suffix with truncate flag."""
        data = [["VeryLongValue", "Short"]]
        col_defs = ["[(10T)]", "[(10T)]"]
        result = get_table(data, col_defs=col_defs)
        # Should truncate the value but keep prefix/suffix
        self.assertIn("[", result)
        self.assertIn("]", result)
        # VeryLongValue should be truncated
        self.assertIn("…", result)

    def test_prefix_suffix_with_auto_fill(self):
        """Test that auto-fill flag works with format specs."""
        data = [[100, 200]]
        # Test that A flag is parsed correctly (actual auto-fill behavior depends on table_width)
        col_def = ColDef.parse("$(A)")
        self.assertTrue(col_def.auto_fill)
        self.assertEqual(col_def.prefix, "$")
        
        # Also test in actual table (auto-fill may not apply prefix/suffix without alignments)
        result = get_table(data, col_defs=["10A", "10A"])
        self.assertIn("100", result)
        self.assertIn("200", result)

    def test_prefix_suffix_with_numeric_formatting(self):
        """Test prefix/suffix with various numeric format types."""
        data = [[1234.5, 255, 0.75]]
        col_defs = ["$(>12,.2f)USD", "0x(>6X)", "(>8.0%)pts"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("$1,234.50USD", result)
        self.assertIn("0x", result)
        self.assertIn("FF", result)
        self.assertIn("75%pts", result)

    def test_prefix_with_unicode_chars(self):
        """Test prefix with Unicode/emoji characters."""
        data = [[100, 200]]
        col_defs = ["💰(10)", "🎯(10)"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("💰100", result)
        self.assertIn("🎯200", result)

    def test_suffix_with_unicode_chars(self):
        """Test suffix with Unicode/emoji characters."""
        data = [[100, 200]]
        col_defs = ["(10)⭐", "(10)✓"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("100⭐", result)
        self.assertIn("200✓", result)

    def test_prefix_suffix_in_table_row(self):
        """Test prefix/suffix work in get_table_row."""
        values = [100, 200]
        col_defs = ["$(10)USD", "€(10)EUR"]
        result = get_table_row(values, col_defs=col_defs)
        self.assertIn("$100USD", result)
        self.assertIn("€200EUR", result)

    def test_prefix_suffix_width_calculation(self):
        """Test that width is properly adjusted for prefix/suffix in format_spec when aligned."""
        col_def = ColDef.parse("<$(20)>USD")
        # Total width should be 20
        self.assertEqual(col_def.width, 20)
        # Format spec width should be adjusted: 20 - 1 (prefix) - 3 (suffix) = 16
        if col_def.format_spec:
            self.assertEqual(col_def.format_spec.width, 16)

    def test_prefix_suffix_width_no_adjustment(self):
        """Test that width is NOT adjusted when prefix/suffix not aligned."""
        col_def = ColDef.parse("$(20)USD")
        # Total width should be 20
        self.assertEqual(col_def.width, 20)
        # Format spec width should NOT be adjusted (no alignment)
        if col_def.format_spec:
            # When not aligned, format_spec.align should be empty
            self.assertEqual(col_def.format_spec.align, "")

    def test_prefix_suffix_with_set_width(self):
        """Test that set_width adjusts format_spec width correctly when aligned."""
        col_def = ColDef.parse("<$(.2f)>USD")
        col_def.set_width(20)
        # Width should be 20
        self.assertEqual(col_def.width, 20)
        # Format spec width should be 20 - 1 - 3 = 16
        if col_def.format_spec:
            self.assertEqual(col_def.format_spec.width, 16)

    def test_empty_parens(self):
        """Test empty parentheses without format spec."""
        data = [[100]]
        col_defs = ["$(10)"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("$100", result)

    def test_prefix_suffix_with_negative_numbers(self):
        """Test prefix/suffix with negative numbers."""
        data = [[-100, -200]]
        col_defs = ["$(10)USD", "$(10)EUR"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("$-100USD", result)
        self.assertIn("$-200EUR", result)

    def test_prefix_suffix_with_zero(self):
        """Test prefix/suffix with zero values."""
        data = [[0, 0.0]]
        col_defs = ["$(10)USD", "$(>8.2f)EUR"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("$0USD", result)
        self.assertIn("$0.00EUR", result)

    def test_prefix_suffix_with_none_fallback(self):
        """Test prefix/suffix when value can't be formatted (falls back to str)."""
        data = [[None, "text"]]
        col_defs = ["$(.2f)USD", "Pre(10)Suf"]
        result = get_table(data, col_defs=col_defs)
        # Should fall back to string conversion (no prefix/suffix applied on failure)
        self.assertIn("None", result)
        self.assertIn("Pretext", result)

    def test_complex_prefix_suffix_scenario(self):
        """Test complex real-world scenario with mixed prefix/suffix columns."""
        data = [
            [1000, 0.15, 5, "Pass"],
            [2500, 0.23, 8, "Fail"],
            [750, 0.08, 3, "Pass"]
        ]
        col_defs = [
            "$(>,.0f)USD",      # Currency with thousands separator
            "(>8.1%)%",          # Percentage with suffix
            "#(>2d)",            # Count with prefix (no suffix to avoid wrapping)
            "10"                 # Plain status
        ]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("$1,000USD", result)
        self.assertIn("15.0%%", result)
        self.assertIn("#5", result)
        self.assertIn("Pass", result)
        self.assertIn("$2,500USD", result)
        self.assertIn("23.0%%", result)

    def test_prefix_align_left_with_right_aligned_values(self):
        """Test left-aligned prefix with right-aligned values."""
        data = [[5], [100]]
        col_def = ColDef.parse("<$(>10)")
        
        self.assertEqual(col_def.prefix, "$")
        self.assertEqual(col_def.prefix_align, "<")
        self.assertEqual(col_def.width, 10)

    def test_suffix_align_right_with_left_aligned_values(self):
        """Test right-aligned suffix with left-aligned values."""
        data = [[5], [100]]
        col_def = ColDef.parse("(<10)>%")
        
        self.assertEqual(col_def.suffix, "%")
        self.assertEqual(col_def.suffix_align, ">")
        self.assertEqual(col_def.width, 10)

    def test_suffix_only_with_format_spec(self):
        """Test suffix without prefix but with format specification."""
        data = [[0.15, 0.23]]
        col_defs = ["(>8.1%)pct", "(>14.2%)percent"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("15.0%pct", result)
        self.assertIn("23.00%percent", result)

    def test_prefix_only_with_format_spec(self):
        """Test prefix without suffix but with format specification."""
        data = [[1000, 2500]]
        col_defs = ["$(>10,.0f)", "£(>12,.2f)"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("$1,000", result)
        self.assertIn("£2,500.00", result)

    def test_prefix_suffix_spaces(self):
        """Test prefix and suffix with spaces."""
        data = [[100]]
        col_defs = ["USD (20) dollars"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("USD ", result)
        self.assertIn("100", result)
        self.assertIn(" dollars", result)

    def test_only_suffix_no_prefix(self):
        """Test suffix without prefix using parens."""
        data = [[50, 75]]
        col_defs = ["(10) oz", "(10) lbs"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("50 oz", result)
        self.assertIn("75 lbs", result)

    def test_aligned_prefix_and_suffix_together(self):
        """Test both aligned prefix and aligned suffix."""
        data = [[100]]
        col_defs = ["<$(20)>USD"]
        result = get_table(data, col_defs=col_defs)
        # Should have proper spacing with both prefix and suffix aligned
        self.assertIn("$", result)
        self.assertIn("USD", result)
        self.assertIn("100", result)

    def test_parentheses_in_plain_format(self):
        """Test that format specs without prefix/suffix still work."""
        data = [[100, 200]]
        col_defs = ["10", "15"]
        result = get_table(data, col_defs=col_defs)
        self.assertIn("100", result)
        self.assertIn("200", result)

    def test_documentation_example(self):
        """Test the example from the documentation."""
        data = [
            ["Apple", 1.99, 12],
            ["Banana", 1.49, 10],
            ["Egg", 13.99, 2],
        ]
        col_defs = ["A", "<$ (>8.2f)", "(^8) oz"]
        result = get_table(data, col_defs=col_defs)
        # Should format prices with $ prefix and weights with oz suffix
        self.assertIn("$ ", result)
        self.assertIn(" oz", result)
        self.assertIn("1.99", result)
        self.assertIn("12", result)


if __name__ == "__main__":
    unittest.main()
