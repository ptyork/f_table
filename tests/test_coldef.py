import unittest
from f_table import ColDef


class TestColDef(unittest.TestCase):
    def test_parse_and_format(self):
        cd = ColDef.parse("<10")
        self.assertEqual(cd.width, 10)
        self.assertTrue(cd.format("abc").startswith("abc"))

    def test_truncate(self):
        cd = ColDef(width=5, truncate=True)
        self.assertIn("…", cd.format("LongValue"))

    def test_parse_right_align(self):
        cd = ColDef.parse(">15")
        self.assertEqual(cd.width, 15)
        self.assertEqual(cd.align, ">")

    def test_parse_center_align(self):
        cd = ColDef.parse("^25")
        self.assertEqual(cd.width, 25)
        self.assertEqual(cd.align, "^")

    def test_parse_auto_and_truncate_flags(self):
        cd = ColDef.parse("<20AT")
        self.assertEqual(cd.width, 20)
        self.assertTrue(cd.auto_fill)
        self.assertTrue(cd.truncate)

    def test_parse_format_spec(self):
        cd = ColDef.parse(".2f")
        self.assertEqual(str(cd.format_spec), ".2f")

    def test_format_center_and_right(self):
        cd_center = ColDef(width=10, align="^")
        self.assertEqual(len(cd_center.format("Hi")), 10)
        cd_right = ColDef(width=10, align=">")
        self.assertTrue(cd_right.format("Hi").endswith("Hi"))

    def test_set_width_adjusts_aligned_prefix_suffix(self):
        cd = ColDef.parse("<$(.2f)>USD")
        cd.set_width(20)
        self.assertEqual(cd.width, 20)
        if cd.format_spec:
            self.assertEqual(cd.format_spec.width, 16)
