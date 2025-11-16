"""Adapter for converting Pandas/Polars DataFrames to table format."""

from typing import Any


###############################################################################
# from_dataframe
###############################################################################


def from_dataframe(
    df: Any, columns: list[str] | None = None, include_index: bool = False
) -> tuple[list[list[Any]], list[str]]:
    """
    Convert a Pandas/Polars DataFrame to table format.

    Args:
        df: Pandas or Polars DataFrame
        columns: Optional list of column names to filter
        include_index: If True, include the DataFrame index as first column

    Returns:
        (rows, headers) tuple

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
        >>> rows, headers = from_dataframe(df)
        >>> # headers: ["name", "age"]
        >>> # rows: [["Alice", 30], ["Bob", 25]]
    """
    # Import here to avoid circular dependency
    from .from_dicts import from_dicts

    # Detect DataFrame type
    df_type = type(df).__name__

    if "DataFrame" not in df_type:
        raise TypeError(f"Expected DataFrame, got {df_type}")

    # Polars (check first since Polars also has to_dict)
    if hasattr(df, "to_dicts"):
        dicts = df.to_dicts()

        if columns:
            dicts = [{k: d[k] for k in columns if k in d} for d in dicts]

        return from_dicts(dicts, columns=columns)

    # Pandas
    elif hasattr(df, "to_dict"):
        # Filter columns if specified
        if columns:
            df = df[[c for c in columns if c in df.columns]]

        headers = list(df.columns)

        if include_index:
            index_name = df.index.name or "index"
            headers = [index_name] + headers
            rows = []
            for idx, row in df.iterrows():
                rows.append([idx] + list(row))
        else:
            rows = df.values.tolist()

        return rows, headers

    else:
        raise TypeError(f"Unsupported DataFrame type: {df_type}")
