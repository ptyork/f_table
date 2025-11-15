# Styles

craftable includes multiple built-in styles to match your environment or output
format. Swap styles via the `style` parameter.

## Available styles

### NoBorderScreenStyle (default)

Minimal, whitespace-delimited with a simple header separator.

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

### BasicScreenStyle

Classic box drawing with Unicode characters (│ ─ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼).

```python
from craftable import get_table, BasicScreenStyle

rows = [["Alice", 30], ["Bob", 25]]
print(get_table(rows, header_row=["Name", "Age"], style=BasicScreenStyle()))
```

Output:

```
┌───────┬─────┐
│  Name │ Age │
├───────┼─────┤
│ Alice │ 30  │
│ Bob   │ 25  │
└───────┴─────┘
```

### RoundedBorderScreenStyle

Rounded corners for a softer look (╭ ╮ ╰ ╯ │ ─).

```python
from craftable import get_table, RoundedBorderScreenStyle

rows = [["Alice", 30], ["Bob", 25]]
print(get_table(rows, header_row=["Name", "Age"], style=RoundedBorderScreenStyle()))
```

Output:

```
╭───────┬─────╮
│  Name │ Age │
├───────┼─────┤
│ Alice │ 30  │
│ Bob   │ 25  │
╰───────┴─────╯
```

### MarkdownStyle

GitHub-flavored Markdown tables for documentation.

```python
from craftable import get_table, MarkdownStyle

rows = [["Alice", 30], ["Bob", 25]]
print(get_table(rows, header_row=["Name", "Age"], style=MarkdownStyle()))
```

Output:

```
|  Name | Age |
| ----- | --- |
| Alice | 30  |
| Bob   | 25  |
```

### ASCIIStyle

Plain ASCII borders for terminals and logs.

```python
from craftable import get_table, ASCIIStyle

rows = [["Alice", 30], ["Bob", 25]]
print(get_table(rows, header_row=["Name", "Age"], style=ASCIIStyle()))
```

Output:

```
+-------+-----+
|  Name | Age |
+-------+-----+
| Alice | 30  |
| Bob   | 25  |
+-------+-----+
```

## Options that affect layout

From `get_table`:

- `table_width`: set the maximum width for the entire table
- `lazy_end`: omit the right border for compact output
- `separate_rows`: add a horizontal separator between rows (non-Markdown styles)

From style classes (subclasses of `TableStyle`):

- `cell_padding`: style-dependent spacing inside each cell
- `min_width`: style-dependent minimum column width

## Customizing styles

You can fine-tune the look of your tables either by tweaking an instance of a
built‑in style or by creating your own style class that derives from
`TableStyle`.

### Option 1: Modify a built‑in style instance

All visual details are exposed as attributes on the style object. You can
instantiate a style, change a few attributes, and pass it to `get_table`.

```python
from craftable import get_table, BasicScreenStyle, BoxChars

rows = [["Alice", 30], ["Bob", 25]]

style = BasicScreenStyle()

# Make cells roomier and swap in double-line rules for the header separator
style.cell_padding = 2
style.header_bottom_line = BoxChars.DOUBLE_HORIZONTAL
style.header_bottom_delimiter = BoxChars.DOUBLE_VERTICAL_AND_HORIZONTAL
style.header_bottom_left = Bo`xChars.DOUBLE_VERTICAL_AND_RIGHT
style.header_bottom_right = BoxChars.DOUBLE_VERTICAL_AND_LEFT

# Use double verticals between values
style.values_delimiter = BoxChars.DOUBLE_VERTICAL
style.values_left = BoxChars.DOUBLE_VERTICAL
style.values_right = BoxChars.DOUBLE_VERTICAL

print(get_table(rows, header_row=["Name", "Age"], style=style))
```

!!! tip 

    Start from the style closest to what you want (e.g., `BasicScreenStyle`,
    `RoundedBorderScreenStyle`, or `MarkdownStyle`) and override only a handful of
    attributes.

All border characters come from `BoxChars` (a small enum of Unicode box‑drawing
symbols). You can also use plain strings like `"|"` or `"-"` if you prefer pure
ASCII.

### Option 2: Create your own style class

For full control, subclass `TableStyle` and set the attributes you care about in `__init__`. Here’s a minimal ASCII style that uses `+`, `-`, and `|`.

```python
from craftable import TableStyle, BoxChars, get_table

class DoubleBorderStyle(TableStyle):
    """Bold outer borders with double-line rules and single-line interior."""
    
    def __init__(self):
        super().__init__()
        
        # Only override what makes this style unique
        # Use double lines for outer borders (horizontal and vertical)
        self.header_top_line = BoxChars.DOUBLE_HORIZONTAL
        self.values_bottom_line = BoxChars.DOUBLE_HORIZONTAL
        self.header_left = BoxChars.DOUBLE_VERTICAL
        self.header_right = BoxChars.DOUBLE_VERTICAL
        self.values_left = BoxChars.DOUBLE_VERTICAL
        self.values_right = BoxChars.DOUBLE_VERTICAL
        
        # Corners: pure double lines
        self.header_top_left = BoxChars.DOUBLE_DOWN_AND_RIGHT
        self.header_top_right = BoxChars.DOUBLE_DOWN_AND_LEFT
        self.values_bottom_left = BoxChars.DOUBLE_UP_AND_RIGHT
        self.values_bottom_right = BoxChars.DOUBLE_UP_AND_LEFT
        
        # Intersections where double borders meet single interior lines
        self.header_top_delimiter = BoxChars.DOUBLE_HORIZONTAL_AND_SINGLE_DOWN
        self.header_bottom_left = BoxChars.SINGLE_VERTICAL_AND_DOUBLE_RIGHT
        self.header_bottom_right = BoxChars.SINGLE_VERTICAL_AND_DOUBLE_LEFT
        self.values_bottom_delimiter = BoxChars.DOUBLE_HORIZONTAL_AND_SINGLE_UP

rows = [["Alice", 30], ["Bob", 25]]
print(get_table(rows, header_row=["Name", "Age"], style=DoubleBorderStyle()))
```

Output:

```
╔═══════╤═════╗
║  Name │ Age ║
╟───────┼─────╢
║ Alice │ 30  ║
║ Bob   │ 25  ║
╚═══════╧═════╝
```

!!! notes

    - You only need to override the attributes that make your style unique. In this
      example, we changed just the outer borders (8 attributes) and inherited ~20+
      other values from `TableStyle`.
    - If you want to build on an existing style instead of `TableStyle`, subclass it
      directly (e.g., `class MyStyle(BasicScreenStyle)`).
    - Markdown layout is handled by `MarkdownStyle` with `align_char=":"` and
      `terminal_style=False`. If you need a Markdown variant, subclass
      `MarkdownStyle` instead and tweak only what you need.

### Recipe: Compact/Dense tables

If you want maximum information density, reduce padding on a base style:

```python
from craftable import get_table, BasicScreenStyle

rows = [["Alice", 30], ["Bob", 25]]

dense = BasicScreenStyle()
dense.cell_padding = 0
dense.min_width = 1
print(get_table(rows, header_row=["Name", "Age"], style=dense))
```

## Style Code References

For class-level APIs like `TableStyle` and `BoxChars`, see the [API
reference](references/styles.md).
