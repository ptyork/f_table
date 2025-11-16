# Getting Started

This page helps you install craftable and print your first table.

## Installation

craftable is published on PyPI. Install with your preferred package manager:

=== "pip"
    ```bash
    pip install craftable
    ```

=== "poetry"
    ```bash
    poetry add craftable
    ```

=== "uv"
    ```bash
    uv add craftable
    ```

    Or if using uv pip:
    ```bash
    uv pip install craftable
    ```

## Your First Table

```python
from craftable import get_table

rows = [
    ["Alice", 30, "Engineer"],
    ["Bob", 25, "Designer"],
]

print(get_table(rows))
```

Output:

```
 Alice  │ 30  │ Engineer 
 Bob    │ 25  │ Designer 
```

## Spicing it Up

Add a `header_row` and try a different look with the `style` parameter:

```python
from craftable import get_table
from craftable.styles import BasicScreenStyle

rows = [
    ["Alice", 30, "Engineer"],
    ["Bob", 25, "Designer"],
]

print(get_table(
    rows,
    header_row=["Name", "Age", "Title"],
    style=BasicScreenStyle()
))
```

Output:

```
┌────────┬─────┬──────────┐
│  Name  │ Age │  Title   │
├────────┼─────┼──────────┤
│ Alice  │ 30  │ Engineer │
│ Bob    │ 25  │ Designer │
└────────┴─────┴──────────┘
```

## What's Next

- Configure widths, wrapping, and truncation in the [Usage guide](usage.md)
- Learn the format mini-language and table flags in the [Formatting
  guide](formatting.md)
- Explore built-in [Styles](styles.md)
- Jump to the [API reference](references/functions.md)
