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

# ══════════════════════════════════════════════════════════════
#  ⚙️  CONFIG  —  Yahan apni values daal do
# ══════════════════════════════════════════════════════════════

SUPPORT_GROUP    = "@upper_moon_chat"           # support group username
BOT_USERNAME     = "liiiilyy_bot"               # apna bot username (@ ke bina)
UPDATES_CHANNEL  = "https://t.me/upper_moon_chat"  # updates channel link

# Private chat video (catbox / direct mp4 link ya Telegram file_id)
VIDEO_URL        = "https://files.catbox.moe/931ph0.mp4"  # ← APNA VIDEO DAALO

# Group chat video
VIDEO_URL_GROUP  = "https://files.catbox.moe/dlg0rb.mp4"  # ← GROUP VIDEO

# Image shown when user hasn't joined support group
GATE_IMAGE_URL   = "https://files.catbox.moe/sn06ft.jpg"   # ← APNI IMAGE DAALO


# ══════════════════════════════════════════════════════════════
#  💬  CAPTIONS
# ══════════════════════════════════════════════════════════════

# Private chat — normal user
def caption_private(first_name: str, user_id: int) -> str:
    kw = random.choice([
        "nyaa~", "hewwo uwu", "h-hai!! (⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)",
        "eep! you found me!! ✧", "o-ohayou~ ✦",
    ])
    return (
        f"┬── ⋅ ⋅ ───── ᯽ ───── ⋅ ⋅ ──┬\n"
        f"  Kση'ηɪᴄʜɪᴡᴧ <a href='tg://user?id={user_id}'>{first_name}</a>! {kw}\n"
        f"┴── ⋅ ⋅ ───── ᯽ ───── ⋅ ⋅ ──┴\n\n"
        f"────────────────────────────\n"
        f"│  🌸 ᴡєʟᴄσϻє ᴛσ <b>LilyBot</b>  │\n"
        f"│  ʏσυꝛ ᴋᴀᴡᴀɪɪ ɢʀᴏᴜᴘ ɢᴜᴀʀᴅɪᴀɴ ☄ │\n"
        f"────────────────────────────\n\n"
        f"━━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n"
        f" 🔨 ʙᴀɴ · ᴋɪᴄᴋ · ᴍᴜᴛᴇ ᴇᴠɪʟ ᴘᴘʟ\n"
        f" ⚠️  ᴡᴀʀɴ ᴀɴᴅ ᴛʀᴀᴄᴋ ʙᴀᴅ ʙᴏʏs\n"
        f" 👋 ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs\n"
        f" 📝 ɴᴏᴛᴇs · ʀᴜʟᴇs · ꜰɪʟᴛᴇʀs\n"
        f" 🔒 ʟᴏᴄᴋ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴛʏᴘᴇ\n"
        f" 🌊 ᴀɴᴛɪ-ꜰʟᴏᴏᴅ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ\n"
        f"━━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n\n"
        f"──────────────────────────\n"
        f" sɪᴍᴘʟʏ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ\n"
        f" ᴀɴᴅ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ✧˖°\n"
        f"──────────────────────────"
    )


# Private chat — owner
def caption_owner(first_name: str, user_id: int) -> str:
    return (
        f"╔══════════════════════════╗\n"
        f"  👑 ᴍʏ ʟᴏʀᴅ ʜᴀs ᴀʀʀɪᴠᴇᴅ 👑\n"
        f"╚══════════════════════════╝\n\n"
        f"<i>*ʙᴏᴡs ᴅᴏᴡɴ ᴘʀᴏꜰᴏᴜɴᴅʟʏ*</i> (｡•̀ᴗ-)✧\n\n"
        f"ᴏᴍɢ ɪᴛ's <a href='tg://user?id={user_id}'><b>ᴛʜᴇ ᴏᴡɴᴇʀ</b></a>!!\n"
        f"ᴇᴠᴇʀʏᴛʜɪɴɢ ɪs ʀᴇᴀᴅʏ ꜰᴏʀ ʏᴏᴜ, sᴀᴍᴀ~ 🌸\n\n"
        f"<b>ʏᴏᴜʀ sᴇᴄʀᴇᴛ ᴄᴍᴅs:</b>\n"
        f"<code>/iam /broadcast /announce</code>\n"
        f"<code>/gban /ungban /gbanlist /stats</code>\n"
        f"<code>/restart /shutdown</code>\n\n"
        f"💀 <i>ɪᴛ's ᴏᴜʀ sᴇᴄʀᴇᴛ ᴏᴋ? 🤫</i>"
    )


# DM sent to user showing their own profile info
def caption_dm(first_name: str, username: str, user_id: int) -> str:
    uname = f"@{username}" if username else "N/A"
    return (
        f"ㅤ<b>ʜᴀs sᴛᴀʀᴛᴇᴅ LilyBot.</b>\n\n"
        f"• <b>ɴᴀᴍᴇ :</b> {first_name}\n"
        f"• <b>ᴜsᴇʀɴᴀᴍᴇ :</b> {uname}\n"
        f"• <b>ɪᴅ :</b> <code>{user_id}</code>\n\n"
        f"<i>ᴛʜᴀɴᴋs ꜰᴏʀ sᴛᴀʀᴛɪɴɢ ᴍᴇ~ 🌸</i>"
    )


# Group chat caption
def caption_group(first_name: str, user_id: int) -> str:
    return (
        f"<i>*teleports behind u*</i>\n"
        f"ɴᴏᴛʜɪɴɢ ᴘᴇʀsᴏɴɴᴇʟ ᴋɪᴅ~ (ง •̀_•́)ง\n\n"
        f"👋 ʜɪ <a href='tg://user?id={user_id}'>{first_name}</a>!\n\n"
        f"🌸 <b>LilyBot</b> ɪs ᴏɴʟɪɴᴇ ᴀɴᴅ ʀᴇᴀᴅʏ ᴛᴏ ɢᴜᴀʀᴅ!! ✦\n"
        f"ᴜsᴇ /help ᴛᴏ sᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs~ (◕‿◕✿)"
    )


# ══════════════════════════════════════════════════════════════
#  ⌨️  KEYBOARDS
# ══════════════════════════════════════════════════════════════

def keyboard_private(is_owner: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            "✜ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✜",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=new"
        )],
        [
            InlineKeyboardButton("˹ sᴜᴘᴘᴏʀᴛ ˼",  url=f"https://t.me/{SUPPORT_GROUP.lstrip('@')}"),
            InlineKeyboardButton("˹ ᴜᴘᴅᴀᴛᴇs ˼", url=UPDATES_CHANNEL),
        ],
        [InlineKeyboardButton("✧ ʜᴇʟᴘ ✧", callback_data="help_main")],
    ]
    if is_owner:
        rows.append([InlineKeyboardButton("👑 Owner Panel~", callback_data="start_owner")])
    return InlineKeyboardMarkup(rows)


def keyboard_group() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "Ⰶ ᴘᴍ ᴍᴇ Ⰶ",
            url=f"https://t.me/{BOT_USERNAME}?start=true"
        )],
        [
            InlineKeyboardButton("ꔷ sᴜᴘᴘᴏʀᴛ ꔷ",  url=f"https://t.me/{SUPPORT_GROUP.lstrip('@')}"),
            InlineKeyboardButton("ꔷ ᴜᴘᴅᴀᴛᴇs ꔷ", url=UPDATES_CHANNEL),
        ],
    ])


HELP_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("👮 ᴀᴅᴍɪɴ ᴄᴍᴅs",   callback_data="help_admin")],
    [InlineKeyboardButton("📝 ɴᴏᴛᴇs & ʀᴜʟᴇs", callback_data="help_notes")],
    [InlineKeyboardButton("🔒 ʟᴏᴄᴋs & ꜰʟᴏᴏᴅ", callback_data="help_locks")],
    [InlineKeyboardButton("⤾ ʙᴀᴄᴋ",           callback_data="help_back")],
])

HELP_ADMIN_TEXT = """\
<b>👮 ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs</b>

◈ /ban – ʙᴀɴ ᴀ ᴜsᴇʀ
◈ /unban – ᴜɴʙᴀɴ ᴀ ᴜsᴇʀ
◈ /kick – ᴋɪᴄᴋ ᴀ ᴜsᴇʀ
◈ /mute [ᴛɪᴍᴇ] – ᴍᴜᴛᴇ ᴀ ᴜsᴇʀ
◈ /unmute – ᴜɴᴍᴜᴛᴇ ᴀ ᴜsᴇʀ
◈ /warn [ʀᴇᴀsᴏɴ] – ᴡᴀʀɴ ᴀ ᴜsᴇʀ
◈ /warns – ᴄʜᴇᴄᴋ ᴡᴀʀɴɪɴɢs
◈ /promote – ᴘʀᴏᴍᴏᴛᴇ ᴛᴏ ᴀᴅᴍɪɴ
◈ /demote – ᴅᴇᴍᴏᴛᴇ ꜰʀᴏᴍ ᴀᴅᴍɪɴ
◈ /pin – ᴘɪɴ ᴀ ᴍᴇssᴀɢᴇ
◈ /adminlist – ʟɪsᴛ ᴀʟʟ ᴀᴅᴍɪɴs"""

HELP_NOTES_TEXT = """\
<b>📝 ɴᴏᴛᴇs & ʀᴜʟᴇs</b>

◈ /save [ɴᴀᴍᴇ] [ᴛᴇxᴛ] – sᴀᴠᴇ ᴀ ɴᴏᴛᴇ
◈ /get [ɴᴀᴍᴇ] – ɢᴇᴛ ᴀ ɴᴏᴛᴇ
◈ /notes – ʟɪsᴛ ᴀʟʟ ɴᴏᴛᴇs
◈ /clear [ɴᴀᴍᴇ] – ᴅᴇʟᴇᴛᴇ ᴀ ɴᴏᴛᴇ
◈ #ɴᴀᴍᴇ – ǫᴜɪᴄᴋ ɢᴇᴛ ɴᴏᴛᴇ

◈ /setrules [ᴛᴇxᴛ] – sᴇᴛ ɢʀᴏᴜᴘ ʀᴜʟᴇs
◈ /rules – sʜᴏᴡ ʀᴜʟᴇs
◈ /resetrules – ᴄʟᴇᴀʀ ʀᴜʟᴇs

◈ /filter [ᴋᴇʏ] [ʀᴇᴘʟʏ] – ᴀᴅᴅ ꜰɪʟᴛᴇʀ
◈ /stop [ᴋᴇʏ] – ʀᴇᴍᴏᴠᴇ ꜰɪʟᴛᴇʀ
◈ /filters – ʟɪsᴛ ꜰɪʟᴛᴇʀs"""

HELP_LOCKS_TEXT = """\
<b>🔒 ʟᴏᴄᴋs & ꜰʟᴏᴏᴅ</b>

◈ /lock [ᴛʏᴘᴇ] – ʟᴏᴄᴋ ᴍᴇssᴀɢᴇ ᴛʏᴘᴇ
◈ /unlock [ᴛʏᴘᴇ] – ᴜɴʟᴏᴄᴋ
◈ /locklist – sʜᴏᴡ ʟᴏᴄᴋ sᴛᴀᴛᴜs
  ᴛʏᴘᴇs: text · media · polls · invite · pin · info

◈ /antiflood [ɴ|ᴏꜰꜰ] – sᴇᴛ ꜰʟᴏᴏᴅ ʟɪᴍɪᴛ
◈ /flood – ᴄʜᴇᴄᴋ ꜰʟᴏᴏᴅ sᴇᴛᴛɪɴɢs

◈ /setwelcome [ᴛᴇxᴛ] – sᴇᴛ ᴡᴇʟᴄᴏᴍᴇ
◈ /welcome on|off – ᴛᴏɢɢʟᴇ ᴡᴇʟᴄᴏᴍᴇ
◈ /setgoodbye [ᴛᴇxᴛ] – sᴇᴛ ɢᴏᴏᴅʙʏᴇ"""


# ══════════════════════════════════════════════════════════════
#  🚀  /start  HANDLER
# ══════════════════════════════════════════════════════════════

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    user      = update.effective_user
    chat      = update.effective_chat
    user_id   = user.id
    first_name = user.first_name
    username  = user.username
    is_owner  = user_id == OWNER_ID or user_id in SUDO_USERS

    # ── GROUP CHAT ────────────────────────────────────────────
    if chat.type != "private":
        try:
            await ctx.bot.send_video(
                chat_id      = chat.id,
                video        = VIDEO_URL_GROUP,
                caption      = caption_group(first_name, user_id),
                parse_mode   = ParseMode.HTML,
                reply_markup = keyboard_group(),
                supports_streaming = True,
            )
        except Exception as e:
            logger.warning(f"Group video failed: {e}")
            await update.message.reply_html(
                caption_group(first_name, user_id),
                reply_markup=keyboard_group()
            )
        return

    # ── PRIVATE CHAT ──────────────────────────────────────────

    # Step 1 — Check if user joined support group
    try:
        member = await ctx.bot.get_chat_member(SUPPORT_GROUP, user_id)
        if member.status == "left":
            join_kb = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "๏ ᴊᴏɪɴ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ ๏",
                    url=f"https://t.me/{SUPPORT_GROUP.lstrip('@')}"
                )
            ]])
            await update.message.reply_photo(
                photo   = GATE_IMAGE_URL,
                caption = (
                    "๏ ᴏᴏᴘs! ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴊᴏɪɴᴇᴅ ᴏᴜʀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ ʏᴇᴛ~\n\n"
                    "ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴛᴏ ᴀᴄᴄᴇss ᴍʏ ꜰᴇᴀᴛᴜʀᴇs! 🌸"
                ),
                reply_markup = join_kb,
                parse_mode   = ParseMode.HTML,
            )
            return
    except Exception as e:
        logger.warning(f"Support group check failed (continuing anyway): {e}")
        # Agar check fail ho toh rokna nahi — continue karo

    # Step 2 — Animated emoji burst (🎀 🦋 🌸)
    for emoji in ["🎀", "🦋", "🌸"]:
        try:
            msg = await update.message.reply_text(emoji)
            await asyncio.sleep(0.8)
            await msg.delete()
        except Exception:
            pass

    # Step 3 — "Starting..." flash
    try:
        starting = await update.message.reply_text("Starting... 🌸")
        await asyncio.sleep(0.8)
        await starting.delete()
    except Exception:
        pass

    # Step 4 — Send user's own profile pic as DM (self-info card)
    try:
        photos = await ctx.bot.get_user_profile_photos(user_id, limit=1)
        photo  = photos.photos[0][0].file_id if photos.total_count > 0 else None

        dm_kb = InlineKeyboardMarkup([[
            InlineKeyboardButton(first_name, url=f"tg://user?id={user_id}")
        ]])

        if photo:
            await ctx.bot.send_photo(
                chat_id      = user_id,
                photo        = photo,
                caption      = caption_dm(first_name, username, user_id),
                parse_mode   = ParseMode.HTML,
                reply_markup = dm_kb,
            )
        else:
            await ctx.bot.send_message(
                chat_id      = user_id,
                text         = caption_dm(first_name, username, user_id),
                parse_mode   = ParseMode.HTML,
                reply_markup = dm_kb,
            )
    except Exception as e:
        logger.warning(f"DM profile card failed: {e}")

    # Step 5 — Main video + caption + buttons
    cap = caption_owner(first_name, user_id) if is_owner else caption_private(first_name, user_id)
    kb  = keyboard_private(is_owner)

    try:
        await ctx.bot.send_video(
            chat_id          = chat.id,
            video            = VIDEO_URL,
            caption          = cap,
            parse_mode       = ParseMode.HTML,
            reply_markup     = kb,
            supports_streaming = True,
        )
    except Exception as e:
        logger.warning(f"Video send failed: {e}")
        # Fallback: plain text
        await update.message.reply_html(cap, reply_markup=kb)


# ══════════════════════════════════════════════════════════════
#  🔘  CALLBACK HANDLER
# ══════════════════════════════════════════════════════════════

async def start_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query    = update.callback_query
    user     = query.from_user
    is_owner = user.id == OWNER_ID or user.id in SUDO_USERS
    data     = query.data
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

    back_to_main_kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("⤾ ʙᴀᴄᴋ", callback_data="help_back")
    ]])

    # ── Help menu ─────────────────────────────────────────────
    if data == "help_main":
        await _edit(
            "✧ ᴄʜᴏᴏsᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ~ ✧",
            HELP_KEYBOARD
        )

    elif data == "help_admin":
        await _edit(HELP_ADMIN_TEXT, back_to_main_kb)

    elif data == "help_notes":
        await _edit(HELP_NOTES_TEXT, back_to_main_kb)

    elif data == "help_locks":
        await _edit(HELP_LOCKS_TEXT, back_to_main_kb)

    elif data == "help_back":
        cap = caption_owner(user.first_name, user.id) if is_owner else caption_private(user.first_name, user.id)
        await _edit(cap, keyboard_private(is_owner))

    # ── Owner panel ───────────────────────────────────────────
    elif data == "start_owner":
        if not is_owner:
            await query.answer("nice try lol 💀", show_alert=True)
            return
        await _edit(
            caption_owner(user.first_name, user.id),
            InlineKeyboardMarkup([[
                InlineKeyboardButton("⤾ ʙᴀᴄᴋ", callback_data="help_back")
            ]])
    )

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
