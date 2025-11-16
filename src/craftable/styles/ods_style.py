"""ODS style: writes an OpenDocument Spreadsheet using odfpy.

Optional dependency: odfpy (group: ods)
"""

from typing import Any, IO, TYPE_CHECKING
from datetime import date, datetime
from pathlib import Path

from .table_style import TableStyle

if TYPE_CHECKING:  # avoid circular import at runtime
    from ..craftable import ColDefList


class OdsStyle(TableStyle):
    def __init__(self, sheet_name: str = "Sheet1"):
        super().__init__()
        self.terminal_style = False
        self.string_output = False  # Binary format
        self.sheet_name = sheet_name

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
        """Write table to ODS file format."""
        try:
            from odf.opendocument import OpenDocumentSpreadsheet  # type: ignore
            from odf import table, text  # type: ignore
        except Exception as e:  # pragma: no cover - only hit without optional dep
            raise ImportError(
                "odfpy is required for OdsStyle; install group 'ods'"
            ) from e

        doc = OpenDocumentSpreadsheet()

        # Define paragraph styles
        from odf.style import Style, TextProperties, ParagraphProperties  # type: ignore

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

        sheet = table.Table(name=self.sheet_name)

        # Write header row
        if header_row:
            tr = table.TableRow()
            for i, h in enumerate(header_row):
                tc = table.TableCell()
                # Determine style based on header_defs alignment
                style_to_use = header_bold_center
                if header_defs and i < len(header_defs):
                    hdr_def = header_defs[i]
                    if ">" in hdr_def.align:
                        style_to_use = header_bold_right
                    elif "<" in hdr_def.align:
                        style_to_use = header_bold_left
                    # Center alignment uses header_bold_center (already bold)
                p = text.P(stylename=style_to_use, text=str(h))
                tc.addElement(p)
                tr.addElement(tc)
            sheet.addElement(tr)

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
                # Prepare value (respect preprocess / postprocess similar to XLSX)
                v2 = col_def.preprocess(val, row, i)
                is_text_mode = (
                    col_def.prefix
                    or col_def.suffix
                    or col_def.postprocessor is not None
                )
                tc_kwargs: dict[str, str] = {}
                cell_text: str
                if v2 is None:
                    cell_text = (
                        col_def.prefix + (col_def.none_text or "") + col_def.suffix
                    )
                # Check boolean FIRST since bool is subclass of int in Python
                elif (not is_text_mode) and isinstance(v2, bool):
                    tc_kwargs = {
                        "valuetype": "boolean",
                        "value": "true" if v2 else "false",
                    }
                    cell_text = "true" if v2 else "false"
                elif (not is_text_mode) and isinstance(v2, (date, datetime)):
                    # ODF date value
                    iso_val = v2.isoformat()
                    tc_kwargs = {"valuetype": "date", "datevalue": iso_val}
                    cell_text = iso_val
                elif (not is_text_mode) and isinstance(v2, (int, float)):
                    # Check if format spec indicates percentage
                    is_percent = (
                        col_def.format_spec
                        and hasattr(col_def.format_spec, "type")
                        and col_def.format_spec.type == "%"
                    )
                    if is_percent:
                        tc_kwargs = {"valuetype": "percentage", "value": str(v2)}
                        cell_text = str(v2)
                    else:
                        tc_kwargs = {"valuetype": "float", "value": str(v2)}
                        cell_text = str(v2)
                else:
                    try:
                        if col_def.format_spec:
                            fmt = f"{{:{col_def.format_spec}}}"
                            cell_text = fmt.format(v2)
                        else:
                            cell_text = str(v2)
                    except Exception:
                        cell_text = str(v2)
                    cell_text = col_def.prefix + cell_text + col_def.suffix
                # Apply postprocessor if any
                if col_def.postprocessor is not None:
                    cell_text = col_def.postprocessor(val, cell_text, row, i)
                tc = table.TableCell(**tc_kwargs)
                # Map ColDef alignment to paragraph style
                if ">" in col_def.align:
                    style = right_style
                elif "^" in col_def.align:
                    style = center_style
                else:
                    style = left_style
                p = text.P(stylename=style, text=cell_text)
                tc.addElement(p)
                tr.addElement(tc)
            sheet.addElement(tr)

        doc.spreadsheet.addElement(sheet)

        doc.save(file)
