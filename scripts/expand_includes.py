#!/usr/bin/env python3
"""
Expand !include directives in YAML files
Usage: python3 expand_includes.py input.yml > output.yml
"""
import sys
import re
from pathlib import Path


def expand_includes(content: str, base_path: Path) -> str:
    """Expand !include directives recursively"""

    def replace_include(match):
        include_path = base_path / match.group(1)
        if not include_path.exists():
            print(f"Warning: {include_path} not found", file=sys.stderr)
            return match.group(0)

        included = include_path.read_text().rstrip('\n')
        # Recursively expand includes
        expanded = expand_includes(included, include_path.parent)

        # Get the line containing !include
        line_start = content.rfind('\n', 0, match.start()) + 1
        line_content = content[line_start:match.start()]

        # Determine context: mapping key or list item
        is_list_item = '- ' in line_content

        if is_list_item:
            # For list items (- !include ...), the dash provides base indentation
            # Get indentation after the dash
            base_indent = len(line_content) - len(line_content.lstrip())
            indent = base_indent + 2  # 2 spaces after the dash
        else:
            # For mapping values (key: !include ...), we need newline + indentation
            # Get key indentation and add 2 spaces
            base_indent = len(line_content) - len(line_content.lstrip())
            indent = base_indent + 2
            # Prepend newline for mapping context
            expanded = '\n' + expanded

        # Add indentation to each line of the included content
        lines = expanded.split('\n')
        indented_lines = []
        for i, line in enumerate(lines):
            if i == 0 and not is_list_item:
                # First line after newline in mapping context
                indented_lines.append(' ' * indent + line if line else '')
            elif i == 0:
                # First line in list context (no extra indent for first line)
                indented_lines.append(line)
            else:
                # Subsequent lines get full indentation
                indented_lines.append(' ' * indent + line if line else '')

        return '\n'.join(indented_lines)

    return re.sub(
        r'!include\s+([^\s\n]+)',
        replace_include,
        content
    )


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 expand_includes.py input.yml", file=sys.stderr)
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: {input_file} not found", file=sys.stderr)
        sys.exit(1)
    
    content = input_file.read_text()
    expanded = expand_includes(content, input_file.parent)
    print(expanded)
