from typing import (
    Any,
    Iterator,
    Iterable,
    SupportsIndex,
    overload,
    TypeAlias,
    Callable,
)
from os import get_terminal_size
from dataclasses import dataclass
import re
from textwrap import wrap
from pathlib import Path
from typing import IO

from .styles.table_style import TableStyle
from .styles.no_border_screen_style import NoBorderScreenStyle


class InvalidTableError(ValueError): ...


class InvalidColDefError(ValueError): ...


# fn(value, row, col_idx)
PreprocessorCallback: TypeAlias = Callable[[Any, list[Any], int], Any]
PreprocessorCallbackList: TypeAlias = Iterable[PreprocessorCallback | None]

# fn(original, text, row, col_idx)
PostprocessorCallback: TypeAlias = Callable[[Any, str, list[Any], int], str]
PostprocessorCallbackList: TypeAlias = Iterable[PostprocessorCallback | None]

###############################################################################
# get_term_width
###############################################################################

MAX_REASONABLE_WIDTH = 120


def get_term_width(max_term_width: int = MAX_REASONABLE_WIDTH):
    try:
        term_width = get_terminal_size().columns
    except:  # noqa: E722
        return max_term_width
    if max_term_width == 0:
        max_term_width = 9999
    return min(max_term_width, term_width)


###############################################################################
# FormatSpec
###############################################################################

_FORMAT_SPEC_PATTERN = re.compile(
    r"((?P<prefix_align>[<>])?(?P<prefix>[^<>]+)?\()?"
    r"((?P<fill>.)?(?P<align>[<>=^]))?"
    r"(?P<sign>[+\- ])?"
    r"(?P<alternate>[z#])?"
    r"(?P<zero>0)?"
    r"(?P<width>\d+)?"
    r"(?P<grouping_option>[_,])?"
    r"(?P<precision>\.\d+)?"
    r"(?P<type>[bcdeEfFgGnosxX%])?"
    r"(?P<table_config>[ATS]+)?"
    r"(\)(?P<suffix_align>[<>])?(?P<suffix>.+)?)?"
)


@dataclass
class FormatSpec:
    fill: str = ""
    align: str = ""
    sign: str = ""
    alternate: str = ""
    zero: str = ""
    width: int = 0
    grouping: str = ""
    precision: str = ""
    type: str = ""

    def __str__(self) -> str:
        return (
            f"{self.fill}{self.align}{self.sign}{self.alternate}"
            f"{self.zero}{self.width if self.width > 0 else ''}{self.grouping}"
            f"{self.precision}{self.type}"
        )


###############################################################################
# ColDef
###############################################################################


@dataclass
class ColDef:
    width: int = 0
    align: str = "<"
    prefix: str = ""
    prefix_align: str = ">"
    suffix: str = ""
    suffix_align: str = "<"
    auto_fill: bool = False
    truncate: bool = False
    strict: bool = False
    format_spec: FormatSpec | None = None
    preprocessor: PreprocessorCallback | None = None
    postprocessor: PostprocessorCallback | None = None
    none_text: str = ""

    def set_width(self, value: int) -> None:
        self.width = value
        if self.format_spec:
            if self.prefix_align == "<" or self.suffix_align == ">":
                adj_width = value - len(self.prefix) - len(self.suffix)
                if adj_width > 0:
                    self.format_spec.width = adj_width

    def format(self, value: Any) -> str:
        # "Inner" format
        if self.format_spec:
            format_string = f"{{:{self.format_spec}}}"
        else:
            format_string = "{}"

        # convert None to user-configurable text
        val = value if value is not None else self.none_text
        try:
            text = format_string.format(val)
        except:  # noqa: E722
            # On failure, fall back to string unless strict mode
            if self.strict:
                raise
            else:
                text = str(val)
        # add prefix and suffix if there is a value
        if value is not None:
            text = f"{self.prefix}{text}{self.suffix}"

        # "Outer" format
        return self.format_text(text)

    # ------------------------------------------------------------------
    # Processor helpers
    # ------------------------------------------------------------------
    def preprocess(self, value: Any, row: list[Any], col_idx: int) -> Any:
        """Apply the column's preprocessor callback if present.

        Swallows exceptions and returns the original value on failure.
        """
        if self.preprocessor and callable(self.preprocessor):
            try:
                return self.preprocessor(value, row, col_idx)
            except Exception:
                return value
        return value

    def postprocess(
        self, original_value: Any, text: str, row: list[Any], col_idx: int
    ) -> str:
        """Apply the column's postprocessor callback if present.

        Runs after width sizing, wrapping and alignment. Should not
        alter the displayed width. Swallows exceptions and returns the
        original text on failure.
        """
        if self.postprocessor and callable(self.postprocessor):
            try:
                return self.postprocessor(original_value, text, row, col_idx)
            except Exception:
                return text
        return text

    def format_text(self, text: str) -> str:
        if len(text) > self.width and self.truncate:
            text = text[: self.width - 1] + "…"

        if self.align == "^":
            text = text.center(self.width)
        elif self.align == ">":
            text = text.rjust(self.width)
        else:
            text = text.ljust(self.width)

        return text

    @staticmethod
    def parse(text) -> "ColDef":
        match = _FORMAT_SPEC_PATTERN.match(text)
        if not match:
            raise InvalidColDefError(f"Invalid format specifier for column: {text}")
        spec = match.groupdict()
        prefix = spec["prefix"] if spec["prefix"] else ""
        prefix_align = spec["prefix_align"] if spec["prefix_align"] else ""
        fill = spec["fill"] if spec["fill"] else ""
        align = spec["align"]
        if not align or align == "=":
            align = ""
            fill = ""
        sign = spec["sign"] if spec["sign"] else ""
        alternate = spec["alternate"] if spec["alternate"] else ""
        zero = spec["zero"] if spec["zero"] else ""
        width = int(spec["width"]) if spec["width"] else 0
        grouping = spec["grouping_option"] if spec["grouping_option"] else ""
        precision = spec["precision"] if spec["precision"] else ""
        type_ = spec["type"] if spec["type"] else ""
        suffix_align = spec["suffix_align"] if spec["suffix_align"] else ""
        suffix = spec["suffix"] if spec["suffix"] else ""

        auto_size = False
        truncate = False

        table_config = spec["table_config"]
        if table_config:
            if "A" in table_config:
                auto_size = True
            if "T" in table_config:
                truncate = True

        format_spec = FormatSpec(
            fill=fill,
            align=align,
            sign=sign,
            alternate=alternate,
            zero=zero,
            grouping=grouping,
            precision=precision,
            type=type_,
        )

        if width and (prefix_align == "<" or suffix_align == ">"):
            adj_width = width - len(prefix) - len(suffix)
            if adj_width > 0:
                format_spec.width = adj_width
        else:
            format_spec.align = ""

        # if format spec is just a number, then just toss it to avoid
        # inadvertent right-aligned numbers.
        try:
            _ = int(str(format_spec))
            format_spec = None
        except ValueError:
            pass

        return ColDef(
            prefix=prefix,
            prefix_align=prefix_align,
            suffix=suffix,
            suffix_align=suffix_align,
            width=width,
            align=align,
            auto_fill=auto_size,
            truncate=truncate,
            format_spec=format_spec,
        )


###############################################################################
# ColDefList
###############################################################################


class ColDefList(list[ColDef]):
    """
    A list of ColDef objects.
    """

    def __init__(self, iterable: Iterable = []):
        super().__init__()
        for val in iterable:
            self.append(val)
        self._adjusted = False
        self._cached_list = None

    @overload
    def __setitem__(self, key: SupportsIndex, value: str | ColDef, /) -> None: ...

    @overload
    def __setitem__(self, key: slice, value: Iterable[str | ColDef], /) -> None: ...

    def __setitem__(self, key, value):
        if isinstance(key, SupportsIndex):
            if isinstance(value, str):
                super().__setitem__(key, ColDef.parse(value))
            elif isinstance(value, ColDef):
                super().__setitem__(key, value)
            else:
                raise ValueError("Column definition contain an invalid value")
        elif isinstance(key, slice) and isinstance(value, Iterable):
            values = ColDefList(value)
            super().__setitem__(key, values)
        else:
            raise ValueError("Column definitions contain an invalid value")

    @overload
    def __getitem__(self, i: SupportsIndex) -> ColDef: ...

    @overload
    def __getitem__(self, i: slice) -> "ColDefList": ...

    def __getitem__(self, i):
        result = super().__getitem__(i)
        if isinstance(i, slice):
            return ColDefList(result)
        else:
            return result

    def __iter__(self) -> Iterator[ColDef]:
        return super().__iter__()

    def append(self, object):
        if isinstance(object, str):
            super().append(ColDef.parse(object))
        elif isinstance(object, ColDef):
            super().append(object)
        else:
            raise ValueError("Column definitions contain an invalid value")

    def as_list(self, clear_cache: bool = False) -> list[ColDef]:
        """
        Convert to a native list and cache it for performance.
        Returns cached list to avoid repeated __getitem__ overhead.
        """
        if self._cached_list is None or clear_cache:
            self._cached_list = list(self)
        return self._cached_list

    @staticmethod
    def parse(specs: Iterable[str]) -> "ColDefList":
        """Parse a list of format spec strings into a ColDefList.

        This is a convenience for building per-column definitions from
        plain strings. Each spec is parsed via ColDef.parse().

        Example:
            specs = ["A", ">8.2f", "^10"]
            col_defs = ColDefList.parse(specs)

        Args:
            specs: Iterable of column definition strings.

        Returns:
            ColDefList: A list-like collection of ColDef objects.
        """
        col_defs = ColDefList()
        for s in specs:
            col_defs.append(ColDef.parse(s))
        return col_defs

    def adjust_to_table(
        self,
        table_data: list[list[Any]],
        table_width: int,
        style: TableStyle,
        has_header: bool = False,
        clear_cache: bool = False,
    ) -> None:
        # Skip if already adjusted
        if self._adjusted and not clear_cache:
            return
        self._adjusted = True

        # ADD MISSING COL DEFS
        max_cols = max([len(row) for row in table_data])
        diff = max_cols - len(self)
        if diff:
            for _ in range(diff):
                self.append(ColDef())

        # ADJUST WIDTHS OF FIELDS TO MATCH REALITY
        for col_idx in range(max_cols):
            col_def = self[col_idx]
            if not col_def.width:
                max_width = 0
                is_header = has_header
                for row in table_data:
                    if is_header:
                        is_header = False
                        cell = str(row[col_idx])
                    else:
                        value = col_def.preprocess(row[col_idx], row, col_idx)
                        cell = col_def.format(value)
                    max_width = max(max_width, len(cell))

                col_def.set_width(max_width)

            if col_def.width < style.min_width:
                col_def.set_width(style.min_width)

        # ADJUST AUTO-FILL COLS TO FILL REMAINING SPACE AVAILABLE IN TOTAL TABLE_WIDTH
        if not table_width:
            return

        padding_len = style.cell_padding * 2 * len(self)
        border_len = len(str(style.values_left)) + len(str(style.values_right))
        delims_len = len(str(style.values_delimiter)) * (len(self) - 1)
        non_text_len = padding_len + border_len + delims_len
        total_len = non_text_len + sum([c.width for c in self])

        fill_cols = [col_idx for col_idx in range(len(self)) if self[col_idx].auto_fill]
        if not fill_cols:
            if total_len <= table_width:
                return
            else:
                largest_col = self[0]
                largest_col_idx = 0
                for col_idx in range(1, len(self)):
                    col_def = self[col_idx]
                    if col_def.width > largest_col.width:
                        largest_col = col_def
                        largest_col_idx = col_idx
                largest_col.auto_fill = True
                fill_cols.append(largest_col_idx)

        fixed_len = sum([c.width for c in self if not c.auto_fill])

        remaining_width = table_width - fixed_len - non_text_len
        fill_width = remaining_width // len(fill_cols)

        if fill_width < style.min_width:
            raise ValueError(
                "Unable to expand columns to fit table width because existing columns are too wide"
            )

        remainder = remaining_width % len(fill_cols)
        for col_idx in fill_cols:
            new_width = fill_width
            if remainder:
                new_width += 1
                remainder -= 1
            self[col_idx].set_width(new_width)

    @staticmethod
    def assert_valid_table(table: Any) -> None:
        if not isinstance(table, list):
            raise ValueError("Table data must be a list of rows")
        for row in table:
            if not isinstance(row, list):
                raise ValueError("Each row in a table must be a list of cells")

    @staticmethod
    def for_table(table: list[list[Any]]) -> "ColDefList":
        ColDefList.assert_valid_table(table)
        max_cols = max([len(row) for row in table])
        col_defs = ColDefList([ColDef() for _ in range(max_cols)])
        return col_defs


###############################################################################
# col_def helpers
###############################################################################


def _get_adjusted_col_defs(
    all_rows: list[list[Any]],
    style: TableStyle,
    col_defs: Iterable[str] | Iterable[ColDef] | ColDefList | None = None,
    table_width: int = 0,
    preprocessors: PreprocessorCallbackList | None = None,
    postprocessors: PostprocessorCallbackList | None = None,
    none_text: str = "",
) -> ColDefList:
    # Normalize col_defs
    if not col_defs:
        _col_defs = ColDefList.for_table(all_rows)
    elif isinstance(col_defs, ColDefList):
        _col_defs = col_defs
    else:
        _col_defs = ColDefList(col_defs)

    # Attach callbacks before width adjustment so preprocessors influence sizing
    if preprocessors:
        _pre_list = list(preprocessors)
        for i, col_def in enumerate(_col_defs):
            if i < len(_pre_list) and _pre_list[i] is not None:
                col_def.preprocessor = _pre_list[i]
    if postprocessors:
        _post_list = list(postprocessors)
        for i, col_def in enumerate(_col_defs):
            if i < len(_post_list) and _post_list[i] is not None:
                col_def.postprocessor = _post_list[i]

    # Apply None display setting across columns
    for col_def in _col_defs:
        if not col_def.none_text:
            col_def.none_text = none_text

    # Adjust column definitions to match table data
    _col_defs.adjust_to_table(all_rows, table_width, style, has_header=True)

    return _col_defs


def _generate_header_defs(
    header_row: Iterable[Any] | None,
    header_defs: Iterable[str] | Iterable[ColDef] | ColDefList | None,
    col_defs: ColDefList,
) -> ColDefList | None:
    # generate viable header definitions
    _header_defs = None
    if header_row:
        # generate default header defs if not supplied
        _header_defs = ColDefList()
        for col_def in col_defs:
            _header_defs.append(ColDef(width=col_def.width, align="^"))

        # if the defs are supplied, we only support alignment so just extract that
        if header_defs:
            _header_defs = ColDefList(header_defs)
            for col_idx in range(len(col_defs)):
                if col_idx < len(_header_defs):
                    header_def = _header_defs[col_idx]
                    if header_def.align:
                        _header_defs[col_idx].align = header_def.align

    return _header_defs


###############################################################################
# get_table_row
###############################################################################


def _get_table_row(
    values: list[Any],
    col_defs: ColDefList,
    style: TableStyle = NoBorderScreenStyle(),
    table_width: int = 0,
    lazy_end: bool = False,
    is_header: bool = False,
) -> str:
    if not table_width and style.terminal_style:
        table_width = get_term_width()

    # Cache _col_defs to a native list. Even though ColDefList is a subclass of
    # list, it has method call overhead on each access. Using the "bare" list is
    # slightly faster, which adds up for large tables.
    _cached_col_defs = col_defs.as_list()

    col_count = len(values)

    formatted_values = []
    for col_idx in range(col_count):
        col_def = _cached_col_defs[col_idx]
        col_val = col_def.preprocess(values[col_idx], values, col_idx)
        text = col_def.format(col_val)
        formatted_values.append(text)

    all_col_lines = []
    for col_idx in range(col_count):
        col_lines = []
        col_def = _cached_col_defs[col_idx]
        text = formatted_values[col_idx]
        split = text.splitlines()
        if not split:
            split = [""]
        for line in split:
            # Performance optimization: Skip textwrap.wrap() for cells that fit
            # This provides ~30% performance improvement since most cells don't need wrapping
            # See profiling/OPTIMIZATION_RESULTS.md for details
            if len(line) > col_def.width:
                wrapped = wrap(line, width=col_def.width)
                if wrapped:
                    for wrapped_line in wrapped:
                        col_lines.append(wrapped_line)
                else:
                    col_lines.append(line)
            else:
                # Line fits within width, no wrapping needed
                col_lines.append(line)
        # Append the collected lines for this column once
        all_col_lines.append(col_lines)

    max_rows = max([len(col) for col in all_col_lines])

    if max_rows == 1:
        # Single line per column; build a single row of cells
        row_cells = []
        for col_idx, cell in enumerate(formatted_values):
            col_def = _cached_col_defs[col_idx]
            cell = col_def.postprocess(values[col_idx], cell, values, col_idx)
            row_cells.append(cell)
        wrapped_rows = [row_cells]
    else:
        wrapped_rows = []
        for row_idx in range(max_rows):
            row = []
            for col_idx in range(col_count):
                col = all_col_lines[col_idx]
                col_def = _cached_col_defs[col_idx]
                if row_idx < len(col):
                    text = col[row_idx]
                else:
                    text = ""
                text = col_def.format_text(text)
                text = col_def.postprocess(values[col_idx], text, values, col_idx)
                row.append(text)
            wrapped_rows.append(row)

    padding = " " * style.cell_padding
    if is_header:
        delim = padding + str(style.header_delimiter) + padding
        left = str(style.header_left) + padding
        right = "" if lazy_end else padding + str(style.header_right)
    else:
        delim = padding + str(style.values_delimiter) + padding
        left = str(style.values_left) + padding
        right = "" if lazy_end else padding + str(style.values_right)

    final_rows = []
    for row in wrapped_rows:
        row_text = left + delim.join(row) + right
        if lazy_end:
            row_text = row_text.rstrip()
        final_rows.append(row_text)

    return "\n".join(final_rows)


def get_table_row(
    values: list[Any],
    style: TableStyle = NoBorderScreenStyle(),
    col_defs: list[str] | list[ColDef] | ColDefList | None = None,
    table_width: int = 0,
    lazy_end: bool = True,
    preprocessors: PreprocessorCallbackList | None = None,
    postprocessors: PostprocessorCallbackList | None = None,
    none_text: str = "",
) -> str:
    """
    Generate a string for a single table row.

    Parameters:
        values:
            A list of values.
        style:
            (optional) A TableStyle object defining the table's appearance.
            Defaults to NoBorderScreenStyle.
        col_defs:
            (optional) Column definitions to control width, alignment, etc. If
            not provided, generates default left-aligned columns based on values.
        table_width:
            (optional) Desired total width of the table. If 0, uses terminal
            width when style.terminal_style is True. Defaults to 0.
        lazy_end:
            (optional) If True, omits the right border of the table. Defaults
            to True.
        preprocessors:
            (optional) List of per-column callbacks applied before formatting
            and sizing. Each entry should be a callable of the form
            ``fn(value, row, col_idx) -> value``. Defaults to None.
        postprocessors:
            (optional) List of per-column callbacks applied after formatting,
            sizing, and wrapping. Each entry should be a callable of the form
            ``fn(original_value, text, row, col_idx) -> str``. Defaults to None.
        none_text:
            (optional) Text to display for None values. Defaults to empty
            string.

    Behavior:
        - If col_defs is not provided, generates default left-aligned column
          definitions based on the values.
        - Applies preprocessors to transform values before formatting.
        - Formats each value according to its column definition.
        - Applies postprocessors to transform formatted text.
        - Renders the row using the specified table style.

    Returns:
        A formatted string representing a single table row, including borders
        and cell padding as defined by the style.
    """

    _col_defs = _get_adjusted_col_defs(
        all_rows=[values],
        style=style,
        col_defs=col_defs,
        table_width=table_width,
        preprocessors=preprocessors,
        postprocessors=postprocessors,
        none_text=none_text,
    )
    return _get_table_row(
        values=values,
        style=style,
        col_defs=_col_defs,
        table_width=table_width,
        lazy_end=lazy_end,
        is_header=False,
    )


###############################################################################
# get_table_header
###############################################################################


def get_table_header(
    header_cols: list[str],
    style: TableStyle = NoBorderScreenStyle(),
    header_defs: Iterable[str] | Iterable[ColDef] | ColDefList | None = None,
    col_defs: Iterable[str] | Iterable[ColDef] | ColDefList | None = None,
    table_width: int = 0,
    lazy_end: bool = True,
) -> str:
    """
    Generate a string for the header of a table.

    Parameters:
        header_cols:
            A list of header column names.
        style:
            (optional) A TableStyle object defining the table's appearance.
            Defaults to NoBorderScreenStyle.
        header_defs:
            (optional) Column definitions for the header row. If not provided,
            defaults to column definitions generated from header_cols.
        col_defs:
            (optional) Column definitions for the rest of the table rows. Only
            required for styles that have an alignment character (e.g.,
            Markdown). If not provided, uses the same as header_defs.
        table_width:
            (optional) Desired total width of the table. Will be automatically
            calculated if not provided. Defaults to 0.
        lazy_end:
            (optional) If True, omits the right border of the table. Defaults
            to True.

    Behavior:
        - If header_defs is not provided, generates default column definitions from header_cols.
        - If col_defs is not provided, uses a copy of header_defs.
        - Adjusts column definitions to fit the specified or calculated table width.
        - Renders the top border if the style includes one.
        - Renders the header row with the specified header definitions.
        - Renders the bottom border (separator between header and data rows).
        - For styles with alignment characters (e.g., Markdown), uses col_defs to determine
          column alignment indicators in the separator line.

    Returns:
        A formatted string representing the table header, including top border,
        header row, and header separator line as defined by the style.
    """
    if not table_width and style.terminal_style:
        table_width = get_term_width()

    _header_defs = _get_adjusted_col_defs(
        all_rows=[header_cols],
        style=style,
        col_defs=header_defs,
        table_width=table_width,
    )

    if not col_defs:
        _col_defs = _header_defs.copy()
    elif isinstance(col_defs, ColDefList):
        _col_defs = col_defs
    else:
        _col_defs = ColDefList(col_defs)

    lazy_end = lazy_end and style.allow_lazy_header
    padding_width = 2 * style.cell_padding

    lines = []
    if style.top_border:
        line = str(style.header_top_line)
        delim = str(style.header_top_delimiter)
        left = str(style.header_top_left)
        right = line if lazy_end else str(style.header_top_right)
        border_lines = [line * (col.width + padding_width) for col in _col_defs]
        border = delim.join(border_lines)
        border = left + border + right
        lines.append(border)

    headers = _get_table_row(
        values=header_cols,
        style=style,
        col_defs=_header_defs,
        table_width=table_width,
        lazy_end=lazy_end,
        is_header=True,
    )
    lines.append(headers)

    line = str(style.header_bottom_line)
    delim = str(style.header_bottom_delimiter)
    left = str(style.header_bottom_left)
    right = line if lazy_end else str(style.header_bottom_right)
    border_lines = []
    for col_idx in range(len(header_cols)):
        header_def = _header_defs[col_idx]
        if not style.align_char:
            h_line = line * (header_def.width + padding_width)
        else:
            col_def = None
            if col_idx < len(_col_defs):
                col_def = _col_defs[col_idx]
            h_line = line * header_def.width
            if col_def and col_def.align == "^":
                h_line = str(style.align_char) + h_line + str(style.align_char)
            elif col_def and col_def.align == ">":
                h_line = " " + h_line + str(style.align_char)
            else:
                h_line = " " + h_line + " "
        border_lines.append(h_line)
    border = delim.join(border_lines)
    border = left + border + right
    lines.append(border)

    return "\n".join(lines)


###############################################################################
# get_table
###############################################################################


def get_table(
    value_rows: Iterable[Iterable[Any]],
    header_row: Iterable[Any] | None = None,
    style: TableStyle = NoBorderScreenStyle(),
    col_defs: Iterable[str] | Iterable[ColDef] | ColDefList | None = None,
    header_defs: Iterable[str] | Iterable[ColDef] | ColDefList | None = None,
    table_width: int = 0,
    lazy_end: bool = False,
    separate_rows: bool = False,
    preprocessors: PreprocessorCallbackList | None = None,
    postprocessors: PostprocessorCallbackList | None = None,
    none_text: str = "",
) -> str:
    """
    Primary function called to generate a table string.

    Parameters:
        value_rows:
            A collection of rows, where each row is a collection of values. This
            is required. However, a default message of "No data to display" will
            be shown if the collection is empty or None.
        header_row:
            (optional) A collection of header column names. Defaults to None.
        style:
            (optional) A TableStyle object defining the table's appearance.
            Defaults to NoBorderScreenStyle.
        col_defs:
            (optional) A collection of column definitions to control width,
            alignment, etc. for data rows. Defaults to left aligned, auto-sized
            columns.
        header_defs:
            (optional) A collection of column definitions for the header row. If
            not provided, defaults to center-aligned columns with the same
            widths as col_defs.
        table_width:
            (optional) Desired total width of the table. Will be automatically
            calculated if not specified. Defaults to 0.
        lazy_end:
            (optional) If True, omits the right border of the table. Defaults to
            False.
        separate_rows:
            (optional) If True, adds a separator line between each row. Defaults
            to False.
        preprocessors:
            (optional) List of per-column callbacks applied before formatting
            and sizing. Each entry should be a callable of the form
            ``fn(value, row, col_idx) -> value``. Defaults to None.
        postprocessors:
            (optional) List of per-column callbacks applied after formatting,
            sizing, and wrapping. Each entry should be a callable of the form
            ``fn(original_value, text, row, col_idx) -> str``. Defaults to None.
        none_text:
            (optional) Text to display for None values. Defaults to empty
            string.

    Behavior:
        - Validates that the style supports string output (raises ValueError if
          not).
        - If value_rows is empty, returns a table with "No data to display"
          message.
        - Converts value_rows to a list of lists for consistent processing.
        - Calculates column widths based on content and table_width constraints.
        - Generates column definitions (col_defs) from content if not provided.
        - Generates header definitions (header_defs) from col_defs if not
          provided, defaulting to center-aligned headers.
        - Renders the table header if header_row is provided or
          style.force_header is True.
        - Renders each data row, optionally adding separator lines between rows
          if separate_rows is True.
        - Renders the bottom border if the style includes one.
        - Applies preprocessors before formatting and postprocessors after
          formatting.

    Returns:
        A formatted string representing the complete table, including all
        borders, header, data rows, and separators as defined by the style.
    """
    # Validate that style supports string output for get_table
    if not getattr(style, "string_output", True):
        raise ValueError(
            f"{style.__class__.__name__} does not support string output. "
            "Use export_table() instead."
        )

    if not value_rows:
        return get_table(
            [["No data to display"]],
            style=style,
            table_width=table_width,
            lazy_end=lazy_end,
        )

    if not table_width and style.terminal_style:
        table_width = get_term_width()

    padding_width = 2 * style.cell_padding

    # convert / copy the rows to a list of lists. Slight overhead but it helps
    # with consistency and prevents accidentally modifying the caller's data.
    _value_rows: list[list[Any]] = [list(row) for row in value_rows]
    _header_row: list[Any] | None = None
    if header_row:
        _header_row = [str(col) for col in header_row]

    # createa a second (shallow) copy to help with calculating column widths
    all_rows = _value_rows.copy()
    if _header_row:
        all_rows.insert(0, _header_row)

    max_cols = max(len(row) for row in all_rows)

    _col_defs = _get_adjusted_col_defs(
        all_rows=all_rows,
        style=style,
        col_defs=col_defs,
        table_width=table_width,
        preprocessors=preprocessors,
        postprocessors=postprocessors,
        none_text=none_text,
    )

    if not header_row and style.force_header:
        header_row = [""] * max_cols

    _header_defs = _generate_header_defs(
        header_row=_header_row,
        header_defs=header_defs,
        col_defs=_col_defs,
    )

    # Delegate to a custom renderer when the style provides one (e.g., HTML/LaTeX)
    renderer = getattr(style, "render_table", None)
    if callable(renderer):
        return str(renderer(_value_rows, _header_row, _col_defs, _header_defs))

    # Generate header and rows
    output_rows = []
    if _header_row:
        if len(_header_row) < max_cols:
            # pad header row
            diff = max_cols - len(_header_row)
            _header_row.extend([""] * diff)
        row = get_table_header(
            header_cols=_header_row,
            style=style,
            header_defs=_header_defs,
            col_defs=_col_defs,
            table_width=table_width,
            lazy_end=lazy_end,
        )
        output_rows.append(row)
    else:
        if style.top_border:
            line = str(style.no_header_top_line)
            delim = str(style.no_header_top_delimiter)
            left = str(style.no_header_top_left)
            right = line if lazy_end else str(style.no_header_top_right)
            border_lines = [line * (col.width + padding_width) for col in _col_defs]
            border = delim.join(border_lines)
            border = left + border + right
            output_rows.append(border)

    # Add Value Rows
    rowcount = 0
    for values in _value_rows:
        rowcount += 1
        lastrow = rowcount == len(_value_rows)
        if len(values) < max_cols:
            # pad row
            diff = max_cols - len(values)
            values.extend([""] * diff)
        row = _get_table_row(
            values=values,
            style=style,
            col_defs=_col_defs,
            table_width=table_width,
            lazy_end=lazy_end,
        )
        output_rows.append(row)

        # Optionally add Separators Between Rows
        if not lastrow and separate_rows and style.row_separator_line:
            line = str(style.row_separator_line)
            left = str(style.row_separator_left)
            right = line if lazy_end else str(style.row_separator_right)
            delim = str(style.row_separator_delimiter)
            sep_lines = [line * (col.width + padding_width) for col in _col_defs]
            separator = delim.join(sep_lines)
            separator = left + separator + right
            output_rows.append(separator)

    # Add Bottom Border
    if style.bottom_border:
        line = str(style.values_bottom_line)
        delim = str(style.values_bottom_delimiter)
        left = str(style.values_bottom_left)
        right = line if lazy_end else str(style.values_bottom_right)
        border_lines = [line * (col.width + padding_width) for col in _col_defs]
        border = delim.join(border_lines)
        border = left + border + right
        output_rows.append(border)

    return "\n".join(output_rows)


###############################################################################
# export_table
###############################################################################


def export_table(
    value_rows: Iterable[Iterable[Any]],
    header_row: Iterable[Any] | None = None,
    style: TableStyle = NoBorderScreenStyle(),
    col_defs: Iterable[str] | Iterable[ColDef] | ColDefList | None = None,
    header_defs: Iterable[str] | Iterable[ColDef] | ColDefList | None = None,
    preprocessors: PreprocessorCallbackList | None = None,
    postprocessors: PostprocessorCallbackList | None = None,
    none_text: str = "",
    file: str | Path | IO[str] | IO[bytes] | None = None,
    encoding: str = "utf-8",
) -> str | Path | None:
    """
    Render the table and optionally write it to a file.

    Parameters:
        value_rows:
            A collection of rows, where each row is a collection of values.
        header_row:
            (optional) A collection of header column names. Defaults to None.
        style:
            (optional) A TableStyle object defining the table's appearance and
            export format. Defaults to NoBorderScreenStyle.
        col_defs:
            (optional) A collection of column definitions to control width,
            alignment, formatting, etc. for data rows. Defaults to left aligned,
            auto-sized columns.
        header_defs:
            (optional) A collection of column definitions for the header row. If
            not provided, defaults to center-aligned columns with the same
            widths as col_defs. Used to control header alignment in exported
            files.
        preprocessors:
            (optional) List of per-column callbacks applied before formatting
            and sizing. Each entry should be a callable of the form
            ``fn(value, row, col_idx) -> value``. Defaults to None.
        postprocessors:
            (optional) List of per-column callbacks applied after formatting,
            sizing, and wrapping. Each entry should be a callable of the form
            ``fn(original_value, text, row, col_idx) -> str``. Defaults to None.
        none_text:
            (optional) Text to display for None values. Defaults to empty
            string.
        file:
            (optional) File path (str or Path) or file-like object (IO) to write
            the output. If None, returns the rendered content as a string.
            Defaults to None.
        encoding:
            (optional) Character encoding for text output. Only used when
            writing text content to a file path. Defaults to "utf-8".

    Behavior:
        - If the style provides a write_table(..., file) method and a file is given,
          delegate writing to the style and return the provided file path/handle.
        - Else, if the style provides render_table(...), render to a string (or bytes).
          If a file is provided, write it; otherwise return the rendered content.
        - Else, fall back to craftable's text renderer via get_table().

    Returns:
        - If file is provided as a path (str or Path), returns the file path for convenience.
        - If file is a file-like object, returns None after writing.
        - Otherwise, returns the rendered content as a string.
    """

    # Normalize inputs similar to get_table()
    _value_rows: list[list[Any]] = [list(row) for row in value_rows]
    _header_row: list[Any] | None = None
    if header_row:
        _header_row = [str(col) for col in header_row]

    all_rows = _value_rows.copy()
    if _header_row:
        all_rows.insert(0, _header_row)

    _col_defs = _get_adjusted_col_defs(
        all_rows=all_rows,
        style=style,
        col_defs=col_defs,
        preprocessors=preprocessors,
        postprocessors=postprocessors,
        none_text=none_text,
    )

    max_cols = max(len(row) for row in all_rows)

    if not header_row and style.force_header:
        header_row = [""] * max_cols

    _header_defs = _generate_header_defs(
        header_row=_header_row,
        header_defs=header_defs,
        col_defs=_col_defs,
    )

    # Prefer explicit writer when available
    writer = getattr(style, "write_table", None)
    if callable(writer) and file is not None:
        writer(_value_rows, _header_row, _col_defs, _header_defs, file)
        return Path(file) if isinstance(file, (str, Path)) else None

    # Otherwise render content and optionally write
    renderer = getattr(style, "render_table", None)
    if callable(renderer):
        content = renderer(_value_rows, _header_row, _col_defs)
        if file is None:
            return str(content)
        # Decide binary vs text write
        if isinstance(content, (bytes, bytearray)):
            if isinstance(file, (str, Path)):
                with open(file, "wb") as f:
                    f.write(content)
                return Path(file)
            else:
                # Assume binary-capable IO
                file.write(content)  # type: ignore[arg-type]
                return None
        else:
            # Text content
            if isinstance(file, (str, Path)):
                with open(file, "w", encoding=encoding) as f:
                    f.write(str(content))
                return Path(file)
            else:
                # Assume text-capable IO
                file.write(str(content))  # type: ignore[arg-type]
                return None

    # Fallback to core text renderer
    content = get_table(
        value_rows,
        header_row=header_row,
        style=style,
        col_defs=_col_defs,
        header_defs=_header_defs,
        preprocessors=preprocessors,
        postprocessors=postprocessors,
        none_text=none_text,
    )
    if file is None:
        return content
    if isinstance(file, (str, Path)):
        with open(file, "w", encoding=encoding) as f:
            f.write(content)
        return Path(file)
    else:
        file.write(content)  # type: ignore[arg-type]
        return None
