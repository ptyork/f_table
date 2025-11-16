#!/usr/bin/env python3
"""
Performance profiling script for craftable.

This script creates various test scenarios and profiles the performance
of get_table() to identify bottlenecks and optimization opportunities.
"""

import cProfile
import pstats
import io
import time
import random
import string
from typing import List, Any

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from craftable import get_table
from craftable.styles.rounded_border_screen_style import RoundedBorderScreenStyle
from craftable.styles.markdown_style import MarkdownStyle


def generate_test_data(
    rows: int, cols: int, data_type: str = "mixed"
) -> List[List[Any]]:
    """Generate test data of various types."""
    data = []

    for i in range(rows):
        row = []
        for j in range(cols):
            if data_type == "mixed":
                # Mix of strings, integers, and floats
                if j % 3 == 0:
                    row.append(
                        "".join(
                            random.choices(
                                string.ascii_letters, k=random.randint(5, 15)
                            )
                        )
                    )
                elif j % 3 == 1:
                    row.append(random.randint(1, 10000))
                else:
                    row.append(random.uniform(0.1, 9999.99))
            elif data_type == "string":
                row.append(
                    "".join(
                        random.choices(string.ascii_letters, k=random.randint(5, 15))
                    )
                )
            elif data_type == "numeric":
                row.append(random.uniform(0.1, 9999.99))
            elif data_type == "integer":
                row.append(random.randint(1, 10000))
        data.append(row)

    return data


def scenario_small_table():
    """Small table: 10 rows × 5 columns (baseline)."""
    data = generate_test_data(10, 5, "mixed")
    col_defs = ["15", "15", "15", "15", "15"]
    return get_table(data, col_defs=col_defs, table_width=120)


def scenario_medium_table():
    """Medium table: 1,000 rows × 10 columns (typical use)."""
    data = generate_test_data(1000, 10, "mixed")
    col_defs = ["12"] * 10
    return get_table(data, col_defs=col_defs, table_width=200)


def scenario_large_table():
    """Large table: 10,000 rows × 20 columns (stress test)."""
    data = generate_test_data(10000, 20, "mixed")
    col_defs = ["10"] * 20
    return get_table(data, col_defs=col_defs, table_width=300)


def scenario_wide_table():
    """Wide table: 100 rows × 100 columns (column-heavy) with MarkdownStyle."""
    data = generate_test_data(100, 100, "mixed")
    col_defs = ["10"] * 100
    # Use MarkdownStyle to avoid screen width constraints
    return get_table(data, col_defs=col_defs, style=MarkdownStyle())


def scenario_deep_table():
    """Deep table: 100,000 rows × 5 columns (row-heavy)."""
    data = generate_test_data(100000, 5, "mixed")
    col_defs = ["15"] * 5
    return get_table(data, col_defs=col_defs, table_width=150)


def scenario_complex_formatting():
    """Complex formatting with various format specs."""
    data = generate_test_data(1000, 8, "mixed")
    col_defs = [
        "<20",  # Left align
        ">15",  # Right align
        "^18",  # Center align
        "$(>12,.2f)USD",  # Prefix, suffix, thousands separator
        "(>10.1%)%",  # Percentage with suffix
        "0x(>8X)",  # Hex with prefix
        "(<15T)",  # Truncate
        "#(>8d)items",  # Prefix and suffix with format
    ]
    return get_table(data, col_defs=col_defs, table_width=200)


def scenario_with_headers():
    """Table with header row."""
    data = generate_test_data(1000, 10, "mixed")
    headers = [f"Column_{i}" for i in range(10)]
    col_defs = ["12"] * 10
    return get_table(data, header_row=headers, col_defs=col_defs, table_width=200)


def scenario_styled_table():
    """Table with custom style."""
    data = generate_test_data(1000, 10, "mixed")
    col_defs = ["12"] * 10
    return get_table(
        data, col_defs=col_defs, style=RoundedBorderScreenStyle(), table_width=200
    )


def scenario_auto_width():
    """Table with auto-width columns."""
    data = generate_test_data(500, 8, "mixed")
    col_defs = ["A"] * 8
    return get_table(data, col_defs=col_defs, table_width=120)


def scenario_unicode_heavy():
    """Table with unicode strings."""
    # Create data with unicode characters
    data = []
    for i in range(1000):
        row = []
        for j in range(8):
            if j % 2 == 0:
                row.append(f"Test_{i}_{j} 🎯💰✓⭐")
            else:
                row.append(random.uniform(0.1, 9999.99))
        data.append(row)

    col_defs = ["20", ">12.2f", "20", ">12.2f", "20", ">12.2f", "20", ">12.2f"]
    return get_table(data, col_defs=col_defs, table_width=200)


def scenario_with_pre_post():
    """Medium table with preprocessors and postprocessors.

    - Pre: capitalize strings in first column
    - Post: bracket numeric column after sizing
    """
    data = generate_test_data(1000, 4, "mixed")
    col_defs = ["<12", ">10.2f", "^8", "<10"]

    def pre_cap(val):
        return str(val).capitalize()

    def post_bracket(original, text):
        return f"[{text}]"

    preprocessors = [pre_cap, None, None, None]
    postprocessors = [None, post_bracket, None, None]
    return get_table(
        data,
        col_defs=col_defs,
        table_width=200,
        preprocessors=preprocessors,
        postprocessors=postprocessors,
    )


def benchmark_scenario(name: str, func, iterations: int = 1):
    """Benchmark a single scenario."""
    print(f"\n{'=' * 70}")
    print(f"Scenario: {name}")
    print(f"{'=' * 70}")

    # Warmup run
    func()

    # Timed runs
    times = []
    for i in range(iterations):
        start = time.perf_counter()
        _ = func()
        end = time.perf_counter()
        times.append(end - start)

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print(f"Iterations: {iterations}")
    print(f"Average time: {avg_time:.4f}s")
    print(f"Min time: {min_time:.4f}s")
    print(f"Max time: {max_time:.4f}s")

    if iterations > 1:
        print(f"Total time: {sum(times):.4f}s")

    return avg_time


def profile_scenario(name: str, func):
    """Profile a single scenario with cProfile."""
    print(f"\n{'=' * 70}")
    print(f"Profiling: {name}")
    print(f"{'=' * 70}")

    profiler = cProfile.Profile()
    profiler.enable()

    func()

    profiler.disable()

    # Create stats object
    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s)

    # Sort by cumulative time and print top 20 functions
    stats.sort_stats("cumulative")
    stats.print_stats(20)

    print(s.getvalue())

    # Also sort by total time
    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s)
    stats.sort_stats("time")
    stats.print_stats(20)

    print("\nTop functions by total time:")
    print(s.getvalue())


def main():
    """Run all profiling scenarios."""
    print("=" * 70)
    print("CRAFTABLE PERFORMANCE PROFILING")
    print("=" * 70)

    scenarios = [
        ("Small Table (10×5)", scenario_small_table, 100),
        ("Medium Table (1000×10)", scenario_medium_table, 10),
        ("Large Table (10000×20)", scenario_large_table, 2),
        ("Wide Table (100×100)", scenario_wide_table, 5),
        ("Deep Table (100000×5)", scenario_deep_table, 1),
        ("Complex Formatting", scenario_complex_formatting, 10),
        ("With Headers", scenario_with_headers, 10),
        ("With Pre/Post", scenario_with_pre_post, 10),
        ("Styled Table", scenario_styled_table, 10),
        ("Auto Width", scenario_auto_width, 10),
        ("Unicode Heavy", scenario_unicode_heavy, 10),
    ]

    print("\n" + "=" * 70)
    print("PHASE 1: BENCHMARKING")
    print("=" * 70)

    results = {}
    for name, func, iterations in scenarios:
        avg_time = benchmark_scenario(name, func, iterations)
        results[name] = avg_time

    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)
    for name, avg_time in results.items():
        print(f"{name:.<50} {avg_time:.4f}s")

    print("\n" + "=" * 70)
    print("PHASE 2: DETAILED PROFILING")
    print("=" * 70)
    print("\nProfiling most representative scenarios for bottleneck analysis...")

    # Profile a few key scenarios in detail
    profile_scenarios = [
        ("Medium Table (1000×10)", scenario_medium_table),
        ("Complex Formatting", scenario_complex_formatting),
        ("Wide Table (100×100)", scenario_wide_table),
    ]

    for name, func in profile_scenarios:
        profile_scenario(name, func)

    print("\n" + "=" * 70)
    print("PROFILING COMPLETE")


if __name__ == "__main__":
    main()
