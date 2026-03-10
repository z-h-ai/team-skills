# Markdown to DOCX Conversion Reference

## Supported Markdown Features

### Headers

```markdown
# H1 Header
## H2 Header
### H3 Header
```

Converted to Word heading styles (Heading 1, Heading 2, etc.)

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

Tables are converted to native Word tables with proper formatting.

### Code Blocks

````markdown
```python
def hello_world():
    print("Hello, World!")
```
````

Code blocks are converted with syntax highlighting (if highlight style is specified).

### Images

```markdown
![Alt text](path/to/image.png)
![Remote image](https://example.com/image.png)
```

Both local and remote images are embedded in the DOCX file.

### Links

```markdown
[Link text](https://example.com)
```

Converted to clickable hyperlinks in Word.

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

## Custom Styling with Reference Documents

To apply consistent styling across conversions:

1. Create a template DOCX with your desired styles:
   - Open Word and set up fonts, colors, heading styles
   - Save as `template.docx`

2. Use it in conversions:
   ```bash
   convert_md_to_docx.py input.md --reference-doc template.docx
   ```

The reference document's styles will be applied to the converted content.

## Table of Contents

To include an automatic table of contents:

```bash
convert_md_to_docx.py input.md --toc
```

The TOC is generated from all headers in the markdown file.

## Limitations

- Complex HTML within markdown may not convert perfectly
- Some pandoc-specific markdown extensions might not be supported
- Mathematical equations require LaTeX syntax (e.g., `$E=mc^2$`)
- Nested tables are not well supported in DOCX format
