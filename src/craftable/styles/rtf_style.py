"""RTF style: writes an RTF file containing a table.

No external dependency required (group: rtf optional/empty).
"""

from typing import Any, IO, TYPE_CHECKING
from pathlib import Path

from .table_style import TableStyle

if TYPE_CHECKING:  # avoid circular import at runtime
    from ..craftable import ColDefList


class RtfStyle(TableStyle):
    def __init__(self):
        super().__init__()
        self.terminal_style = False
        self.string_output = False  # RTF is not human-readable string output

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
        """Write table to RTF file format."""
        # Render an actual RTF table using \trowd/\cellx/\cell/\row.
        # Widths are approximated from column character widths.

        def char_width_to_twips(chars: int) -> int:
            # Approximate: ~240 twips per character (roughly 12pt mono width)
            return max(1, int(chars) * 240)

        # Compute cell boundaries (\cellx) as cumulative widths
        cellx_positions: list[int] = []
        x = 0
        for cd in col_defs:
            # Add minimal padding around text visually
            col_twips = char_width_to_twips(max(cd.width, 1) + 2)
            x += col_twips
            cellx_positions.append(x)

        parts: list[str] = []
        parts.append("{\\rtf1\\ansi")

        def row_to_rtf(
            cells: list[str], bold: bool = False, use_header_defs: bool = False
        ) -> None:
            parts.append("\\trowd\\trgaph108")
            # Define cell boundaries
            for cx in cellx_positions:
                parts.append(f"\\cellx{cx}")
            # Cell contents
            for idx, text in enumerate(cells):
                # Alignment mapping using paragraph alignment
                # For headers, use header_defs alignment if available
                if use_header_defs and header_defs and idx < len(header_defs):
                    hdr_def = header_defs[idx]
                    if ">" in hdr_def.align:
                        align = "\\qr"
                    elif "^" in hdr_def.align:
                        align = "\\qc"
                    else:
                        align = "\\ql"
                else:
                    cd = col_defs[idx]
                    if ">" in cd.align:
                        align = "\\qr"
                    elif "^" in cd.align:
                        align = "\\qc"
                    else:
                        align = "\\ql"
                content = self._escape(text)
                # Wrap in \b ... \b0 for header bold
                if bold:
                    parts.append(f"{{\\intbl {align} \\b {content} \\b0 \\cell}}")
                else:
                    parts.append(f"{{\\intbl {align} {content} \\cell}}")
            parts.append("\\row")

        # Write header row
        if header_row:
            row_to_rtf([str(h) for h in header_row], bold=True, use_header_defs=True)

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
            formatted = [
                _format_for_export(cd, v, row, i)
                for i, (v, cd) in enumerate(zip(row, col_defs))
            ]
            row_to_rtf(formatted, bold=False)

        parts.append("}")
        rtf_content = "".join(parts)

        # Write to file
        if isinstance(file, (str, Path)):
            with open(file, "w", encoding="utf-8") as f:
                f.write(rtf_content)
        else:
            # Assume file-like object
            file.write(rtf_content)  # type: ignore[arg-type]

    def _escape(self, text: str) -> str:
        # Escape backslashes and braces for RTF
        return text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
