#!/usr/bin/env python3
"""
Final Fix - Remove ALL misplaced imports from all plugins
"""

import os
import re

def fix_plugin(filename):
    """Fix a single plugin by removing misplaced imports"""
    filepath = f"plugins/{filename}"
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Split into lines
        lines = content.split('\n')
        new_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this is a misplaced import block (starts with import sys and has indentation)
            if (line.strip() == 'import sys' and 
                i > 0 and 
                (line.startswith('    ') or line.startswith('\t') or 
                 # Check if previous line suggests we're inside a function
                 any(prev_line.strip().startswith(('from client import', 'from emoji_handler')) 
                     for prev_line in lines[max(0, i-3):i]))):
                
                # Skip this entire import block
                while i < len(lines) and (
                    lines[i].strip().startswith(('import', 'sys.path', '# Add parent', '# Import comment', 'from plugins.comments')) or
                    lines[i].strip() == ''
                ):
                    i += 1
                continue
            
            new_lines.append(line)
            i += 1
        
        new_content = '\\n'.join(new_lines)
        
        # Add imports at the top if missing
        if 'from plugins.comments import vzoel_comments' not in new_content:
            lines_to_check = new_content.split('\\n')
            insert_point = 0
            
            # Find insertion point after existing imports
            for idx, line in enumerate(lines_to_check):
                if line.strip().startswith(('import ', 'from ')) and 'import' in line:
                    insert_point = idx + 1
                elif line.strip() and not line.strip().startswith(('#', 'import', 'from', '\"\"\"', \"'''\")):
                    break
            
            # Insert required imports
            required_imports = [
                'import sys',
                'import os',
                '',
                '# Add parent directory to path for imports', 
                'sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))',
                '',
                '# Import comment system',
                'from plugins.comments import vzoel_comments',
                ''
            ]
            
            for imp in reversed(required_imports):
                lines_to_check.insert(insert_point, imp)
            
            new_content = '\\n'.join(lines_to_check)
        
        # Write if changed
        if new_content != content:
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"✅ Fixed {filename}")
            return True
        else:
            print(f"⏭️  {filename} was already clean")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {filename}: {e}")
        return False

def main():
    """Fix all problematic plugins"""
    plugins = [
        'vc.py', 'pizol.py', 'idchecker.py', 'system.py', 
        'fun.py', 'blacklist.py', 'gcast.py'
    ]
    
    print("🛠️  Final Plugin Fix")
    print("====================")
    
    fixed_count = 0
    for plugin in plugins:
        if fix_plugin(plugin):
            fixed_count += 1
    
    print(f"\\n📊 Final Results:")
    print(f"Fixed: {fixed_count}/{len(plugins)} plugins")
    print("\\n🎉 All plugins should now load without errors!")

if __name__ == "__main__":
    main()