"""Rounded border screen style with arc characters."""

from .box_chars import BoxChars
from .table_style import TableStyle


class RoundedBorderScreenStyle(TableStyle):
    """Rounded corners for a softer look (╭ ╮ ╰ ╯ │ ─)."""

    def __init__(self):
        super().__init__()
        self.header_top_left = BoxChars.SINGLE_ARC_DOWN_AND_RIGHT
        self.header_top_right = BoxChars.SINGLE_ARC_DOWN_AND_LEFT
        self.no_header_top_left = BoxChars.SINGLE_ARC_DOWN_AND_RIGHT
        self.no_header_top_right = BoxChars.SINGLE_ARC_DOWN_AND_LEFT
        self.values_bottom_left = BoxChars.SINGLE_ARC_UP_AND_RIGHT
        self.values_bottom_right = BoxChars.SINGLE_ARC_UP_AND_LEFT
