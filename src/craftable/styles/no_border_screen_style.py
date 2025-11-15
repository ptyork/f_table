"""No border screen style for minimal output."""

from .table_style import TableStyle


class NoBorderScreenStyle(TableStyle):
    """Minimal, whitespace-delimited with a simple header separator."""

    def __init__(self):
        super().__init__()
        self.top_border = False
        self.bottom_border = False
        self.header_left = ""
        self.header_right = ""
        self.header_bottom_left = ""
        self.header_bottom_right = ""
        self.values_left = ""
        self.values_right = ""
        self.values_bottom_left = ""
        self.values_bottom_right = ""
        self.row_separator_line = "◦"
        self.row_separator_left = ""
        self.row_separator_right = ""
