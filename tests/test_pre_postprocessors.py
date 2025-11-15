import unittest
import re
from craftable import get_table, get_table_row
from craftable.styles.no_border_screen_style import NoBorderScreenStyle


class TestPrePostProcessors(unittest.TestCase):
    def test_preprocessor_applies_before_formatting_affecting_value(self):
        rows = [[1, 2, 3]]
        col_defs = [">3d", ">3d", ">3d"]

        def pre_double(x):
            return x * 2

        table = get_table(
            rows,
            col_defs=col_defs,
            style=NoBorderScreenStyle(),
            table_width=40,
            preprocessors=[pre_double, pre_double, pre_double],
        )
        self.assertIn("  2", table)
        self.assertIn("  4", table)
        self.assertIn("  6", table)

    def test_postprocessor_applies_after_format_text_single_row(self):
        row = ["ab", "cd"]
        col_defs = ["<5", "<5"]

        def post_upper(orig, text: str) -> str:
            return text.upper()

        out = get_table_row(
            row,
            col_defs=col_defs,
            style=NoBorderScreenStyle(),
            table_width=30,
            preprocessors=None,
            postprocessors=[post_upper, post_upper],
        )
        self.assertIn("AB", out)
        self.assertIn("CD", out)

    def test_pre_and_post_combined_in_table(self):
        rows = [["alice", 1.2345], ["bob", 9.0]]
        col_defs = ["<10", ">8.2f"]

        def pre_cap(val):
            return str(val).capitalize()

        def post_bracket(original, text):
            return f"[{text}]"

        table = get_table(
            rows,
            header_row=["Name", "Value"],
            col_defs=col_defs,
            style=NoBorderScreenStyle(),
            table_width=60,
            preprocessors=[pre_cap, None],
            postprocessors=[None, post_bracket],
        )
        self.assertIn("Alice", table)
        self.assertIn("Bob", table)
        # Allow for either bracketed alignment variant
        self.assertTrue(re.search(r"\[[^\]]*1\.23[^\]]*\]", table) or "[    1.23]" in table)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()