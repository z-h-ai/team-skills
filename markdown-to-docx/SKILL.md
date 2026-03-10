---
name: markdown-to-docx
description: Convert Markdown documents to DOCX format with full formatting preservation including tables, code blocks with syntax highlighting, images, links, and custom styling. Use when Claude needs to convert .md or .markdown files to Word documents (.docx), whether for technical documentation, reports, notes, or any text content that needs to be in Word format. Supports all common markdown features and allows custom styling through reference documents.
---

# Markdown to DOCX Converter

## Overview

Convert Markdown files to professional DOCX documents while preserving formatting, tables, code blocks, images, and links. This skill uses pandoc for high-quality conversions with optional custom styling.

## Quick Start

Basic conversion:

```bash
scripts/convert_md_to_docx.py input.md
```

This creates `input.docx` in the same directory with all markdown formatting preserved.

## Common Conversion Patterns

### Convert with Specific Output Path

```bash
scripts/convert_md_to_docx.py input.md -o /path/to/output.docx
```

### Apply Custom Styling

Use a reference DOCX template to apply consistent fonts, colors, and styles:

```bash
scripts/convert_md_to_docx.py input.md --reference-doc template.docx
```

The template's styles (fonts, heading formats, colors) will be applied to the converted document.

### Include Table of Contents

```bash
scripts/convert_md_to_docx.py input.md --toc
```

Generates an automatic TOC from all headers in the markdown.

### Custom Code Highlighting

Choose from multiple syntax highlighting themes:

```bash
scripts/convert_md_to_docx.py input.md --highlight-style tango
```

Available styles: `pygments` (default), `tango`, `espresso`, `zenburn`, `kate`, `monochrome`, `breezedark`, `haddock`

### Combined Options

```bash
scripts/convert_md_to_docx.py report.md \
  -o final_report.docx \
  --reference-doc company_template.docx \
  --toc \
  --highlight-style pygments
```

## Workflow for User Requests

When a user asks to convert markdown to docx:

1. **Identify the source file(s)** - Get the markdown file path(s)
2. **Check for styling requirements** - Ask if custom styling is needed
3. **Verify pandoc is available** - The script checks automatically
4. **Run the conversion** - Use the script with appropriate options
5. **Confirm success** - Report the output file location

### Example User Interaction

**User:** "Convert this markdown file to Word format"

**Claude:**
1. Identifies the markdown file
2. Runs: `scripts/convert_md_to_docx.py document.md`
3. Confirms: "Converted document.md to document.docx"

**User:** "Convert with our company template and add a table of contents"

**Claude:**
1. Locates the template file
2. Runs: `scripts/convert_md_to_docx.py document.md --reference-doc template.docx --toc`
3. Confirms conversion with styling applied

## Supported Markdown Features

The conversion preserves:

- **Headers** (H1-H6) → Word heading styles
- **Text formatting** (bold, italic, strikethrough, inline code)
- **Line breaks** → Single newlines are preserved as hard line breaks in DOCX
- **Lists** (ordered, unordered, nested)
- **Tables** → Native Word tables
- **Code blocks** → Formatted with optional syntax highlighting
- **Images** (local and remote) → Embedded in DOCX
- **Links** → Clickable hyperlinks
- **Blockquotes** → Formatted quotes
- **Horizontal rules** → Section dividers

For detailed markdown syntax examples, see [references/conversion_guide.md](references/conversion_guide.md).

## Dependencies

**Required:** pandoc must be installed on the system.

The script automatically checks for pandoc and provides installation instructions if missing:

- **macOS:** `brew install pandoc`
- **Ubuntu/Debian:** `sudo apt-get install pandoc`
- **Windows:** Download from https://pandoc.org/installing.html

## Troubleshooting

**Pandoc not found:**
- Run the script - it will show installation instructions
- After installing, verify with: `pandoc --version`

**Images not appearing:**
- Check that image paths are correct (relative or absolute)
- Remote images require internet connection

**Formatting issues:**
- Use `--reference-doc` with a properly styled template
- Ensure markdown syntax is correct
- Complex nested structures may need simplification

**Code highlighting not working:**
- Try different `--highlight-style` options
- Some styles work better with specific languages

## Creating Custom Style Templates

To create a reference document for consistent styling:

1. Convert any markdown to DOCX first (creates a base document)
2. Open the DOCX in Word
3. Modify styles:
   - Right-click on text → Modify Style
   - Change fonts, colors, spacing for Heading 1, Heading 2, Normal, etc.
4. Save as `template.docx`
5. Use in future conversions: `--reference-doc template.docx`

## Resources

### scripts/convert_md_to_docx.py
Main conversion script with full functionality and error handling.

### references/conversion_guide.md
Detailed guide on supported markdown features, syntax examples, and conversion limitations. Load when users need detailed information about markdown support or encounter conversion issues.
