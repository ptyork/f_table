# craftable — craft elegant tables using format strings

Generate clean, flexible text tables in the terminal or in text files using a
familiar, Python-native formatting approach. craftable focuses on attractive and
predictable output, zero dependencies, a simple and elegant API, and fast
rendering without requiring a full TUI library.

- Small, zero-dependency API
- Works with plain Python data (lists/rows)
- Built-in adapters for dicts, dataclasses, numpy, pandas, SQL, and more
- Column definitions use Python's format mini-language
- Multiple built-in styles: no borders, box drawing, rounded, ASCII, Markdown
- Supports wrapping, truncation, alignment, and auto-fill columns
- Simple, but flexible and extensible to meet most any use case

## Quick example

```python
from craftable import get_table

data = [
    ["Alice", 147000, .035, "Engineer"],
    ["Bob", 88000, .0433, "Designer"],
]

print(get_table(
    data,
    header_row=["Name", "Salary", "Adj", "Title"],
    col_defs=["A","<$ (,)", ">.2%", "A"],
    table_width=50,
))
```

Output:

```
      Name     │   Salary  │  Adj  │    Title     
───────────────┼───────────┼───────┼──────────────
 Alice         │ $ 147,000 │ 3.50% │ Engineer     
 Bob           │ $  88,000 │ 4.33% │ Designer     
```

## Data Adapters

Convert Python data structures directly into tables with built-in adapters:

```python
from craftable import get_table
from craftable.adapters import from_dicts

# List of dictionaries (handles missing keys gracefully)
data = [
    {"name": "Alice", "age": 30, "city": "LA"},
    {"name": "Bob", "age": 25},  # missing 'city'
]

rows, headers = from_dicts(data)
print(get_table(rows, header_row=headers))
```

Adapters available for: dicts, dataclasses, numpy arrays, pandas/polars DataFrames,
SQL cursors, and more. See the [Adapters documentation](https://ptyork.github.io/craftable/adapters/)
for details.

## When to use craftable

Use craftable when you need reliable text tables in logs, CLIs, or scripts, and
want the control of Python format specs without heavy UI tooling. If you need
interactive widgets or color/styling, consider pairing with Rich — but for
static tables, craftable is intentionally simple and fast.

## Getting Started

Read the online documentation:

[https://ptyork.github.io/craftable](https://ptyork.github.io/craftable)

Available as `craftable` in PyPI with zero additional dependencies, so you can
install or add to your project using your favorite package manager.

### pip

```bash
pip install craftable
```

### poetry

```bash
poetry add craftable
```

### uv

```bash
uv add craftable
```

Or if using uv pip:
```bash
uv pip install craftable
```
