# Data Adapters

Craftable includes a comprehensive set of adapters to convert various Python data structures into table format. All adapters return a tuple of `(rows, headers)` that can be directly used with `get_table()`.

## Overview

Each adapter function follows a consistent pattern:

- **Returns**: `tuple[list[list[Any]], list[str]]` - (value rows, header row)
- **Tolerates** missing/ragged data - fills gaps with `None`
- **Supports** optional column filtering via `columns` parameter
- **Zero dependencies** for core adapters (numpy/pandas optional)

## Available Adapters

### `from_dicts()`

Convert a list of dictionaries to table format. Ideal for JSON-like data or API responses.

**Features:**
- Automatically discovers all keys across all dictionaries
- Tolerates missing keys (fills with `None`)
- Supports column ordering: `"detect"` (default) or `"alpha"`
- Optional `first_only` mode to ignore keys beyond first dict

```python
from craftable import get_table
from craftable.adapters import from_dicts

data = [
    {"name": "Alice", "age": 30, "city": "LA"},
    {"name": "Bob", "age": 25},  # Missing 'city'
    {"name": "Charlie", "city": "NYC"}  # Missing 'age'
]

rows, headers = from_dicts(data)
print(get_table(rows, header_row=headers))
```

Output:
```
   name  │ age  │ city 
─────────┼──────┼──────
 Alice   │ 30   │ LA   
 Bob     │ 25   │ None 
 Charlie │ None │ NYC  
```

**Column Filtering:**
```python
# Only show specific columns
rows, headers = from_dicts(data, columns=["name", "city"])
print(get_table(rows, header_row=headers))
```

**Column Ordering:**
```python
# Order alphabetically
rows, headers = from_dicts(data, order="alpha")

# Use only keys from first dict (ignore "city" from Charlie)
rows, headers = from_dicts(data, first_only=True)
# headers: ["name", "age"]

# Combine: first dict keys only, sorted alphabetically
rows, headers = from_dicts(data, first_only=True, order="alpha")
```

---

### `from_mapping_of_lists()`

Convert a dictionary-of-lists (columnar format) to table format. Common with pandas-style data.

**Features:**
- Handles ragged columns (different lengths) by padding with `None`
- Preserves insertion order of keys (Python 3.7+)

```python
from craftable import get_table
from craftable.adapters import from_mapping_of_lists

data = {
    "name": ["Alice", "Bob", "Charlie"],
    "score": [95, 87, 92],
    "grade": ["A", "B", "A"]
}

rows, headers = from_mapping_of_lists(data)
print(get_table(rows, header_row=headers))
```

Output:
```
   name  │ score │ grade 
─────────┼───────┼───────
 Alice   │ 95    │ A     
 Bob     │ 87    │ B     
 Charlie │ 92    │ A     
```

**Ragged Columns:**
```python
ragged = {
    "name": ["Alice", "Bob"],
    "score": [95, 87, 92]  # Extra value
}
rows, headers = from_mapping_of_lists(ragged)
# Row 3: [None, 92]
```

---

### `from_dataclasses()`

Convert dataclass instances to table format. Type-safe alternative to dictionaries.

**Features:**
- Automatically extracts field names
- Excludes private fields (starting with `_`) by default
- Supports column filtering

```python
from dataclasses import dataclass
from craftable import get_table
from craftable.adapters import from_dataclasses

@dataclass
class Employee:
    name: str
    age: int
    department: str
    salary: float

employees = [
    Employee("Alice", 30, "Engineering", 95000),
    Employee("Bob", 25, "Marketing", 75000),
]

rows, headers = from_dataclasses(employees)
print(get_table(rows, header_row=headers))
```

Output:
```
  name │ age │  department │  salary 
───────┼─────┼─────────────┼─────────
 Alice │ 30  │ Engineering │ 95000.0 
 Bob   │ 25  │ Marketing   │ 75000.0 
```

**Private Fields:**
```python
@dataclass
class Record:
    name: str
    _internal_id: int  # Excluded by default

# Include private fields
rows, headers = from_dataclasses(data, include_private=True)
```

---

### `from_models()`

Generic adapter for model instances (Pydantic, attrs, dataclasses, or plain objects).

**Features:**
- Auto-detects model type and uses appropriate conversion
- Supports Pydantic v1 (`dict()`) and v2 (`model_dump()`)
- Falls back to `__dict__` for plain classes

```python
from craftable import get_table
from craftable.adapters import from_models

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

people = [Person("Alice", 30), Person("Bob", 25)]
rows, headers = from_models(people)
print(get_table(rows, header_row=headers))
```

**Works with Pydantic:**
```python
from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str

users = [User(username="alice", email="alice@example.com")]
rows, headers = from_models(users)
```

---

### `from_records()`

Convert an iterable of tuples/lists to table format with optional headers.

**Features:**
- Simple conversion for raw record data
- Auto-generates headers (`col_0`, `col_1`, ...) if not provided

```python
from craftable import get_table
from craftable.adapters import from_records

data = [
    ("Alice", 30, "LA"),
    ("Bob", 25, "NYC")
]

rows, headers = from_records(data, columns=["name", "age", "city"])
print(get_table(rows, header_row=headers))
```

Output:
```
  name │ age │ city 
───────┼─────┼──────
 Alice │ 30  │ LA   
 Bob   │ 25  │ NYC  
```

**Auto-generated Headers:**
```python
rows, headers = from_records(data)
# headers: ["col_0", "col_1", "col_2"]
```

---

### `from_sql()`

Convert database query results to table format. Works with DB-API cursors.

**Features:**
- Auto-detects column names from cursor description
- Works with raw rows + description
- Falls back to generic headers if no description

```python
from craftable import get_table
from craftable.adapters import from_sql

# Using a cursor directly
cursor.execute("SELECT name, age, city FROM users")
rows, headers = from_sql(cursor)
print(get_table(rows, header_row=headers))

# Using rows + description
cursor.execute("SELECT * FROM products")
result_rows = cursor.fetchall()
rows, headers = from_sql(result_rows, description=cursor.description)
```

**Column Filtering:**
```python
# Only show specific columns
rows, headers = from_sql(cursor, columns=["name", "email"])
```

---

### `from_numpy()`

Convert NumPy arrays to table format. Requires `numpy` to be installed.

**Features:**
- Supports 1D and 2D arrays
- Handles structured arrays (uses field names as headers)
- Optional index column

```python
import numpy as np
from craftable import get_table
from craftable.adapters import from_numpy

# 2D array
arr = np.array([[1, 2, 3], [4, 5, 6]])
rows, headers = from_numpy(arr)
# headers: ["0", "1", "2"]

# 1D array
arr = np.array([10, 20, 30])
rows, headers = from_numpy(arr)
# headers: ["value"]

# With index column
rows, headers = from_numpy(arr, include_index=True)
# headers: ["index", "value"]
```

**Structured Arrays:**
```python
dtype = [('name', 'U10'), ('age', 'i4')]
arr = np.array([('Alice', 30), ('Bob', 25)], dtype=dtype)
rows, headers = from_numpy(arr)
# headers: ["name", "age"]
```

---

### `from_dataframe()`

Convert Pandas or Polars DataFrames to table format. Requires respective library.

**Features:**
- Auto-detects Pandas vs Polars
- Optional index column
- Column filtering support

```python
import pandas as pd
from craftable import get_table
from craftable.adapters import from_dataframe

df = pd.DataFrame({
    "name": ["Alice", "Bob"],
    "score": [95, 87]
})

rows, headers = from_dataframe(df)
print(get_table(rows, header_row=headers))
```

Output:
```
  name │ score 
───────┼───────
 Alice │ 95    
 Bob   │ 87    
```

**With Index:**
```python
rows, headers = from_dataframe(df, include_index=True)
# Adds first column with index values
```

**Column Filtering:**
```python
rows, headers = from_dataframe(df, columns=["name"])
```

---

## Common Patterns

### Combining with Custom Formatting

Adapters return raw data - use `get_table()` parameters for formatting:

```python
data = [
    {"product": "Widget A", "price": 19.99, "stock": 150},
    {"product": "Widget B", "price": 29.99, "stock": 75},
]

rows, headers = from_dicts(data)

table = get_table(
    rows,
    header_row=headers,
    col_defs=[
        "product:20",     # Fixed width
        "price:>8.2f",    # Right-aligned, 2 decimals
        "stock:>6d"       # Right-aligned integer
    ]
)
```

### Filtering and Transforming

```python
# Filter at adapter level
rows, headers = from_dicts(data, columns=["name", "score"])

# Or filter with ColDef
rows, headers = from_dicts(data)
table = get_table(rows, header_row=headers, col_defs=["name", "score"])
```

### Handling None Values

All adapters use `None` for missing values. You have two ways to customize the display:

1) Quick, global replacement per table

```python
from craftable import get_table

table = get_table(rows, header_row=headers, none_text="(missing)")
```

2) Per‑column replacement using `ColDef.none_text`

```python
from craftable import get_table
from craftable import ColDefList

specs = ["name", "age"]
col_defs = ColDefList.parse(specs)  # convenience parser
col_defs[0].none_text = "N/A"       # only for the first column
col_defs[1].none_text = "--"        # different placeholder for age

table = get_table(rows, header_row=headers, col_defs=col_defs)
```

Notes:
- Per‑column `none_text` overrides the global `none_text` parameter when both are provided.
- `none_text` is treated as normal text for width/truncation/wrapping.

---

## Error Handling

Adapters validate input and raise appropriate errors:

- `TypeError` - Wrong data type (e.g., non-dataclass passed to `from_dataclasses()`)
- `ImportError` - Missing optional dependency (numpy/pandas)
- `ValueError` - Invalid data shape (e.g., 3D numpy array)

```python
try:
    rows, headers = from_numpy(array)
except ImportError:
    print("NumPy not installed")
except ValueError as e:
    print(f"Invalid array shape: {e}")
```

---

## Performance Notes

- **from_dicts()** - Iterates all dicts to find headers (O(n*m) where m = avg
  keys)
- **from_mapping_of_lists()** - Most efficient for columnar data (O(n))
- **from_dataclasses()** - Uses `fields()` introspection (O(1) per type)
- **from_numpy()/from_dataframe()** - Delegates to library's `.tolist()` methods

Craftable strives to optimize for speed and efficiency, but it necessarily must
load multiple copies of a dataset into memory in order to generate a large
table. For extremely large datasets (>100K rows), consider:

1. Column filtering
2. Pagination
3. Using native library display methods

---

## See Also

- [Getting Started](getting-started.md) - Basic usage
- [Formatting Guide](formatting.md) - Column definitions and styling
- [API Reference](references/functions.md) - Complete API documentation
