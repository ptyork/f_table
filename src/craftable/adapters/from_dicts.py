"""Adapter for converting list of dictionaries to table format."""

from typing import Any, Iterable


###############################################################################
# from_dicts
###############################################################################


def from_dicts(
    data: Iterable[dict[str, Any]],
    columns: list[str] | None = None,
    order: str = "detect",
    first_only: bool = False,
) -> tuple[list[list[Any]], list[str]]:
    """
    Convert a list of dictionaries to table format.

    Tolerates missing keys - fills with None for missing values.

    Args:
        data: Iterable of dictionaries
        columns: Optional list of column names to filter/order results.
                If provided, only these columns will be included in the output.
        order: How to order columns when columns is None:
              "detect" - order of first appearance across all dicts (default)
              "alpha" - alphabetical sort
        first_only: If True, only include keys from the first dict (ignore keys
                   in subsequent dicts). Useful when you know the schema and want
                   to ignore unexpected keys. Default: False

    Returns:
        (rows, headers) tuple

    Example:
        >>> data = [{"name": "Alice", "age": 30}, {"name": "Bob", "city": "NYC"}]
        >>> rows, headers = from_dicts(data)
        >>> # headers: ["name", "age", "city"]
        >>> # rows: [["Alice", 30, None], ["Bob", None, "NYC"]]

        >>> # With first_only=True, "city" is ignored
        >>> rows, headers = from_dicts(data, first_only=True)
        >>> # headers: ["name", "age"]
        >>> # rows: [["Alice", 30], ["Bob", None]]
    """
    data_list = list(data)
    if not data_list:
        return [], []

    # Determine column order
    if columns is not None:
        headers = columns
    else:
        if first_only:
            # Only use keys from first dict
            headers = list(data_list[0].keys()) if data_list else []
            if order == "alpha":
                headers = sorted(headers)
        elif order == "alpha":
            # Collect all keys and sort
            all_keys = set()
            for item in data_list:
                all_keys.update(item.keys())
            headers = sorted(all_keys)
        else:  # "detect"
            # Order by first appearance
            headers = []
            seen = set()
            for item in data_list:
                for key in item.keys():
                    if key not in seen:
                        headers.append(key)
                        seen.add(key)

    # Build rows, tolerating missing keys
    rows = []
    for item in data_list:
        row = [item.get(header, None) for header in headers]
        rows.append(row)

    return rows, headers
