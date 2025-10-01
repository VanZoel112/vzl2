#!/usr/bin/env python3
"""
Fix markdown bold (**) in all plugin files
Replaces **text** with UPPERCASE TEXT for stability

Author: Vzoel Fox's
"""

import re
from pathlib import Path

def fix_markdown_bold(text):
    """Replace **text** with UPPERCASE TEXT"""

    # Pattern to match **text**
    pattern = r'\*\*([^*]+)\*\*'

    def replace_func(match):
        content = match.group(1)
        # Convert to uppercase
        return content.upper()

    return re.sub(pattern, replace_func, text)


def process_file(file_path):
    """Process a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        fixed_content = fix_markdown_bold(content)

        if fixed_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✓ Fixed: {file_path.name}")
            return True
        else:
            print(f"  Skipped: {file_path.name} (no changes)")
            return False

    except Exception as e:
        print(f"✗ Error processing {file_path.name}: {e}")
        return False


def main():
    """Main function"""
    print("Fixing markdown bold in plugin files...")
    print()

    # Get all Python files in plugins/
    plugins_dir = Path("plugins")
    plugin_files = list(plugins_dir.glob("*.py"))

    # Also check core files I created
    core_dir = Path("core")
    if core_dir.exists():
        core_files = list(core_dir.glob("*.py"))
        plugin_files.extend(core_files)

    fixed_count = 0

    for file_path in plugin_files:
        # Skip __init__.py and emoji_template.py
        if file_path.name in ['__init__.py', 'emoji_template.py']:
            continue

        if process_file(file_path):
            fixed_count += 1

    print()
    print(f"Done! Fixed {fixed_count} files")


if __name__ == "__main__":
    main()
