            
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

HELP_TEXT = """
🌹 <b>LilyBot Commands</b>

<b>Admin Tools</b>
/ban – Ban a user
/unban – Unban a user
/kick – Kick (remove) a user
/mute [time] – Mute a user (e.g. /mute 1h)
/unmute – Unmute a user
/warn [reason] – Warn a user
/unwarn – Remove last warning
/warns – Check warnings
/warnlimit [n] – Set warning limit
/resetwarns – Reset a user's warnings
/promote – Promote to admin
/demote – Demote from admin
/pin – Pin replied message
/unpin – Unpin current pinned message
/adminlist – List group admins

<b>Welcome</b>
/setwelcome [text] – Set welcome message
  Variables: {first}, {last}, {username}, {mention}, {count}
/welcome on|off – Toggle welcome
/setgoodbye [text] – Set goodbye message
/goodbye on|off – Toggle goodbye
/resetwelcome – Reset to default

<b>Filters</b>
/filter [keyword] [reply] – Add a filter
/stop [keyword] – Remove a filter
/filters – List all filters

<b>Anti-Flood</b>
/antiflood [n|off] – Set flood limit (messages/5s)
/flood – Check current flood settings

<b>General</b>
/id – Get chat/user ID
/info – Get user info
/help – Show this message

<b>📝 Notes</b>
/save [name] [text] – Save a note
/get [name] – Get a note (or type #name)
/notes – List all notes
/clear [name] – Delete a note

<b>📜 Rules</b>
/setrules [text] – Set group rules
/rules – Show group rules
/resetrules – Clear rules

<b>🔒 Locks</b>
/lock [type] – Lock message type
/unlock [type] – Unlock message type
/locklist – Show lock status
Types: text, media, polls, invite, pin, info
"""


# ✦━━━━━━━━ CONFIG ━━━━━━━━✦

BOT_NAME = "『 ʟɪʟʏ вσт 』"
BOT_USERNAME = "@liiiilyy_bot"
SUPPORT_GROUP = "@upper_moon_chat"

VIDEO_PRIVATE = "https://files.catbox.moe/931ph0.mp4"
VIDEO_GROUP = "https://files.catbox.moe/dlg0rb.mp4"

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
        caption=HELP_TEXT,
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

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await reply(update, HELP_TEXT)
