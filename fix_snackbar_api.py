"""
Script to fix all instances of old Flet SnackBar API to new API.
Converts: page.snack_bar = ft.SnackBar(...); page.snack_bar.open = True
To: page.open(ft.SnackBar(...))
"""

import os
import re

def fix_file(filepath):
    """Fix snackbar API in a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    changes = 0

    # Pattern 1: page.snack_bar = ft.SnackBar(...) followed by page.snack_bar.open = True
    # This is the most common pattern
    pattern1 = r'(\s*)([\w.]+)\.snack_bar\s*=\s*(ft\.SnackBar\([^)]+\))\s*\n\s*\2\.snack_bar\.open\s*=\s*True'

    def replacement1(match):
        nonlocal changes
        changes += 1
        indent = match.group(1)
        page_var = match.group(2)
        snackbar = match.group(3)
        return f'{indent}{page_var}.open({snackbar})'

    content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE)

    # Pattern 2: More complex multi-line SnackBars
    pattern2 = r'(\s*)([\w.]+)\.snack_bar\s*=\s*ft\.SnackBar\(\s*\n((?:.*\n)*?)\s*\)\s*\n\s*\2\.snack_bar\.open\s*=\s*True'

    def replacement2(match):
        nonlocal changes
        changes += 1
        indent = match.group(1)
        page_var = match.group(2)
        snackbar_content = match.group(3)
        return f'{indent}{page_var}.open(ft.SnackBar(\n{snackbar_content}\n{indent}))'

    content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE)

    # Pattern 3: Just assigning snackbar then updating separately
    # self.page.snack_bar = snack followed by self.page.snack_bar.open = True
    pattern3 = r'(\s*)([\w.]+)\.snack_bar\s*=\s*(\w+)\s*\n\s*\2\.snack_bar\.open\s*=\s*True'

    def replacement3(match):
        nonlocal changes
        changes += 1
        indent = match.group(1)
        page_var = match.group(2)
        snack_var = match.group(3)
        return f'{indent}{page_var}.open({snack_var})'

    content = re.sub(pattern3, replacement3, content, flags=re.MULTILINE)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return changes
    return 0

def main():
    """Fix all Python files in the app directory."""
    total_changes = 0
    files_changed = 0

    for root, dirs, files in os.walk('app'):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                changes = fix_file(filepath)
                if changes > 0:
                    files_changed += 1
                    total_changes += changes
                    print(f"✓ {filepath}: {changes} fixes")

    print(f"\n{'='*60}")
    print(f"Fixed {total_changes} snackbar instances across {files_changed} files")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
