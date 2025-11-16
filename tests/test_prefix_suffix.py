"""Tests for prefix and suffix in ColDef formatting and width calculations."""

import unittest
from craftable import get_table, get_table_row, ColDef


class TestPrefixSuffix(unittest.TestCase):
    """Prefix/suffix handling in column definitions."""

    def test_basic_prefix(self):
        out = get_table([[100]], col_defs=["$(10)"])
        self.assertIn("$100", out)

    def test_prefix_suffix_width_calculation(self):
        cd = ColDef.parse("<$(20)>USD")
        self.assertEqual(cd.width, 20)
        if cd.format_spec:
            self.assertEqual(cd.format_spec.width, 16)

    def test_numeric_formatting_with_prefix_suffix(self):
        out = get_table([[1234.5, 0.75]], col_defs=["$(>12,.2f)USD", "(>8.0%)pts"])
        # Implementation formats percentage without trailing zero when .0f precision like 0.75 -> 75%
        self.assertIn("$1,234.50USD", out)
        self.assertTrue("75%pts" in out or "75.0%pts" in out)

    def test_unicode_prefix_and_suffix(self):
        out = get_table([[100, 200]], col_defs=["💰(10)", "(10)⭐"])
        self.assertIn("💰100", out)
        self.assertIn("200⭐", out)

    def test_only_suffix_no_prefix(self):
        out = get_table([[50, 75]], col_defs=["(10) oz", "(10) lbs"])
        self.assertIn("50 oz", out)
        self.assertIn("75 lbs", out)

    def test_string_values_with_prefix_suffix(self):
        out = get_table([["Alice", "Bob"]], col_defs=["Mr. (15) Sr.", "Ms. (15) Jr."])
        self.assertIn("Mr. Alice Sr.", out)
        self.assertIn("Ms. Bob Jr.", out)

    def test_prefix_suffix_set_width_adjusts_format_width(self):
        cd = ColDef.parse("<$(.2f)>USD")
        cd.set_width(20)
        self.assertEqual(cd.width, 20)
        if cd.format_spec:
            self.assertEqual(cd.format_spec.width, 16)

    def test_prefix_align_left_with_right_aligned_values(self):
        cd = ColDef.parse("<$(>10)")
        self.assertEqual(cd.prefix, "$")
        self.assertEqual(cd.prefix_align, "<")
        self.assertEqual(cd.width, 10)

    def test_suffix_align_right_with_left_aligned_values(self):
        cd = ColDef.parse("(<10)>%")
        self.assertEqual(cd.suffix, "%")
        self.assertEqual(cd.suffix_align, ">")
        self.assertEqual(cd.width, 10)

    def test_prefix_suffix_in_table_row(self):
        out = get_table_row([100, 200], col_defs=["$(10)USD", "€(10)EUR"])
        self.assertIn("$100USD", out)
        self.assertIn("€200EUR", out)
