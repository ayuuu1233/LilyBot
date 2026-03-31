            
# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
#      🌸 KAWAII START SYSTEM 🌸
# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦

import asyncio
import random
import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)

# ✦━━━━━━━━ CONFIG ━━━━━━━━✦

BOT_NAME = "KawaiiGuardian"
BOT_USERNAME = "your_bot_username"
SUPPORT_GROUP = "your_support_group"

VIDEO_PRIVATE = "https://files.catbox.moe/nfu6s9.mp4"
VIDEO_GROUP = "https://telegra.ph/file/0b2e8e33d07a0d0e5914f.mp4"

STICKER_ID = "CAACAgUAAxkBAAEBeVpm-jtB-lkO8Oixy5SZHTAy1Ymp4QACEgwAAv75EFbYc5vQ3hQ1Ph4E"

# ✦━━━━━━━━ GREETINGS ━━━━━━━━✦

GREETINGS = [
    "ʜᴇʏʏ~ ᴜᴡᴜ 💕",
    "ɴʏᴀᴀ~ 🌸",
    "ʏᴏʜʜᴏ~ ✨",
    "ᴋᴏɴɴɪᴄʜɪᴡᴀ~ 🫶",
]

# ✦━━━━━━━━ PRIVATE CAPTION ━━━━━━━━✦

def build_private_caption(user):
    greet = random.choice(GREETINGS)

    return f"""
┏━━━❖ 🌸 ❖━━━┓
  {greet}

  <b><a href="tg://user?id={user.id}">{user.first_name}</a></b>
┗━━━❖ 🌸 ❖━━━┛

✨ <b>Welcome to {BOT_NAME}</b>

➤ Your Cute Anime Guardian 💫  
➤ Protecting Groups Like a Pro ⚔️  

───────────────
🌷 Features:

✦ Ban • Mute • Kick  
✦ Anti-Flood System  
✦ Notes & Filters  
✦ Auto Welcome  

───────────────

💖 Add me to your group
and make me admin Senpai~
"""

# ✦━━━━━━━━ GROUP CAPTION ━━━━━━━━✦

def build_group_caption(user):
    return f"""
🌸 <b>{BOT_NAME} Activated!</b>

Hey <a href="tg://user?id={user.id}">{user.first_name}</a> 👀

✨ I'm now guarding this group
⚔️ Ready to protect & manage

➤ Use /help to see commands
"""

# ✦━━━━━━━━ BUTTONS ━━━━━━━━✦

def private_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Me", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
        ],
        [
            InlineKeyboardButton("🌸 Support", url=f"https://t.me/{SUPPORT_GROUP}"),
            InlineKeyboardButton("✨ Help", callback_data="help")
        ]
    ])

def group_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Me", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
        ],
        [
            InlineKeyboardButton("🌸 Support", url=f"https://t.me/{SUPPORT_GROUP}")
        ]
    ])

# ✦━━━━━━━━ START HANDLER ━━━━━━━━✦

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    chat = update.effective_chat

    # ✦━━━━━━━━ GROUP MODE ━━━━━━━━✦
    if chat.type != "private":
        try:
            await ctx.bot.send_video(
                chat_id=chat.id,
                video=VIDEO_GROUP,
                caption=build_group_caption(user),
                parse_mode=ParseMode.HTML,
                reply_markup=group_buttons(),
                supports_streaming=True
            )
        except:
            await update.message.reply_html(build_group_caption(user))
        return

    # ✦━━━━━━━━ PRIVATE MODE ━━━━━━━━✦

    # 1. Sticker Entry
    try:
        await ctx.bot.send_sticker(chat.id, STICKER_ID)
        await asyncio.sleep(0.5)
    except:
        pass

    # 2. Typing Effect
    await ctx.bot.send_chat_action(chat.id, "typing")
    await asyncio.sleep(1)

    # 3. Video + Caption
    await ctx.bot.send_video(
        chat_id=chat.id,
        video=VIDEO_PRIVATE,
        caption=build_private_caption(user),
        parse_mode=ParseMode.HTML,
        reply_markup=private_buttons(),
        supports_streaming=True
    )

# ✦━━━━━━━━ CALLBACK ━━━━━━━━✦

async def start_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "help":
        await query.edit_message_caption(
            caption="""
🌸 <b>Help Menu</b>

➤ /ban - Ban user  
➤ /mute - Mute user  
➤ /kick - Kick user  
➤ /warn - Warn system  

✨ More features coming soon~
""",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅ Back", callback_data="back")]
            ])
        )

    elif query.data == "back":
        await query.edit_message_caption(
            caption=build_private_caption(query.from_user),
            parse_mode=ParseMode.HTML,
            reply_markup=private_buttons()
    )
