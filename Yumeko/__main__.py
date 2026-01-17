
import os
import importlib
import asyncio
import shutil
from asyncio import sleep
from pyrogram import idle, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import random
from Yumeko import app, log, scheduler
from config import config
from Yumeko.helper.on_start import edit_restart_message, clear_downloads_folder, notify_startup
from Yumeko.admin.roleassign import ensure_owner_is_hokage
from Yumeko.helper.state import initialize_services
from Yumeko.database import init_db
from Yumeko.decorator.save import save
from Yumeko.decorator.errors import error
from pyrogram import Client


MODULES = ["modules", "watchers", "admin", "decorator"]
LOADED_MODULES = {}



STICKER_FILE_ID = random.choices(config.START_STICKER_FILE_ID, weights=[1, 1])[0]

def cleanup():
    for root, dirs, _ in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                pycache_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(pycache_path)
                except Exception as e:
                    print(f"[bold yellow]Failed to delete {pycache_path}: {e}[/]")


# Load modules and extract __module__ and __help__
def load_modules_from_folder(folder_name):
    folder_path = os.path.join(os.path.dirname(__file__), folder_name)
    for filename in os.listdir(folder_path):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            module = importlib.import_module(f"Yumeko.{folder_name}.{module_name}")
            __module__ = getattr(module, "__module__", None)
            __help__ = getattr(module, "__help__", None)
            if __module__ and __help__:
                LOADED_MODULES[__module__] = __help__

def load_all_modules():
    for folder in MODULES:
        load_modules_from_folder(folder)
    log.info(f"Loaded {len(LOADED_MODULES)} modules: {', '.join(sorted(LOADED_MODULES.keys()))}")

# Pagination Logic
def get_paginated_buttons(page=1, items_per_page=15):
    modules = sorted(LOADED_MODULES.keys())
    total_pages = (len(modules) + items_per_page - 1) // items_per_page

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    current_modules = modules[start_idx:end_idx]

    buttons = [
        InlineKeyboardButton(mod, callback_data=f"help_{i}_{page}")
        for i, mod in enumerate(current_modules, start=start_idx)
    ]
    button_rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]

    # Navigation buttons logic
    if page == 1:  # First page: Next and Close vertically
        button_rows.append([
            InlineKeyboardButton("➡️", callback_data=f"area_{page + 1}")
        ])
        button_rows.append([
            InlineKeyboardButton("🗑️", callback_data="delete")
        ])
        button_rows.append([
            InlineKeyboardButton("Bᴀᴄᴋ", callback_data="st_back")
        ])
    elif page == total_pages:  # Last page: Back and Close vertically
        button_rows.append([
            InlineKeyboardButton("⬅️", callback_data=f"area_{page - 1}")
        ])
        button_rows.append([
            InlineKeyboardButton("🗑️", callback_data="delete")
        ])
        button_rows.append([
            InlineKeyboardButton("Bᴀᴄᴋ", callback_data="st_back")
        ])
    else:  # Other pages: Back, Close, Next horizontally
        button_rows.append([
            InlineKeyboardButton("⬅️", callback_data=f"area_{page - 1}"),
            InlineKeyboardButton("🗑️", callback_data="delete"),
            InlineKeyboardButton("➡️", callback_data=f"area_{page + 1}"),
        ])
        button_rows.append([
            InlineKeyboardButton("Bᴀᴄᴋ", callback_data="st_back")
        ])

    return InlineKeyboardMarkup(button_rows)

# Helper to generate the main menu buttons
def get_main_menu_buttons():
    buttons = [
        [
            InlineKeyboardButton(
                "➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f"https://t.me/{app.me.username}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton("🤝 Sᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT_LINK),
            InlineKeyboardButton("👤 ᴏᴡɴᴇʀ", user_id=config.OWNER_ID)
        ],
        [
            InlineKeyboardButton("Cᴏᴍᴍᴀɴᴅs", callback_data="yumeko_help"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)

@app.on_callback_query(filters.regex("st_back"))
@error
async def start_lol(_, c : CallbackQuery):
        
    user_mention = c.from_user.mention(style="md")
    bot_mention = app.me.mention(style="md")
    await c.message.edit(
        text = f"**ʜᴇʏ, {𝗎𝗌𝖾𝗋_𝗆𝖾𝗇𝗍𝗂𝗈𝗇} 🎀**\n"
        f"**ɪ'ᴍ  {𝖻𝗈𝗍_𝗆𝖾𝗇𝗍𝗂𝗈𝗇} ♡💫, ʏᴏᴜʀ ᴍᴜʟᴛɪᴛᴀsᴋɪɴɢ ᴀssɪsᴛᴀɴᴛ ʙᴏᴛ, ʙᴜɪʟᴛ ᴛᴏ sᴛʀᴇᴀᴍʟɪɴᴇ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ᴡɪᴛʜ ᴀᴅᴠᴀɴᴄᴇᴅ ᴛᴏᴏʟs ᴀɴᴅ ғᴇᴀᴛᴜʀᴇs! 🌸**\n\n"
        f"[✨]({𝖼𝗈𝗇𝖿𝗂𝗀.𝖲𝖳𝖠𝖱𝖳_𝖨𝖬𝖦_𝖴𝖱𝖫}) **✨ ʜᴇʀᴇ's ᴡʜᴀᴛ ɪ ᴄᴀɴ ᴅᴏ:**\n"
        f" • ᴇғғɪᴄɪᴇɴᴛ ɢʀᴏᴜᴘ sᴜᴘᴇʀᴠɪsɪᴏɴ🛠\n"
        f" • ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴏᴅᴇʀᴀᴛɪᴏɴ ᴏᴘᴛɪᴏɴs🚫\n"
        f" • ᴇɴᴛᴇʀᴛᴀɪɴɪɴɢ ᴀɴᴅ ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ᴍᴏᴅᴜʟᴇs🎮\n\n"
        f"📚 **📚 Nᴇᴇᴅ ʜᴇʟᴘ ᴏʀ ᴡᴀɴɴᴀ ᴇxᴘʟᴏʀᴇ??**\n"
        f"ᴄʟɪᴄᴋ ᴛʜᴇ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ꜰᴏʀ ᴀ ᴄᴏᴍᴘʟᴇᴛᴇ ʟɪsᴛ ᴏғ ᴍʏ ᴄᴏᴍᴍᴀɴᴅs ᴀɴᴅ ᴍᴏᴅᴜʟᴇs. 💬",
        reply_markup=get_main_menu_buttons(),
        invert_media = True
    )


@app.on_callback_query(filters.regex("source_code"))
@error
async def source_code(_, clb: CallbackQuery):
    await clb.message.edit(
        text=(
            "✨ **Name:** Yumeko\n"
            "👨‍💻 **Developer:** [Aadiii](tg://user?id=5630057244)\n\n"
            "🤝 **Supporters:**\n"
            "   • [Eren Yeager](tg://user?id=2033411815)\n"
            "   • [ChatGPT](https://chatgpt.com)\n\n"
            "🤖 **Bots Under This Repository:**\n"
            "   • [Nezuko](https://t.me/NezukoProxBot)\n"
            "   • [Frieren](https://t.me/FrierenzBot)\n"
            "   • [Nobara](https://t.me/Nobara_Xprobot)\n"
            "   • [Arlecchino](https://t.me/ArlecchinoProxBot)\n"
            "   • [Kafka Honkai](https://t.me/Kafka_Xprobot)\n"
            "   • [Mikasa](https://t.me/Mikasa_Xprobot)\n\n"           
            "📂 **Source Code:** [Yumeko GitHub Repository](https://github.com/john-wick00/Yumekoo)"
        ),
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Bᴀᴄᴋ", callback_data="st_back")
            ]
        ]),
        disable_web_page_preview=True
    )

@app.on_message(filters.command("start" , config.COMMAND_PREFIXES) & filters.private)
@error
@save
async def start_cmd(_, message : Message):
    
    # Check for parameters passed with the start command
    if len(message.command) > 1 and message.command[1] == "help":
        await help_command(Client, message)
        return
    
    await message.react("🍓" , big = True)
    
    x = await message.reply_text(f"`Hie {message.from_user.first_name} <3`")
    await sleep(0.3)
    await x.edit_text("⚡️")
    await sleep(0.6)
    await x.edit_text("🎊")
    await sleep(0.6)
    await x.delete()
    
    await message.reply_cached_media(file_id = STICKER_FILE_ID)    
    
    await sleep(0.2)
    
    user_mention = message.from_user.mention(style="md")
    bot_mention = app.me.mention(style="md")
    await message.reply(
        text = f"**ʜᴇʏ, {𝗎𝗌𝖾𝗋_𝗆𝖾𝗇𝗍𝗂𝗈𝗇} 🎀**\n"
        f"**ɪ'ᴍ  {𝖻𝗈𝗍_𝗆𝖾𝗇𝗍𝗂𝗈𝗇} ♡💫, ʏᴏᴜʀ ᴍᴜʟᴛɪᴛᴀsᴋɪɴɢ ᴀssɪsᴛᴀɴᴛ ʙᴏᴛ, ʙᴜɪʟᴛ ᴛᴏ sᴛʀᴇᴀᴍʟɪɴᴇ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ᴡɪᴛʜ ᴀᴅᴠᴀɴᴄᴇᴅ ᴛᴏᴏʟs ᴀɴᴅ ғᴇᴀᴛᴜʀᴇs! 🌸**\n\n"
        f"[✨]({𝖼𝗈𝗇𝖿𝗂𝗀.𝖲𝖳𝖠𝖱𝖳_𝖨𝖬𝖦_𝖴𝖱𝖫}) **✨ ʜᴇʀᴇ's ᴡʜᴀᴛ ɪ ᴄᴀɴ ᴅᴏ:**\n"
        f" • ᴇғғɪᴄɪᴇɴᴛ ɢʀᴏᴜᴘ sᴜᴘᴇʀᴠɪsɪᴏɴ🛠\n"
        f" • ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴏᴅᴇʀᴀᴛɪᴏɴ ᴏᴘᴛɪᴏɴs🚫\n"
        f" • ᴇɴᴛᴇʀᴛᴀɪɴɪɴɢ ᴀɴᴅ ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ᴍᴏᴅᴜʟᴇs🎮\n\n"
        f"📚 **📚 Nᴇᴇᴅ ʜᴇʟᴘ ᴏʀ ᴡᴀɴɴᴀ ᴇxᴘʟᴏʀᴇ??**\n"
        f"ᴄʟɪᴄᴋ ᴛʜᴇ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ꜰᴏʀ ᴀ ᴄᴏᴍᴘʟᴇᴛᴇ ʟɪsᴛ ᴏғ ᴍʏ ᴄᴏᴍᴍᴀɴᴅs ᴀɴᴅ ᴍᴏᴅᴜʟᴇs. 💬",
        reply_markup=get_main_menu_buttons(),
        invert_media = True ,
        message_effect_id= 5159385139981059251
    )


@app.on_message(filters.command("help", prefixes=config.COMMAND_PREFIXES) & filters.private)
@error
@save
async def help_command(client, message: Message):
    prefixes = " ".join(config.COMMAND_PREFIXES)
    await message.reply(
        text=f"**📚 ʜᴇʀᴇ’s ᴀ ᴄᴏᴍᴘʟᴇᴛᴇ ʟɪsᴛ ᴏғ ᴀʟʟ ᴍʏ ғᴜɴᴄᴛɪᴏɴᴀʟ ᴍᴏᴅᴜʟᴇs!**\n"
             f"**🧩 ᴛᴀᴘ ᴏɴ ᴀɴʏ ᴍᴏᴅᴜʟᴇ ʙᴇʟᴏᴡ ᴛᴏ ᴠɪᴇᴡ ɪᴛs ғᴜʟʟ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ ᴀɴᴅ ᴜsᴀɢᴇ.**\n\n"
             f"🔧 sᴜᴘᴘᴏʀᴛᴇᴅ ᴘʀᴇғɪxᴇs:** {prefixes} \n\n"
             f"[📩]({config.HELP_IMG_URL}) **𝖥𝗈𝗎𝗇𝖽 𝖺 𝖻𝗎𝗀?**\n"
             f"📬 ᴜsᴇ ᴛʜᴇ /bug ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ʀᴇᴘᴏʀᴛ ɪᴛ ᴀɴᴅ ɪ’ʟʟ ғɪx ɪᴛ ᴀs sᴏᴏɴ ᴀs ᴘᴏssɪʙʟᴇ!",
        reply_markup=get_paginated_buttons(),
        invert_media = True
    )

@app.on_callback_query(filters.regex(r"^yumeko_help$"))
async def show_help_menu(client, query: CallbackQuery):
    prefixes = " ".join(config.COMMAND_PREFIXES)
    await query.message.edit(
        text=f"**📚 ʜᴇʀᴇ’s ᴀ ᴄᴏᴍᴘʟᴇᴛᴇ ʟɪsᴛ ᴏғ ᴀʟʟ ᴍʏ ғᴜɴᴄᴛɪᴏɴᴀʟ ᴍᴏᴅᴜʟᴇs!**\n"
             f"**🧩 ᴛᴀᴘ ᴏɴ ᴀɴʏ ᴍᴏᴅᴜʟᴇ ʙᴇʟᴏᴡ ᴛᴏ ᴠɪᴇᴡ ɪᴛs ғᴜʟʟ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ ᴀɴᴅ ᴜsᴀɢᴇ.**\n\n"
             f"🔧 sᴜᴘᴘᴏʀᴛᴇᴅ ᴘʀᴇғɪxᴇs:** {prefixes} \n\n"
             f"[📩]({config.HELP_IMG_URL}) **𝖥𝗈𝗎𝗇𝖽 𝖺 𝖻𝗎𝗀?**\n"
             f"📬 ᴜsᴇ ᴛʜᴇ /bug ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ʀᴇᴘᴏʀᴛ ɪᴛ ᴀɴᴅ ɪ’ʟʟ ғɪx ɪᴛ ᴀs sᴏᴏɴ ᴀs ᴘᴏssɪʙʟᴇ!",
        reply_markup=get_paginated_buttons(),
        invert_media=True
    )

# Callback query handler for module help
@app.on_callback_query(filters.regex(r"^help_\d+_\d+$"))
async def handle_help_callback(client, query: CallbackQuery):
    data = query.data
    try:
        # Extract the numeric index and page from the callback data
        parts = data.split("_")
        module_index = int(parts[1])
        current_page = int(parts[2])

        modules = sorted(LOADED_MODULES.keys())

        # Retrieve the module name using the index
        module_name = modules[module_index]
        help_text = LOADED_MODULES.get(module_name, "No help available for this module.")

        # Edit the message to display the help text
        await query.message.edit(
            text=f"{help_text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Back", callback_data=f"area_{current_page}")]
            ])
        )
    except (ValueError, IndexError) as e:
        await query.answer("Invalid module selected. Please try again.")

# Callback query handler for pagination
@app.on_callback_query(filters.regex(r"^area_\d+$"))
async def handle_pagination_callback(client, query: CallbackQuery):
    data = query.data
    try:
        page = int(data[5:])
        prefixes = " ".join(config.COMMAND_PREFIXES)

        # Edit both the message text and reply markup
        await query.message.edit(
        text=f"**📚 ʜᴇʀᴇ’s ᴀ ᴄᴏᴍᴘʟᴇᴛᴇ ʟɪsᴛ ᴏғ ᴀʟʟ ᴍʏ ғᴜɴᴄᴛɪᴏɴᴀʟ ᴍᴏᴅᴜʟᴇs!**\n"
             f"**🧩 ᴛᴀᴘ ᴏɴ ᴀɴʏ ᴍᴏᴅᴜʟᴇ ʙᴇʟᴏᴡ ᴛᴏ ᴠɪᴇᴡ ɪᴛs ғᴜʟʟ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ ᴀɴᴅ ᴜsᴀɢᴇ.**\n\n"
             f"🔧 sᴜᴘᴘᴏʀᴛᴇᴅ ᴘʀᴇғɪxᴇs:** {prefixes} \n\n"
             f"[📩]({config.HELP_IMG_URL}) **𝖥𝗈𝗎𝗇𝖽 𝖺 𝖻𝗎𝗀?**\n"
             f"📬 ᴜsᴇ ᴛʜᴇ /bug ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ʀᴇᴘᴏʀᴛ ɪᴛ ᴀɴᴅ ɪ’ʟʟ ғɪx ɪᴛ ᴀs sᴏᴏɴ ᴀs ᴘᴏssɪʙʟᴇ!",
            reply_markup=get_paginated_buttons(page),
            invert_media=True
        )
    except Exception as e:
        await query.answer("Error occurred while navigating pages. Please try again.")

# Callback query handler for main menu
@app.on_callback_query(filters.regex(r"^main_menu$"))
async def handle_main_menu_callback(client, query: CallbackQuery):
    prefixes = " ".join(config.COMMAND_PREFIXES)

    await query.message.edit(
        text=f"**📚 ʜᴇʀᴇ’s ᴀ ᴄᴏᴍᴘʟᴇᴛᴇ ʟɪsᴛ ᴏғ ᴀʟʟ ᴍʏ ғᴜɴᴄᴛɪᴏɴᴀʟ ᴍᴏᴅᴜʟᴇs!**\n"
             f"**🧩 ᴛᴀᴘ ᴏɴ ᴀɴʏ ᴍᴏᴅᴜʟᴇ ʙᴇʟᴏᴡ ᴛᴏ ᴠɪᴇᴡ ɪᴛs ғᴜʟʟ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ ᴀɴᴅ ᴜsᴀɢᴇ.**\n\n"
             f"🔧 sᴜᴘᴘᴏʀᴛᴇᴅ ᴘʀᴇғɪxᴇs:** {prefixes} \n\n"
             f"[📩]({config.HELP_IMG_URL}) **𝖥𝗈𝗎𝗇𝖽 𝖺 𝖻𝗎𝗀?**\n"
             f"📬 ᴜsᴇ ᴛʜᴇ /bug ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ʀᴇᴘᴏʀᴛ ɪᴛ ᴀɴᴅ ɪ’ʟʟ ғɪx ɪᴛ ᴀs sᴏᴏɴ ᴀs ᴘᴏssɪʙʟᴇ!",
        reply_markup=get_paginated_buttons(),
        invert_media=True
    )
    
@app.on_message(filters.command(["start" , "help"], prefixes=config.COMMAND_PREFIXES) & filters.group)
async def start_command(client, message: Message):
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("Sᴛᴀʀᴛ ɪɴ ᴘᴍ", url="https://t.me/riselia_xbot?start=help")]
    ])
    await message.reply(
        text=f"**𝖧𝖾𝗅𝗅𝗈, {message.from_user.first_name} <3**\n"
             f"𝖢𝗅𝗂𝖼𝗄 𝗍𝗁𝖾 𝖻𝗎𝗍𝗍𝗈𝗇 𝖻𝖾𝗅𝗈𝗐 𝗍𝗈 𝖾𝗑𝗉𝗅𝗈𝗋𝖾 𝗆𝗒 𝖿𝖾𝖺𝗍𝗎𝗋𝖾𝗌 𝖺𝗇𝖽 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌!",
        reply_markup=button
    )



if __name__ == "__main__":
    load_all_modules()

    try:
        app.start()
        initialize_services()
        ensure_owner_is_hokage()
        edit_restart_message()
        clear_downloads_folder()
        notify_startup()

        loop = asyncio.get_event_loop()

        async def initialize_async_components():

            await init_db()
            scheduler.start()
            
            # Schedule the antiflood cleanup task to run every 5 minutes

            
            log.info("Async components initialized.")

            bot_details = await app.get_me()
            log.info(f"Bot Configured: Name: {bot_details.first_name}, ID: {bot_details.id}, Username: @{bot_details.username}")

        loop.run_until_complete(initialize_async_components())
        log.info("Bot started. Press Ctrl+C to stop.")
        idle()
        
        cleanup()
    
        app.stop()

    except Exception as e:
        log.exception(e)
