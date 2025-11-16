"""Adapter for converting dict-of-lists (columnar format) to table format."""

from typing import Any, Mapping, Sequence


###############################################################################
# from_mapping_of_lists
###############################################################################


def from_mapping_of_lists(
    data: Mapping[str, Sequence[Any]], columns: list[str] | None = None
) -> tuple[list[list[Any]], list[str]]:
    """
    Convert a dict-of-lists (columnar format) to table format.

    Tolerates ragged columns - pads shorter columns with None.

    Args:
        data: Mapping where keys are column names, values are column data
        columns: Optional list of column names to filter/order results

    Returns:
        (rows, headers) tuple

    Example:
        >>> data = {"name": ["Alice", "Bob"], "age": [30, 25, 35]}
        >>> rows, headers = from_mapping_of_lists(data)
        >>> # headers: ["name", "age"]
        >>> # rows: [["Alice", 30], ["Bob", 25], [None, 35]]
    """
    if not data:
        return [], []

    # Determine headers
    if columns is not None:
        headers = [col for col in columns if col in data]
    else:
        headers = list(data.keys())

    if not headers:
        return [], []

    # Find max length
    max_len = max(len(data[h]) for h in headers)

    # Build rows
    rows = []
    for i in range(max_len):
        row = [data[h][i] if i < len(data[h]) else None for h in headers]
        rows.append(row)

    return rows, headers
