"""Styles subpackage for craftable.

All table styles are available in this subpackage.
Import them like: from craftable.styles import DocxStyle, XlsxStyle, etc.
"""

from .box_chars import BoxChars
from .table_style import TableStyle
from .basic_screen_style import BasicScreenStyle
from .rounded_border_screen_style import RoundedBorderScreenStyle
from .no_border_screen_style import NoBorderScreenStyle
from .markdown_style import MarkdownStyle
from .ascii_style import ASCIIStyle
from .docx_style import DocxStyle
from .xlsx_style import XlsxStyle
from .odt_style import OdtStyle
from .ods_style import OdsStyle
from .rtf_style import RtfStyle

__all__ = [
    "BoxChars",
    "TableStyle",
    "BasicScreenStyle",
    "RoundedBorderScreenStyle",
    "NoBorderScreenStyle",
    "MarkdownStyle",
    "ASCIIStyle",
    "DocxStyle",
    "XlsxStyle",
    "OdtStyle",
    "OdsStyle",
    "RtfStyle",
]
