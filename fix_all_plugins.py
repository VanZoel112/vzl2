#!/usr/bin/env python3
"""
Fix all plugins to use correct import pattern
"""

import os
import re
from pathlib import Path

def fix_plugin_imports(plugin_file):
    """Fix imports in a single plugin file"""
    try:
        with open(plugin_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already fixed
        if 'vzoel_client = None' in content:
            print(f"✅ {plugin_file.name} already fixed")
            return True
        
        print(f"🔧 Fixing {plugin_file.name}...")
        
        # Find the import section (after docstring, before functions)
        lines = content.split('\n')
        new_lines = []
        in_imports = False
        imports_added = False
        
        for i, line in enumerate(lines):
            # Add import fixes after telethon import
            if 'from telethon import events' in line and not imports_added:
                new_lines.append(line)
                new_lines.append('import sys')
                new_lines.append('import os')
                new_lines.append('')
                new_lines.append('# Add parent directory to path for imports')
                new_lines.append('sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))')
                new_lines.append('')
                imports_added = True
                continue
            
            # Add global variables after __author__ line or before first function
            if (('__author__' in line or 'async def vzoel_init' in line) and 
                'vzoel_client = None' not in content):
                
                if '__author__' in line:
                    new_lines.append(line)
                    new_lines.append('')
                    new_lines.append('# Global references (will be set by vzoel_init)')
                    new_lines.append('vzoel_client = None')
                    new_lines.append('vzoel_emoji = None')
                    new_lines.append('')
                    continue
                elif 'async def vzoel_init' in line:
                    new_lines.append('# Global references (will be set by vzoel_init)')
                    new_lines.append('vzoel_client = None')
                    new_lines.append('vzoel_emoji = None')
                    new_lines.append('')
                    new_lines.append(line)
                    continue
            
            # Fix vzoel_init function signature
            if 'async def vzoel_init(client, vzoel_emoji):' in line:
                new_lines.append('async def vzoel_init(client, emoji_handler):')
                new_lines.append('    """Plugin initialization"""')
                new_lines.append('    global vzoel_client, vzoel_emoji')
                new_lines.append('    ')
                new_lines.append('    # Set global references')
                new_lines.append('    vzoel_client = client')
                new_lines.append('    vzoel_emoji = emoji_handler')
                new_lines.append('    ')
                # Skip the original docstring and any content until the actual code
                while i + 1 < len(lines) and (lines[i + 1].strip().startswith('"""') or 
                                              lines[i + 1].strip().startswith('"') or
                                              not lines[i + 1].strip()):
                    i += 1
                continue
            
            # Remove local imports
            if ('from client import vzoel_client' in line or 
                'from emoji_handler import vzoel_emoji' in line):
                continue
            
            # Add global declaration to handler functions
            if re.match(r'async def \w+_handler\(event\):', line.strip()):
                new_lines.append(line)
                new_lines.append('    """' + (lines[i+1].strip().replace('"""', '') if i+1 < len(lines) and '"""' in lines[i+1] else 'Handler function') + '"""')
                # Skip original docstring
                if i+1 < len(lines) and '"""' in lines[i+1]:
                    i += 1
                new_lines.append('    if event.is_private or event.sender_id == (await event.client.get_me()).id:')
                new_lines.append('        global vzoel_client, vzoel_emoji')
                new_lines.append('        ')
                # Skip original if statement
                while i + 1 < len(lines) and 'if event.is_private' in lines[i + 1]:
                    i += 1
                continue
            
            new_lines.append(line)
        
        # Write the fixed content
        new_content = '\n'.join(new_lines)
        
        with open(plugin_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Fixed {plugin_file.name}")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {plugin_file.name}: {e}")
        return False

def main():
    """Fix all plugins in the plugins directory"""
    plugins_dir = Path('plugins')
    
    if not plugins_dir.exists():
        print("❌ Plugins directory not found")
        return
    
    print("🦊 Vzoel Fox's Plugin Import Fixer")
    print("=" * 50)
    
    plugin_files = list(plugins_dir.glob("*.py"))
    total_files = len(plugin_files)
    fixed_count = 0
    
    for plugin_file in plugin_files:
        if plugin_file.name.startswith('_'):
            continue
            
        if fix_plugin_imports(plugin_file):
            fixed_count += 1
    
    print(f"\n📊 Results: {fixed_count}/{total_files} plugins fixed")
    print("🦊 Plugin import fixes completed!")

if __name__ == "__main__":
    main()