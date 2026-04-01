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

BOT_NAME      = "『 ʟɪʟʏ вσт 』"
BOT_USERNAME  = "liiiilyy_bot"          # ✦ NO @ here — used inside URLs
SUPPORT_GROUP = "upper_moon_chat"       # ✦ NO @ here — used inside URLs

VIDEO_PRIVATE = "https://files.catbox.moe/931ph0.mp4"
VIDEO_GROUP   = "https://files.catbox.moe/dlg0rb.mp4"

STICKER_ID = "CAACAgIAAxkBAAFGEk9py21yQ49JGaKmsC2SjjhlJDIwACLXIAAp0y-Eqfu3A5hCItKToE"


# ✦━━━━━━━━ GREETINGS ━━━━━━━━✦

GREETINGS = [
    "ʜᴇʏʏ~ ᴜᴡᴜ 💕",
    "ɴʏᴀᴀ~ 🌸",
    "ʏᴏʜʜᴏ~ ✨",
    "ᴋᴏɴɴɪᴄʜɪᴡᴀ~ 🫶",
]


# ✦━━━━━━━━ CAPTIONS ━━━━━━━━✦

def build_private_caption(user):
    greet = random.choice(GREETINGS)
    return (
        f"┏━━━❖ 🌸 ❖━━━┓\n"
        f"  {greet}\n\n"
        f"  <b><a href=\"tg://user?id={user.id}\">{user.first_name}</a></b>\n"
        f"┗━━━❖ 🌸 ❖━━━┛\n\n"
        f"✨ <b>Welcome to {BOT_NAME}</b>\n\n"
        f"➤ Your Cute Anime Guardian 💫\n"
        f"➤ Protecting Groups Like a Pro ⚔️\n\n"
        f"───────────────\n"
        f"🌷 Features:\n\n"
        f"✦ Ban • Mute • Kick\n"
        f"✦ Anti-Flood System\n"
        f"✦ Notes & Filters\n"
        f"✦ Auto Welcome\n\n"
        f"───────────────\n\n"
        f"💖 Add me to your group\n"
        f"and make me admin Senpai~"
    )


def build_group_caption(user):
    return (
        f"🌸 <b>{BOT_NAME} Activated!</b>\n\n"
        f"Hey <a href=\"tg://user?id={user.id}\">{user.first_name}</a> 👀\n\n"
        f"✨ I'm now guarding this group\n"
        f"⚔️ Ready to protect &amp; manage\n\n"
        f"➤ Use /help to see commands"
    )


# ✦━━━━━━━━ BUTTONS ━━━━━━━━✦

def private_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "➕ Add Me to Group",
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton(
                "🌸 Support",
                url=f"https://t.me/{SUPPORT_GROUP}"
            ),
            InlineKeyboardButton(
                "✨ Help",
                callback_data="help"
            )
        ]
    ])


def group_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "➕ Add Me to Group",
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton(
                "🌸 Support",
                url=f"https://t.me/{SUPPORT_GROUP}"
            )
        ]
    ])


def back_button():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⬅️ Back", callback_data="back")
        ]
    ])


# ✦━━━━━━━━ START HANDLER ━━━━━━━━✦

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    chat = update.effective_chat

    # ── GROUP MODE ──────────────────────────────────
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
        except Exception as e:
            logger.warning(f"Group video send failed: {e}")
            await update.message.reply_html(
                build_group_caption(user),
                reply_markup=group_buttons()
            )
        return

    # ── PRIVATE MODE ────────────────────────────────

    # 1. Sticker entry
    try:
        await ctx.bot.send_sticker(chat.id, STICKER_ID)
        await asyncio.sleep(0.5)
    except Exception as e:
        logger.warning(f"Sticker send failed: {e}")

    # 2. Typing effect
    try:
        await ctx.bot.send_chat_action(chat.id, "typing")
        await asyncio.sleep(1)
    except Exception as e:
        logger.warning(f"Chat action failed: {e}")

    # 3. Video + Caption
    try:
        await ctx.bot.send_video(
            chat_id=chat.id,
            video=VIDEO_PRIVATE,
            caption=build_private_caption(user),
            parse_mode=ParseMode.HTML,
            reply_markup=private_buttons(),
            supports_streaming=True
        )
    except Exception as e:
        logger.error(f"Private video send failed: {e}")
        await update.message.reply_html(
            build_private_caption(user),
            reply_markup=private_buttons()
        )


# ✦━━━━━━━━ CALLBACK HANDLER ━━━━━━━━✦

async def start_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    # ── Help button ─────────────────────────────────
    if query.data == "help":
        try:
            await query.edit_message_caption(
                caption=HELP_TEXT,
                parse_mode=ParseMode.HTML,
                reply_markup=back_button()
            )
        except Exception as e:
            logger.warning(f"edit_message_caption failed, trying edit_message_text: {e}")
            try:
                await query.edit_message_text(
                    text=HELP_TEXT,
                    parse_mode=ParseMode.HTML,
                    reply_markup=back_button()
                )
            except Exception as e2:
                logger.error(f"Help callback fully failed: {e2}")

    # ── Back button ─────────────────────────────────
    elif query.data == "back":
        try:
            await query.edit_message_caption(
                caption=build_private_caption(query.from_user),
                parse_mode=ParseMode.HTML,
                reply_markup=private_buttons()
            )
        except Exception as e:
            logger.warning(f"edit_message_caption failed on back, trying edit_message_text: {e}")
            try:
                await query.edit_message_text(
                    text=build_private_caption(query.from_user),
                    parse_mode=ParseMode.HTML,
                    reply_markup=private_buttons()
                )
            except Exception as e2:
                logger.error(f"Back callback fully failed: {e2}")


# ✦━━━━━━━━ HELP COMMAND ━━━━━━━━✦

async def help_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        HELP_TEXT,
        parse_mode=ParseMode.HTML
    )
