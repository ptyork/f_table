# API Reference

This section provides comprehensive API documentation for craftable, including functions, classes, styles, and exceptions.

## Core Functions

**[Functions](functions.md)** — Primary table generation functions

Complete API documentation for the main functions used to generate and export tables:

- `get_table()` — Generate a complete formatted table as a string
- `export_table()` — Render and optionally write tables to files
- `get_table_row()` — Generate a single formatted table row
- `get_table_header()` — Generate just the header section of a table

## Data Structures

**[Classes](classes.md)** — Column definition classes

Documentation for classes used to configure column formatting and behavior:

- `ColDef` — Column definition class for controlling width, alignment, formatting, and more
- `ColDefList` — Collection of column definitions with automatic sizing and adjustment methods

## Error Handling

**[Exceptions](exceptions.md)** — Custom exceptions

Documentation for exceptions that may be raised during table generation:

- `InvalidTableError` — Raised when table structure or configuration is invalid
- `InvalidColDefError` — Raised when column definition format is invalid

## Styles

### Text Output Styles

**[Text Styles](text_styles.md)** — Styles for terminal and text output

Documentation for built-in styles that generate text-based table output for terminals, logs, and plain text files:

- `NoBorderScreenStyle` — Minimal, compact style with no borders (default)
- `BasicScreenStyle` — Classic box-drawing characters with borders
- `RoundedBorderScreenStyle` — Modern rounded corners with Unicode characters
- `MarkdownStyle` — GitHub-flavored Markdown table format
- `ASCIIStyle` — 7-bit ASCII compatible characters for maximum compatibility
- `TableStyle` — Base class for creating custom text-based styles
- `BoxChars` — Helper class for defining box-drawing character sets

### Document Export Styles

**[Document Styles](doc_styles.md)** — Styles for document file formats

Documentation for styles that export tables to common document formats:

- `DocxStyle` — Microsoft Word (.docx) document format
- `XlsxStyle` — Microsoft Excel (.xlsx) spreadsheet format with native type support
- `OdtStyle` — OpenDocument Text (.odt) format
- `OdsStyle` — OpenDocument Spreadsheet (.ods) format with native type support
- `RtfStyle` — Rich Text Format (.rtf) for universal document compatibility

These document styles support features like native numeric types, date handling, and format-specific styling options.
