"""ASCII-only table style for plain terminals."""

from .table_style import TableStyle


class ASCIIStyle(TableStyle):
    """ASCII-only style for plain terminals and logs (uses + - |)."""

    def __init__(self):
        super().__init__()
        self.terminal_style = False

        # Outer borders
        self.top_border = True
        self.bottom_border = True

        # Header borders
        self.header_top_line = "-"
        self.header_top_delimiter = "+"
        self.header_top_left = "+"
        self.header_top_right = "+"

        self.header_delimiter = "|"
        self.header_left = "|"
        self.header_right = "|"

        self.header_bottom_line = "-"
        self.header_bottom_delimiter = "+"
        self.header_bottom_left = "+"
        self.header_bottom_right = "+"

        # Data borders
        self.values_delimiter = "|"
        self.values_left = "|"
        self.values_right = "|"

        self.values_bottom_line = "-"
        self.values_bottom_delimiter = "+"
        self.values_bottom_left = "+"
        self.values_bottom_right = "+"

        # Row separator
        self.row_separator_line = "-"
        self.row_separator_left = "|"
        self.row_separator_right = "|"
