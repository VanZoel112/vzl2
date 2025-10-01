"""
Enhanced Help Plugin for 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 - Premium Edition
Fitur: Plugin list dengan pagination dan premium emoji
𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠
Version: 2.0.0 - VZL2 Native Help System
"""

from telethon import events, Button
from telethon.events import CallbackQuery
import os
import glob
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from central emoji template (VZL2 style)
from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, PREMIUM_EMOJIS

# Plugin Info
PLUGIN_INFO = {
    "name": "help",
    "version": "2.0.0",
    "description": "Enhanced help system dengan pagination dan premium emoji",
    "author": "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠",
    "commands": [".help", ".next", ".back"],
    "features": ["plugin pagination", "premium emoji", "command details", "VZL2 native"]
}

__version__ = "2.0.0"
__author__ = "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠"

# Global references (will be set by vzoel_init)
vzoel_client = None
vzoel_emoji = None

# Help state untuk pagination dan settings
HELP_STATE = {
    'current_page': 0,
    'plugins_per_page': 8,
    'show_details': True,
    'compact_mode': False,
    'show_categories': True
}

def get_all_plugins():
    """Get list semua plugin yang tersedia"""
    plugins_dir = "plugins"
    plugin_files = glob.glob(f"{plugins_dir}/*.py")
    plugins = []

    for plugin_file in plugin_files:
        plugin_name = os.path.basename(plugin_file)[:-3]  # Remove .py
        if not plugin_name.startswith('_') and plugin_name != '__init__':
            plugins.append(plugin_name)

    # Add core commands
    plugins.insert(0, 'core')
    return sorted(plugins)

def get_plugin_commands(plugin_name):
    """Get commands dari plugin tertentu"""
    if plugin_name == 'core':
        return ['.alive', '.ping', '.help', '.emojis']

    # Music & VC commands
    if plugin_name == 'music':
        return ['.play', '.song', '.pause', '.resume', '.stop', '.queue']
    if plugin_name == 'vc':
        return ['.jvc', '.lvc', '.joinvc', '.leavevc', '.stopvc', '.vcstatus']
    if plugin_name == 'report':
        return ['.report', '.reports', '.unreport']

    try:
        plugin_path = f"plugins/{plugin_name}.py"
        if os.path.exists(plugin_path):
            with open(plugin_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # Simple extraction dari pattern r'\.command'
                import re
                patterns = re.findall(r'pattern=r[\'"]\\\.(\w+)', content)
                if patterns:
                    return [f'.{cmd}' for cmd in patterns]

                # Fallback: cari PLUGIN_INFO commands
                if 'PLUGIN_INFO' in content:
                    start = content.find('"commands"')
                    if start != -1:
                        end = content.find(']', start)
                        if end != -1:
                            commands_str = content[start:end+1]
                            commands = re.findall(r'[\'"](\.[^\'\"]*)[\'"]', commands_str)
                            return commands
        return []
    except:
        return []

async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji

    # Set global references
    vzoel_client = client
    vzoel_emoji = emoji_handler

    signature = f"{get_emoji('utama')}{get_emoji('centang')}{get_emoji('aktif')}"
    print(f"{signature} Help Plugin loaded v{PLUGIN_INFO['version']} - VZL2 Native")

@events.register(events.NewMessage(pattern=r'\.help'))
async def help_handler(event):
    """Main help command handler"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji

        try:
            # Reset ke page 0
            HELP_STATE['current_page'] = 0

            # Get semua plugins
            all_plugins = get_all_plugins()
            total_plugins = len(all_plugins)
            plugins_per_page = HELP_STATE['plugins_per_page']
            total_pages = (total_plugins - 1) // plugins_per_page + 1

            # Get plugins untuk page saat ini
            start_idx = HELP_STATE['current_page'] * plugins_per_page
            end_idx = start_idx + plugins_per_page
            page_plugins = all_plugins[start_idx:end_idx]

            # Build help text
            help_text = f"{get_emoji('utama')} VZOEL FOX'S PLUGINS (Page 1/{total_pages})\n\n"
            help_text += f"{get_emoji('centang')} Total Plugins: {total_plugins}\n"
            help_text += f"{get_emoji('aktif')} Page: 1 of {total_pages}\n\n"

            for idx, plugin_name in enumerate(page_plugins, 1):
                commands = get_plugin_commands(plugin_name)

                if plugin_name == 'core':
                    help_text += f"{get_emoji('proses')} {idx}. `{plugin_name}` - Core functions\n"
                else:
                    help_text += f"{get_emoji('proses')} {idx}. `{plugin_name}`\n"

                if commands:
                    if len(commands) <= 3:
                        help_text += f"   └ Commands: `{', '.join(commands)}`\n"
                    else:
                        help_text += f"   └ Commands: `{', '.join(commands[:3])}` + {len(commands)-3} more\n"
                else:
                    help_text += f"   └ Commands: `See plugin for details`\n"
                help_text += "\n"

            # Navigation
            if total_pages > 1:
                help_text += f"{get_emoji('kuning')} Navigation:\n"
                help_text += f"{get_emoji('loading')} `.next` - Next page\n"
                help_text += f"{get_emoji('merah')} `.back` - Previous page\n\n"

            help_text += f"{get_emoji('telegram')} VZL2 Premium System\n"
            help_text += f"{get_emoji('adder1')} Powered by Vzoel Fox's Technology"

            # Inline navigation buttons
            buttons = []
            if total_pages > 1:
                nav_row = []
                if HELP_STATE['current_page'] > 0:
                    nav_row.append(Button.inline(f"{get_emoji('merah')} Back", b"help_back"))
                if HELP_STATE['current_page'] < total_pages - 1:
                    nav_row.append(Button.inline(f"{get_emoji('loading')} Next", b"help_next"))
                if nav_row:
                    buttons.append(nav_row)

            # Category buttons
            if HELP_STATE['show_categories']:
                buttons.append([
                    Button.inline(f"{get_emoji('proses')} Core", b"help_cat_core"),
                    Button.inline(f"{get_emoji('telegram')} Tools", b"help_cat_tools")
                ])
                buttons.append([
                    Button.inline(f"{get_emoji('centang')} Report", b"help_cat_report"),
                    Button.inline(f"{get_emoji('aktif')} All", b"help_cat_all")
                ])

            # Toggle settings buttons
            details_emoji = get_emoji('centang') if HELP_STATE['show_details'] else get_emoji('kuning')
            compact_emoji = get_emoji('centang') if HELP_STATE['compact_mode'] else get_emoji('kuning')
            cat_emoji = get_emoji('centang') if HELP_STATE['show_categories'] else get_emoji('kuning')

            buttons.append([
                Button.inline(f"{details_emoji} Details", b"help_toggle_details"),
                Button.inline(f"{compact_emoji} Compact", b"help_toggle_compact")
            ])
            buttons.append([
                Button.inline(f"{cat_emoji} Categories", b"help_toggle_categories")
            ])

            await safe_send_premium(event, help_text, buttons=buttons)

        except Exception as e:
            error_text = f"{get_emoji('merah')} Help Error: `{str(e)}`\n\n"
            error_text += f"{get_emoji('telegram')} VZL2 Help System"
            await safe_send_premium(event, error_text)

@events.register(events.NewMessage(pattern=r'\.next'))
async def next_handler(event):
    """Handle .next command for pagination"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        try:
            all_plugins = get_all_plugins()
            total_plugins = len(all_plugins)
            plugins_per_page = HELP_STATE['plugins_per_page']
            total_pages = (total_plugins - 1) // plugins_per_page + 1
            current_page = HELP_STATE['current_page']

            if current_page < total_pages - 1:
                HELP_STATE['current_page'] += 1
                new_page = HELP_STATE['current_page']

                # Get plugins untuk page baru
                start_idx = new_page * plugins_per_page
                end_idx = start_idx + plugins_per_page
                page_plugins = all_plugins[start_idx:end_idx]

                # Build help text untuk page baru
                help_text = f"{get_emoji('utama')} VZOEL FOX'S PLUGINS (Page {new_page + 1}/{total_pages})\n\n"
                help_text += f"{get_emoji('centang')} Total Plugins: {total_plugins}\n"
                help_text += f"{get_emoji('aktif')} Page: {new_page + 1} of {total_pages}\n\n"

                for idx, plugin_name in enumerate(page_plugins, start_idx + 1):
                    commands = get_plugin_commands(plugin_name)

                    if plugin_name == 'core':
                        help_text += f"{get_emoji('proses')} {idx}. `{plugin_name}` - Core functions\n"
                    else:
                        help_text += f"{get_emoji('proses')} {idx}. `{plugin_name}`\n"

                    if commands:
                        if len(commands) <= 3:
                            help_text += f"   └ Commands: `{', '.join(commands)}`\n"
                        else:
                            help_text += f"   └ Commands: `{', '.join(commands[:3])}` + {len(commands)-3} more\n"
                    else:
                        help_text += f"   └ Commands: `See plugin for details`\n"
                    help_text += "\n"

                # Navigation
                help_text += f"{get_emoji('kuning')} Navigation:\n"
                help_text += f"{get_emoji('merah')} `.back` - Previous page\n"
                if new_page < total_pages - 1:
                    help_text += f"{get_emoji('loading')} `.next` - Next page\n"
                help_text += "\n"

                help_text += f"{get_emoji('telegram')} VZL2 Premium System\n"
                help_text += f"{get_emoji('adder1')} Powered by Vzoel Fox's Technology"

                await safe_send_premium(event, help_text)
            else:
                error_text = f"{get_emoji('merah')} Already at last page!\n\n"
                error_text += f"{get_emoji('centang')} Current page: {current_page + 1}/{total_pages}\n"
                error_text += f"{get_emoji('kuning')} Use `.back` for previous page\n\n"
                error_text += f"{get_emoji('telegram')} VZL2 Help System"
                await safe_send_premium(event, error_text)

        except Exception as e:
            error_text = f"{get_emoji('merah')} Next Error: `{str(e)}`\n\n"
            error_text += f"{get_emoji('telegram')} VZL2 Help System"
            await safe_send_premium(event, error_text)

@events.register(events.NewMessage(pattern=r'\.back'))
async def back_handler(event):
    """Handle .back command for navigation"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        try:
            current_page = HELP_STATE['current_page']

            if current_page > 0:
                HELP_STATE['current_page'] -= 1
                new_page = HELP_STATE['current_page']

                all_plugins = get_all_plugins()
                total_plugins = len(all_plugins)
                plugins_per_page = HELP_STATE['plugins_per_page']
                total_pages = (total_plugins - 1) // plugins_per_page + 1

                # Get plugins untuk page baru
                start_idx = new_page * plugins_per_page
                end_idx = start_idx + plugins_per_page
                page_plugins = all_plugins[start_idx:end_idx]

                # Build help text untuk page baru
                help_text = f"{get_emoji('utama')} VZOEL FOX'S PLUGINS (Page {new_page + 1}/{total_pages})\n\n"
                help_text += f"{get_emoji('centang')} Total Plugins: {total_plugins}\n"
                help_text += f"{get_emoji('aktif')} Page: {new_page + 1} of {total_pages}\n\n"

                for idx, plugin_name in enumerate(page_plugins, start_idx + 1):
                    commands = get_plugin_commands(plugin_name)

                    if plugin_name == 'core':
                        help_text += f"{get_emoji('proses')} {idx}. `{plugin_name}` - Core functions\n"
                    else:
                        help_text += f"{get_emoji('proses')} {idx}. `{plugin_name}`\n"

                    if commands:
                        if len(commands) <= 3:
                            help_text += f"   └ Commands: `{', '.join(commands)}`\n"
                        else:
                            help_text += f"   └ Commands: `{', '.join(commands[:3])}` + {len(commands)-3} more\n"
                    else:
                        help_text += f"   └ Commands: `See plugin for details`\n"
                    help_text += "\n"

                # Navigation
                if total_pages > 1:
                    help_text += f"{get_emoji('kuning')} Navigation:\n"
                    if new_page > 0:
                        help_text += f"{get_emoji('merah')} `.back` - Previous page\n"
                    if new_page < total_pages - 1:
                        help_text += f"{get_emoji('loading')} `.next` - Next page\n"
                    help_text += "\n"

                help_text += f"{get_emoji('telegram')} VZL2 Premium System\n"
                help_text += f"{get_emoji('adder1')} Powered by Vzoel Fox's Technology"

                await safe_send_premium(event, help_text)
            else:
                error_text = f"{get_emoji('merah')} Already at first page!\n\n"
                error_text += f"{get_emoji('centang')} Current page: 1\n"
                error_text += f"{get_emoji('kuning')} Use `.next` for next page\n\n"
                error_text += f"{get_emoji('telegram')} VZL2 Help System"
                await safe_send_premium(event, error_text)

        except Exception as e:
            error_text = f"{get_emoji('merah')} Back Error: `{str(e)}`\n\n"
            error_text += f"{get_emoji('telegram')} VZL2 Help System"
            await safe_send_premium(event, error_text)


# Inline button callbacks
@events.register(CallbackQuery(pattern=b"help_next"))
async def help_next_callback(event):
    """Handle next button callback"""
    await next_handler(event)
    await event.answer()


@events.register(CallbackQuery(pattern=b"help_back"))
async def help_back_callback(event):
    """Handle back button callback"""
    await back_handler(event)
    await event.answer()


@events.register(CallbackQuery(pattern=b"help_cat_(.+)"))
async def help_category_callback(event):
    """Handle category filter callback"""
    category = event.data.decode().split('_')[-1]

    all_plugins = get_all_plugins()

    # Filter by category
    if category == 'core':
        filtered = ['core']
    elif category == 'tools':
        filtered = [p for p in all_plugins if p in ['payment', 'gcast', 'tagall', 'blacklist']]
    elif category == 'report':
        filtered = [p for p in all_plugins if p == 'report']
    else:  # all
        filtered = all_plugins

    # Build response
    help_text = f"{get_emoji('utama')} VZOEL FOX'S - {category.upper()}\n\n"
    help_text += f"{get_emoji('centang')} Total: {len(filtered)} plugins\n\n"

    for idx, plugin_name in enumerate(filtered, 1):
        commands = get_plugin_commands(plugin_name)
        help_text += f"{get_emoji('proses')} {idx}. `{plugin_name}`\n"

        if commands:
            help_text += f"   └ `{', '.join(commands)}`\n"
        help_text += "\n"

    help_text += f"{get_emoji('telegram')} VZL2 Premium System\n"
    help_text += f"{get_emoji('adder1')} Powered by Vzoel Fox's Technology"

    # Category buttons
    buttons = [
        [
            Button.inline(f"{get_emoji('proses')} Core", b"help_cat_core"),
            Button.inline(f"{get_emoji('telegram')} Tools", b"help_cat_tools")
        ],
        [
            Button.inline(f"{get_emoji('centang')} Report", b"help_cat_report"),
            Button.inline(f"{get_emoji('aktif')} All", b"help_cat_all")
        ]
    ]

    await event.edit(help_text, buttons=buttons)
    await event.answer(f"{get_emoji('centang')} Showing {category} category")


@events.register(CallbackQuery(pattern=b"help_toggle_details"))
async def help_toggle_details(event):
    """Toggle show details"""
    HELP_STATE['show_details'] = not HELP_STATE['show_details']

    # Refresh help display
    all_plugins = get_all_plugins()
    total_plugins = len(all_plugins)
    plugins_per_page = HELP_STATE['plugins_per_page']
    total_pages = (total_plugins - 1) // plugins_per_page + 1
    current_page = HELP_STATE['current_page']

    start_idx = current_page * plugins_per_page
    end_idx = start_idx + plugins_per_page
    page_plugins = all_plugins[start_idx:end_idx]

    # Build help text
    help_text = f"{get_emoji('utama')} VZOEL FOX'S PLUGINS (Page {current_page + 1}/{total_pages})\n\n"
    help_text += f"{get_emoji('centang')} Total Plugins: {total_plugins}\n"
    help_text += f"{get_emoji('aktif')} Page: {current_page + 1} of {total_pages}\n\n"

    for idx, plugin_name in enumerate(page_plugins, start_idx + 1):
        commands = get_plugin_commands(plugin_name)

        if plugin_name == 'core':
            help_text += f"{get_emoji('proses')} {idx}. `{plugin_name}` - Core functions\n"
        else:
            help_text += f"{get_emoji('proses')} {idx}. `{plugin_name}`\n"

        if HELP_STATE['show_details'] and commands:
            if len(commands) <= 3:
                help_text += f"   └ Commands: `{', '.join(commands)}`\n"
            else:
                help_text += f"   └ Commands: `{', '.join(commands[:3])}` + {len(commands)-3} more\n"
        help_text += "\n"

    help_text += f"{get_emoji('telegram')} VZL2 Premium System\n"
    help_text += f"{get_emoji('adder1')} Powered by Vzoel Fox's Technology"

    # Rebuild buttons
    buttons = []
    if total_pages > 1:
        nav_row = []
        if current_page > 0:
            nav_row.append(Button.inline(f"{get_emoji('merah')} Back", b"help_back"))
        if current_page < total_pages - 1:
            nav_row.append(Button.inline(f"{get_emoji('loading')} Next", b"help_next"))
        if nav_row:
            buttons.append(nav_row)

    if HELP_STATE['show_categories']:
        buttons.append([
            Button.inline(f"{get_emoji('proses')} Core", b"help_cat_core"),
            Button.inline(f"{get_emoji('telegram')} Tools", b"help_cat_tools")
        ])
        buttons.append([
            Button.inline(f"{get_emoji('centang')} Report", b"help_cat_report"),
            Button.inline(f"{get_emoji('aktif')} All", b"help_cat_all")
        ])

    details_emoji = get_emoji('centang') if HELP_STATE['show_details'] else get_emoji('kuning')
    compact_emoji = get_emoji('centang') if HELP_STATE['compact_mode'] else get_emoji('kuning')
    cat_emoji = get_emoji('centang') if HELP_STATE['show_categories'] else get_emoji('kuning')

    buttons.append([
        Button.inline(f"{details_emoji} Details", b"help_toggle_details"),
        Button.inline(f"{compact_emoji} Compact", b"help_toggle_compact")
    ])
    buttons.append([
        Button.inline(f"{cat_emoji} Categories", b"help_toggle_categories")
    ])

    await event.edit(help_text, buttons=buttons)
    status = "ON" if HELP_STATE['show_details'] else "OFF"
    await event.answer(f"{get_emoji('centang')} Details: {status}")


@events.register(CallbackQuery(pattern=b"help_toggle_compact"))
async def help_toggle_compact(event):
    """Toggle compact mode"""
    HELP_STATE['compact_mode'] = not HELP_STATE['compact_mode']

    # Adjust plugins per page based on compact mode
    HELP_STATE['plugins_per_page'] = 12 if HELP_STATE['compact_mode'] else 8

    # Refresh display (trigger help handler)
    await help_handler(event)

    status = "ON" if HELP_STATE['compact_mode'] else "OFF"
    await event.answer(f"{get_emoji('centang')} Compact Mode: {status}")


@events.register(CallbackQuery(pattern=b"help_toggle_categories"))
async def help_toggle_categories(event):
    """Toggle category buttons"""
    HELP_STATE['show_categories'] = not HELP_STATE['show_categories']

    # Refresh display
    await help_handler(event)

    status = "Shown" if HELP_STATE['show_categories'] else "Hidden"
    await event.answer(f"{get_emoji('centang')} Categories: {status}")