"""Adapter for converting dataclass instances to table format."""

from typing import Any, Iterable
from dataclasses import fields, is_dataclass


###############################################################################
# from_dataclasses
###############################################################################


def from_dataclasses(
    data: Iterable[Any], columns: list[str] | None = None, include_private: bool = False
) -> tuple[list[list[Any]], list[str]]:
    """
    Convert a list of dataclass instances to table format.

    Args:
        data: Iterable of dataclass instances
        columns: Optional list of field names to filter/order results
        include_private: If True, include fields starting with underscore

    Returns:
        (rows, headers) tuple

    Example:
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class Person:
        ...     name: str
        ...     age: int
        >>> data = [Person("Alice", 30), Person("Bob", 25)]
        >>> rows, headers = from_dataclasses(data)
        >>> # headers: ["name", "age"]
        >>> # rows: [["Alice", 30], ["Bob", 25]]
    """
    data_list = list(data)
    if not data_list:
        return [], []

    first = data_list[0]
    if not is_dataclass(first):
        raise TypeError(f"Expected dataclass instances, got {type(first).__name__}")

    # Get field names
    all_fields = [f.name for f in fields(first)]
    if not include_private:
        all_fields = [f for f in all_fields if not f.startswith("_")]

    # Apply column filter
    if columns is not None:
        headers = [col for col in columns if col in all_fields]
    else:
        headers = all_fields

    # Build rows
    rows = []
    for item in data_list:
        row = [getattr(item, h, None) for h in headers]
        rows.append(row)

    return rows, headers
