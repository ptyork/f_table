"""ODT style: writes an OpenDocument Text document using odfpy.

Optional dependency: odfpy (group: odt)
"""

from typing import Any, IO, TYPE_CHECKING
from pathlib import Path

from .table_style import TableStyle

if TYPE_CHECKING:  # avoid circular import at runtime
    from ..craftable import ColDefList


class OdtStyle(TableStyle):
    def __init__(self):
        super().__init__()
        self.terminal_style = False
        self.string_output = False  # Binary format

    ###############################################################################
    # write_table
    ###############################################################################

    def write_table(
        self,
        value_rows: list[list[Any]],
        header_row: list[str] | None,
        col_defs: "ColDefList",
        header_defs: "ColDefList | None",
        file: str | Path | IO[bytes],
    ) -> None:
        """Write table to ODT file format."""
        try:
            from odf.opendocument import OpenDocumentText  # type: ignore
            from odf import table, text  # type: ignore
        except Exception as e:  # pragma: no cover - only hit without optional dep
            raise ImportError(
                "odfpy is required for OdtStyle; install group 'odt'"
            ) from e

        doc = OpenDocumentText()

        # Define paragraph styles
        from odf.style import Style, TextProperties, ParagraphProperties  # type: ignore

        odf_table = table.Table(name="Table1")

        # Define alignment styles
        left_style = Style(name="LeftAlign", family="paragraph")
        left_style.addElement(ParagraphProperties(textalign="left"))
        doc.automaticstyles.addElement(left_style)

        center_style = Style(name="CenterAlign", family="paragraph")
        center_style.addElement(ParagraphProperties(textalign="center"))
        doc.automaticstyles.addElement(center_style)

        right_style = Style(name="RightAlign", family="paragraph")
        right_style.addElement(ParagraphProperties(textalign="right"))
        doc.automaticstyles.addElement(right_style)

        # Bold styles for headers
        header_bold_left = Style(name="HeaderBoldLeft", family="paragraph")
        header_bold_left.addElement(TextProperties(fontweight="bold"))
        header_bold_left.addElement(ParagraphProperties(textalign="left"))
        doc.automaticstyles.addElement(header_bold_left)

        header_bold_center = Style(name="HeaderBoldCenter", family="paragraph")
        header_bold_center.addElement(TextProperties(fontweight="bold"))
        header_bold_center.addElement(ParagraphProperties(textalign="center"))
        doc.automaticstyles.addElement(header_bold_center)

        header_bold_right = Style(name="HeaderBoldRight", family="paragraph")
        header_bold_right.addElement(TextProperties(fontweight="bold"))
        header_bold_right.addElement(ParagraphProperties(textalign="right"))
        doc.automaticstyles.addElement(header_bold_right)

        # Write header row with proper alignment
        if header_row:
            hdr_row = table.TableRow()
            for i, header in enumerate(header_row):
                cell = table.TableCell()
                # Use header_defs for alignment if provided
                if header_defs and i < len(header_defs):
                    hdr_def = header_defs[i]
                    if hdr_def.align == ">":
                        p = text.P(stylename=header_bold_right, text=str(header))
                    elif hdr_def.align == "^":
                        p = text.P(stylename=header_bold_center, text=str(header))
                    else:  # Left or default
                        p = text.P(stylename=header_bold_left, text=str(header))
                else:
                    # Default to centered bold
                    p = text.P(stylename=header_bold_center, text=str(header))
                cell.addElement(p)
                hdr_row.addElement(cell)
                odf_table.addElement(hdr_row)

        # Helper for formatting with preprocess/postprocess
        def _format_for_export(cd, val, row: list[Any], col_idx: int) -> str:
            v2 = cd.preprocess(val, row, col_idx)
            try:
                if v2 is None:
                    s = cd.prefix + (cd.none_text or "") + cd.suffix
                elif cd.format_spec:
                    fmt = f"{{:{cd.format_spec}}}"
                    s = cd.prefix + fmt.format(v2) + cd.suffix
                else:
                    s = cd.prefix + str(v2) + cd.suffix
            except Exception:
                s = cd.prefix + (cd.none_text if v2 is None else str(v2)) + cd.suffix
            return cd.postprocess(val, s, row, col_idx)

        # Write data rows
        for row in value_rows:
            tr = table.TableRow()
            for i, (val, col_def) in enumerate(zip(row, col_defs)):
                tc = table.TableCell()
                # Map ColDef alignment to paragraph style
                if ">" in col_def.align:
                    style = right_style
                elif "^" in col_def.align:
                    style = center_style
                else:
                    style = left_style
                p = text.P(
                    stylename=style, text=_format_for_export(col_def, val, row, i)
                )
                tc.addElement(p)
                tr.addElement(tc)
            odf_table.addElement(tr)

        doc.text.addElement(odf_table)

        # Save (OpenDocumentText.save accepts filename or file-like)
        doc.save(file)
