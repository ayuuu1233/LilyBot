        # handlers/start.py
# ✦ Kawaii autistic start command with GIF + inline buttons ✦
# ─────────────────────────────────────────────────────────────
# Bot.py mein ye lines add karo:
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
#  🎲  KAWAII ASSETS
# ══════════════════════════════════════════════════════════════

# ✅ Ye actual Telegram-hosted GIF file_ids hain — 100% kaam karenge
# Agar koi specific GIF chahiye toh:
#   1. Apne bot ko woh GIF bhejo
#   2. Bot se /id reply karo — file_id milega
#   3. Neeche replace kar do
KAWAII_GIFS = [
    "CgACAgIAAxkBAAIBB2YkAAGVH2QgSwABl2o5XXP5AAFvqQACLxMAAuKhIEtB0trxcBqPDTQE",  # anime wave
    "CgACAgIAAxkBAAIBCGYkAAGWH9iFAAFl0VdZkc3dAAF7qQACMBMAAuKhIEsxnmUfaP5YxzQE",  # kawaii girl
    "CgACAgIAAxkBAAIBCWYkAAGXzQABMsZ2AAFkMQABemqpAAIxEwAC4qEgS2t0AAF5wAABpzQE",  # anime happy
    "CgACAgQAAxkBAAIBCmYkAAGYzQABMsZ2AAFkMAABemqpAAIyEwAC4qEgS9Eq6WOeAAF4KDQE",  # cute nod
]

# Fallback imgur GIF URLs (slower but works if file_ids fail)
KAWAII_GIF_URLS = [
    "https://i.imgur.com/5TJA9IG.gif",
    "https://i.imgur.com/VhQkSZ6.gif",
    "https://i.imgur.com/rWXyEJH.gif",
]

KAWAII_WORDS = [
    "nyaa~",
    "hewwo uwu",
    "h-hai!! (⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)",
    "eep! you found me!! ✧",
    "*pokes head out* o-ohayou~",
    "hiii!!! (ﾉ´ヮ`)ﾉ*: ･ﾟ",
]


# ══════════════════════════════════════════════════════════════
#  📝  MESSAGE TEMPLATES
# ══════════════════════════════════════════════════════════════

START_PRIVATE = """\
╔══════════════════════════╗
  🌸 ʜᴇʟʟᴏ, {name}~ {kw} 🌸
╚══════════════════════════╝

ᴏᴍɢ ʜɪ ʜɪ ʜɪ!! (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧
ɪ'ᴍ <b>LilyBot</b>, ʏᴏᴜʀ ᴜʟᴛʀᴀ ᴋᴀᴡᴀɪɪ ɢʀᴏᴜᴘ ɢᴜᴀʀᴅɪᴀɴ ✦

<b>ᴡʜᴀᴛ ɪ ᴄᴀɴ ᴅᴏ~</b>
┌─────────────────────────┐
│ 🔨 ʙᴀɴ ᴇᴠɪʟ ᴘᴘʟ          │
│ ⚠️  ᴡᴀʀɴ ʙᴀᴅ ʙᴏʏs         │
│ 👋 ᴡᴇʟᴄᴏᴍᴇ ɴᴇᴡ ꜰʀɪᴇɴᴅs   │
│ 📝 sᴀᴠᴇ ɴᴏᴛᴇs & ʀᴜʟᴇs    │
│ 🔒 ʟᴏᴄᴋ ᴛʜɪɴɢs ᴜᴡᴜ        │
│ 🌊 sᴛᴏᴘ ꜰʟᴏᴏᴅᴇʀs~         │
└─────────────────────────┘

<i>ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ & ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ✧˖°</i>"""

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

💀 <i>ɴᴏ ᴏɴᴇ ᴇʟsᴇ ᴄᴀɴ sᴇᴇ ᴛʜɪs~
ɪᴛ's ᴏᴜʀ sᴇᴄʀᴇᴛ ᴏᴋ? 🤫</i>"""

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
            InlineKeyboardButton("➕ Add to Group",  url="https://t.me/liiiilyy_bot?startgroup=true"),
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
#  🚀  /start HANDLER
# ══════════════════════════════════════════════════════════════

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user     = update.effective_user
    chat     = update.effective_chat
    is_owner = user.id == OWNER_ID or user.id in SUDO_USERS

    # Group mein — short sassy reply
    if chat.type != "private":
        await update.message.reply_html(START_GROUP)
        return

    # Private chat — full kawaii experience
    caption = START_OWNER if is_owner else START_PRIVATE.format(
        name=user.first_name,
        kw=random.choice(KAWAII_WORDS),
    )
    kb = _keyboard(is_owner)

    # ── Step 1: Try Telegram file_ids (fastest) ──────────────
    sent = False
    shuffled_ids = KAWAII_GIFS.copy()
    random.shuffle(shuffled_ids)

    for file_id in shuffled_ids:
        try:
            await ctx.bot.send_animation(
                chat_id      = chat.id,
                animation    = file_id,
                caption      = caption,
                parse_mode   = ParseMode.HTML,
                reply_markup = kb,
            )
            sent = True
            break
        except Exception as e:
            logger.warning(f"file_id failed: {e}")
            continue

    # ── Step 2: Fallback — imgur GIF URLs ────────────────────
    if not sent:
        shuffled_urls = KAWAII_GIF_URLS.copy()
        random.shuffle(shuffled_urls)
        for url in shuffled_urls:
            try:
                await ctx.bot.send_animation(
                    chat_id      = chat.id,
                    animation    = url,
                    caption      = caption,
                    parse_mode   = ParseMode.HTML,
                    reply_markup = kb,
                )
                sent = True
                break
            except Exception as e:
                logger.warning(f"URL gif failed: {e}")
                continue

    # ── Step 3: Final fallback — sticker + plain text ────────
    if not sent:
        try:
            await ctx.bot.send_sticker(
                chat_id = chat.id,
                sticker = "CAACAgIAAxkBAAEBKKFl6_QAASmm9FHAAWSf0rV4AAFn7CkAAkYBAAIw1CEFo7A-aZvW7ZQUBA"
            )
        except Exception:
            pass
        await update.message.reply_html(caption, reply_markup=kb)


# ══════════════════════════════════════════════════════════════
#  🔘  CALLBACK HANDLER
# ══════════════════════════════════════════════════════════════

async def start_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query    = update.callback_query
    user     = query.from_user
    is_owner = user.id == OWNER_ID or user.id in SUDO_USERS
    await query.answer()

    async def _edit(text: str, kb: InlineKeyboardMarkup):
        try:
            await query.edit_message_caption(
                caption=text, parse_mode=ParseMode.HTML, reply_markup=kb
            )
        except Exception:
            try:
                await query.edit_message_text(
                    text=text, parse_mode=ParseMode.HTML, reply_markup=kb
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
#  💡  APNA GIF FILE_ID KAISE NIKALE
# ══════════════════════════════════════════════════════════════
#
#  Method 1 — Sabse aasaan:
#    1. @RawDataBot pe koi bhi GIF bhejo
#    2. Woh file_id reply mein dega
#    3. Usse KAWAII_GIFS list mein daal do
#
#  Method 2 — Code se:
#    async def get_file_id(update, ctx):
#        if update.message.animation:
#            print(update.message.animation.file_id)
#    # ye handler add karo bot mein temporarily
#
# ══════════════════════════════════════════════════════════════
