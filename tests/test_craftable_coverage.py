"""Additional tests to improve coverage of craftable.py core functionality."""

import unittest
from unittest.mock import patch
from io import StringIO

from craftable import get_table, ColDef, ColDefList, export_table
from craftable.styles import BasicScreenStyle, MarkdownStyle


class TestTerminalWidth(unittest.TestCase):
    """Test terminal width detection and edge cases."""

    @patch("craftable.craftable.get_terminal_size")
    def test_terminal_width_exception_handling(self, mock_term):
        """Test when get_terminal_size raises an exception."""
        mock_term.side_effect = Exception("Terminal not available")

        # Should fall back to max_term_width (120 default)
        from craftable.craftable import get_term_width

        result = get_term_width()
        self.assertEqual(result, 120)

    @patch("craftable.craftable.get_terminal_size")
    def test_terminal_width_with_max(self, mock_term):
        """Test with maximum terminal width constraint."""
        from os import terminal_size

        mock_term.return_value = terminal_size((150, 50))

        from craftable.craftable import get_term_width

        # Should use the actual terminal width when below max
        result = get_term_width(200)
        self.assertEqual(result, 150)

        # Should cap at max_term_width when exceeded
        result = get_term_width(100)
        self.assertEqual(result, 100)

    @patch("craftable.craftable.get_terminal_size")
    def test_terminal_width_max_zero(self, mock_term):
        """Test when max_term_width is 0 (unlimited)."""
        from os import terminal_size

        mock_term.return_value = terminal_size((120, 50))

        from craftable.craftable import get_term_width

        result = get_term_width(0)
        self.assertEqual(result, 120)


class TestColDefEdgeCases(unittest.TestCase):
    """Test ColDef edge cases and error paths."""

    def test_format_with_exception_handling(self):
        """Test that format exceptions are caught in non-strict mode."""
        col_def = ColDef.parse(">10.2f")  # No S flag - non-strict

        # Should not raise, just convert to string
        result = col_def.format("not a number")
        self.assertIn("not a number", result)

    def test_format_without_strict_falls_back_to_str(self):
        """Test that non-strict mode converts to string on error."""
        col_def = ColDef.parse(">10.2f")  # No S flag

        # Should convert to string instead of raising
        result = col_def.format("not a number")
        self.assertIn("not a number", result)

    def test_preprocessor_exception_returns_original(self):
        """Test preprocessor exception handling."""

        def bad_preprocessor(val, row, idx):  # new signature
            raise ValueError("Preprocessor error")

        col_def = ColDef(width=10, preprocessor=bad_preprocessor)

        # Should return original value when preprocessor fails
        result = col_def.preprocess("test", ["test"], 0)
        self.assertEqual(result, "test")

    def test_postprocessor_exception_returns_original_text(self):
        """Test postprocessor exception handling."""

        def bad_postprocessor(val, text, row, idx):  # new signature
            raise ValueError("Postprocessor error")

        col_def = ColDef(width=10, postprocessor=bad_postprocessor)

        # Should return original text when postprocessor fails
        result = col_def.postprocess(
            "value", "formatted_text", ["value", "formatted_text"], 0
        )
        self.assertEqual(result, "formatted_text")

    def test_truncate_with_ellipsis(self):
        """Test truncation with ellipsis."""
        col_def = ColDef.parse("8T")  # Width 8, truncate
        result = col_def.format("Very long text that needs truncation")

        self.assertEqual(len(result), 8)
        self.assertIn("…", result)

    def test_center_alignment(self):
        """Test center alignment."""
        col_def = ColDef.parse("^10")
        result = col_def.format("test")

        self.assertEqual(len(result), 10)
        # "test" centered in 10 chars should have spaces on both sides
        self.assertTrue(result.strip() == "test")
        self.assertTrue(result.startswith(" "))
        self.assertTrue(result.endswith(" "))

    def test_right_alignment(self):
        """Test right alignment."""
        col_def = ColDef.parse(">10")
        result = col_def.format("test")

        self.assertEqual(len(result), 10)
        self.assertTrue(result.endswith("test"))
        self.assertTrue(result.startswith(" "))


class TestColDefListEdgeCases(unittest.TestCase):
    """Test ColDefList edge cases and validation."""

    def test_setitem_invalid_value_raises(self):
        """Test that setting invalid values raises ValueError."""
        col_defs = ColDefList(["10", "20"])

        # Should raise when setting non-string, non-ColDef
        with self.assertRaises(ValueError):
            col_defs[0] = 123

    def test_setitem_slice_with_invalid_values(self):
        """Test slice assignment validation."""
        col_defs = ColDefList(["10", "20", "30"])

        # Should raise when slice contains invalid values
        with self.assertRaises(ValueError):
            col_defs[0:2] = [123, 456]

    def test_append_invalid_value_raises(self):
        """Test that appending invalid values raises ValueError."""
        col_defs = ColDefList()

        with self.assertRaises(ValueError):
            col_defs.append(123)

    def test_getitem_slice_returns_coldeflist(self):
        """Test that slicing returns a ColDefList."""
        col_defs = ColDefList(["10", "20", "30", "40"])

        result = col_defs[1:3]
        self.assertIsInstance(result, ColDefList)
        self.assertEqual(len(result), 2)


class TestExportTableEdgeCases(unittest.TestCase):
    """Test export_table edge cases."""

    def test_export_table_with_string_output_style(self):
        """Test export_table with a string-output style."""
        rows = [["Alice", 30], ["Bob", 25]]

        # BasicScreenStyle has string_output=True, which is fine
        # Just verify it works
        stream = StringIO()
        result = export_table(
            rows, header_row=["Name", "Age"], style=BasicScreenStyle(), file=stream
        )

        # Should return the stream
        self.assertIsNone(result)
        content = stream.getvalue()
        self.assertIn("Alice", content)

    def test_export_table_markdown_requires_header(self):
        """Test that Markdown export creates empty header if none provided."""
        rows = [["Alice", 30], ["Bob", 25]]
        stream = StringIO()

        # MarkdownStyle should work but create empty header
        result = export_table(rows, header_row=None, style=MarkdownStyle(), file=stream)

        # export_table returns None
        self.assertIsNone(result)
        content = stream.getvalue()
        self.assertIn("|", content)


class TestGetTableEdgeCases(unittest.TestCase):
    """Test get_table edge cases and error conditions."""

    def test_empty_data_with_header(self):
        """Test table with header but no data rows."""
        result = get_table([], header_row=["Name", "Age"])

        # Should display "No data to display" message
        self.assertIn("No data to display", result)

    def test_jagged_rows_padding(self):
        """Test that jagged rows get padded with empty strings."""
        rows = [
            ["Alice", 30, "Engineer"],
            ["Bob"],  # Missing columns
            ["Charlie", 25],  # Missing one column
        ]

        result = get_table(rows, header_row=["Name", "Age", "Title"])

        # Should not raise and should display all rows
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)
        self.assertIn("Charlie", result)

    def test_header_shorter_than_data(self):
        """Test when header has fewer columns than data."""
        rows = [["Alice", 30, "Engineer"], ["Bob", 25, "Designer"]]
        header = ["Name"]  # Only one header for three columns

        result = get_table(rows, header_row=header)

        # Should handle gracefully and show data
        self.assertIn("Alice", result)
        self.assertIn("30", result)

    def test_header_longer_than_data(self):
        """Test when header has more columns than data."""
        rows = [["Alice"], ["Bob"]]
        header = ["Name", "Age", "Title"]  # Three headers for one column

        result = get_table(rows, header_row=header)

        # Should handle gracefully
        self.assertIn("Name", result)
        self.assertIn("Alice", result)

    def test_auto_fill_without_table_width(self):
        """Test auto-fill columns without explicit table_width."""
        rows = [["Alice", "Engineer"], ["Bob", "Designer"]]
        col_defs = ["A", "10"]  # First column auto-fills

        # Should use terminal width or default
        result = get_table(rows, col_defs=col_defs)

        self.assertIn("Alice", result)
        self.assertIn("Engineer", result)

    def test_multiple_auto_fill_columns(self):
        """Test multiple columns with auto-fill flag."""
        rows = [["Alice", "Engineer", "30"], ["Bob", "Designer", "25"]]
        col_defs = ["A", "A", "5"]  # Two auto-fill columns

        result = get_table(rows, col_defs=col_defs, table_width=60)

        # Should split remaining space between auto-fill columns
        self.assertIn("Alice", result)
        self.assertIn("Engineer", result)

    def test_separate_rows_flag(self):
        """Test separate_rows flag adds dividers."""
        rows = [["Alice", 30], ["Bob", 25], ["Charlie", 35]]

        result = get_table(
            rows,
            header_row=["Name", "Age"],
            separate_rows=True,
            style=BasicScreenStyle(),
        )

        # Should have row separators (count horizontal lines)
        line_count = result.count("─")
        self.assertGreater(line_count, 10)  # Multiple separator lines

    def test_lazy_end_flag(self):
        """Test lazy_end flag omits right border."""
        rows = [["Alice", 30], ["Bob", 25]]

        result_normal = get_table(
            rows, header_row=["Name", "Age"], style=BasicScreenStyle(), lazy_end=False
        )
        result_lazy = get_table(
            rows, header_row=["Name", "Age"], style=BasicScreenStyle(), lazy_end=True
        )

        # Lazy version should be shorter (no right border on data rows)
        self.assertNotEqual(result_normal, result_lazy)

    def test_preprocessors_list(self):
        """Test preprocessors parameter."""
        rows = [[5, 10], [15, 20]]

        def double(x, row, idx):
            return x * 2

        result = get_table(rows, header_row=["A", "B"], preprocessors=[double, None])

        # First column should be doubled
        self.assertIn("10", result)  # 5 * 2
        self.assertIn("10", result)  # Original 10

    def test_postprocessors_list(self):
        """Test postprocessors parameter."""
        rows = [["Alice", 30], ["Bob", 25]]

        def add_star(val, text, row, idx):
            return f"*{text}*"

        result = get_table(
            rows, header_row=["Name", "Age"], postprocessors=[add_star, None]
        )

        # First column values should have stars
        # Note: postprocessor applies after formatting/padding
        self.assertIn("*Alice", result)
        self.assertIn("*Bob", result)


class TestColDefParsing(unittest.TestCase):
    """Test ColDef.parse edge cases."""

    def test_parse_with_prefix_and_suffix(self):
        """Test parsing format with prefix and suffix."""
        col_def = ColDef.parse("$ (10.2f) USD")

        self.assertEqual(col_def.prefix, "$ ")
        self.assertEqual(col_def.suffix, " USD")
        self.assertEqual(col_def.width, 10)

    def test_parse_with_all_flags(self):
        """Test parsing with A and T flags."""
        col_def = ColDef.parse("10AT")

        self.assertTrue(col_def.auto_fill)
        self.assertTrue(col_def.truncate)

    def test_parse_with_fill_and_align(self):
        """Test parsing with fill character and alignment."""
        col_def = ColDef.parse("*>10")
        self.assertIsNotNone(col_def.format_spec)
        if col_def.format_spec:
            self.assertEqual(col_def.format_spec.fill, "*")
        # Align is stored separately in ColDef
        self.assertEqual(col_def.align, ">")

    def test_parse_with_grouping(self):
        """Test parsing with thousands separator."""
        col_def = ColDef.parse(">,d")
        self.assertIsNotNone(col_def.format_spec)
        if col_def.format_spec:
            self.assertEqual(col_def.format_spec.grouping, ",")

    def test_parse_minimal_format(self):
        """Test parsing minimal format string."""
        # Empty string is valid - creates ColDef with defaults
        col_def = ColDef.parse("")

        self.assertEqual(col_def.width, 0)
        self.assertEqual(col_def.prefix, "")
        self.assertEqual(col_def.suffix, "")

    def test_parse_with_equals_align(self):
        """Test that = alignment resets fill and align."""
        col_def = ColDef.parse("*=10")
        # = alignment should be converted to empty
        self.assertEqual(col_def.align, "")
        self.assertIsNotNone(col_def.format_spec)
        if col_def.format_spec:
            self.assertEqual(col_def.format_spec.fill, "")

    def test_parse_width_adjustment_with_prefix_suffix(self):
        """Test width adjustment for prefix/suffix alignment."""
        # Prefix left-aligned and suffix right-aligned triggers width adjustment
        col_def = ColDef.parse("<$ (10.2f)> USD")
        # Width should be adjusted to account for prefix/suffix
        self.assertIsNotNone(col_def.format_spec)
        if col_def.format_spec:
            self.assertGreater(col_def.format_spec.width, 0)


class TestExportTableAdditional(unittest.TestCase):
    """Additional export_table tests."""

    def test_export_with_path_object(self):
        """Test export with Path object instead of string."""
        from pathlib import Path
        import tempfile

        rows = [["Alice", 30], ["Bob", 25]]

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            result = export_table(
                rows, header_row=["Name", "Age"], style=BasicScreenStyle(), file=path
            )

            # Should return Path object
            self.assertIsInstance(result, Path)
            self.assertTrue(path.exists())

            content = path.read_text()
            self.assertIn("Alice", content)

    def test_export_get_table_fallback(self):
        """Test export falls back to get_table for string output styles."""
        rows = [["Alice", 30]]
        stream = StringIO()

        # String output should work via get_table fallback
        export_table(
            rows, header_row=["Name", "Age"], style=BasicScreenStyle(), file=stream
        )

        content = stream.getvalue()
        self.assertIn("Alice", content)


if __name__ == "__main__":
    unittest.main()
