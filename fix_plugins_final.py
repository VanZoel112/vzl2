#!/usr/bin/env python3
"""
Final Plugin Fix - Remove all misplaced imports and fix indentation
"""

import os
from pathlib import Path

def fix_plugin_completely(file_path):
    """Completely fix a plugin file by removing misplaced imports"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Find all imports at the top level
        top_imports = set()
        new_lines = []
        
        # Collect existing top-level imports
        in_docstring = False
        docstring_count = 0
        found_first_function = False
        
        for line in lines:
            # Track docstring
            if '"""' in line:
                docstring_count += 1
                if docstring_count >= 2:
                    in_docstring = False
                else:
                    in_docstring = True
            
            # Skip docstring lines
            if in_docstring:
                new_lines.append(line)
                continue
            
            # Check if we've found the first function/class
            if not found_first_function and (line.strip().startswith('async def ') or line.strip().startswith('def ') or line.strip().startswith('class ')):
                found_first_function = True
            
            # If it's an import line and not inside a function
            if (line.strip().startswith(('import ', 'from ')) and 
                'import' in line and 
                not line.startswith('    ') and  # No indentation
                not found_first_function):
                
                # Add to top imports
                top_imports.add(line.strip())
                new_lines.append(line)
                
            # If it's a misplaced import (has indentation), skip it
            elif (line.strip().startswith(('import sys', '# Add parent directory', 'sys.path.append', '# Import comment system', 'from plugins.comments')) and 
                  (line.startswith('    ') or line.startswith('\t'))):
                
                # Skip misplaced imports
                continue
                
            # Keep all other lines
            else:
                new_lines.append(line)
        
        # Add missing imports at the top if not present
        essential_imports = [
            'import sys',
            '',
            '# Add parent directory to path for imports',
            'sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))',
            '',
            '# Import comment system',
            'from plugins.comments import vzoel_comments'
        ]
        
        # Find where to insert imports
        insert_point = 0
        for i, line in enumerate(new_lines):
            if line.strip().startswith(('import ', 'from ')) and 'import' in line:
                insert_point = i + 1
            elif line.strip() and not line.strip().startswith('#') and not line.strip().startswith(('import ', 'from ', '"""', "'''")):
                break
        
        # Check if essential imports are missing
        content_str = '\n'.join(new_lines)
        if 'from plugins.comments import vzoel_comments' not in content_str:
            # Insert essential imports
            for imp in reversed(essential_imports):
                new_lines.insert(insert_point, imp)
        
        # Clean up excessive empty lines
        cleaned_lines = []
        prev_empty = False
        
        for line in new_lines:
            if line.strip() == '':
                if not prev_empty:
                    cleaned_lines.append(line)
                prev_empty = True
            else:
                cleaned_lines.append(line)
                prev_empty = False
        
        new_content = '\n'.join(cleaned_lines)
        
        # Only write if content changed
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Fixed {file_path.name}")
            return True
        else:
            print(f"⏭️  No changes needed for {file_path.name}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {file_path.name}: {e}")
        return False

def main():
    """Main function to fix all plugins"""
    print("🔧 Final Vzoel Fox's Plugin Fix")
    print("=============================")
    
    # List of plugins with errors
    error_plugins = [
        'limit.py', 'tagall.py', 'vc.py', 'pizol.py', 
        'idchecker.py', 'system.py', 'fun.py', 'blacklist.py', 'gcast.py'
    ]
    
    plugins_dir = Path("plugins")
    fixed_count = 0
    
    for plugin_name in error_plugins:
        file_path = plugins_dir / plugin_name
        if file_path.exists():
            if fix_plugin_completely(file_path):
                fixed_count += 1
        else:
            print(f"❌ Plugin not found: {plugin_name}")
    
    print(f"\n📊 Final Fix Summary:")
    print(f"Processed: {len(error_plugins)}")
    print(f"Fixed: {fixed_count}")
    
    print(f"\n🎉 Final fix complete! All plugins should now load properly.")

if __name__ == "__main__":
    main()