#!/usr/bin/env python3
"""
Fix Plugin Syntax Errors
Repairs indentation and import placement issues in Vzoel Fox's plugins
"""

import os
import re
from pathlib import Path

def fix_import_placement(content, filename):
    """Fix misplaced imports that break indentation"""
    
    # Check if imports are misplaced inside functions
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    # Find the correct place for imports (after initial docstring and existing imports)
    import_insert_point = 0
    
    # Skip docstring
    in_docstring = False
    for idx, line in enumerate(lines):
        if '"""' in line:
            if not in_docstring:
                in_docstring = True
            else:
                in_docstring = False
                import_insert_point = idx + 1
                break
    
    # Find where existing imports end
    for idx in range(import_insert_point, len(lines)):
        line = lines[idx].strip()
        if line.startswith(('import ', 'from ')) and 'import' in line:
            import_insert_point = idx + 1
        elif line and not line.startswith('#') and not line.startswith(('import ', 'from ')):
            break
    
    # Look for misplaced imports and collect them
    misplaced_imports = []
    new_lines = []
    
    for idx, line in enumerate(lines):
        # Check if this is a misplaced import (has leading whitespace and is inside a function)
        if (line.strip().startswith(('import sys', '# Add parent directory', 'sys.path.append', '# Import comment system', 'from plugins.comments')) 
            and line.startswith('    ')):  # Has indentation
            
            # This is a misplaced import, skip it
            if line.strip() not in [l.strip() for l in misplaced_imports]:
                misplaced_imports.append(line.strip())
            continue
        else:
            new_lines.append(line)
    
    # Insert the collected imports at the correct location
    if misplaced_imports:
        # Add imports after the existing import section
        result_lines = new_lines[:import_insert_point]
        
        # Add the collected imports
        for imp in misplaced_imports:
            if imp not in [l.strip() for l in result_lines]:
                result_lines.append(imp)
        
        # Add a blank line after imports
        if result_lines and result_lines[-1].strip():
            result_lines.append('')
        
        # Add the rest of the file
        result_lines.extend(new_lines[import_insert_point:])
        
        return '\n'.join(result_lines)
    
    return content

def fix_file(file_path):
    """Fix syntax issues in a plugin file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix import placement
        content = fix_import_placement(content, file_path.name)
        
        # Remove empty lines that might cause issues
        lines = content.split('\n')
        cleaned_lines = []
        
        for i, line in enumerate(lines):
            # Skip excessive empty lines
            if line.strip() == '' and i > 0 and lines[i-1].strip() == '':
                continue
            cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed {file_path.name}")
            return True
        else:
            print(f"⏭️  No fixes needed for {file_path.name}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {file_path.name}: {e}")
        return False

def main():
    """Main fix function"""
    print("🔧 Vzoel Fox's Plugin Syntax Fix")
    print("==============================")
    
    # List of plugins that had errors
    error_plugins = [
        'limit.py', 'tagall.py', 'vc.py', 'pizol.py', 
        'idchecker.py', 'system.py', 'fun.py', 'blacklist.py', 'gcast.py'
    ]
    
    plugins_dir = Path("plugins")
    fixed_count = 0
    
    for plugin_name in error_plugins:
        file_path = plugins_dir / plugin_name
        if file_path.exists():
            if fix_file(file_path):
                fixed_count += 1
        else:
            print(f"❌ Plugin not found: {plugin_name}")
    
    print(f"\n📊 Fix Summary:")
    print(f"Processed: {len(error_plugins)}")
    print(f"Fixed: {fixed_count}")
    
    if fixed_count > 0:
        print(f"\n🎉 Fixed {fixed_count} plugin syntax errors!")
        print("Try running the client again.")
    else:
        print("\n✅ All plugins were already correct!")

if __name__ == "__main__":
    main()