#!/usr/bin/env python3
"""
Convert Markdown files to DOCX format with support for:
- Tables
- Code blocks with syntax highlighting
- Images and links
- Custom styling
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


def convert_markdown_to_docx(
    input_file: str,
    output_file: str = None,
    reference_doc: str = None,
    toc: bool = False,
    highlight_style: str = "pygments"
):
    """
    Convert a Markdown file to DOCX using pandoc.

    Args:
        input_file: Path to input markdown file
        output_file: Path to output docx file (optional)
        reference_doc: Path to reference docx for styling (optional)
        toc: Include table of contents (default: False)
        highlight_style: Code highlighting style (default: pygments)
    """
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
        sys.exit(1)

    if not input_path.suffix.lower() in ['.md', '.markdown']:
        print(f"Warning: Input file '{input_file}' doesn't have .md extension", file=sys.stderr)

    # Generate output filename if not provided
    if output_file is None:
        output_file = input_path.with_suffix('.docx')

    output_path = Path(output_file)

    # Build pandoc command
    # Using markdown+hard_line_breaks to preserve single line breaks
    cmd = [
        'pandoc',
        str(input_path),
        '-o', str(output_path),
        '-f', 'markdown+hard_line_breaks',
        '-t', 'docx',
        f'--highlight-style={highlight_style}',
        '--standalone'
    ]

    # Add table of contents if requested
    if toc:
        cmd.append('--toc')

    # Add reference document for custom styling
    if reference_doc:
        ref_path = Path(reference_doc)
        if ref_path.exists():
            cmd.extend(['--reference-doc', str(ref_path)])
        else:
            print(f"Warning: Reference document '{reference_doc}' not found, ignoring", file=sys.stderr)

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
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Convert Markdown files to DOCX format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic conversion
  %(prog)s input.md

  # Specify output file
  %(prog)s input.md -o output.docx

  # Use custom styling
  %(prog)s input.md --reference-doc template.docx

  # Include table of contents
  %(prog)s input.md --toc

  # Custom code highlighting
  %(prog)s input.md --highlight-style tango

Available highlight styles:
  pygments, tango, espresso, zenburn, kate, monochrome, breezedark, haddock
        """
    )

    parser.add_argument(
        'input',
        help='Input Markdown file'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output DOCX file (default: input filename with .docx extension)'
    )

    parser.add_argument(
        '--reference-doc',
        help='Reference DOCX file for custom styling'
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

    args = parser.parse_args()

    # Check if pandoc is installed
    if not check_pandoc_installed():
        print("Error: pandoc is not installed", file=sys.stderr)
        print("\nTo install pandoc:", file=sys.stderr)
        print("  macOS:   brew install pandoc", file=sys.stderr)
        print("  Ubuntu:  sudo apt-get install pandoc", file=sys.stderr)
        print("  Windows: Download from https://pandoc.org/installing.html", file=sys.stderr)
        sys.exit(1)

    convert_markdown_to_docx(
        input_file=args.input,
        output_file=args.output,
        reference_doc=args.reference_doc,
        toc=args.toc,
        highlight_style=args.highlight_style
    )


if __name__ == '__main__':
    main()
