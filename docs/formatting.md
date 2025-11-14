# Formatting guide

f_table uses Python's [format specification
mini-language](https://docs.python.org/3/library/string.html#format-specification-mini-language)
for values plus a few table-specific flags for column behavior.

## Format specification strings

Column definitions are strings that combine:

- **Width and alignment**: same as Python (`<`, `>`, `^`)
- **Type and Precision**: same as Python (e.g., `.2f`, `.0%`, `d`)
- **Table Flags**: `A` (auto-fill), `T` (truncate), `S` (strict)
- **Prefix and Suffix**: Add text before or after each cell value

General pattern: `[align][width][.precision][type][flags]`

Expanded pattern: `[prefix_align][prefix](<pattern>)[suffix_align][suffix]`

Examples:

- `"20"` — minimum 20 characters (left-align by default)
- `">10.2f"` — right-align, 10 chars wide, 2 decimal float
- `"20T"` — 20 chars, truncate with ellipsis
- `"^A"` — center-align, auto-fill to table width

!!! note 

    Format strings are converted internally to `ColDef` objects for
    processing. You should generally use string specifications in your code,
    unless you wish to pre-parse the strings into `ColDef` and `ColDefList`
    objects and cache them for performance purposes. See the [API
    reference](references/classes.md) for implementation details.

## Alignment

The behavior is identical to standard Python format specifiers. The `align`
character can be one of:

- `<` left-align (default for most values)
- `>` right-align (default for numbers)
- `^` center-align

!!! note

    Unless the `S` (strict) flag is added, if an exception is thrown when
    formatting a value, it is converted to a string and is thus left-aligned. This
    may cause some confusion if you find some of your numbers being left-aligned.
    Thus it is recommended to specify `>` for columns that you with to ensure are
    right-aligned.

## Width

If provided, width can deviate somewhat from the expected behavior in Python
format specifiers. By default, f_table interprets it to be the __exact__ width
of the content of the column, while f-strings consider this to be a minimum
width. Consider the following:

```python
from math import pi

print("f-string:")
print(f"{pi:5} | {3.1:5}")
print("f-table:")
print(get_table([[pi, 3.1]], col_defs=["5","5"]))
```

The output is:

```
f-string:
3.141592653589793 |   3.1
f-table:
 3.141 │ 3.1
 59265 │
 35897 │
 93    │
```

If width is omitted, then the column size will be the lower of:

  - maximum width of the header and data values for the cloumn
  - the maximum width possible constrained by a specified table_size and 
    the required width of all other columns

!!! note

    See below for column width implications when specifying the `A` table flag.

## Precision and type

Use [standard Python format
specifiers](https://docs.python.org/3/library/string.html#format-specification-mini-language).
For example:

```python
col_defs = ["10", ".2f"]   # float with 2 decimals
col_defs = ["10", ".0%"]   # percentage with 0 decimals
col_defs = ["10", "d"]     # integer decimal
```

Example with output:

```python
rows = [[123.456, 0.789], [7.5, 0.012]]
col_defs = [">.2f", ">.1%"]
print(get_table(rows, header_row=["Value", "Percent"], col_defs=col_defs))
```

Output:

```
  Value  │ Percent 
─────────┼─────────
  123.46 │   78.9% 
    7.50 │    1.2% 
```

## Table flags

Append flags to the end of a column spec string (after type/precision):

### T — Truncate

Cuts off long text and appends an ellipsis (`…`):

```python
rows = [["This is a very long sentence that should be truncated", "OK"]]
col_defs = ["20T", "5"]
print(get_table(rows, col_defs=col_defs))
```

Output:

```
 This is a very long… │ OK    
```

The default behavior is to wrap long lines. So the above with simply `<20` as
the first column definition would appear as follows:

```
 This is a very long  │ OK    
 sentence that should │       
 be truncated         │       
```

### A — Auto-fill

Expands the column to fill remaining available table_width after taking into
account the width of all other columns.

!!! note

    For all "terminal" styles (i.e., all except for MarkdownTableStyle),
    when any column defs have an `A` attribute, table_width will default to the
    width of the terminal window.

For example:

```python
from f_table import get_table, BasicScreenStyle

rows = [["Alice", "Engineer", "30"], ["Bob", "Designer", "25"]]
col_defs = ["A", "<10", "<5"]  # first column auto-expands
print(get_table(rows, col_defs=col_defs, table_width=60, style=BasicScreenStyle()))
```

Output:

```
┌─────────────────────────────────────┬────────────┬───────┐
│ Alice                               │ Engineer   │ 30    │
│ Bob                                 │ Designer   │ 25    │
└─────────────────────────────────────┴────────────┴───────┘
```

**Multiple auto-fill columns**: When multiple columns have `A`, remaining space
is divided evenly:

```python
rows = [["Alice", "Engineer", "30"], ["Bob", "Designer", "25"]]
col_defs = ["A", "^A", "<5"]  # first two share expansion
print(get_table(rows, col_defs=col_defs, table_width=60, style=BasicScreenStyle()))
```

Output (both auto-fill columns get equal extra space):

```
┌─────────────────────────┬────────────────────────┬───────┐
│ Alice                   │        Engineer        │ 30    │
│ Bob                     │        Designer        │ 25    │
└─────────────────────────┴────────────────────────┴───────┘
```

### S — Strict

If specified, values that cannot be formatted using the supplied format string
will raise an exception. By default these values fall back to a simple string
conversion.

### Combining flags

You can combine flags:

```python
col_defs = ["^AT"]  # centered,auto-fill,truncate
```

These are simply additional flags added at the end of a standard string format
specification, so you can automatically size columns to fit rounded numbers,
etc.

```python
col_defs = [">.2fAS"]  # right-aligned,float rounded to 2 decimals,auto-fill, strict
```

## Prefix and Suffix

Values provided here will be appended to the start and end of each cell value,
respectively.

The prefix_align value can be `<` (left) or `>` (right, default). This
determines if the prefix is left-aligned in the cell or if it will simply be
prepended to the value.

The suffix_align value can be `<` (left, default) or `>` (right). This
determines if the suffix is right-aligned in the cell or if it will simply be
append to the value.

To add a prefix or suffix, simply enclose the format string in parentheses. Any
text before the opening paren will be the prefix. Any text after the closing
paren will be the suffix. If provided, the prefix_align value must be the very
first character of the column definition, and the suffix_align character must be
the first character after the closing paren.

!!! note

    Left aligning a prefix is usually only valuable if the cell is right aligned.
    Likewise right_aligning suffixes is only valuable for left aligned values.

Example:

```python
data = [
    ["Apple", 1.99, 12, ],
    ["Banana", 1.49, 10, ],
    ["Egg", 13.99, 2, ],
]

print(get_table(
    data,
    header_row=["Product", "Price", "Weight"],
    col_defs=["A","<$ (>8.2f)", "(^8) oz"],
    table_width=40,
    style=RoundedBorderScreenStyle(),
))
```

Results:

```
╭────────────────┬──────────┬──────────╮
│    Product     │  Price   │  Weight  │
├────────────────┼──────────┼──────────┤
│ Apple          │ $   1.99 │  12 oz   │
│ Banana         │ $   1.49 │  10 oz   │
│ Egg            │ $  13.99 │   2 oz   │
╰────────────────┴──────────┴──────────╯
```

## Header definitions

Header alignment can be controlled separately via `header_defs`. These will
accept all of the components of a column definition, however, only alignment
(`<`, `^`, or `>`) has any effect.

Example:

```python
from f_table import get_table

rows = [["Alice", 30], ["Bob", 25]]
print(get_table(
    rows,
    header_row=["Name", "Age"],
    col_defs=["<10", ">5"],     # data columns: left, right
    header_defs=["^", ">"],  # headers: center, right
))
```

This centers "Name" while left-aligning the data below it.

If no header_defs are provided, the headers will be centered.
