# Usage Guide

This guide shows the basics of how to invoke and use craftable.

## Core Functions

There are two main functions used to generate tables:

- `get_table` — render a complete table (headers, rows, borders)
- `export_table` — save a table to a file

!!! note

    See the [API reference](references/functions.md) for full function signatures
    and details.

`get_table` is the primary entry point. In most cases, there will be no need to
call any other functions. 'get_table' has the following definition:

```python
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
```

## Values

`value_rows` is the only required argument. It is a two-dimensional collection
of data to be displayed. It should a collection of rows, with each row being a
collection of cell values. The structure should resemble this:

```
[
  [<val>, <val>],   # row
  [<val>, <val>],   # row
]
```

The table will be tolerant of jagged data, appending empty cells as needed to
ensure a clean tabular output.

## Headers

The optional `header_row` named argument should contain a single collection of values to be used as headers for the table. If no header_row is specified, then no header will be displayed.

The following demonstrates usage of this parameter:

```python
from craftable import get_table

rows = [["Alice", 30], ["Bob", 25]]
print(get_table(rows, header_row=["Name", "Age"]))
```

Output:

```
  Name │ Age 
───────┼─────
 Alice │ 30  
 Bob   │ 25  
```

!!! note

    If a particular table style requires that a header exist (e.g., Markdown
    tables), then an empty header row will be generated if none is specified.

## Column and Header Definitions

`col_defs` and `header_defs` are collections of strings that define how each
column should be formatted. These strings use Python's format mini-language plus
table-specific flags (see [Formatting guide](formatting.md)). The simplicity and
elegance of this is where craftable shines and the main reason for its creation.

```python
from craftable import get_table

rows = [["Alice", 30], ["Bob", 25]]
col_defs = ["10", ">5"]  # left-align 10 chars, right-align 5 chars
print(get_table(rows, col_defs=col_defs))
```

!!! note

    Column definitions are internally converted to `ColDef` objects for processing, but you should always use string specifications as shown above. See the [API reference](references/classes.md) for implementation details.

Default `col_defs` create auto-sized, left-aligned cells. Default `header_defs`
create auto-sized, center-aligned cells.

## Style and Table Width

- `style` specifies the style class to use to render the table. See below for
  the list of included options.
- `table_width` constrains the entire rendered table width if desired. Note that
  this is the actual total width of the string, including all borders and
  padding.
- `lazy_end=True` omits the rightmost border. This is mostly useful for styles
  that are geared for file (vs. screen/terminal) output (ASCII and Markdown). If
  the data is structured such the width of the value in the last column varies
  significantly (but can be quite large), this can eliminate a lot of wasted
  disk space by right-trimming the end of each line.
- `separate_rows=True` draws a divider line between each data row.
- `none_text=""` specifies the text to display for None values. By default, None
  values are displayed as empty strings.
- `preprocessors` / `postprocessors` (advanced): column-indexed callbacks.
  Preprocessors run before formatting and influence widths; postprocessors run
  after sizing/alignment/wrapping for decorations like colors/styles (should
  not change displayed width).

The following is a more complete, styled example:

```python
from craftable import get_table
from craftable.styles import RoundedBorderScreenStyle

rows = [["Alice", 30], ["Bob", 25], ["Charlie", 35]]
print(get_table(
    rows,
    header_row=["Name", "Age"],
    col_defs=["A","5>"],
    header_defs=["<",">"],
    style=RoundedBorderScreenStyle(),
    table_width=30,
    separate_rows=True,
))
```

Output:

```
╭──────────────────────┬─────╮
│ Name                 │ Age │
├──────────────────────┼─────┤
│ Alice                │  30 │
│◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦│◦◦◦◦◦│
│ Bob                  │  25 │
│◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦│◦◦◦◦◦│
│ Charlie              │  35 │
╰──────────────────────┴─────╯
```

The style classes included with craftable are:

- `NoBorderScreenStyle` — minimal, compact (default)
- `BasicScreenStyle` — classic box drawing
- `RoundedBorderScreenStyle` — rounded corners
- `ASCIIStyle` — classic, 7-bit ASCII drawing
- `MarkdownStyle` — GitHub-flavored Markdown tables

Modifying existing styles or creating custom styles is trivial.

See [Styles](styles.md) for additional visual examples and the [API
reference](references/text_styles.md) for class details.

## Quick Exporting to Files

Use `export_table()` with a document style to write files directly:

```python
from craftable import export_table
from craftable.adapters import from_dicts
from craftable.styles import XlsxStyle

data = [
    {"product": "Widget A", "price": 19.99, "stock": 150},
    {"product": "Widget B", "price": 29.99, "stock": 75},
]

rows, headers = from_dicts(data)
export_table(
    rows,
    header_row=headers,
    style=XlsxStyle(),
    file="report.xlsx",
    none_text="—",
)
```

See more export styles in [Styles](styles.md#document-export-styles).

## Handling None Values

Craftable replaces column values of `None` with configurable text before
applying formatting and prefix/suffix:

- Global per-table: pass `none_text="—"` to `get_table()` or `export_table()`.
- Per column: set `ColDef.none_text` for selective overrides.

Example:

```python
from craftable import get_table, ColDefList

rows = [[None, 12.34], ["Bob", None]]
specs = ["^10", ">8.2f"]
col_defs = ColDefList.parse(specs)
col_defs[0].none_text = "(n/a)"  # only for first column

print(get_table(rows, header_row=["Name", "Value"], col_defs=col_defs, none_text="—"))
```

!!! notes

    - Prefixes and Suffixes in the format string _are not_ applied to None values.
    - Preprocessors and Postprocessors _are_ called for None values.
    - Per-column `none_text` takes precedence over the global parameter.
    - The substituted text participates in width, truncation (T flag), and wrapping
      like any other string.
  
## Preprocessors and Postprocessors

Pre/Post processors provide per‑column hooks for transforming raw values and
decorating already formatted text, with full row context.

Preprocessors run beforfe any sizing or formatting is performed. This can be
useful to conditionally hide certain values or to convert values that are not
specifically supported by format specification mini-language, such as date/time
formatting.

Postprocessors run after all other formatting, alignment, and wrapping has
occurred. This is likely most useful to conditionally add ANSI codes or Rich
formatting codes that would otherwise affect the column size calculations.

Signatures:

```python
# value before formatting
def preprocessor(value, row, col_idx) -> Any: ...

# original raw value & formatted text after width/alignment/wrapping
def postprocessor(original_value, text, row, col_idx) -> str: ...
```

Parameters:

| Name | When | Description |
|------|------|-------------|
| `value` / `original_value` | Input | Raw cell value prior to any formatting or prefix/suffix handling |
| `text` | Post only | The fully formatted, aligned (and possibly wrapped) cell text |
| `row` | Both | The entire list of original values for the current row |
| `col_idx` | Both | Zero‑based column index for the cell |

Behavior:

* Preprocessors run before width calculation, so their returned value affects sizing.
* Postprocessors run after formatting/alignment; their return text must keep the
  same visible width (avoid adding/removing padding characters).
* Exceptions are swallowed (unless the column is strict) and the original
  value/text is used.
* Use `None` in the callback list for columns without a processor.

Example with both:

```python
from craftable import get_table
from datetime import date

def fmt_date(value, row, col_idx):
  if hasattr(value, "strftime"):
    return value.strftime("%Y-%m-%d")
  return value

def color_negative(original, text, row, col_idx):
  try:
    if float(original) < 0:
      return f"\x1b[31m{text}\x1b[0m"  # red
  except Exception:
    pass
  return text

rows = [["Sale", -45.2, date(2025,11,15)], ["Refund", 12.5, date(2025,11,14)]]
print(get_table(
  rows,
  header_row=["Type", "Amount", "Date"],
  col_defs=["<10", ">10.2f", "<12"],
  preprocessors=[None, None, fmt_date],
  postprocessors=[None, color_negative, None],
))
```

See the [Formatting Guide](formatting.md#advanced-preprocessors-and-postprocessors) for deeper discussion and patterns.


## Working with Adapters

The `get_table` function works natively with a two-dimensional collection of
data (i.e., list of lists) and an option list of header values. Hoowever, it
also ships with a robust set of _adapters_ to transform other data structures
into craftable-compatible structures.

Included adapters include:

- Dictionaries (JSON-like): `from_dicts`
- Columnar (mapping of lists): `from_mapping_of_lists`
- Dataclasses: `from_dataclasses`
- Mixed models (Pydantic/attrs/plain): `from_models`
- Database cursor/rows: `from_sql`
- NumPy arrays: `from_numpy`
- DataFrames (Pandas/Polars): `from_dataframe`
- Raw tuples/lists: `from_records`

See details and patterns in [Adapters](adapters.md).

## Large Dataset Tips

When working with large datasets, consider these optimization strategies:

- **Text vs. Screen Styles**: unless specified, the max width of a screen style
  will be the terminal width (or 120 if run with no active terminal). This may
  be limiting for very wide data sets. If the output is intended to be a text
  file. Consider using ASCII ro Markdown styles, or modify a style to set the
  `terminal_style` flag to false.
- **Pagination/chunking**: Render subsets to keep output readable and memory
  usage low.
- **`lazy_end=True`**: Omit the right border and right-trim cell content from
  the right-most cells to reduce wasted memory from right filled spaces.
- **`separate_rows=True`**: Add horizontal dividers between rows to improve
  readability of dense data.
- **Auto-fill columns**: Use one or more `A` flags in column definitions to
  absorb extra width when `table_width` is set.
- **Preprocessing**: Prefer preprocessors to normalize data early (affects
  sizing) and avoid heavy transformations after formatting.
- **Column filtering**: Use adapter `columns=[...]` parameters to load only
  needed columns from the source.

