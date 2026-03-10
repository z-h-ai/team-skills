---
name: markdown-to-pdf
description: Convert Markdown documents to PDF format with full formatting preservation including tables, code blocks with syntax highlighting, images, links, and custom page layout. Use when Claude needs to convert .md or .markdown files to PDF documents, whether for technical documentation, reports, presentations, or any text content that needs to be in PDF format. Supports all common markdown features and allows customization of page size, margins, and fonts.
---

# Markdown to PDF Converter

## Overview

Convert Markdown files to professional PDF documents while preserving formatting, tables, code blocks, images, and links. This skill uses pandoc with LaTeX engines for high-quality PDF generation with customizable page layout.

## Quick Start

Basic conversion:

```bash
scripts/convert_md_to_pdf.py input.md
```

This creates `input.pdf` in the same directory with all markdown formatting preserved.

## Common Conversion Patterns

### Convert with Specific Output Path

```bash
scripts/convert_md_to_pdf.py input.md -o /path/to/output.pdf
```

### Include Table of Contents

```bash
scripts/convert_md_to_pdf.py input.md --toc
```

Generates an automatic TOC from all headers in the markdown.

### Custom Code Highlighting

Choose from multiple syntax highlighting themes:

```bash
scripts/convert_md_to_pdf.py input.md --highlight-style tango
```

Available styles: `pygments` (default), `tango`, `espresso`, `zenburn`, `kate`, `monochrome`, `breezedark`, `haddock`

### Custom Page Layout

Customize margins, font size, and paper size:

```bash
scripts/convert_md_to_pdf.py input.md --margin 0.75in --font-size 12pt --paper-size letter
```

**Paper sizes:** `a4` (default), `letter`, `a5`, `b5`, `executive`, `legal`

**Font sizes:** `10pt`, `11pt` (default), `12pt`, `14pt`, etc.

**Margins:** Any valid LaTeX dimension (e.g., `1in`, `2cm`, `20mm`)

### Choose PDF Engine

Different engines offer different features:

```bash
scripts/convert_md_to_pdf.py input.md --pdf-engine pdflatex
```

**Available engines:**
- `xelatex` (default) - Best Unicode and font support
- `pdflatex` - Fast, good for English documents
- `lualatex` - Modern, good for complex layouts
- `wkhtmltopdf` - HTML-based rendering

### Combined Options

```bash
scripts/convert_md_to_pdf.py report.md \
  -o final_report.pdf \
  --toc \
  --highlight-style pygments \
  --margin 0.75in \
  --font-size 12pt \
  --paper-size letter
```

## Workflow for User Requests

When a user asks to convert markdown to PDF:

1. **Identify the source file(s)** - Get the markdown file path(s)
2. **Check for layout requirements** - Ask about page size, margins, TOC
3. **Verify dependencies** - The script checks for pandoc and LaTeX
4. **Run the conversion** - Use the script with appropriate options
5. **Confirm success** - Report the output file location

### Example User Interaction

**User:** "Convert this markdown file to PDF"

**Claude:**
1. Identifies the markdown file
2. Runs: `scripts/convert_md_to_pdf.py document.md`
3. Confirms: "Converted document.md to document.pdf"

**User:** "Convert with table of contents and letter size paper"

**Claude:**
1. Runs: `scripts/convert_md_to_pdf.py document.md --toc --paper-size letter`
2. Confirms conversion with specified options

## Supported Markdown Features

The conversion preserves:

- **Headers** (H1-H6) → PDF heading styles with hierarchy
- **Text formatting** (bold, italic, strikethrough, inline code)
- **Line breaks** → Single newlines are preserved as hard line breaks
- **Lists** (ordered, unordered, nested)
- **Tables** → Professional PDF tables
- **Code blocks** → Formatted with syntax highlighting
- **Images** (local and remote) → Embedded in PDF
- **Links** → Clickable hyperlinks
- **Blockquotes** → Formatted quotes
- **Horizontal rules** → Section dividers
- **Mathematical equations** → LaTeX math rendering (e.g., `$E=mc^2$`)

For detailed markdown syntax examples, see [references/conversion_guide.md](references/conversion_guide.md).

## Dependencies

**Required:**
1. **pandoc** - Document converter
2. **LaTeX distribution** - For PDF generation (xelatex, pdflatex, etc.)

The script automatically checks for pandoc and provides installation instructions if missing.

### Installing Dependencies

**macOS:**
```bash
brew install pandoc
brew install --cask mactex-no-gui  # or mactex for full distribution
```

**Ubuntu/Debian:**
```bash
sudo apt-get install pandoc
sudo apt-get install texlive-xetex texlive-fonts-recommended texlive-latex-extra
```

**Windows:**
- Download pandoc from https://pandoc.org/installing.html
- Download MiKTeX from https://miktex.org/download

## Troubleshooting

**Pandoc not found:**
- Run the script - it will show installation instructions
- After installing, verify with: `pandoc --version`

**LaTeX errors:**
- Install a LaTeX distribution (see Dependencies above)
- Try a different PDF engine: `--pdf-engine pdflatex`
- For simple documents, try: `--pdf-engine wkhtmltopdf` (no LaTeX required)

**Images not appearing:**
- Check that image paths are correct (relative or absolute)
- Remote images require internet connection
- Some PDF engines handle images differently

**Unicode/font issues:**
- Use `--pdf-engine xelatex` (default) for best Unicode support
- Ensure your system has the required fonts installed

**Code highlighting not working:**
- Try different `--highlight-style` options
- Some styles work better with specific languages

**Page layout issues:**
- Adjust margins: `--margin 0.5in` or `--margin 2cm`
- Change font size: `--font-size 10pt` or `--font-size 12pt`
- Try different paper size: `--paper-size letter`

## Advanced Usage

### Custom LaTeX Headers

For advanced users who need custom LaTeX configuration, you can create a YAML metadata block at the top of your markdown:

```markdown
---
title: "My Document"
author: "Author Name"
date: "2026-01-07"
geometry: margin=1in
fontsize: 12pt
---

# Your content here
```

### Batch Conversion

Convert multiple files:

```bash
for file in *.md; do
  scripts/convert_md_to_pdf.py "$file" --toc --highlight-style pygments
done
```

## Resources

### scripts/convert_md_to_pdf.py
Main conversion script with full functionality and error handling.

### references/conversion_guide.md
Detailed guide on supported markdown features, syntax examples, page layout options, and conversion limitations. Load when users need detailed information about markdown support or encounter conversion issues.
