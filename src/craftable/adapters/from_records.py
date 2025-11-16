"""Adapter for converting tuples/lists to table format."""

from typing import Any, Iterable


###############################################################################
# from_records
###############################################################################


def from_records(
    data: Iterable[tuple | list], columns: list[str] | None = None
) -> tuple[list[list[Any]], list[str]]:
    """
    Convert an iterable of tuples/lists to table format.

    Args:
        data: Iterable of tuples or lists (rows)
        columns: Column headers. If None, generates "col_0", "col_1", etc.

    Returns:
        (rows, headers) tuple

    Example:
        >>> data = [("Alice", 30), ("Bob", 25)]
        >>> rows, headers = from_records(data, columns=["name", "age"])
    """
    rows = [list(row) for row in data]

    if not rows:
        return [], columns or []

    n_cols = len(rows[0]) if rows else 0

    if columns:
        headers = columns[:n_cols]  # Truncate if too many
        # Pad if too few
        if len(headers) < n_cols:
            headers += [f"col_{i}" for i in range(len(headers), n_cols)]
    else:
        headers = [f"col_{i}" for i in range(n_cols)]

    return rows, headers
