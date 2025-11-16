# Recipes

Practical, copy-paste examples demonstrating common Craftable patterns and advanced techniques.


## Color-code negative values with ANSI escape codes  {#color-code}

Use a postprocessor to add red coloring to negative numbers:

```python
from craftable import get_table

def red_negative(original, text, row, col_idx):
    try:
        if float(original) < 0:
            return f"\x1b[31m{text}\x1b[0m"  # red
    except (ValueError, TypeError):
        pass
    return text

data = [
    ["Widget A", 1250.50, -45.20],
    ["Widget B", -320.00, 150.75],
    ["Widget C", 890.25, 220.00],
]

print(get_table(
    data,
    header_row=["Product", "Revenue", "Cost"],
    col_defs=["<20", ">10.2f", ">10.2f"],
    postprocessors=[None, red_negative, red_negative],
))
```

Example output (colors removed for clarity):

```text
       Product        │  Revenue   │    Cost    
──────────────────────┼────────────┼────────────
 Widget A             │    1250.50 │     -45.20 
 Widget B             │    -320.00 │     150.75 
 Widget C             │     890.25 │     220.00 
```


## Format currency with prefix and conditional coloring {#currency}

Combine prefix formatting with postprocessors for currency display:

```python
from craftable import get_table

def color_by_value(original, text, row, col_idx):
    try:
        val = float(original)
        if val < 0:
            return f"\x1b[31m{text}\x1b[0m"  # red
        elif val > 1000:
            return f"\x1b[32m{text}\x1b[0m"  # green
    except (ValueError, TypeError):
        pass
    return text

transactions = [
    ["Groceries", -152.43],
    ["Paycheck", 2500.00],
    ["Utilities", -89.12],
    ["Bonus", 1500.00],
]

print(get_table(
    transactions,
    header_row=["Description", "Amount"],
    col_defs=["", "<$ (>10.2f)"],
    postprocessors=[None, color_by_value],
))
```

Example output (colors removed for clarity):

```text
 Description │   Amount
─────────────┼────────────
 Groceries   │ $  -152.43
 Paycheck    │ $  2500.00
 Utilities   │ $   -89.12
 Bonus       │ $  1500.00
```


## Build a progress/status indicator table {#icons}

Use Unicode characters and postprocessors for visual status:

```python
from craftable import get_table

def status_icon(original, text, row, col_idx):
    status_map = {
        "done": "✓",
        "pending": "⧗",
        "failed": "✗",
    }
    return status_map.get(original, text)

tasks = [
    ["Deploy to prod", "done"],
    ["Run tests", "done"],
    ["Update docs", "pending"],
    ["Code review", "failed"],
]

print(get_table(
    tasks,
    header_row=["Task", "Status"],
    col_defs=["", "^8"],
    postprocessors=[None, status_icon],
))
```

Example output:

```text
      Task      │  Status
────────────────┼──────────
 Deploy to prod │ ✓
 Run tests      │ ✓
 Update docs    │ ⧗
 Code review    │ ✗
```


## Convert dates with preprocessor, color with postprocessor {#dates}

Chain preprocessing (for formatting) and postprocessing (for decoration):

```python
from craftable import get_table
from datetime import date, timedelta

def format_date(val, row, col_idx):
    if isinstance(val, date):
        return val.strftime("%Y-%m-%d")
    return val

def highlight_recent(original, text, row, col_idx):
    if isinstance(original, date):
        days_ago = (date.today() - original).days
        if days_ago < 7:
            return f"\x1b[1m{text}\x1b[0m"  # bold
    return text

events = [
    ["Meeting", date.today() - timedelta(days=2)],
    ["Launch", date.today() - timedelta(days=30)],
    ["Review", date.today()],
]

print(get_table(
    events,
    header_row=["Event", "Date"],
    col_defs=["<20", "<12"],
    preprocessors=[None, format_date],
    postprocessors=[None, highlight_recent],
))
```

Example output (bold removed for clarity):

```text
        Event         │     Date     
──────────────────────┼──────────────
 Meeting              │ 2025-11-13   
 Launch               │ 2025-10-16   
 Review               │ 2025-11-15   
```


## Generate a multi-level grouped summary {#hierarchy}

Build hierarchical data with visual indentation:

```python
from craftable import get_table

def indent_category(value, row, col_idx):
    if isinstance(value, str) and value.startswith("  "):
        return f"  └─ {value.strip()}"
    return value

data = [
    ["Electronics", None, 5420.00],
    ["  Laptops", 3, 3200.00],
    ["  Monitors", 5, 2220.00],
    ["Furniture", None, 1890.50],
    ["  Desks", 2, 890.00],
    ["  Chairs", 4, 1000.50],
]

print(get_table(
    data,
    header_row=["Category", "Qty", "Total"],
    col_defs=["<25", ">5", ">10.2f"],
    preprocessors=[indent_category, None, None],
))
```

Example output:

```text
          Category         │  Qty  │   Total
───────────────────────────┼───────┼────────────
 Electronics               │       │    5420.00
   └─ Laptops              │     3 │    3200.00
   └─ Monitors             │     5 │    2220.00
 Furniture                 │       │    1890.50
   └─ Desks                │     2 │     890.00
   └─ Chairs               │     4 │    1000.50
```


## Build a linked styles overview table (Markdown) {#markdown-table}

Generate a Markdown table with postprocessor-added links to page anchors:

```python
from itertools import zip_longest
from craftable import get_table
from craftable.styles import MarkdownStyle

display = [
    "NoBorderScreenStyle",
    "BasicScreenStyle",
    "RoundedBorderScreenStyle",
    "MarkdownStyle",
    "ASCIIStyle",
]
export = [
    "XlsxStyle",
    "OdsStyle",
    "OdtStyle",
    "DocxStyle",
    "RtfStyle",
]

rows = [list(pair) for pair in zip_longest(display, export)]

anchor_map = {
    "NoBorderScreenStyle": "style-noborder",
    "BasicScreenStyle": "style-basic",
    "RoundedBorderScreenStyle": "style-rounded",
    "MarkdownStyle": "style-markdown",
    "ASCIIStyle": "style-ascii",
    "XlsxStyle": "style-xlsx",
    "OdsStyle": "style-ods",
    "OdtStyle": "style-odt",
    "DocxStyle": "style-docx",
    "RtfStyle": "style-rtf",
}

def linkify(original, text, row, col_idx):
    if not text.strip():
        return text
    anchor = anchor_map.get(original, "")
    anchor_text = f"[{original}](#{anchor})" if anchor else original
    return text.replace(original, anchor_text)

print(get_table(
    rows,
    header_row=["Display Styles", "Export Styles"],
    style=MarkdownStyle(),
    postprocessors=[linkify,linkify],
))
```

Example output (raw Markdown table):

```text
|      Display Styles      | Export Styles |
| ------------------------ | ------------- |
| [NoBorderScreenStyle](#style-noborder)      | [XlsxStyle](#style-xlsx)     |
| [BasicScreenStyle](#style-basic)         | [OdsStyle](#style-ods)      |
| [RoundedBorderScreenStyle](#style-rounded) | [OdtStyle](#style-odt)      |
| [MarkdownStyle](#style-markdown)            | [DocxStyle](#style-docx)     |
| [ASCIIStyle](#style-ascii)               | [RtfStyle](#style-rtf)      |
```

See this table rendered on the [styles page](styles.md).


## Truncate long log messages for compact output {#truncate}

Use the truncate flag for log-friendly tables:

```python
from craftable import get_table
from craftable.styles import NoBorderScreenStyle

logs = [
    ["2025-01-15 10:23:45", "INFO", "Application started successfully"],
    ["2025-01-15 10:24:12", "WARN", "Database connection pool is running low on available connections"],
    ["2025-01-15 10:25:03", "ERROR", "Failed to process request: timeout exceeded after 30 seconds"],
]

print(get_table(
    logs,
    header_row=["Timestamp", "Level", "Message"],
    col_defs=["<19", "<6", "40T"],  # T flag = truncate with ellipsis
    style=NoBorderScreenStyle(),
))
```

Example output:

```text
      Timestamp      │ Level  │                 Message
─────────────────────┼────────┼───────────────────────────────────────────
 2025-01-15 10:23:45 │ INFO   │ Application started successfully
 2025-01-15 10:24:12 │ WARN   │ Database connection pool is running low…
 2025-01-15 10:25:03 │ ERROR  │ Failed to process request: timeout exce…
```


## Long log messages for without wrapping {#log}

Use an appropriate style and set `lazy_end=True`:

```python
from craftable import get_table
from craftable.styles import ASCIIStyle

logs = [
    ["2025-01-15 10:23:45", "INFO", "Application started successfully"],
    ["2025-01-15 10:24:12", "WARN", "Database connection pool is running low on available connections"],
    ["2025-01-15 10:25:03", "ERROR", "Failed to process request: timeout exceeded after 30 seconds"],
]

print(get_table(
    logs,
    header_row=["Timestamp", "Level", "Message"],
    style=ASCIIStyle(),
    lazy_end=True,
))
```

Example output:

```text
+---------------------+-------+-------------------------------------------------------------------
|      Timestamp      | Level |                             Message
+---------------------+-------+-------------------------------------------------------------------
| 2025-01-15 10:23:45 | INFO  | Application started successfully
| 2025-01-15 10:24:12 | WARN  | Database connection pool is running low on available connections
| 2025-01-15 10:25:03 | ERROR | Failed to process request: timeout exceeded after 30 seconds
+---------------------+-------+-------------------------------------------------------------------
```


## Pivot data from columnar to row format {#pivot}

Transform a mapping-of-lists into a transposed table:

```python
from craftable import get_table
from craftable.adapters import from_mapping_of_lists

stats = {
    "metric": ["CPU %", "Memory MB", "Disk I/O"],
    "server_a": [45.2, 2048, 1250],
    "server_b": [78.9, 4096, 3420],
    "server_c": [23.1, 1024, 890],
}

rows, headers = from_mapping_of_lists(stats)
print(get_table(rows, header_row=headers, col_defs=["<12", ">10", ">10", ">10"]))
```

Example output:

```text
    metric    │  server_a  │  server_b  │  server_c  
──────────────┼────────────┼────────────┼────────────
 CPU %        │       45.2 │       78.9 │       23.1 
 Memory MB    │       2048 │       4096 │       1024 
 Disk I/O     │       1250 │       3420 │        890 
```


## Create a comparison table with trend indicators {#trend}

Show before/after comparisons with visual markers:

```python
from craftable import get_table

def trend_arrow(val, row, col_idx):
    """Add up/down arrows based on change from prior column."""
    trend = " "
    try:
        prior_val = row[col_idx - 1]
        if val > prior_val:
            trend = "↑"
        elif val < prior_val:
            trend = "↓"
    except Exception:
        pass

    return f"{val} {trend}"


# Manually add trend info to data
comparisons = [
    ["Response time (ms)", "245", "198"],
    ["Error rate (%)", "2.1", "0.8"],
    ["Throughput (req/s)", "1200", "1450"],
]

print(
    get_table(
        comparisons,
        header_row=["Metric", "Before", "After"],
        col_defs=["<20", ">10", ">10"],
        preprocessors=[None, None, trend_arrow],
    )
)
```

Example output:

```text
        Metric        │   Before   │   After    
──────────────────────┼────────────┼────────────
 Response time (ms)   │        245 │      198 ↓ 
 Error rate (%)       │        2.1 │      0.8 ↓ 
 Throughput (req/s)   │       1200 │     1450 ↑ 
```


## Display percentages with progress bars {#progress-bars}

Use Unicode block characters for inline progress visualization:

```python
from craftable import get_table

def progress_bar(val, row, col_idx):
    try:
        pct = float(val)
        bars = int(pct / 10)
        return "█" * bars + "░" * (10 - bars) + f" {val}%"
    except (ValueError, TypeError):
        return val

completion = [
    ["Backend API", 85],
    ["Frontend UI", 60],
    ["Database migrations", 100],
    ["Documentation", 45],
]

print(get_table(
    completion,
    header_row=["Component", "Progress"],
    preprocessors=[None, progress_bar],
))
```

Example output:

```text
      Component      │     Progress
─────────────────────┼─────────────────
 Backend API         │ ████████░░ 85%
 Frontend UI         │ ██████░░░░ 60%
 Database migrations │ ██████████ 100%
 Documentation       │ ████░░░░░░ 45%
```
