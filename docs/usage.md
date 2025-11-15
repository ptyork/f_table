# Usage Guide

This guide shows the basics of how invoke and use f-table.

## Core Functions

There are three functions that can be used to generate tables:

- `get_table` — render a complete table (headers, rows, borders)
- `get_table_row` — render a single row
- `get_table_header` — render just the header block

!!! note

    See the [API reference](references/functions.md) for full function signatures
    and details.

`get_table` should be considered the primary entry point. In most cases, there
will be no need to call any other functions. 'get_table' has the following
definition:

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
    preprocessors: List[Callable[[Any], Any] | None] | None = None,
    postprocessors: List[Callable[[Any, str], str] | None] | None = None,
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
from f_table import get_table

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
elegance of this is where f-table shines and the main reason for it's creation.

```python
from f_table import get_table

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
- `lazy_end=True` omits the rightmost border. This is especiall useful for log
  files that may have long messages, as often you want them nicely formatted,
  but you also want to avoid line wrapping and keep each entry on a single line.
- `separate_rows=True` draws a divider line between each data row.
- `preprocessors`/`postprocessors` (advanced): column-indexed callbacks.
  Preprocessors run before formatting and influence widths; postprocessors run
  after sizing/wrapping for decorations like colors/styles (should not change
  displayed width).

The following is a more complete, styled example:

```python
from f_table import get_table, RoundedBorderScreenStyle

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

The style classes inacluded with f-table are:

- `NoBorderScreenStyle` — minimal, compact (default)
- `BasicScreenStyle` — classic box drawing
- `RoundedBorderScreenStyle` — rounded corners
- `ASCIIStyle` — classic, 7-bit ASCII drawing
- `MarkdownStyle` — GitHub-flavored Markdown tables

Modifying existing styles or creating custom styles is trivial.

See [Styles](styles.md) for additional visual examples and the [API
reference](references/styles.md) for class details.

## Advanced: Preprocessors and Postprocessors

These allow you more advanced control over the formatting of individual cells
through the use of custom callback funcitons. Usage and examples are provided in
the [Formatting Guide](formatting.md#advanced-preprocessors-and-postprocessors).
