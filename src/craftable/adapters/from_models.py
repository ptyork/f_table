"""Adapter for converting model instances (Pydantic, attrs, etc.) to table format."""

from typing import Any, Iterable
from dataclasses import is_dataclass


###############################################################################
# from_models
###############################################################################


def from_models(
    data: Iterable[Any], columns: list[str] | None = None, include_private: bool = False
) -> tuple[list[list[Any]], list[str]]:
    """
    Convert a list of model instances (Pydantic, attrs, etc.) to table format.

    Tries multiple strategies:
    1. model_dump() / dict() for Pydantic
    2. asdict() for attrs
    3. __dict__ fallback
    4. is_dataclass() for dataclasses

    Args:
        data: Iterable of model instances
        columns: Optional list of field names to filter/order results
        include_private: If True, include fields starting with underscore

    Returns:
        (rows, headers) tuple
    """
    # Import here to avoid circular dependency
    from .from_dataclasses import from_dataclasses
    from .from_dicts import from_dicts

    data_list = list(data)
    if not data_list:
        return [], []

    first = data_list[0]

    # Try dataclass first
    if is_dataclass(first):
        return from_dataclasses(data_list, columns, include_private)

    # Convert to dicts
    dicts = []
    for item in data_list:
        # Try various conversion methods
        if hasattr(item, "model_dump"):  # Pydantic v2
            d = item.model_dump()
        elif hasattr(item, "dict"):  # Pydantic v1
            d = item.dict()
        elif hasattr(item, "__dict__"):
            d = item.__dict__.copy()
        else:
            raise TypeError(f"Cannot convert {type(item).__name__} to dict")

        # Filter private if needed
        if not include_private:
            d = {k: v for k, v in d.items() if not k.startswith("_")}

        dicts.append(d)

    return from_dicts(dicts, columns=columns)
