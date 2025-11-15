from pprint import pprint
from datetime import date, datetime
from craftable import (
    get_table,
    ColDef,
    BasicScreenStyle,
    MarkdownStyle,
    NoBorderScreenStyle,
    RoundedBorderScreenStyle,
)

def l():
    print("\n" + "*" * 80 + "\n")


from rich.console import Console

def fmt_date(value):
    if isinstance(value, date):
        try:
            return value.strftime("%a, %b %d, %Y")
        except Exception as e:
            print(f"Error formatting date: {e}")
    return value

def fmt_currency(original, text):
    try:
        value = float(original)
        if value < 0:
            return f"[red]{text}[/red]"
    except Exception:
        pass
    return text

data = [
    [ "Lowe's", -54.25, date(2025, 6, 15) ],
    [ "Walmart", -62.83, date(2025, 6, 17) ],
    [ "Petsmart", -35.4, datetime(2025, 6, 17) ],
    [ "Deposit", 1500.0, date(2025, 6, 18) ],
]

console = Console()
console.print(get_table(
    data,
    header_row = [ "Transaction", "Amount", "Date" ],
    col_defs = [ "<A", "<$ (>10.2f)", "<" ],
    preprocessors = [ None, None, fmt_date ],
    postprocessors = [ None, fmt_currency, None ],
    style=RoundedBorderScreenStyle(),
    table_width=60,
))

exit()



data = [
    ["Alice", 147000, .035, "Engineer"],
    ["Bob", 88000, .0433, "Designer"],
]

print(get_table(
    data,
    header_row=["Name", "Salary", "Adj", "Title"],
    col_defs=["A","<$ (,)", ">.2%", "A"],
    table_width=50,
))


data = [
    ["Apple", 1.99, 12, ],
    ["Banana", 1.49, 10, ],
    ["Egg", 13.99, 2, ],
]

print(get_table(
    data,
    header_row=["Product", "Price", "Weight"],
    col_defs=["A","<$ (>8.2f)", "(^8) oz"],
    table_width=40,
    style=RoundedBorderScreenStyle(),
))
print(get_table(
    data,
    header_row=["Product", "Price", "Weight"],
    col_defs=["A","<$ (<8.2f)", "(<8) oz"],
    table_width=40,
    style=RoundedBorderScreenStyle(),
))
print(get_table(
    data,
    header_row=["Product", "Price", "Weight"],
    col_defs=["A","$ (8.2f)", "(>8) oz"],
    table_width=40,
    style=RoundedBorderScreenStyle(),
))
print(get_table(
    data,
    header_row=["Product", "Price", "Weight"],
    col_defs=["A","$ (>8.2f)", "(<8)> oz"],
    table_width=40,
    style=RoundedBorderScreenStyle(),
))
print(get_table(
    data,
    header_row=["Product", "Price", "Weight"],
    col_defs=["A","<$ (>15.2f) boo", "(<8)> oz"],
    table_width=50,
    style=RoundedBorderScreenStyle(),
))
print(get_table(
    data,
    header_row=["Product", "Price", "Weight"],
    col_defs=["A","$ (<15.2f)> boo", "(<8)> oz"],
    table_width=50,
    style=RoundedBorderScreenStyle(),
))



exit()

variable_table = [
    ["abc", "123", "123 123 123"],
    ["abc", "123 123", "123 123 123 123"],
    ["abc", "123", "123 123 123 123 123"],
    ["abc", "123 123", "123 123"],
]
variable_table_head = ["col 1", "col 2", "col 3"]

wrapping_table = [
    [
        "a",
        "123",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
        "sed do eiusmod tempor incididunt ut labore et dolore magna "
        "aliqua. Ut enim ad minim veniam, quis nostrud exercitation "
        "ullamco laboris nisi ut aliquip ex ea commodo consequat.",
    ],
    [
        "a",
        "123",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
        "sed do eiusmod tempor incididunt ut labore et dolore magna "
        "aliqua. Ut enim ad minim veniam, quis nostrud exercitation "
        "ullamco laboris nisi ut aliquip ex ea commodo consequat.",
    ],
]

embedded_newline_table = [
    [
        "This is a line",
        "This is a line that already has newlines in it.\n"
        "  * will it wrap?\n"
        "  * will it indent properly?",
    ],
    [
        "This is a line",
        "This is a line that already has newlines in it.\n"
        "  * will it wrap?\n"
        "  * will it indent properly?",
    ],
    [
        "This is a line",
        "This is a line that already has newlines in it.\n"
        "  * will it wrap?\n"
        "  * will it indent properly?",
    ],
]
embedded_newline_table_head = ["LINE", "LINE WITH NEWLINES"]

jagged_table = [
    ["abc", "123", ],
    ["abc", "123", 789, ],
    ["abc", ],
]

print(get_table(jagged_table))
l()


print(get_table(variable_table))
l()
print(get_table(variable_table, variable_table_head))
l()
print(get_table(wrapping_table))
l()

print(get_table(variable_table, style=BasicScreenStyle(), lazy_end=True))
l()
print(
    get_table(
        variable_table,
        variable_table_head,
        style=BasicScreenStyle(),
        col_defs=["10", "^10T", ">30"],
    )
)
l()
print(
    get_table(
        wrapping_table, style=BasicScreenStyle(), col_defs=["10", "^10", "30T"]
    )
)
l()
print(
    get_table(
        wrapping_table, style=BasicScreenStyle(), col_defs=["10", "^10", "70"]
    )
)
l()
print(
    get_table(
        wrapping_table,
        style=BasicScreenStyle(),
        col_defs=["", "^", ">A"],
        table_width=50,
    )
)
l()

print(get_table(variable_table, style=MarkdownStyle(), lazy_end=True))
l()
print(
    get_table(
        variable_table,
        variable_table_head,
        style=MarkdownStyle(),
        col_defs=["", "^", ""],
    )
)
l()
print(
    get_table(
        variable_table,
        variable_table_head,
        style=MarkdownStyle(),
        col_defs=["", "^", ""],
        header_defs=["", "", "<"],
    )
)
l()
print(get_table(wrapping_table, style=MarkdownStyle(), table_width=80))
l()
print(get_table(wrapping_table, style=MarkdownStyle(), lazy_end=True))
l()

print(get_table(embedded_newline_table))
l()
print(get_table(embedded_newline_table, table_width=50))
l()
print(get_table(embedded_newline_table, style=NoBorderScreenStyle()))
l()
print(get_table(embedded_newline_table, style=RoundedBorderScreenStyle()))
l()
print(
    get_table(
        embedded_newline_table,
        header_row=embedded_newline_table_head,
        style=RoundedBorderScreenStyle(),
        separate_rows=True,
    )
)
l()
