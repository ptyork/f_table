"""Interactive test program for craftable.

Pick a sample data source (via various input adapters), then choose an output
style and whether to include headers. For styles that require file export, a
file will be created in the current working directory.
"""

from typing import Callable

import importlib.util
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from craftable import export_table, get_table
from craftable.styles import (
    ASCIIStyle,
    BasicScreenStyle,
    MarkdownStyle,
    NoBorderScreenStyle,
    RoundedBorderScreenStyle,
    DocxStyle,
    XlsxStyle,
    OdtStyle,
    OdsStyle,
    RtfStyle,
)


def _has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


# Availability of optional stacks
HAS_NUMPY = _has_module("numpy")
HAS_PANDAS = _has_module("pandas")
HAS_POLARS = _has_module("polars")
HAS_DOCX = _has_module("docx")
HAS_OPENPYXL = _has_module("openpyxl")
HAS_ODF = _has_module("odf.opendocument")


# Types
Rows = list[list[object]]
Headers = list[str]
SourceFn = Callable[[], tuple[Rows, Headers]]


def _from_dicts_basic() -> tuple[Rows, Headers]:
    from craftable.adapters import from_dicts

    data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
    return from_dicts(data)


def _from_dicts_missing() -> tuple[Rows, Headers]:
    from craftable.adapters import from_dicts

    data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "city": "NYC"},
    ]
    return from_dicts(data)


def _from_mapping_basic() -> tuple[Rows, Headers]:
    from craftable.adapters import from_mapping_of_lists

    data = {"name": ["Alice", "Bob"], "age": [30, 25]}
    return from_mapping_of_lists(data)


def _from_mapping_ragged() -> tuple[Rows, Headers]:
    from craftable.adapters import from_mapping_of_lists

    data = {"name": ["Alice", "Bob"], "age": [30, 25, 35]}
    return from_mapping_of_lists(data)


def _from_dataclasses_people() -> tuple[Rows, Headers]:
    from craftable.adapters import from_dataclasses

    @dataclass
    class Person:
        name: str
        age: int

    people = [Person("Alice", 30), Person("Bob", 25)]
    return from_dataclasses(people)


def _from_models_simple() -> tuple[Rows, Headers]:
    from craftable.adapters import from_models

    class Person:
        def __init__(self, name: str, age: int) -> None:
            self.name = name
            self.age = age

    people = [Person("Alice", 30), Person("Bob", 25)]
    return from_models(people)


def _from_records_tuples() -> tuple[Rows, Headers]:
    from craftable.adapters import from_records

    data = [("Alice", 30), ("Bob", 25)]
    return from_records(data)


def _from_sql_with_description() -> tuple[Rows, Headers]:
    from craftable.adapters import from_sql

    description = [("name", None), ("age", None), ("city", None)]
    rows_data = [("Alice", 30, "LA"), ("Bob", 25, "NYC")]
    return from_sql(rows_data, description=description)


def _from_numpy_1d() -> tuple[Rows, Headers]:  # type: ignore[return-type]
    from craftable.adapters import from_numpy
    import numpy as np  # noqa: F401

    arr = np.array([1, 2, 3])
    return from_numpy(arr)


def _from_numpy_2d() -> tuple[Rows, Headers]:  # type: ignore[return-type]
    from craftable.adapters import from_numpy
    import numpy as np  # noqa: F401

    arr = np.array([[1, 2], [3, 4]])
    return from_numpy(arr)


def _from_numpy_structured() -> tuple[Rows, Headers]:  # type: ignore[return-type]
    from craftable.adapters import from_numpy
    import numpy as np  # noqa: F401

    dtype = [("name", "U10"), ("age", "i4")]
    arr = np.array([("Alice", 30), ("Bob", 25)], dtype=dtype)
    return from_numpy(arr)


def _from_pandas_df() -> tuple[Rows, Headers]:
    from craftable.adapters import from_dataframe
    import pandas as pd  # type: ignore

    df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
    return from_dataframe(df)


def _from_polars_df() -> tuple[Rows, Headers]:
    from craftable.adapters import from_dataframe
    import polars as pl  # type: ignore

    df = pl.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
    return from_dataframe(df)


# ---------------------------------------------------------------------------
# Basic list-of-lists sources (no adapter)
# ---------------------------------------------------------------------------


def _lists_basic() -> tuple[Rows, Headers]:
    rows: Rows = [
        ["Alice", 30, 95000.25, True],
        ["Bob", 25, 88000.0, False],
        ["Carol", 40, 120000.75, True],
    ]
    headers: Headers = ["name", "age", "salary", "active"]
    return rows, headers


def _lists_mixed() -> tuple[Rows, Headers]:
    rows: Rows = [
        ["Widget", 12, 0.1534, "A"],
        ["Gadget", 3, 0.50789, "B"],
        ["Doohickey", 100, 0.00012, "C"],
    ]
    headers: Headers = ["item", "count", "ratio", "grade"]
    return rows, headers


def _lists_jagged() -> tuple[Rows, Headers]:
    rows: Rows = [
        ["Short", 1],
        ["Medium text", 2, "Extra"],
        ["A very very long piece of text that will wrap", 3],
    ]
    headers: Headers = ["description", "value", "note"]
    return rows, headers


def _prompt_choice(
    title: str, options: list[tuple[str, str]], allow_back: bool = False
) -> str | None:
    print(f"\n{title}")
    for i, (key, label) in enumerate(options, start=1):
        print(f"  {i}. {label}")
    if allow_back:
        print("  0. Back")
    while True:
        sel = input("Enter choice #: ").strip()
        if allow_back and sel == "0":
            return None
        try:
            idx = int(sel) - 1
            if 0 <= idx < len(options):
                return options[idx][0]
        except Exception:
            pass
        print("Invalid choice, please try again.")


def _style_from_key(key: str):
    if key == "screen-basic":
        return BasicScreenStyle(), False, None
    if key == "screen-noborder":
        return NoBorderScreenStyle(), False, None
    if key == "screen-rounded":
        return RoundedBorderScreenStyle(), False, None
    if key == "screen-ascii":
        return ASCIIStyle(), False, None
    if key == "screen-markdown":
        return MarkdownStyle(), False, None
    if key == "file-rtf":
        return RtfStyle(), True, ".rtf"
    if key == "file-docx":
        return DocxStyle(), True, ".docx"
    if key == "file-xlsx":
        return XlsxStyle(), True, ".xlsx"
    if key == "file-odt":
        return OdtStyle(), True, ".odt"
    if key == "file-ods":
        return OdsStyle(), True, ".ods"
    raise ValueError(key)


# ---------------------------------------------------------------------------
# Column specification builder
# ---------------------------------------------------------------------------


def _build_col_defs(
    option: str, rows: Rows, headers: Headers | None
) -> list[str] | None:
    """Dynamically build column spec strings based on actual data.

    Inspects each column across all rows to infer a representative value/type.
    Ensures returned spec list length matches the maximum column count.
    Options:
        none: return None (auto sizing)
        simple: basic alignment & numeric formatting
        complex: richer formatting (currency, percent, truncation)
    """
    if option == "none":
        return None

    # Determine max columns, gather sample values per column
    col_count = max((len(r) for r in rows), default=0)
    if col_count == 0:
        return None

    samples: list[object | None] = [None] * col_count
    for r in rows:
        for i in range(col_count):
            if samples[i] is not None:
                continue
            if i < len(r) and r[i] is not None:
                samples[i] = r[i]

    # Helper: normalized header name
    def h(i: int) -> str:
        if headers and i < len(headers):
            return str(headers[i]).strip().lower()
        return ""

    specs: list[str] = []
    for i in range(col_count):
        val = samples[i]
        name = h(i)
        if option == "simple":
            if isinstance(val, bool):
                specs.append("^5")
            elif isinstance(val, int):
                specs.append(">6d")
            elif isinstance(val, float):
                specs.append(">10.2f")
            else:
                specs.append("<A" if i == 0 else "<20")
            continue
        # complex
        if isinstance(val, (int, float)) and name in {
            "salary",
            "price",
            "amount",
            "cost",
        }:
            specs.append("<$ (>12,.2f)")  # currency-like
        elif isinstance(val, float) and name in {"ratio", "pct", "percent", "rate"}:
            specs.append(">8.2%")
        elif isinstance(val, int) and name in {"age", "count", "value"}:
            specs.append(">6d")
        elif isinstance(val, float):
            specs.append(">10.3f")
        elif isinstance(val, bool):
            specs.append("^7")
        else:
            # text columns: first gets auto-fill, others wrap/truncate if long
            if i == 0:
                specs.append("<A")
            else:
                specs.append("<30T")
    return specs


def main() -> None:
    # Build data source options
    data_sources: list[tuple[str, str, SourceFn, bool]] = [
        ("lists-basic", "Lists: basic (no adapter)", _lists_basic, True),
        ("lists-mixed", "Lists: mixed types (no adapter)", _lists_mixed, True),
        ("lists-jagged", "Lists: jagged / varying columns", _lists_jagged, True),
        ("dicts-basic", "Dicts: basic (from_dicts)", _from_dicts_basic, True),
        (
            "dicts-missing",
            "Dicts: missing keys (from_dicts)",
            _from_dicts_missing,
            True,
        ),
        (
            "mapping-basic",
            "Mapping of lists: basic (from_mapping_of_lists)",
            _from_mapping_basic,
            True,
        ),
        (
            "mapping-ragged",
            "Mapping of lists: ragged (from_mapping_of_lists)",
            _from_mapping_ragged,
            True,
        ),
        (
            "dataclasses",
            "Dataclasses: people (from_dataclasses)",
            _from_dataclasses_people,
            True,
        ),
        ("models", "Models: simple class (from_models)", _from_models_simple, True),
        ("records", "Records: tuples (from_records)", _from_records_tuples, True),
        ("sql", "SQL: rows + description (from_sql)", _from_sql_with_description, True),
    ]
    if HAS_NUMPY:
        data_sources.extend(
            [
                ("numpy-1d", "NumPy: 1D array (from_numpy)", _from_numpy_1d, True),
                ("numpy-2d", "NumPy: 2D array (from_numpy)", _from_numpy_2d, True),
                (
                    "numpy-structured",
                    "NumPy: structured array (from_numpy)",
                    _from_numpy_structured,
                    True,
                ),
            ]
        )
    if HAS_PANDAS:
        data_sources.append(
            ("pandas", "Pandas DataFrame (from_dataframe)", _from_pandas_df, True)
        )
    if HAS_POLARS:
        data_sources.append(
            ("polars", "Polars DataFrame (from_dataframe)", _from_polars_df, True)
        )

    # Build style options (mark unavailable optional ones)
    style_options: list[tuple[str, str, bool]] = [
        ("screen-basic", "Screen: basic", True),
        ("screen-noborder", "Screen: no border", True),
        ("screen-rounded", "Screen: rounded border", True),
        ("screen-ascii", "Screen: ASCII", True),
        ("screen-markdown", "Screen: Markdown", True),
        ("file-rtf", "File: RTF (.rtf)", True),  # no external dep
        ("file-docx", "File: DOCX (.docx)", HAS_DOCX),
        ("file-xlsx", "File: XLSX (.xlsx)", HAS_OPENPYXL),
        ("file-odt", "File: ODT (.odt)", HAS_ODF),
        ("file-ods", "File: ODS (.ods)", HAS_ODF),
    ]

    print("Craftable interactive tester")
    print("============================")

    while True:
        # Choose data source
        ds_menu = [
            (k, (v + (" [unavailable]" if not ok else "")))
            for k, v, _fn, ok in [(d[0], d[1], d[2], d[3]) for d in data_sources]
        ]
        ds_key = _prompt_choice("Choose a sample data source:", ds_menu)
        if ds_key is None:
            break

        # Find function for chosen data source
        ds_entry = next((d for d in data_sources if d[0] == ds_key), None)
        if not ds_entry:
            print("Unknown selection.")
            continue
        if not ds_entry[3]:
            print("That data source is unavailable in this environment.")
            continue
        make_rows = ds_entry[2]
        try:
            rows, headers = make_rows()
        except Exception as e:
            print(f"Error building data source: {e}")
            continue

        # Header preference
        include_headers = input("Include headers? [Y/n]: ").strip().lower() not in {
            "n",
            "no",
        }
        header_row = headers if include_headers else None

        # Column specifications (none / simple / complex)
        col_spec_options = [
            ("none", "No column specs (auto-size)"),
            ("simple", "Simple specs (align & numeric formats)"),
            ("complex", "Complex specs (currency, %, truncation)"),
        ]
        col_choice = _prompt_choice("Choose column spec style:", col_spec_options)
        col_defs = _build_col_defs(col_choice or "none", rows, header_row)
        if col_defs:
            print("\nGenerated column specs:")
            for i, spec in enumerate(col_defs, start=1):
                print(f"  Col {i}: {spec}")

        # Choose style
        st_menu = []
        for key, label, ok in style_options:
            st_menu.append((key, label + (" [unavailable]" if not ok else "")))
        st_key = _prompt_choice("Choose an output style:", st_menu)
        if st_key is None:
            continue

        st_entry = next((s for s in style_options if s[0] == st_key), None)
        if not st_entry:
            print("Unknown selection.")
            continue
        if not st_entry[2]:
            print("That style is unavailable (missing optional dependency).")
            continue

        style, requires_file, ext = _style_from_key(st_key)

        # Perform output
        try:
            if not requires_file:
                # Render to screen and print
                table = get_table(
                    rows, header_row=header_row, style=style, col_defs=col_defs
                )
                print("\n" + table + "\n")
            else:
                # Export to file in current directory
                base = f"table_{ds_key}_{st_key}"
                # Add a date-based suffix to avoid collisions
                suffix = date.today().isoformat().replace("-", "")
                filename = f"{base}_{suffix}{ext}"
                path = Path(os.getcwd()) / filename
                out = export_table(
                    rows,
                    header_row=header_row,
                    style=style,
                    file=path,
                    col_defs=col_defs,
                )  # type: ignore[arg-type]
                print(f"Exported to: {out}")
        except ImportError as ie:
            print(f"Missing dependency: {ie}")
        except Exception as e:
            print(f"Error generating output: {e}")

        again = input("Run again? [Y/n]: ").strip().lower()
        if again in {"n", "no"}:
            break


if __name__ == "__main__":
    main()
