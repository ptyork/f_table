"""Basic RTF export test."""

from craftable import export_table
from craftable.styles import RtfStyle


def test_rtf_write_to_file(tmp_path):
    rows = [["A", 1], ["B", 2]]
    headers = ["Col1", "Col2"]
    path = tmp_path / "table.rtf"
    out = export_table(rows, header_row=headers, style=RtfStyle(), file=path)
    assert out == path
    assert path.exists() and path.stat().st_size > 0
    content = path.read_text(encoding="utf-8")
    # Contains RTF header and table constructs
    assert "{\\rtf1" in content
    assert "\\trowd" in content
    assert "\\cell" in content
    assert "\\row" in content
    # header likely bold
    assert "\\b" in content
