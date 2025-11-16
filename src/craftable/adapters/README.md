# Data Structure Adapters

This module provides convenience functions to convert various Python data
structures into (rows, headers) tuples suitable for `craftable.get_table()`.

All adapters return: `tuple[list[list[Any]], list[str]]` representing (value_rows, headers).
All adapters support an optional `columns` parameter to filter/order columns.

## Available Adapters

- **from_dicts** - Convert list of dictionaries to table format
- **from_mapping_of_lists** - Convert dict-of-lists (columnar format) to table format
- **from_dataclasses** - Convert dataclass instances to table format
- **from_models** - Convert model instances (Pydantic, attrs, etc.) to table format
- **from_records** - Convert tuples/lists to table format with optional headers
- **from_sql** - Convert DB-API cursor results to table format
- **from_numpy** - Convert NumPy arrays to table format (requires numpy)
- **from_dataframe** - Convert Pandas/Polars DataFrames to table format (requires pandas/polars)

## Design Principles

1. **Tolerance**: All adapters tolerate missing/ragged data and fill gaps with `None`
2. **Consistency**: All return the same tuple format for easy use with `get_table()`
3. **Optional Dependencies**: Core adapters have zero dependencies; numpy/pandas are optional
4. **Filtering**: All support column filtering to reduce output

## Testing

To run tests for all adapters including those requiring optional dependencies:

```bash
# Install optional adapter dependencies
uv sync --group adapters

# Run tests with the project venv
.venv/bin/python -m pytest tests/test_adapters.py -v
```

The `adapters` dependency group includes:
- `numpy>=1.24.0` - for `from_numpy()` adapter
- `pandas>=2.0.0` - for `from_dataframe()` adapter
