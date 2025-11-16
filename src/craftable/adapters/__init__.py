"""
Data structure adapters for craftable.

This module provides convenience functions to convert various Python data
structures into (rows, headers) tuples suitable for craftable.get_table().

All adapters return: (value_rows: list[list[Any]], headers: list[str])
All adapters support an optional `columns` parameter to filter/order columns.
"""

from .from_dicts import from_dicts
from .from_mapping_of_lists import from_mapping_of_lists
from .from_dataclasses import from_dataclasses
from .from_models import from_models
from .from_records import from_records
from .from_sql import from_sql
from .from_numpy import from_numpy
from .from_dataframe import from_dataframe

__all__ = [
    "from_dicts",
    "from_mapping_of_lists",
    "from_dataclasses",
    "from_models",
    "from_records",
    "from_sql",
    "from_numpy",
    "from_dataframe",
]
