# handlers/locks.py  –  Lock certain message types in the group

from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes

import database as db
from helpers import admin_only, bot_admin_required, reply

LOCK_TYPES = {
    "text":    "can_send_messages",
    "media":   "can_send_other_messages",
    "polls":   "can_send_polls",
    "invite":  "can_invite_users",
    "pin":     "can_pin_messages",
    "info":    "can_change_info",
}


def _get_locks(chat_id: int) -> dict:
    row = db.fetchone("SELECT * FROM locks WHERE chat_id=?", (chat_id,))
    if row:
        return dict(row)
    return {k: 0 for k in LOCK_TYPES}


@admin_only
@bot_admin_required
async def lock(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args or ctx.args[0].lower() not in LOCK_TYPES:
        types = ", ".join(LOCK_TYPES.keys())
        return await reply(update, f"Usage: /lock [type]\nTypes: {types}")

    lock_type = ctx.args[0].lower()
    chat_id   = update.effective_chat.id

    db.execute(
        f"INSERT INTO locks(chat_id, {lock_type}) VALUES(?,1) "
        f"ON CONFLICT(chat_id) DO UPDATE SET {lock_type}=1",
        (chat_id,)
    )

    # Apply via ChatPermissions
    locks = _get_locks(chat_id)
    locks[lock_type] = 1
    perms = _build_permissions(locks)
    await update.effective_chat.set_permissions(perms)
    await reply(update, f"🔒 <b>{lock_type}</b> has been locked.")


@admin_only
@bot_admin_required
async def unlock(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args or ctx.args[0].lower() not in LOCK_TYPES:
        types = ", ".join(LOCK_TYPES.keys())
        return await reply(update, f"Usage: /unlock [type]\nTypes: {types}")

    lock_type = ctx.args[0].lower()
    chat_id   = update.effective_chat.id

    db.execute(
        f"INSERT INTO locks(chat_id, {lock_type}) VALUES(?,0) "
        f"ON CONFLICT(chat_id) DO UPDATE SET {lock_type}=0",
        (chat_id,)
    )
    locks = _get_locks(chat_id)
    locks[lock_type] = 0
    perms = _build_permissions(locks)
    await update.effective_chat.set_permissions(perms)
    await reply(update, f"🔓 <b>{lock_type}</b> has been unlocked.")


async def locklist(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    locks  = _get_locks(update.effective_chat.id)
    lines  = ["<b>🔐 Lock Status:</b>"]
    for lt in LOCK_TYPES:
        status = "🔒 Locked" if locks.get(lt, 0) else "🔓 Unlocked"
        lines.append(f"• {lt}: {status}")
    await reply(update, "\n".join(lines))


def _build_permissions(locks: dict) -> ChatPermissions:
    return ChatPermissions(
        can_send_messages       = not locks.get("text",   0),
        can_send_other_messages = not locks.get("media",  0),
        can_send_polls          = not locks.get("polls",  0),
        can_invite_users        = not locks.get("invite", 0),
        can_pin_messages        = not locks.get("pin",    0),
        can_change_info         = not locks.get("info",   0),
    )
