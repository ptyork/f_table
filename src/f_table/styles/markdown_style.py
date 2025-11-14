"""Markdown table style for GitHub-flavored markdown."""

from .table_style import TableStyle


class MarkdownStyle(TableStyle):
    """GitHub-flavored Markdown tables for documentation."""

    def __init__(self):
        super().__init__()
        self.top_border = False
        self.bottom_border = False
        self.terminal_style = False
        self.allow_lazy_header = False
        self.force_header = True
        self.align_char = ":"

        self.min_width = 3

        self.header_delimiter = "|"
        self.header_left = "|"
        self.header_right = "|"

        self.header_bottom_line = "-"
        self.header_bottom_delimiter = "|"
        self.header_bottom_left = "|"
        self.header_bottom_right = "|"

        self.values_delimiter = "|"
        self.values_left = "|"
        self.values_right = "|"

        self.row_separator_line = ""
        self.row_separator_delimiter = ""
        self.row_separator_left = ""
        self.row_separator_right = ""
