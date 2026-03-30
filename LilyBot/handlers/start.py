                # handlers/start.py
# ✦ Kawaii start — Video pehle, caption + buttons neeche ✦
# ─────────────────────────────────────────────────────────────
# bot.py mein add karo:
#
#   from handlers import start as start_handler
#
#   app.add_handler(CommandHandler("start", start_handler.start))
#   app.add_handler(CallbackQueryHandler(start_handler.start_callback, pattern="^start_"))
# ─────────────────────────────────────────────────────────────

import random
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import OWNER_ID, SUDO_USERS
from handlers.admin import HELP_TEXT

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
#  🎬  VIDEO / ANIMATION
#  Yahan apna video URL ya Telegram file_id daal do
#  
#  URL format:   "https://example.com/your-video.mp4"
#  file_id format: "BAACAgIAAxkBAAI..."  (from @RawDataBot)
#
#  Multiple daal sakte ho — random ek chalega har baar
# ══════════════════════════════════════════════════════════════

START_VIDEOS = [
    "https://your-video-url-here.mp4",   # ← APNA VIDEO URL YAHAN DAALO
    # "https://another-video.mp4",       # ← Aur videos add kar sakte ho
]

# Agar video nahi chalti toh fallback animation URL (optional)
FALLBACK_ANIMATION = None  # e.g. "https://your-fallback.gif"


# ══════════════════════════════════════════════════════════════
#  💬  KAWAII WORDS  (random greeting)
# ══════════════════════════════════════════════════════════════

KAWAII_WORDS = [
    "nyaa~",
    "hewwo uwu",
    "h-hai!! (⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)",
    "eep! you found me!! ✧",
    "*pokes head out* o-ohayou~",
    "hiii!!! (ﾉ´ヮ`)ﾉ*: ･ﾟ",
]


# ══════════════════════════════════════════════════════════════
#  📝  CAPTIONS
# ══════════════════════════════════════════════════════════════

# Normal user — private chat
START_PRIVATE = """\
╔══════════════════════════╗
  🌸 ʜᴇʟʟᴏ, {name}~ {kw} 🌸
╚══════════════════════════╝

ᴏᴍɢ ʜɪ ʜɪ ʜɪ!! (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧
ɪ'ᴍ <b>LilyBot</b>, ʏᴏᴜʀ ᴜʟᴛʀᴀ ᴋᴀᴡᴀɪɪ ɢʀᴏᴜᴘ ɢᴜᴀʀᴅɪᴀɴ ✦

<b>ᴡʜᴀᴛ ɪ ᴄᴀɴ ᴅᴏ~</b>
┌─────────────────────────┐
│ 🔨  ʙᴀɴ ᴇᴠɪʟ ᴘᴘʟ         │
│ ⚠️  ᴡᴀʀɴ ʙᴀᴅ ʙᴏʏs         │
│ 👋  ᴡᴇʟᴄᴏᴍᴇ ɴᴇᴡ ꜰʀɪᴇɴᴅs  │
│ 📝  sᴀᴠᴇ ɴᴏᴛᴇs & ʀᴜʟᴇs   │
│ 🔒  ʟᴏᴄᴋ ᴛʜɪɴɢs ᴜᴡᴜ       │
│ 🌊  sᴛᴏᴘ ꜰʟᴏᴏᴅᴇʀs~        │
└─────────────────────────┘

<i>ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ & ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ✧˖°</i>"""

# Owner only — extra aura 💀
START_OWNER = """\
╔══════════════════════════╗
  👑 ᴍʏ ʟᴏʀᴅ ʜᴀs ᴀʀʀɪᴠᴇᴅ 👑
╚══════════════════════════╝

<i>*ʙᴏᴡs ᴅᴏᴡɴ ᴘʀᴏꜰᴏᴜɴᴅʟʏ*</i> (｡•̀ᴗ-)✧

ᴏᴍɢ ɪᴛ's <b>ᴛʜᴇ ᴏᴡɴᴇʀ</b>!! ᴇᴠᴇʀʏᴛʜɪɴɢ ɪs ʀᴇᴀᴅʏ ꜰᴏʀ ʏᴏᴜ, sᴀᴍᴀ~ 🌸

<b>ʏᴏᴜʀ sᴇᴄʀᴇᴛ ᴄᴍᴅs:</b>
<code>/iam /broadcast /announce</code>
<code>/gban /ungban /gbanlist /stats</code>
<code>/restart /shutdown</code>

💀 <i>ɪᴛ's ᴏᴜʀ sᴇᴄʀᴇᴛ ᴏᴋ? 🤫</i>"""

# Group chat — short sassy
START_GROUP = """\
<i>*teleports behind u*</i>
ɴᴏᴛʜɪɴɢ ᴘᴇʀsᴏɴɴᴇʟ ᴋɪᴅ~ (ง •̀_•́)ง

🌸 <b>LilyBot</b> ɪs ᴏɴʟɪɴᴇ ᴀɴᴅ ʀᴇᴀᴅʏ ᴛᴏ ɢᴜᴀʀᴅ!! ✦
ᴜsᴇ /help ᴛᴏ sᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs~ (◕‿◕✿)"""


# ══════════════════════════════════════════════════════════════
#  ⌨️  INLINE KEYBOARD
# ══════════════════════════════════════════════════════════════

def _keyboard(is_owner: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("📖 Commands~",    callback_data="start_help"),
            InlineKeyboardButton("➕ Add to Group",  url="https://t.me/@liiiilyy_bot?startgroup=true"),
        ],
        [
            InlineKeyboardButton("🌸 GitHub",   url="https://github.com/"),
            InlineKeyboardButton("💬 Support",  url="https://t.me/upper_moon_chat"),
        ],
    ]
    if is_owner:
        rows.append([
            InlineKeyboardButton("👑 Owner Panel~", callback_data="start_owner"),
        ])
    return InlineKeyboardMarkup(rows)


# ══════════════════════════════════════════════════════════════
#  🚀  /start  HANDLER
# ══════════════════════════════════════════════════════════════

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user     = update.effective_user
    chat     = update.effective_chat
    is_owner = user.id == OWNER_ID or user.id in SUDO_USERS

    # ── Group chat — short reply ──────────────────────────────
    if chat.type != "private":
        await update.message.reply_html(START_GROUP)
        return

    # ── Private chat — video + caption below ─────────────────
    caption = START_OWNER if is_owner else START_PRIVATE.format(
        name=user.first_name,
        kw=random.choice(KAWAII_WORDS),
    )
    kb      = _keyboard(is_owner)
    video   = random.choice(START_VIDEOS)

    # Try sending as video with caption embedded below
    sent = False
    try:
        await ctx.bot.send_video(
            chat_id      = chat.id,
            video        = video,
            caption      = caption,
            parse_mode   = ParseMode.HTML,
            reply_markup = kb,
            # supports_streaming=True makes it play instantly without full download
            supports_streaming = True,
        )
        sent = True
    except Exception as e:
        logger.warning(f"send_video failed: {e}")

    # Fallback: try as animation (works for .gif / .mp4)
    if not sent and FALLBACK_ANIMATION:
        try:
            await ctx.bot.send_animation(
                chat_id      = chat.id,
                animation    = FALLBACK_ANIMATION,
                caption      = caption,
                parse_mode   = ParseMode.HTML,
                reply_markup = kb,
            )
            sent = True
        except Exception as e:
            logger.warning(f"send_animation fallback failed: {e}")

    # Final fallback: plain text only (always works)
    if not sent:
        await update.message.reply_html(caption, reply_markup=kb)


# ══════════════════════════════════════════════════════════════
#  🔘  CALLBACK HANDLER  (button taps)
# ══════════════════════════════════════════════════════════════

async def start_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query    = update.callback_query
    user     = query.from_user
    is_owner = user.id == OWNER_ID or user.id in SUDO_USERS
    await query.answer()

    async def _edit(text: str, kb: InlineKeyboardMarkup):
        """Edit caption on video message, else edit text."""
        try:
            await query.edit_message_caption(
                caption      = text,
                parse_mode   = ParseMode.HTML,
                reply_markup = kb,
            )
        except Exception:
            try:
                await query.edit_message_text(
                    text         = text,
                    parse_mode   = ParseMode.HTML,
                    reply_markup = kb,
                )
            except Exception as e:
                logger.warning(f"edit failed: {e}")

    back_btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("« ᴋᴀᴡᴀɪɪ ʙᴀᴄᴋ~ 🌸", callback_data="start_back")
    ]])

    if query.data == "start_help":
        await _edit(HELP_TEXT, back_btn)

    elif query.data == "start_owner":
        if not is_owner:
            await query.answer("nice try lol 💀", show_alert=True)
            return
        await _edit(START_OWNER, InlineKeyboardMarkup([[
            InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data="start_back")
        ]]))

    elif query.data == "start_back":
        caption = START_OWNER if is_owner else START_PRIVATE.format(
            name=user.first_name,
            kw=random.choice(KAWAII_WORDS),
        )
        await _edit(caption, _keyboard(is_owner))


# ══════════════════════════════════════════════════════════════
#  💡  VIDEO URL KAISE ADD KARE
# ══════════════════════════════════════════════════════════════
#
#  Option A — Direct URL (easiest):
#    START_VIDEOS = ["https://your-cdn.com/kawaii.mp4"]
#    Telegram directly URL se video fetch karega
#
#  Option B — Telegram file_id (fastest, no re-upload):
#    1. Apne bot ko video bhejo in private chat
#    2. @RawDataBot ko forward karo — file_id milega
#    3. START_VIDEOS = ["BAACAgIAAxkBAAI..."]
#
#  Option C — Multiple videos (random ek play hoga):
#    START_VIDEOS = [
#        "https://url1.mp4",
#        "https://url2.mp4",
#        "BAACAgIAAxkBAAI...",   # file_id bhi mix kar sakte ho
#    ]
#
# ══════════════════════════════════════════════════════════════
