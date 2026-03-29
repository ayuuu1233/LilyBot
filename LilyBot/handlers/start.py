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

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import OWNER_ID, SUDO_USERS
from handlers.admin import HELP_TEXT   # reuse existing help text


# ══════════════════════════════════════════════════════════════
#  🎲  KAWAII ASSETS  —  edit freely
# ══════════════════════════════════════════════════════════════

# Random GIFs — bot sends one at random each time
# Swap any URL with a Telegram file_id for faster delivery
KAWAII_GIFS = [
    "https://media.tenor.com/x8v1oNUOmg4AAAAd/anime-cute.gif",
    "https://media.tenor.com/GKB0MoP6X-QAAAAd/anime-wave-hello.gif",
    "https://media.tenor.com/pGRLKZQMb1cAAAAd/kawaii-anime.gif",
    "https://media.tenor.com/Vy_fuCGxxEgAAAAd/anime-happy.gif",
    "https://media.tenor.com/7B5PBiX7z5UAAAAd/anime-girl-cute.gif",
]

# Random kawaii greeting word — changes every /start
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

# Shown to normal users in private chat
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

# Shown ONLY to owner — extra aura 💀
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

# Shown in group chats — short & sassy
START_GROUP = """\
<i>*teleports behind u*</i>
ɴᴏᴛʜɪɴɢ ᴘᴇʀsᴏɴɴᴇʟ ᴋɪᴅ~ (ง •̀_•́)ง

🌸 <b>LilyBot</b> ɪs ᴏɴʟɪɴᴇ ᴀɴᴅ ʀᴇᴀᴅʏ ᴛᴏ ɢᴜᴀʀᴅ!! ✦
ᴜsᴇ /help ᴛᴏ sᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs~ (◕‿◕✿)"""


# ══════════════════════════════════════════════════════════════
#  ⌨️  INLINE KEYBOARD BUILDER
# ══════════════════════════════════════════════════════════════

def _keyboard(is_owner: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("📖 Commands~",   callback_data="start_help"),
            # ⬇ Replace with your actual bot username
            InlineKeyboardButton("➕ Add to Group", url="https://t.me/@liiiilyy_bot?startgroup=true"),
        ],
        [
            InlineKeyboardButton("🌸 GitHub",  url="https://github.com/"),
            # ⬇ Replace with your support group link
            InlineKeyboardButton("💬 Support", url="https://t.me/@upper_moon_chat"),
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

    # ── Group chat — quick sassy reply ───────────────────────
    if chat.type != "private":
        await update.message.reply_html(START_GROUP)
        return

    # ── Private chat — full kawaii experience ────────────────
    caption = START_OWNER if is_owner else START_PRIVATE.format(
        name=user.first_name,
        kw=random.choice(KAWAII_WORDS),
    )
    kb  = _keyboard(is_owner)
    gif = random.choice(KAWAII_GIFS)

    try:
        # Send GIF with caption
        await ctx.bot.send_animation(
            chat_id    = chat.id,
            animation  = gif,
            caption    = caption,
            parse_mode = ParseMode.HTML,
            reply_markup = kb,
        )
    except Exception:
        # Fallback: plain text if GIF fails (e.g. bad URL)
        await update.message.reply_html(caption, reply_markup=kb)


# ══════════════════════════════════════════════════════════════
#  🔘  CALLBACK HANDLER  (inline button taps)
# ══════════════════════════════════════════════════════════════

async def start_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query    = update.callback_query
    user     = query.from_user
    is_owner = user.id == OWNER_ID or user.id in SUDO_USERS
    await query.answer()

    async def _edit(text: str, kb: InlineKeyboardMarkup):
        """Edit caption if media message, else edit text."""
        try:
            await query.edit_message_caption(
                caption=text, parse_mode=ParseMode.HTML, reply_markup=kb
            )
        except Exception:
            await query.edit_message_text(
                text=text, parse_mode=ParseMode.HTML, reply_markup=kb
            )

    back_btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("« ᴋᴀᴡᴀɪɪ ʙᴀᴄᴋ~ 🌸", callback_data="start_back")
    ]])

    # ── 📖 Commands button ────────────────────────────────────
    if query.data == "start_help":
        await _edit(HELP_TEXT, back_btn)

    # ── 👑 Owner Panel button ─────────────────────────────────
    elif query.data == "start_owner":
        if not is_owner:
            await query.answer("nice try lol 💀", show_alert=True)
            return
        await _edit(START_OWNER, InlineKeyboardMarkup([[
            InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data="start_back")
        ]]))

    # ── « Back button ─────────────────────────────────────────
    elif query.data == "start_back":
        caption = START_OWNER if is_owner else START_PRIVATE.format(
            name=user.first_name,
            kw=random.choice(KAWAII_WORDS),
        )
        await _edit(caption, _keyboard(is_owner))
