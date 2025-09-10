#!/usr/bin/env python3
"""
Clean All Plugins - Remove all misplaced imports from inside functions
"""

import os
from pathlib import Path

def clean_plugin(file_path):
    """Remove all misplaced imports from plugin file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        cleaned_lines = []
        inside_function = False
        indent_level = 0
        
        for i, line in enumerate(lines):
            original_line = line
            stripped = line.strip()
            
            # Detect function/method definitions
            if stripped.startswith(('def ', 'async def ', 'class ')):
                inside_function = True
                indent_level = len(line) - len(line.lstrip())
                cleaned_lines.append(original_line)
                continue
            
            # Reset when we exit function scope (back to top level or another function)
            if inside_function and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                inside_function = False
                indent_level = 0
            
            # Skip misplaced imports inside functions
            if inside_function and (
                stripped.startswith('import sys') or
                stripped.startswith('# Add parent directory') or  
                stripped.startswith('sys.path.append') or
                stripped.startswith('# Import comment system') or
                stripped.startswith('from plugins.comments import vzoel_comments')
            ):
                continue
                
            # Keep all other lines
            cleaned_lines.append(original_line)
        
        # Add required imports at top if not present
        content = ''.join(cleaned_lines)
        if 'from plugins.comments import vzoel_comments' not in content:
            # Find insertion point after existing imports
            insert_point = 0
            for i, line in enumerate(cleaned_lines):
                if line.strip().startswith(('import ', 'from ')) and 'import' in line:
                    insert_point = i + 1
                elif line.strip() and not line.strip().startswith('#') and not line.strip().startswith(('import ', 'from ', '"""', "'''")):
                    break
            
            # Insert required imports
            imports_to_add = [
                'import sys\n',
                'import os\n', 
                '\n',
                '# Add parent directory to path for imports\n',
                'sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\n',
                '\n',
                '# Import comment system\n', 
                'from plugins.comments import vzoel_comments\n',
                '\n'
            ]
            
            for imp in reversed(imports_to_add):
                cleaned_lines.insert(insert_point, imp)
        
        new_content = ''.join(cleaned_lines)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Cleaned {file_path.name}")
            return True
        else:
            print(f"⏭️  No cleaning needed for {file_path.name}")
            return False
            
    except Exception as e:
        print(f"❌ Error cleaning {file_path.name}: {e}")
        return False

def main():
    """Clean all problematic plugins"""
    print("🧹 Vzoel Fox's Plugin Cleaner")
    print("==========================")
    
    error_plugins = [
        'tagall.py', 'vc.py', 'pizol.py', 
        'idchecker.py', 'system.py', 'fun.py', 'blacklist.py', 'gcast.py'
    ]
    
    plugins_dir = Path("plugins")
    cleaned_count = 0
    
    for plugin_name in error_plugins:
        file_path = plugins_dir / plugin_name
        if file_path.exists():
            if clean_plugin(file_path):
                cleaned_count += 1
        else:
            print(f"❌ Plugin not found: {plugin_name}")
    
    print(f"\n📊 Cleaning Summary:")
    print(f"Processed: {len(error_plugins)}")
    print(f"Cleaned: {cleaned_count}")
    
    print(f"\n🎉 Plugin cleaning complete!")

if __name__ == "__main__":
    main()