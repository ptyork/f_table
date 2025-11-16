"""Base table style class."""

from abc import ABC

from .box_chars import BoxChars


class TableStyle(ABC):
    """Abstract base class for table styles.

    Defines all the visual attributes that control how a table is rendered,
    including borders, delimiters, padding, and special characters.
    """

    def __init__(self):
        self.top_border = True
        self.bottom_border = True
        self.terminal_style = True
        self.string_output = True  # False for binary formats (DOCX/XLSX/ODF/RTF)
        self.allow_lazy_header = True
        self.force_header = False
        self.align_char = None

        self.cell_padding = 1
        self.min_width = 1

        self.no_header_top_line = BoxChars.SINGLE_HORIZONTAL
        self.no_header_top_delimiter = BoxChars.SINGLE_DOWN_AND_HORIZONTAL
        self.no_header_top_left = BoxChars.SINGLE_DOWN_AND_RIGHT
        self.no_header_top_right = BoxChars.SINGLE_DOWN_AND_LEFT

        self.header_top_line = BoxChars.SINGLE_HORIZONTAL
        self.header_top_delimiter = BoxChars.SINGLE_DOWN_AND_HORIZONTAL
        self.header_top_left = BoxChars.SINGLE_DOWN_AND_RIGHT
        self.header_top_right = BoxChars.SINGLE_DOWN_AND_LEFT

        self.header_delimiter = BoxChars.SINGLE_VERTICAL
        self.header_left = BoxChars.SINGLE_VERTICAL
        self.header_right = BoxChars.SINGLE_VERTICAL

        self.header_bottom_line = BoxChars.SINGLE_HORIZONTAL
        self.header_bottom_delimiter = BoxChars.SINGLE_VERTICAL_AND_HORIZONTAL
        self.header_bottom_left = BoxChars.SINGLE_VERTICAL_AND_RIGHT
        self.header_bottom_right = BoxChars.SINGLE_VERTICAL_AND_LEFT

        self.values_delimiter = BoxChars.SINGLE_VERTICAL
        self.values_left = BoxChars.SINGLE_VERTICAL
        self.values_right = BoxChars.SINGLE_VERTICAL

        self.values_bottom_line = BoxChars.SINGLE_HORIZONTAL
        self.values_bottom_delimiter = BoxChars.SINGLE_UP_AND_HORIZONTAL
        self.values_bottom_left = BoxChars.SINGLE_UP_AND_RIGHT
        self.values_bottom_right = BoxChars.SINGLE_UP_AND_LEFT

        self.row_separator_line = "◦"
        self.row_separator_delimiter = BoxChars.SINGLE_VERTICAL
        self.row_separator_left = BoxChars.SINGLE_VERTICAL
        self.row_separator_right = BoxChars.SINGLE_VERTICAL
