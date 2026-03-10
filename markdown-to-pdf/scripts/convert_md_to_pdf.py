#!/usr/bin/env python3
"""
Convert Markdown files to PDF format with support for:
- Tables
- Code blocks with syntax highlighting
- Images and links
- Custom styling
- Page layout options
"""

import argparse
import subprocess
import sys
from pathlib import Path


def check_pandoc_installed():
    """Check if pandoc is installed on the system."""
    try:
        result = subprocess.run(
            ['pandoc', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def convert_markdown_to_pdf(
    input_file: str,
    output_file: str = None,
    toc: bool = False,
    highlight_style: str = "pygments",
    pdf_engine: str = "xelatex",
    margin: str = "1in",
    font_size: str = "11pt",
    paper_size: str = "a4"
):
    """
    Convert a Markdown file to PDF using pandoc.

    Args:
        input_file: Path to input markdown file
        output_file: Path to output pdf file (optional)
        toc: Include table of contents (default: False)
        highlight_style: Code highlighting style (default: pygments)
        pdf_engine: PDF engine to use (default: xelatex)
        margin: Page margins (default: 1in)
        font_size: Base font size (default: 11pt)
        paper_size: Paper size (default: a4)
    """
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
        sys.exit(1)

    if not input_path.suffix.lower() in ['.md', '.markdown']:
        print(f"Warning: Input file '{input_file}' doesn't have .md extension", file=sys.stderr)

    # Generate output filename if not provided
    if output_file is None:
        output_file = input_path.with_suffix('.pdf')

    output_path = Path(output_file)

    # Build pandoc command
    cmd = [
        'pandoc',
        str(input_path),
        '-o', str(output_path),
        '-f', 'markdown+hard_line_breaks',
        '-t', 'pdf',
        f'--pdf-engine={pdf_engine}',
        f'--highlight-style={highlight_style}',
        '--standalone',
        f'-V', f'geometry:margin={margin}',
        f'-V', f'fontsize={font_size}',
        f'-V', f'papersize={paper_size}'
    ]

    # Add table of contents if requested
    if toc:
        cmd.append('--toc')

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Successfully converted '{input_file}' to '{output_path}'")
        return str(output_path)
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion:", file=sys.stderr)
        print(e.stderr, file=sys.stderr)

        # Check for common LaTeX errors
        if 'xelatex' in e.stderr or 'pdflatex' in e.stderr:
            print("\nNote: PDF conversion requires a LaTeX distribution:", file=sys.stderr)
            print("  macOS:   brew install --cask mactex-no-gui", file=sys.stderr)
            print("  Ubuntu:  sudo apt-get install texlive-xetex texlive-fonts-recommended", file=sys.stderr)
            print("  Windows: Download MiKTeX from https://miktex.org/download", file=sys.stderr)

        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Convert Markdown files to PDF format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic conversion
  %(prog)s input.md

  # Specify output file
  %(prog)s input.md -o output.pdf

  # Include table of contents
  %(prog)s input.md --toc

  # Custom code highlighting
  %(prog)s input.md --highlight-style tango

  # Custom page layout
  %(prog)s input.md --margin 0.75in --font-size 12pt --paper-size letter

Available highlight styles:
  pygments, tango, espresso, zenburn, kate, monochrome, breezedark, haddock

Available PDF engines:
  xelatex (default, best Unicode support), pdflatex, lualatex, wkhtmltopdf

Available paper sizes:
  a4 (default), letter, a5, b5, executive, legal
        """
    )

    parser.add_argument(
        'input',
        help='Input Markdown file'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output PDF file (default: input filename with .pdf extension)'
    )

    parser.add_argument(
        '--toc',
        action='store_true',
        help='Include table of contents'
    )

    parser.add_argument(
        '--highlight-style',
        default='pygments',
        choices=['pygments', 'tango', 'espresso', 'zenburn', 'kate', 'monochrome', 'breezedark', 'haddock'],
        help='Code highlighting style (default: pygments)'
    )

    parser.add_argument(
        '--pdf-engine',
        default='xelatex',
        choices=['xelatex', 'pdflatex', 'lualatex', 'wkhtmltopdf'],
        help='PDF engine to use (default: xelatex)'
    )

    parser.add_argument(
        '--margin',
        default='1in',
        help='Page margins (default: 1in)'
    )

    parser.add_argument(
        '--font-size',
        default='11pt',
        help='Base font size (default: 11pt)'
    )

    parser.add_argument(
        '--paper-size',
        default='a4',
        choices=['a4', 'letter', 'a5', 'b5', 'executive', 'legal'],
        help='Paper size (default: a4)'
    )

    args = parser.parse_args()

    # Check if pandoc is installed
    if not check_pandoc_installed():
        print("Error: pandoc is not installed", file=sys.stderr)
        print("\nTo install pandoc:", file=sys.stderr)
        print("  macOS:   brew install pandoc", file=sys.stderr)
        print("  Ubuntu:  sudo apt-get install pandoc", file=sys.stderr)
        print("  Windows: Download from https://pandoc.org/installing.html", file=sys.stderr)
        sys.exit(1)

    convert_markdown_to_pdf(
        input_file=args.input,
        output_file=args.output,
        toc=args.toc,
        highlight_style=args.highlight_style,
        pdf_engine=args.pdf_engine,
        margin=args.margin,
        font_size=args.font_size,
        paper_size=args.paper_size
    )


if __name__ == '__main__':
    main()
