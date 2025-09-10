#!/usr/bin/env python3
"""
Update All Plugins to use Working Systems
Mass update script to apply Vzoel Fox's working implementation to all plugins
Created by: Vzoel Fox's
"""

import os
import re
from pathlib import Path

def update_plugin_imports(file_path):
    """Update plugin imports to use working systems"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Track changes
    changes_made = []
    
    # Update comment system import
    if 'from plugins.comments import vzoel_comments' in content:
        content = content.replace(
            'from plugins.comments import vzoel_comments',
            'from vzoel_comments_working import vzoel_comments'
        )
        changes_made.append('Updated comment system import')
    
    # Update emoji handler usage to use working methods
    # Replace get_emoji calls to use premium parameter
    emoji_pattern = r'vzoel_emoji\.get_emoji\(["\']([^"\']+)["\']\)'
    matches = re.findall(emoji_pattern, content)
    
    for match in matches:
        old_call = f'vzoel_emoji.get_emoji("{match}")'
        new_call = f'vzoel_emoji.get_emoji("{match}", premium=True)'
        content = content.replace(old_call, new_call)
        
        old_call_single = f"vzoel_emoji.get_emoji('{match}')"
        new_call_single = f"vzoel_emoji.get_emoji('{match}', premium=True)"
        content = content.replace(old_call_single, new_call_single)
    
    if matches:
        changes_made.append(f'Updated {len(matches)} emoji calls to use premium parameter')
    
    # Update getemoji calls
    getemoji_pattern = r'vzoel_emoji\.getemoji\(["\']([^"\']+)["\']\)'
    getemoji_matches = re.findall(getemoji_pattern, content)
    
    for match in getemoji_matches:
        old_call = f'vzoel_emoji.getemoji("{match}")'
        new_call = f'vzoel_emoji.getemoji("{match}", premium=True)'
        content = content.replace(old_call, new_call)
        
        old_call_single = f"vzoel_emoji.getemoji('{match}')"
        new_call_single = f"vzoel_emoji.getemoji('{match}', premium=True)"
        content = content.replace(old_call_single, new_call_single)
    
    if getemoji_matches:
        changes_made.append(f'Updated {len(getemoji_matches)} getemoji calls to use premium parameter')
    
    # Update vzoel_signature calls
    if 'vzoel_emoji.get_vzoel_signature()' in content:
        content = content.replace(
            'vzoel_emoji.get_vzoel_signature()',
            'vzoel_emoji.get_vzoel_signature(premium=True)'
        )
        changes_made.append('Updated vzoel_signature call to use premium parameter')
    
    # Update comment system calls to use simplified methods
    comment_replacements = [
        ('vzoel_comments.get_process(', 'vzoel_comments.process('),
        ('vzoel_comments.get_success(', 'vzoel_comments.result('),
        ('vzoel_comments.get_error(', 'vzoel_comments.error('),
        ('vzoel_comments.get_vzoel(', 'vzoel_comments.vzoel('),
        ('vzoel_comments.get_command(', 'vzoel_comments.response('),
    ]
    
    for old_call, new_call in comment_replacements:
        if old_call in content:
            content = content.replace(old_call, new_call)
            changes_made.append(f'Updated comment call: {old_call} -> {new_call}')
    
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
    print("🦊 Vzoel Fox's Working Systems Update")
    print("=" * 50)
    
    # Get plugins directory
    plugins_dir = Path("plugins")
    
    if not plugins_dir.exists():
        print("❌ Plugins directory not found!")
        return
    
    # Find all Python files in plugins directory
    python_files = list(plugins_dir.glob("*.py"))
    python_files = [f for f in python_files if f.name not in ['__init__.py', 'comments.py']]
    
    print(f"📁 Found {len(python_files)} plugin files to update")
    print()
    
    updated_count = 0
    
    # Update each plugin file
    for file_path in python_files:
        try:
            if update_plugin_imports(file_path):
                updated_count += 1
        except Exception as e:
            print(f"❌ Error updating {file_path.name}: {e}")
    
    print()
    print(f"🎉 Update completed!")
    print(f"📊 Updated {updated_count} out of {len(python_files)} files")
    print()
    print("✨ All plugins now use Vzoel Fox's working systems:")
    print("   - emoji_handler_working.py for premium emojis")
    print("   - vzoel_comments_working.py for comments")
    print()
    print("🔄 You may need to restart the bot to apply changes")

if __name__ == "__main__":
    main()