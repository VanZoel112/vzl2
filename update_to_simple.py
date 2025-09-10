#!/usr/bin/env python3
"""
Update All Plugins to Simple Mapping
Mass update to Vzoel Fox's simple internal mapping
Created by: Vzoel Fox's
"""

import os
import re
from pathlib import Path

def update_plugin_to_simple(file_path):
    """Update plugin to use simple mapping"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changes_made = []
    
    # Update import statements
    if 'from vzoel_comments_working import vzoel_comments' in content:
        content = content.replace(
            'from vzoel_comments_working import vzoel_comments',
            'from vzoel_simple import vzoel_comments'
        )
        changes_made.append('Updated to simple comments import')
    
    # Update any remaining working imports
    if 'from emoji_handler_working import' in content:
        content = content.replace(
            'from emoji_handler_working import',
            'from vzoel_simple import'
        )
        changes_made.append('Updated to simple emoji import')
    
    # Write updated content
    if changes_made:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Updated {file_path.name}")
        for change in changes_made:
            print(f"   - {change}")
    else:
        print(f"⚪ No changes needed for {file_path.name}")
    
    return len(changes_made) > 0

def main():
    """Main update process"""
    print("🦊 Vzoel Fox's Simple Mapping Update")
    print("=" * 50)
    
    # Update client.py first
    client_file = Path("client.py")
    if client_file.exists():
        print("🔧 Updating client.py...")
        with open(client_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'from emoji_handler_working import vzoel_emoji' in content:
            content = content.replace(
                'from emoji_handler_working import vzoel_emoji',
                'from vzoel_simple import vzoel_emoji'
            )
            
            with open(client_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Updated client.py to use simple emoji mapping")
    
    # Get plugins directory
    plugins_dir = Path("plugins")
    
    if not plugins_dir.exists():
        print("❌ Plugins directory not found!")
        return
    
    # Find all Python files in plugins directory
    python_files = list(plugins_dir.glob("*.py"))
    python_files = [f for f in python_files if f.name not in ['__init__.py']]
    
    print(f"📁 Found {len(python_files)} plugin files to update")
    print()
    
    updated_count = 0
    
    # Update each plugin file
    for file_path in python_files:
        try:
            if update_plugin_to_simple(file_path):
                updated_count += 1
        except Exception as e:
            print(f"❌ Error updating {file_path.name}: {e}")
    
    print()
    print(f"🎉 Update completed!")
    print(f"📊 Updated {updated_count} out of {len(python_files)} plugin files")
    print()
    print("✨ All files now use Vzoel Fox's simple mapping:")
    print("   - Internal emoji mapping with premium support")
    print("   - Simple comment system with Vzoel Fox's branding")
    print("   - No external dependencies")
    print()
    print("🔄 Restart vzl2 to apply changes")

if __name__ == "__main__":
    main()