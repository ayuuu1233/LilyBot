# handlers/antispam.py  –  Anti-flood protection

import time
from collections import defaultdict
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes

import database as db
from helpers import admin_only, bot_admin_required, reply
from config import DEFAULT_FLOOD_LIMIT

# In-memory tracker: {chat_id: {user_id: [timestamps]}}
_flood_tracker: dict = defaultdict(lambda: defaultdict(list))

FLOOD_WINDOW = 5   # seconds


def _get_limit(chat_id: int) -> int:
    row = db.fetchone("SELECT limit_ FROM flood_settings WHERE chat_id=?", (chat_id,))
    return row["limit_"] if row else DEFAULT_FLOOD_LIMIT


@admin_only
async def set_antiflood(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        return await reply(update, "Usage: /antiflood [number|off]\nExample: /antiflood 5")
    arg = ctx.args[0].lower()
    val = 0 if arg == "off" else (int(arg) if arg.isdigit() else None)
    if val is None:
        return await reply(update, "Usage: /antiflood [number|off]")
    chat_id = update.effective_chat.id
    db.execute(
        "INSERT INTO flood_settings(chat_id,limit_) VALUES(?,?) ON CONFLICT(chat_id) DO UPDATE SET limit_=excluded.limit_",
        (chat_id, val)
    )
    if val == 0:
        await reply(update, "✅ Anti-flood is now <b>disabled</b>.")
    else:
        await reply(update, f"✅ Anti-flood set to <b>{val} messages / {FLOOD_WINDOW}s</b>.\nOffenders will be muted.")


async def flood_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    limit = _get_limit(update.effective_chat.id)
    if limit == 0:
        await reply(update, "🌊 Anti-flood is currently <b>disabled</b>.")
    else:
        await reply(update, f"🌊 Anti-flood limit: <b>{limit} messages / {FLOOD_WINDOW}s</b>")


@bot_admin_required
async def check_flood(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    chat_id = update.effective_chat.id
    user_id = msg.from_user.id if msg.from_user else None
    if not user_id:
        return

    limit = _get_limit(chat_id)
    if limit == 0:
        return

    now = time.time()
    timestamps = _flood_tracker[chat_id][user_id]
    # Keep only messages within the window
    timestamps = [t for t in timestamps if now - t < FLOOD_WINDOW]
    timestamps.append(now)
    _flood_tracker[chat_id][user_id] = timestamps

    if len(timestamps) > limit:
        # Mute the flooder
        try:
            await update.effective_chat.restrict_member(
                user_id, ChatPermissions(can_send_messages=False)
            )
            await msg.reply_html(
                f"🚨 {msg.from_user.mention_html()} has been <b>muted</b> for flooding!"
            )
        except Exception:
            pass
        _flood_tracker[chat_id][user_id] = []
