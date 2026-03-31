# handlers/admin.py  –  Ban, Kick, Mute, Pin, Promote, Info …

import asyncio
import logging
import random
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from datetime import timedelta
from telegram import ChatPermissions
import re
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from helpers import admin_only, bot_admin_required, reply, resolve_target
from config import OWNER_ID, SUDO_USERS
from handlers.admin import HELP_TEXT

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

#content = re.sub(r'HELP_TEXT = """.*?"""', new_help, content, flags=re.DOTALL)

#with open("/home/claude/rosebot/handlers/admin.py", "w") as f:
    #f.write(content)


#async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    #if update.effective_chat.type == "private":
        #await reply(update, (
            #"🌹 <b>Hello! I'm LilyBot</b>\n\n"
            #"Add me to a group and make me admin to get started.\n"
            #"Use /help to see all commands."
        #))
    #else:
        #await reply(update, "🌹 I'm alive! Use /help to see commands.")


#async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    #await reply(update, HELP_TEXT)

  # ╔══════════════════════════════════════════════════╗
# ║           handlers/start.py                     ║
# ║   LilyBot — /start  (exact video style)         ║
# ╚══════════════════════════════════════════════════╝
#
# bot.py mein add karo:
#
#   from handlers import start as start_handler
#   app.add_handler(CommandHandler("start", start_handler.start))
#   app.add_handler(CallbackQueryHandler(
#       start_handler.start_callback, pattern="^st_"
#   ))




# ╔══════════════════════════════════════════════════╗
# ║  ⚙️  CONFIG — Bas yahi 6 cheezein badalni hain   ║
# ╚══════════════════════════════════════════════════╝

BOT_NAME       = "LilyBot"
BOT_USERNAME   = "liiiilyy_bot"           # @ ke bina
SUPPORT_GROUP  = "@upper_moon_chat"
UPDATES_LINK   = "https://t.me/upper_moon_chat"

# Sticker file_id — @RawDataBot ko koi sticker bhejo, file_id milega
# Abhi ek default kawaii sticker hai, apna daal sakte ho
STICKER_ID     = "CAACAgIAAxkBAAFGEk9py21yQ49JGa-8KmsC2SjjhlJDIwACLXIAAp0y-Eqfu3A5hCItKToE"

# Video URLs — private chat aur group chat ke liye alag
VIDEO_PRIVATE  = "https://files.catbox.moe/931ph0.mp4"   # ← apna video daalo
VIDEO_GROUP    = "https://files.catbox.moe/dlg0rb.mp4"

# Gate image (support group join nahi kiya toh yeh dikhega)
GATE_IMAGE     = "https://files.catbox.moe/sn06ft.jpg"


# ╔══════════════════════════════════════════════════╗
# ║  📝  CAPTIONS                                   ║
# ╚══════════════════════════════════════════════════╝

_GREETS = [
    "ɴʏᴀᴀ~", "ʜᴇᴡᴡᴏ ᴜᴡᴜ", "ᴏʜᴀʏᴏᴜ~ ✦",
    "ʜ-ʜᴀɪ!! ✨", "ʏᴀʜʜᴏ~ (ﾉ◕ヮ◕)ﾉ", "ᴋᴏɴɴɪᴄʜɪᴡᴀ~ 🌙",
]


def _caption_private(name: str, uid: int) -> str:
    greet = random.choice(_GREETS)
    return (
        f"┬── ⋅ ⋅ ───── ᯽ ───── ⋅ ⋅ ──┬\n"
        f"  {greet} <a href='tg://user?id={uid}'>{name}</a>!\n"
        f"┴── ⋅ ⋅ ───── ᯽ ───── ⋅ ⋅ ──┴\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"  🌸 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ <b>{BOT_NAME}</b>\n"
        f"  ʏᴏᴜʀ ᴋᴀᴡᴀɪɪ ɢʀᴏᴜᴘ ɢᴜᴀʀᴅɪᴀɴ ☄\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n"
        f" 🔨 ʙᴀɴ · ᴋɪᴄᴋ · ᴍᴜᴛᴇ ᴜsᴇʀs\n"
        f" ⚠️  ᴡᴀʀɴ & ᴛʀᴀᴄᴋ ʙᴀᴅ ʙᴏʏs\n"
        f" 👋 ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs\n"
        f" 📝 ɴᴏᴛᴇs · ʀᴜʟᴇs · ꜰɪʟᴛᴇʀs\n"
        f" 🔒 ʟᴏᴄᴋ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴛʏᴘᴇ\n"
        f" 🌊 ᴀɴᴛɪ-ꜰʟᴏᴏᴅ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ\n"
        f"━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n\n"
        f"──────────────────────\n"
        f" sɪᴍᴘʟʏ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ\n"
        f" ᴀɴᴅ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ✧˖°\n"
        f"──────────────────────"
    )


def _caption_owner(name: str, uid: int) -> str:
    return (
        f"┬── ⋅ ⋅ ───── ᯽ ───── ⋅ ⋅ ──┬\n"
        f"  👑 ᴍʏ ʟᴏʀᴅ <a href='tg://user?id={uid}'>{name}</a>!\n"
        f"┴── ⋅ ⋅ ───── ᯽ ───── ⋅ ⋅ ──┴\n\n"
        f"<i>*ʙᴏᴡs ᴅᴏᴡɴ ᴘʀᴏꜰᴏᴜɴᴅʟʏ*</i> (｡•̀ᴗ-)✧\n\n"
        f"ᴇᴠᴇʀʏᴛʜɪɴɢ ɪs ʀᴇᴀᴅʏ ꜰᴏʀ ʏᴏᴜ, sᴀᴍᴀ~ 🌸\n\n"
        f"<b>👑 ᴏᴡɴᴇʀ ᴄᴍᴅs:</b>\n"
        f"<code>/iam</code> · <code>/broadcast</code> · <code>/announce</code>\n"
        f"<code>/gban</code> · <code>/ungban</code> · <code>/stats</code>\n"
        f"<code>/restart</code> · <code>/shutdown</code>\n\n"
        f"💀 <i>ssshhh~ ɪᴛ's ᴏᴜʀ sᴇᴄʀᴇᴛ 🤫</i>"
    )


def _caption_group(name: str, uid: int) -> str:
    return (
        f"<i>*ᴛᴇʟᴇᴘᴏʀᴛs ʙᴇʜɪɴᴅ ᴜ*</i> ɴᴏᴛʜɪɴɢ ᴘᴇʀsᴏɴɴᴇʟ ᴋɪᴅ~\n\n"
        f"👋 ʜᴇʏ <a href='tg://user?id={uid}'>{name}</a>!\n\n"
        f"🌸 <b>{BOT_NAME}</b> ɪs ᴏɴʟɪɴᴇ & ʀᴇᴀᴅʏ ᴛᴏ ɢᴜᴀʀᴅ ✦\n"
        f"ᴜsᴇ /help ꜰᴏʀ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs~ (◕‿◕✿)"
    )


# ╔══════════════════════════════════════════════════╗
# ║  ⌨️  KEYBOARDS                                  ║
# ╚══════════════════════════════════════════════════╝

def _kb_private(is_owner: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            f"✜ ᴀᴅᴅ {BOT_NAME} ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✜",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=new"
        )],
        [
            InlineKeyboardButton("˹ sᴜᴘᴘᴏʀᴛ ˼",  url=f"https://t.me/{SUPPORT_GROUP.lstrip('@')}"),
            InlineKeyboardButton("˹ ᴜᴘᴅᴀᴛᴇs ˼", url=UPDATES_LINK),
        ],
        [InlineKeyboardButton("✧ ʜᴇʟᴘ ✧", callback_data="st_help")],
    ]
    if is_owner:
        rows.append([InlineKeyboardButton("👑 ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ ✦", callback_data="st_owner")])
    return InlineKeyboardMarkup(rows)


def _kb_group() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "Ⰶ ᴘᴍ ᴍᴇ Ⰶ",
            url=f"https://t.me/{BOT_USERNAME}?start=hi"
        )],
        [
            InlineKeyboardButton("ꔷ sᴜᴘᴘᴏʀᴛ ꔷ", url=f"https://t.me/{SUPPORT_GROUP.lstrip('@')}"),
            InlineKeyboardButton("ꔷ ᴜᴘᴅᴀᴛᴇs ꔷ", url=UPDATES_LINK),
        ],
    ])


# Help menu
_KB_HELP_MAIN = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("👮 ᴀᴅᴍɪɴ",   callback_data="st_h_admin"),
        InlineKeyboardButton("📝 ɴᴏᴛᴇs",   callback_data="st_h_notes"),
    ],
    [
        InlineKeyboardButton("🔒 ʟᴏᴄᴋs",   callback_data="st_h_locks"),
        InlineKeyboardButton("👋 ᴡᴇʟᴄᴏᴍᴇ", callback_data="st_h_welcome"),
    ],
    [InlineKeyboardButton("⤾ ʙᴀᴄᴋ", callback_data="st_back")],
])

_KB_BACK_HELP = InlineKeyboardMarkup([[
    InlineKeyboardButton("⤾ ʙᴀᴄᴋ", callback_data="st_help")
]])

_HELP_TEXTS = {
    "st_h_admin": (
        "<b>👮 ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs</b>\n\n"
        "◈ /ban – ʙᴀɴ ᴜsᴇʀ\n"
        "◈ /unban – ᴜɴʙᴀɴ\n"
        "◈ /kick – ᴋɪᴄᴋ ᴜsᴇʀ\n"
        "◈ /mute [ᴛɪᴍᴇ] – ᴍᴜᴛᴇ\n"
        "◈ /unmute – ᴜɴᴍᴜᴛᴇ\n"
        "◈ /warn [ʀᴇᴀsᴏɴ] – ᴡᴀʀɴ\n"
        "◈ /warns – ᴄʜᴇᴄᴋ ᴡᴀʀɴs\n"
        "◈ /warnlimit [ɴ] – sᴇᴛ ʟɪᴍɪᴛ\n"
        "◈ /resetwarns – ʀᴇsᴇᴛ\n"
        "◈ /promote – ᴍᴀᴋᴇ ᴀᴅᴍɪɴ\n"
        "◈ /demote – ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ\n"
        "◈ /pin – ᴘɪɴ ᴍsɢ\n"
        "◈ /unpin – ᴜɴᴘɪɴ\n"
        "◈ /adminlist – ʟɪsᴛ ᴀᴅᴍɪɴs"
    ),
    "st_h_notes": (
        "<b>📝 ɴᴏᴛᴇs, ʀᴜʟᴇs & ꜰɪʟᴛᴇʀs</b>\n\n"
        "◈ /save [ɴ] [ᴛxᴛ] – sᴀᴠᴇ ɴᴏᴛᴇ\n"
        "◈ /get [ɴ] – ɢᴇᴛ ɴᴏᴛᴇ\n"
        "◈ /notes – ʟɪsᴛ ɴᴏᴛᴇs\n"
        "◈ /clear [ɴ] – ᴅᴇʟᴇᴛᴇ\n"
        "◈ #ɴᴀᴍᴇ – ǫᴜɪᴄᴋ ɢᴇᴛ\n\n"
        "◈ /setrules – sᴇᴛ ʀᴜʟᴇs\n"
        "◈ /rules – sʜᴏᴡ ʀᴜʟᴇs\n"
        "◈ /resetrules – ᴄʟᴇᴀʀ\n\n"
        "◈ /filter [ᴋ] [ʀ] – ᴀᴅᴅ\n"
        "◈ /stop [ᴋ] – ʀᴇᴍᴏᴠᴇ\n"
        "◈ /filters – ʟɪsᴛ ᴀʟʟ"
    ),
    "st_h_locks": (
        "<b>🔒 ʟᴏᴄᴋs & ꜰʟᴏᴏᴅ</b>\n\n"
        "◈ /lock [ᴛʏᴘᴇ] – ʟᴏᴄᴋ\n"
        "◈ /unlock [ᴛʏᴘᴇ] – ᴜɴʟᴏᴄᴋ\n"
        "◈ /locklist – sᴛᴀᴛᴜs\n\n"
        "  ᴛʏᴘᴇs:\n"
        "  text · media · polls\n"
        "  invite · pin · info\n\n"
        "◈ /antiflood [ɴ|ᴏꜰꜰ] – sᴇᴛ\n"
        "◈ /flood – ᴄʜᴇᴄᴋ sᴇᴛᴛɪɴɢs"
    ),
    "st_h_welcome": (
        "<b>👋 ᴡᴇʟᴄᴏᴍᴇ & ɢᴏᴏᴅʙʏᴇ</b>\n\n"
        "◈ /setwelcome [ᴛxᴛ] – sᴇᴛ\n"
        "◈ /welcome on|off – ᴛᴏɢɢʟᴇ\n"
        "◈ /setgoodbye [ᴛxᴛ] – sᴇᴛ\n"
        "◈ /goodbye on|off – ᴛᴏɢɢʟᴇ\n"
        "◈ /resetwelcome – ʀᴇsᴇᴛ\n\n"
        "<b>ᴠᴀʀɪᴀʙʟᴇs:</b>\n"
        "<code>{first}</code> <code>{last}</code>\n"
        "<code>{mention}</code> <code>{count}</code>\n"
        "<code>{chat}</code> <code>{id}</code>"
    ),
}


# ╔══════════════════════════════════════════════════╗
# ║  🚀  /start HANDLER                             ║
# ╚══════════════════════════════════════════════════╝

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    user     = update.effective_user
    chat     = update.effective_chat
    uid      = user.id
    name     = user.first_name
    is_owner = uid == OWNER_ID or uid in SUDO_USERS

    # ── GROUP ────────────────────────────────────────────────
    if chat.type != "private":
        try:
            await ctx.bot.send_video(
                chat_id            = chat.id,
                video              = VIDEO_GROUP,
                caption            = _caption_group(name, uid),
                parse_mode         = ParseMode.HTML,
                reply_markup       = _kb_group(),
                supports_streaming = True,
            )
        except Exception:
            await update.message.reply_html(
                _caption_group(name, uid),
                reply_markup=_kb_group()
            )
        return

    # ── PRIVATE ──────────────────────────────────────────────

    # 1️⃣  Support group gate
    try:
        member = await ctx.bot.get_chat_member(SUPPORT_GROUP, uid)
        if member.status == "left":
            await update.message.reply_photo(
                photo        = GATE_IMAGE,
                caption      = (
                    "<b>🚧 ʜᴏʟᴅ ᴜᴘ~</b>\n\n"
                    "ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴊᴏɪɴᴇᴅ ᴏᴜʀ\n"
                    "sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ ʏᴇᴛ~ 🌸\n\n"
                    "<i>ᴊᴏɪɴ ᴛᴏ ᴜɴʟᴏᴄᴋ ᴀʟʟ ꜰᴇᴀᴛᴜʀᴇs!</i>"
                ),
                parse_mode   = ParseMode.HTML,
                reply_markup = InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        "๏ ᴊᴏɪɴ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ ๏",
                        url=f"https://t.me/{SUPPORT_GROUP.lstrip('@')}"
                    )
                ]]),
            )
            return
    except Exception as e:
        logger.warning(f"Gate check skipped: {e}")

    # 2️⃣  Sticker — exact video mein yahi tha sabse pehle
    try:
        await ctx.bot.send_sticker(
            chat_id = chat.id,
            sticker = STICKER_ID,
        )
        await asyncio.sleep(0.6)
    except Exception as e:
        logger.warning(f"Sticker failed: {e}")

    # 3️⃣  Video + caption + buttons
    cap = _caption_owner(name, uid) if is_owner else _caption_private(name, uid)
    kb  = _kb_private(is_owner)

    try:
        await ctx.bot.send_video(
            chat_id            = chat.id,
            video              = VIDEO_PRIVATE,
            caption            = cap,
            parse_mode         = ParseMode.HTML,
            reply_markup       = kb,
            supports_streaming = True,
        )
    except Exception as e:
        logger.warning(f"Video failed: {e}")
        # Fallback — plain text
        await update.message.reply_html(cap, reply_markup=kb)


# ╔══════════════════════════════════════════════════╗
# ║  🔘  CALLBACK HANDLER                           ║
# ╚══════════════════════════════════════════════════╝

async def start_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query    = update.callback_query
    user     = query.from_user
    is_owner = user.id == OWNER_ID or user.id in SUDO_USERS
    data     = query.data
    await query.answer()

    async def _edit(text: str, kb: InlineKeyboardMarkup) -> None:
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

    if data == "st_help":
        await _edit("✧ ᴄʜᴏᴏsᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ~ ✧", _KB_HELP_MAIN)

    elif data in _HELP_TEXTS:
        await _edit(_HELP_TEXTS[data], _KB_BACK_HELP)

    elif data == "st_back":
        cap = _caption_owner(user.first_name, user.id) if is_owner \
              else _caption_private(user.first_name, user.id)
        await _edit(cap, _kb_private(is_owner))

    elif data == "st_owner":
        if not is_owner:
            await query.answer("nice try lol 💀", show_alert=True)
            return
        await _edit(
            _caption_owner(user.first_name, user.id),
            InlineKeyboardMarkup([[
                InlineKeyboardButton("⤾ ʙᴀᴄᴋ", callback_data="st_back")
            ]])
        )


# ╔══════════════════════════════════════════════════╗
# ║  💡  APNA STICKER ID KAISE NIKALE               ║
# ╚══════════════════════════════════════════════════╝
#
#  1. @RawDataBot ko koi sticker bhejo
#  2. Woh file_id reply karega
#  3. STICKER_ID mein paste karo
#
#  Ya bot mein temporarily ye handler add karo:
#
#  async def get_sticker(update, ctx):
#      if update.message.sticker:
#          await update.message.reply_text(
#              update.message.sticker.file_id
#          )
#  app.add_handler(MessageHandler(filters.Sticker.ALL, get_sticker))
#
# ╚══════════════════════════════════════════════════╝      
    

# ── Ban ───────────────────────────────────────────────────────────────────────

@admin_only
@bot_admin_required
async def ban(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")

    reason = " ".join(ctx.args[1:]) if ctx.args and not update.message.reply_to_message else " ".join(ctx.args)
    await update.effective_chat.ban_member(uid)
    text = f"🔨 {mention} has been <b>banned</b>."
    if reason:
        text += f"\n📝 Reason: {reason}"
    await reply(update, text)


@admin_only
@bot_admin_required
async def unban(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")
    await update.effective_chat.unban_member(uid)
    await reply(update, f"✅ {mention} has been <b>unbanned</b>.")


# ── Kick ──────────────────────────────────────────────────────────────────────

@admin_only
@bot_admin_required
async def kick(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")
    await update.effective_chat.ban_member(uid)
    await update.effective_chat.unban_member(uid)   # unban immediately = kick
    await reply(update, f"👟 {mention} has been <b>kicked</b>.")


# ── Mute ──────────────────────────────────────────────────────────────────────

def _parse_time(arg: str):
    """Parse '1h', '30m', '2d' → timedelta or None."""
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    if arg and arg[-1] in units and arg[:-1].isdigit():
        return timedelta(seconds=int(arg[:-1]) * units[arg[-1]])
    return None


@admin_only
@bot_admin_required
async def mute(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")

    duration = None
    remaining_args = list(ctx.args)
    if update.message.reply_to_message and ctx.args:
        duration = _parse_time(ctx.args[0])
    elif not update.message.reply_to_message and len(ctx.args) > 1:
        duration = _parse_time(ctx.args[1])

    no_send = ChatPermissions(can_send_messages=False)
    until = None
    if duration:
        from datetime import datetime, timezone
        until = datetime.now(timezone.utc) + duration

    await update.effective_chat.restrict_member(uid, no_send, until_date=until)
    dur_text = f" for {ctx.args[-1]}" if duration else " indefinitely"
    await reply(update, f"🔇 {mention} has been <b>muted</b>{dur_text}.")


@admin_only
@bot_admin_required
async def unmute(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")
    all_perms = ChatPermissions(
        can_send_messages=True, can_send_polls=True,
        can_send_other_messages=True, can_add_web_page_previews=True,
        can_change_info=False, can_invite_users=True, can_pin_messages=False
    )
    await update.effective_chat.restrict_member(uid, all_perms)
    await reply(update, f"🔊 {mention} has been <b>unmuted</b>.")


# ── Pin ───────────────────────────────────────────────────────────────────────

@admin_only
@bot_admin_required
async def pin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await reply(update, "⚠️ Reply to the message you want to pin.")
    loud = "silent" not in (ctx.args or [])
    await update.message.reply_to_message.pin(disable_notification=not loud)
    await reply(update, "📌 Message pinned.")


@admin_only
@bot_admin_required
async def unpin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await ctx.bot.unpin_chat_message(update.effective_chat.id)
    await reply(update, "📌 Message unpinned.")


# ── Promote / Demote ──────────────────────────────────────────────────────────

@admin_only
@bot_admin_required
async def promote(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")
    await update.effective_chat.promote_member(
        uid,
        can_delete_messages=True, can_restrict_members=True,
        can_pin_messages=True, can_invite_users=True
    )
    await reply(update, f"⭐ {mention} has been <b>promoted</b> to admin.")


@admin_only
@bot_admin_required
async def demote(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")
    await update.effective_chat.promote_member(uid)   # empty = strip all rights
    await reply(update, f"🔽 {mention} has been <b>demoted</b>.")


# ── Admin list ────────────────────────────────────────────────────────────────

async def adminlist(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    admins = await update.effective_chat.get_administrators()
    lines = []
    for a in admins:
        name = a.user.full_name
        tag  = " 👑" if a.status == "creator" else ""
        lines.append(f"• {name}{tag}")
    await reply(update, "<b>Admins in this group:</b>\n" + "\n".join(lines))


# ── ID / Info ─────────────────────────────────────────────────────────────────

async def get_id(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    chat_id = update.effective_chat.id
    if msg.reply_to_message:
        uid = msg.reply_to_message.from_user.id
        await reply(update, f"👤 User ID: <code>{uid}</code>\n💬 Chat ID: <code>{chat_id}</code>")
    else:
        await reply(update, f"👤 Your ID: <code>{msg.from_user.id}</code>\n💬 Chat ID: <code>{chat_id}</code>")


async def user_info(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    lines = [
        f"<b>User Info</b>",
        f"• ID: <code>{target.id}</code>",
        f"• Name: {target.full_name}",
    ]
    if target.username:
        lines.append(f"• Username: @{target.username}")
    lines.append(f"• Link: {target.mention_html()}")
    await reply(update, "\n".join(lines))
