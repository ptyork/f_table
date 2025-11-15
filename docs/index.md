# craftable — craft elegant terminal tables using format strings

Generate clean, flexible text tables in the terminal or in text files using a
familiar, Python-native formatting approach. craftable focuses on attractive and
predictable output, zero dependencies, a simple and elegant API, and fast
rendering without requiring a full TUI library.

- Small, zero-dependency API
- Works with plain Python data (lists/rows)
- Column definitions use Python’s format mini-language
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

## What you’ll find in this guide
- [Getting Started](getting-started.md): install and first table
- [Usage Guide](usage.md): headers, widths, wrapping, truncation, alignment
- [Formatting Guide](formatting.md): column definitions and flags
- [Styles](styles.md): pick a look (box, rounded, markdown, no border)
- [API Reference](references/functions.md): full docs for public functions and classes

## When to use craftable

Use craftable when you need reliable text tables in logs, CLIs, or scripts, and
want the control of Python format specs without heavy UI tooling. If you need
interactive widgets or color/styling, consider pairing with Rich — but for
static tables, craftable is intentionally simple and fast.
