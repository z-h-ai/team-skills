# Markdown to PDF Conversion Reference

## Supported Markdown Features

### Headers

```markdown
# H1 Header
## H2 Header
### H3 Header
```

Converted to PDF heading styles with proper hierarchy and formatting.

### Text Formatting

```markdown
**bold text**
*italic text*
~~strikethrough~~
`inline code`
```

### Lists

```markdown
- Unordered list
- Another item
  - Nested item

1. Ordered list
2. Second item
```

### Tables

```markdown
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
```

Tables are converted to professional PDF tables with proper borders and alignment.

### Code Blocks

````markdown
```python
def hello_world():
    print("Hello, World!")
```
````

Code blocks are converted with syntax highlighting based on the specified style.

### Images

```markdown
![Alt text](path/to/image.png)
![Remote image](https://example.com/image.png)
```

Both local and remote images are embedded in the PDF file.

### Links

```markdown
[Link text](https://example.com)
```

Converted to clickable hyperlinks in the PDF.

### Blockquotes

```markdown
> This is a blockquote
> Multiple lines
```

### Horizontal Rules

```markdown
---
or
***
```

### Mathematical Equations

LaTeX math syntax is supported:

```markdown
Inline math: $E=mc^2$

Display math:
$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$
```

## Code Highlighting Styles

Available syntax highlighting themes:

- **pygments** - Default, clean and professional
- **tango** - Colorful and vibrant
- **espresso** - Dark theme inspired
- **zenburn** - Low contrast, easy on eyes
- **kate** - KDE editor style
- **monochrome** - Black and white only
- **breezedark** - Modern dark theme
- **haddock** - Haskell documentation style

## PDF Engines

### xelatex (Default)

- Best Unicode support
- Excellent font handling
- Recommended for documents with non-Latin characters
- Supports system fonts

### pdflatex

- Fast compilation
- Good for English documents
- Limited Unicode support
- Standard LaTeX fonts only

### lualatex

- Modern LaTeX engine
- Good Unicode support
- Advanced typography features
- Slower than xelatex

### wkhtmltopdf

- HTML-based rendering
- No LaTeX installation required
- Different rendering approach
- May handle some layouts differently

## Page Layout Options

### Paper Sizes

- **a4** (210mm × 297mm) - Default, international standard
- **letter** (8.5in × 11in) - US standard
- **a5** (148mm × 210mm) - Half of A4
- **b5** (176mm × 250mm) - Between A5 and A4
- **executive** (7.25in × 10.5in) - US executive
- **legal** (8.5in × 14in) - US legal

### Margins

Margins can be specified in various units:

- Inches: `1in`, `0.75in`, `1.5in`
- Centimeters: `2cm`, `2.5cm`
- Millimeters: `20mm`, `25mm`
- Points: `72pt`, `90pt`

Examples:
```bash
--margin 1in          # All margins 1 inch
--margin 0.75in       # All margins 0.75 inches
--margin 2cm          # All margins 2 centimeters
```

### Font Sizes

Common font sizes:
- `10pt` - Small, more content per page
- `11pt` - Default, good readability
- `12pt` - Larger, easier to read
- `14pt` - Very large, presentation style

## Table of Contents

To include an automatic table of contents:

```bash
scripts/convert_md_to_pdf.py input.md --toc
```

The TOC is generated from all headers in the markdown file with clickable links.

## Advanced Customization

### YAML Metadata Block

Add metadata at the top of your markdown file:

```markdown
---
title: "Document Title"
author: "Author Name"
date: "2026-01-07"
geometry: margin=1in
fontsize: 12pt
documentclass: article
---

# Your content starts here
```

### Custom Fonts

With xelatex, you can specify system fonts:

```markdown
---
mainfont: "Times New Roman"
monofont: "Courier New"
---
```

### Page Numbering

```markdown
---
header-includes: |
  \usepackage{fancyhdr}
  \pagestyle{fancy}
  \fancyhead[L]{Document Title}
  \fancyhead[R]{\thepage}
---
```

## Limitations

- Complex HTML within markdown may not convert perfectly
- Some pandoc-specific markdown extensions might not be supported
- Nested tables are not well supported in PDF format
- Very large images may cause page layout issues
- Some LaTeX packages may need to be installed separately
- Mathematical equations require LaTeX syntax (not all markdown math extensions work)

## Best Practices

### For Professional Documents

```bash
scripts/convert_md_to_pdf.py document.md \
  --toc \
  --margin 1in \
  --font-size 11pt \
  --paper-size letter \
  --highlight-style pygments
```

### For Technical Documentation

```bash
scripts/convert_md_to_pdf.py technical.md \
  --toc \
  --margin 0.75in \
  --font-size 10pt \
  --paper-size a4 \
  --highlight-style kate
```

### For Presentations/Reports

```bash
scripts/convert_md_to_pdf.py report.md \
  --toc \
  --margin 1in \
  --font-size 12pt \
  --paper-size letter \
  --highlight-style tango
```

## Troubleshooting Common Issues

### Issue: "xelatex not found"

**Solution:** Install a LaTeX distribution:
- macOS: `brew install --cask mactex-no-gui`
- Ubuntu: `sudo apt-get install texlive-xetex`
- Windows: Install MiKTeX

### Issue: Missing fonts

**Solution:**
- Use xelatex engine (default)
- Install required fonts on your system
- Or specify available fonts in YAML metadata

### Issue: Images too large

**Solution:**
- Resize images before conversion
- Or use markdown image sizing: `![](image.png){width=50%}`

### Issue: Code blocks not highlighted

**Solution:**
- Specify language in code blocks: ` ```python `
- Try different highlight styles
- Ensure pandoc is up to date

### Issue: Unicode characters not displaying

**Solution:**
- Use xelatex engine (default)
- Ensure proper font support
- Check file encoding is UTF-8

## Performance Tips

- Use `pdflatex` for faster compilation of simple documents
- Optimize images before embedding (reduce file size)
- For large documents, consider splitting into chapters
- Use `--pdf-engine wkhtmltopdf` if LaTeX is causing issues
