"""Adapter for converting NumPy arrays to table format."""

from typing import Any


###############################################################################
# from_numpy
###############################################################################


def from_numpy(
    array: Any, columns: list[str] | None = None, include_index: bool = False
) -> tuple[list[list[Any]], list[str]]:
    """
    Convert a NumPy array to table format.

    Handles:
    - 1D arrays (single column)
    - 2D arrays (rows × columns)
    - Structured arrays (uses dtype.names for headers)

    Args:
        array: NumPy array
        columns: Optional list of column names/indices to filter
        include_index: If True, prepend an index column

    Returns:
        (rows, headers) tuple

    Example:
        >>> import numpy as np
        >>> arr = np.array([[1, 2], [3, 4]])
        >>> rows, headers = from_numpy(arr)
        >>> # headers: ["0", "1"]
        >>> # rows: [[1, 2], [3, 4]]
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError(
            "NumPy is required for from_numpy(). Install with: pip install numpy"
        )

    if not isinstance(array, np.ndarray):
        raise TypeError(f"Expected numpy.ndarray, got {type(array).__name__}")

    # Handle structured arrays
    if array.dtype.names:
        field_names = list(array.dtype.names)
        if columns:
            field_names = [f for f in field_names if f in columns]

        rows = []
        for i, record in enumerate(array):
            if include_index:
                row = [i] + [record[f] for f in field_names]
            else:
                row = [record[f] for f in field_names]
            rows.append(row)

        headers = (["index"] if include_index else []) + field_names
        return rows, headers

    # Handle 1D arrays
    if array.ndim == 1:
        headers = ["index", "value"] if include_index else ["value"]
        if include_index:
            rows = [[i, v] for i, v in enumerate(array)]
        else:
            rows = [[v] for v in array]
        return rows, headers

    # Handle 2D arrays
    if array.ndim == 2:
        n_cols = array.shape[1]
        col_indices = list(range(n_cols))

        # Apply column filter
        if columns:
            col_indices = [i for i in col_indices if str(i) in columns or i in columns]

        headers = (["index"] if include_index else []) + [str(i) for i in col_indices]

        rows = []
        for i, row in enumerate(array):
            if include_index:
                r = [i] + [row[j] for j in col_indices]
            else:
                r = [row[j] for j in col_indices]
            rows.append(r)

        return rows, headers

    raise ValueError(
        f"Cannot convert {array.ndim}D array to table (only 1D and 2D supported)"
    )
