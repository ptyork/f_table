"""Adapter for converting DB-API cursor results to table format."""

from typing import Any


###############################################################################
# from_sql
###############################################################################


def from_sql(
    cursor_or_rows: Any,
    columns: list[str] | None = None,
    description: Any | None = None,
) -> tuple[list[list[Any]], list[str]]:
    """
    Convert DB-API cursor or result rows to table format.

    Args:
        cursor_or_rows: DB-API cursor or iterable of rows
        columns: Optional list of column names to filter
        description: Optional cursor.description (auto-detected if cursor provided)

    Returns:
        (rows, headers) tuple

    Example:
        >>> # Using a cursor
        >>> cursor.execute("SELECT name, age FROM users")
        >>> rows, headers = from_sql(cursor)

        >>> # Using raw rows + description
        >>> rows, headers = from_sql(result_rows, description=cursor.description)
    """
    # Try to get description from cursor
    if hasattr(cursor_or_rows, "description"):
        description = cursor_or_rows.description
        rows = [list(row) for row in cursor_or_rows]
    else:
        rows = [list(row) for row in cursor_or_rows]

    if not description:
        # No description available, generate generic headers
        if rows:
            n_cols = len(rows[0]) if rows else 0
            headers = [f"col_{i}" for i in range(n_cols)]
        else:
            headers = []
    else:
        # Extract column names from description
        headers = [col[0] for col in description]

    # Apply column filter
    if columns:
        if description:
            # Find indices of requested columns
            indices = [i for i, h in enumerate(headers) if h in columns]
            headers = [headers[i] for i in indices]
            rows = [[row[i] for i in indices] for row in rows]
        # else: can't filter without knowing column names

    return rows, headers
