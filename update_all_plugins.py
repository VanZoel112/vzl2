#!/usr/bin/env python3
"""
Batch Update All Plugins with Comment System and Premium Emojis
Updates all VzoelFox plugins to use the new comment system and premium emojis
"""

import os
import re
from pathlib import Path

def update_plugin_imports(content):
    """Add imports for comment system"""
    if "from plugins.comments import vzoel_comments" in content:
        return content  # Already updated
    
    # Find existing imports
    import_section = content.find("import os") 
    if import_section == -1:
        import_section = content.find("import sys")
    if import_section == -1:
        import_section = content.find("import asyncio")
    
    if import_section != -1:
        # Find end of current imports
        lines = content.split('\n')
        insert_line = 0
        
        for i, line in enumerate(lines):
            if ("import " in line or "from " in line) and not line.strip().startswith("#"):
                insert_line = i + 1
        
        # Add sys path if not present
        sys_path_added = False
        for i in range(max(0, insert_line - 5), min(len(lines), insert_line + 5)):
            if "sys.path.append" in lines[i]:
                sys_path_added = True
                break
        
        if not sys_path_added:
            lines.insert(insert_line, "import sys")
            lines.insert(insert_line + 1, "")
            lines.insert(insert_line + 2, "# Add parent directory to path for imports")
            lines.insert(insert_line + 3, "sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))")
            lines.insert(insert_line + 4, "")
            lines.insert(insert_line + 5, "# Import comment system")
            lines.insert(insert_line + 6, "from plugins.comments import vzoel_comments")
            insert_line += 7
        else:
            lines.insert(insert_line, "# Import comment system")
            lines.insert(insert_line + 1, "from plugins.comments import vzoel_comments")
            insert_line += 2
            
        content = '\n'.join(lines)
    
    return content

def update_emoji_imports(content):
    """Update emoji handler imports to premium version"""
    content = re.sub(
        r'from emoji_handler import vzoel_emoji',
        'from emoji_handler_premium import vzoel_emoji',
        content
    )
    return content

def update_common_messages(content):
    """Update common static messages to use comment system"""
    
    # Process messages
    replacements = [
        (r'"Processing\.\.\."', 'vzoel_comments.get_process("processing")'),
        (r'"Loading\.\.\."', 'vzoel_comments.get_process("loading")'),
        (r'"Calculating\.\.\."', 'vzoel_comments.get_process("calculating")'),
        (r'"Connecting\.\.\."', 'vzoel_comments.get_process("connecting")'),
        (r'"Generating\.\.\."', 'vzoel_comments.get_process("generating")'),
        (r'"Scanning\.\.\."', 'vzoel_comments.get_process("scanning")'),
        (r'"Checking\.\.\."', 'vzoel_comments.get_process("checking")'),
        (r'"Testing\.\.\."', 'vzoel_comments.get_process("testing")'),
        
        # Success messages
        (r'"Done!"', 'vzoel_comments.get_success("done")'),
        (r'"Completed!"', 'vzoel_comments.get_success("completed")'),
        (r'"Success!"', 'vzoel_comments.get_success("completed")'),
        (r'"Sent!"', 'vzoel_comments.get_success("sent")'),
        (r'"Saved!"', 'vzoel_comments.get_success("saved")'),
        
        # Error messages
        (r'"Failed!"', 'vzoel_comments.get_error("failed")'),
        (r'"Error!"', 'vzoel_comments.get_error("failed")'),
        (r'"Timeout!"', 'vzoel_comments.get_error("timeout")'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    return content

def update_premium_emojis(content):
    """Update emoji usage to premium format"""
    
    # Common emoji patterns
    emoji_patterns = [
        (r'vzoel_emoji\.get_emoji\((.*?)\)', r'vzoel_emoji.getemoji(\1, premium=True)'),
        (r'vzoel_emoji\.get_vzoel_signature\(\)', r'vzoel_emoji.get_vzoel_signature(premium=True)'),
    ]
    
    for pattern, replacement in emoji_patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def update_vzoel_branding(content):
    """Update VzoelFox branding to use comment system"""
    
    # Replace common VzoelFox text with comment system
    branding_replacements = [
        (r'"VzoelFox\'s Assistant"', 'vzoel_comments.get_vzoel("signature")'),
        (r'"Vzoel Fox\'s Assistant"', 'vzoel_comments.get_vzoel("signature")'),
        (r'"©2025 ~ Vzoel Fox\'s \(LTPN\)"', 'vzoel_comments.get_vzoel("copyright")'),
        (r'"Enhanced by Vzoel Fox\'s Ltpn"', 'vzoel_comments.get_vzoel("tagline")'),
        (r'"Created by: Vzoel Fox\'s"', 'vzoel_comments.get_vzoel("creator")'),
    ]
    
    for pattern, replacement in branding_replacements:
        content = re.sub(pattern, replacement, content)
    
    return content

def update_plugin_file(file_path):
    """Update a single plugin file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already updated or is comments.py itself
        if "vzoel_comments" in content or "comments.py" in str(file_path):
            print(f"⏭️  Skipping {file_path.name} - already updated or is comments plugin")
            return False
            
        original_content = content
        
        # Apply updates
        content = update_plugin_imports(content)
        content = update_emoji_imports(content)
        content = update_common_messages(content)
        content = update_premium_emojis(content)
        content = update_vzoel_branding(content)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated {file_path.name}")
            return True
        else:
            print(f"⏭️  No changes needed for {file_path.name}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {file_path.name}: {e}")
        return False

def main():
    """Main update function"""
    print("🦊 VzoelFox Plugin Update System")
    print("=================================")
    print("Updating all plugins with comment system and premium emojis...\n")
    
    plugins_dir = Path("plugins")
    if not plugins_dir.exists():
        print("❌ Plugins directory not found!")
        return
    
    updated_count = 0
    total_count = 0
    
    # Process all Python files in plugins directory
    for file_path in plugins_dir.glob("*.py"):
        if file_path.name.startswith("__"):
            continue
            
        total_count += 1
        if update_plugin_file(file_path):
            updated_count += 1
    
    print(f"\n📊 Update Summary:")
    print(f"Total plugins: {total_count}")
    print(f"Updated: {updated_count}")
    print(f"Skipped: {total_count - updated_count}")
    
    if updated_count > 0:
        print(f"\n🎉 Successfully updated {updated_count} plugins!")
        print("All plugins now support:")
        print("• 📝 Centralized comment system")
        print("• 🎭 Premium emoji integration")
        print("• 🦊 VzoelFox branding via comment system")
    else:
        print("\n✅ All plugins are already up to date!")

if __name__ == "__main__":
    main()