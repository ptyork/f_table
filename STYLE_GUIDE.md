# Craftable Code Style Guide

This document outlines the code style conventions used in the Craftable project,
derived from the patterns established in `craftable.py`.

## General Principles

1. **Consistency is key**: Follow established patterns throughout the codebase
2. **Readability over cleverness**: Code should be easy to understand
3. **Type safety**: Use type hints consistently
4. **Clear documentation**: Every public function needs a comprehensive
   docstring

## Module Structure

### Section Dividers

Use section dividers with headers for major functional blocks:

```python
###############################################################################
# Function or Class Name
###############################################################################
```

These dividers help visually organize code into logical sections.

### Import Organization

Organize imports in the following order, with blank lines between groups:

1. Standard library `typing` imports
2. Other standard library imports
3. Third-party library imports
4. Local/relative imports

```python
from typing import Any, Iterable, List
from dataclasses import dataclass
import re

from .styles.table_style import TableStyle
```

### Blank Lines

- Two blank lines between top-level functions and classes
- One blank line between method definitions in a class
- Blank line before `return` statements (unless the function body is trivial)
- Blank line after major logical sections within a function

```python
def example_function(data: list[Any]) -> tuple[list, list]:
    """Process data and return results."""
    data_list = list(data)
    if not data_list:
        return [], []

    # Process the data
    headers = extract_headers(data_list)
    rows = process_rows(data_list, headers)

    return rows, headers
```

## Documentation

### Docstrings

Use triple-quoted docstrings for all public functions:

```python
def from_dicts(
    data: Iterable[dict[str, Any]],
    columns: list[str] | None = None,
) -> tuple[list[list[Any]], list[str]]:
    """
    Convert a list of dictionaries to table format.
    
    Tolerates missing keys - fills with None for missing values.
    
    Args:
        data:
            Iterable of dictionaries
        columns:
            (optional) List of column names to filter/order results. If 
            provided, only these columns will be included in the output.
    
    Returns:
        (rows, headers) tuple
        
    Example:
        >>> data = [{"name": "Alice", "age": 30}]
        >>> rows, headers = from_dicts(data)
    """
```

**Docstring structure:**
1. One-line summary
2. Blank line
3. Extended description (if needed)
4. Args section (with indented descriptions for multi-line)
5. Behavior section (optional)
6. Returns section
7. Example section (optional)

### Comments

- Use comments to explain **why**, not **what**
- Place comments on their own line above the code they describe
- Use descriptive comments for non-obvious logic

```python
# Determine column order by first appearance
headers = []
seen = set()
for item in data_list:
    for key in item.keys():
        if key not in seen:
            headers.append(key)
            seen.add(key)
```

## Type Hints

### Modern Syntax

Use modern type hint syntax (Python 3.10+):

- `list[str]` instead of `List[str]`
- `dict[str, Any]` instead of `Dict[str, Any]`
- `tuple[int, str]` instead of `Tuple[int, str]`
- `Type | None` instead of `Optional[Type]`

```python
def process(data: list[dict[str, Any]]) -> tuple[list[list[Any]], list[str]]:
    pass
```

### Type Aliases

Define type aliases at the module level for complex types:

```python
PreprocessorCallback: TypeAlias = Callable[[Any, List[Any], int], Any]
PostprocessorCallback: TypeAlias = Callable[[Any, str, List[Any], int], str]
```

### TYPE_CHECKING

Use `TYPE_CHECKING` to avoid circular imports:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..craftable import ColDefList

def write_table(col_defs: "ColDefList") -> None:
    pass
```

## Exception Handling

### Specific Exceptions

Catch specific exceptions whenever possible:

```python
try:
    import numpy as np
except ImportError:
    raise ImportError("NumPy is required for from_numpy(). Install with: pip install numpy")
```

### Bare Except

Only use bare `except:` when absolutely necessary, and add a noqa comment to
prevent linter complaints:

```python
try:
    term_width = get_terminal_size().columns
except:  # noqa: E722
    return max_term_width
```

### Exception Chaining

Use `from` to chain exceptions:

```python
except Exception as e:
    raise ImportError("Failed to import module") from e
```

## Naming Conventions

### Filenames, Variables, Functions and Methods

- Use `snake_case` for variables and functions
- Use descriptive names that clearly indicate purpose
- Avoid abbreviations unless universally understood

```python
def from_dataclasses(data: Iterable[Any]) -> tuple[list[list[Any]], list[str]]:
    data_list = list(data)
    first_item = data_list[0]
```

### Classes

- Use `CamelCase` for class names
- Avoid consecutive uppercase letters (e.g., `DocxStyle` instead of `DOCXStyle`)
- Use descriptive names implying purpose and/or base class
- Prefer separate files per class
- Filenames revert to conventions above (e.g., `docx_style.py`)

### Constants

Use `UPPER_SNAKE_CASE` for module-level constants:

```python
MAX_REASONABLE_WIDTH = 120
```

### Private Members

Prefix with single underscore for internal/private use:

```python
def _format_for_export(col_def, value):
    """Internal helper function."""
    pass
```

## Code Organization

### Function Length

- Keep functions focused on a single task
- Extract complex logic into helper functions
- Aim for functions under 50 lines when possible

### Early Returns

Use early returns to avoid deep nesting:

```python
def process_data(data: list) -> list:
    if not data:
        return []

    # Main processing logic
    return processed_data
```

### List/Dict Comprehensions

Use comprehensions for simple transformations, but prefer explicit loops for
complex logic:

```python
# Good: simple transformation
headers = [col.name for col in columns]

# Better as loop: complex logic
rows = []
for item in data:
    if item.is_valid():
        processed = transform(item)
        rows.append(processed)
```

## Testing

- Use pytest as a test runner, but maintain compatibility with unittest unless
  absolutely necessary

### Test Structure

- Use classes that derive from unittest.TestCase
- Group related tests in test classes
- Use descriptive test method names starting with `test_`
- Include docstrings explaining what is being tested

```python
class TestFromDicts(unittest.TestCase):
    """Tests for from_dicts adapter."""

    def test_basic_dicts(self):
        """Test converting list of dicts with consistent keys."""
        data = [{"name": "Alice", "age": 30}]
        rows, headers = from_dicts(data)
        
        self.assertEqual(headers, ["name", "age"])
        self.assertEqual(rows, [["Alice", 30]])
```

## Auto Forrmatting and Linting

This project uses `ruff` for both file formatting and linting. All files should
be formatted and no linting errors should be present when committing or
submitting a pull request.

## Summary

These guidelines ensure:

- Consistent code structure across the project
- Easy navigation and understanding
- Type safety and better IDE support
- Clear documentation for users and contributors
- Maintainable and testable code

When in doubt, refer to `craftable.py` as the canonical example.
