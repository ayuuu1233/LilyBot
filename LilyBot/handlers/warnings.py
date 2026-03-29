# handlers/warnings.py  –  Warn system with auto-action

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import database as db
from helpers import admin_only, bot_admin_required, reply, resolve_target, is_admin
from config import DEFAULT_WARN_LIMIT


def _get_settings(chat_id: int):
    row = db.fetchone("SELECT limit_, action FROM warn_settings WHERE chat_id=?", (chat_id,))
    if row:
        return row["limit_"], row["action"]
    return DEFAULT_WARN_LIMIT, "ban"


def _get_warns(chat_id: int, user_id: int):
    row = db.fetchone("SELECT count, reasons FROM warnings WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    if row:
        return row["count"], row["reasons"].split("||") if row["reasons"] else []
    return 0, []


@admin_only
@bot_admin_required
async def warn(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")

    # Don't warn admins
    if await is_admin(update, uid):
        return await reply(update, "❌ You can't warn an admin.")

    reason = " ".join(ctx.args) if (ctx.args and update.message.reply_to_message) else (
        " ".join(ctx.args[1:]) if ctx.args else ""
    )

    chat_id = update.effective_chat.id
    count, reasons = _get_warns(chat_id, uid)
    count += 1
    if reason:
        reasons.append(reason)

    db.execute(
        "INSERT INTO warnings(chat_id,user_id,count,reasons) VALUES(?,?,?,?) "
        "ON CONFLICT(chat_id,user_id) DO UPDATE SET count=excluded.count, reasons=excluded.reasons",
        (chat_id, uid, count, "||".join(reasons))
    )

    limit, action = _get_settings(chat_id)
    text = f"⚠️ {mention} has been warned! (<b>{count}/{limit}</b>)"
    if reason:
        text += f"\n📝 Reason: {reason}"

    if count >= limit:
        text += f"\n\n🚨 Warn limit reached! Action: <b>{action}</b>"
        if action == "ban":
            await update.effective_chat.ban_member(uid)
        elif action == "kick":
            await update.effective_chat.ban_member(uid)
            await update.effective_chat.unban_member(uid)
        elif action == "mute":
            from telegram import ChatPermissions
            await update.effective_chat.restrict_member(uid, ChatPermissions(can_send_messages=False))
        db.execute("DELETE FROM warnings WHERE chat_id=? AND user_id=?", (chat_id, uid))
    else:
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("🗑 Remove warn", callback_data=f"warn_remove_{uid}"),
        ]])
        return await update.message.reply_html(text, reply_markup=kb)

    await reply(update, text)


@admin_only
async def unwarn(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")

    chat_id = update.effective_chat.id
    count, reasons = _get_warns(chat_id, uid)
    if count == 0:
        return await reply(update, f"{mention} has no warnings.")

    count -= 1
    reasons = reasons[:-1] if reasons else []
    db.execute(
        "UPDATE warnings SET count=?, reasons=? WHERE chat_id=? AND user_id=?",
        (count, "||".join(reasons), chat_id, uid)
    )
    limit, _ = _get_settings(chat_id)
    await reply(update, f"✅ Removed one warning from {mention}. Now at <b>{count}/{limit}</b>.")


async def warns(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        uid = update.effective_user.id
        mention = update.effective_user.mention_html()

    chat_id = update.effective_chat.id
    count, reasons = _get_warns(chat_id, uid)
    limit, _ = _get_settings(chat_id)

    if count == 0:
        return await reply(update, f"{mention} has no warnings. 🎉")

    lines = [f"📋 {mention} has <b>{count}/{limit}</b> warnings:"]
    for i, r in enumerate(reasons, 1):
        lines.append(f"  {i}. {r or '(no reason)'}")
    await reply(update, "\n".join(lines))


@admin_only
async def set_warn_limit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args or not ctx.args[0].isdigit():
        return await reply(update, "Usage: /warnlimit [number]")
    n = max(1, int(ctx.args[0]))
    chat_id = update.effective_chat.id
    db.execute(
        "INSERT INTO warn_settings(chat_id,limit_) VALUES(?,?) ON CONFLICT(chat_id) DO UPDATE SET limit_=excluded.limit_",
        (chat_id, n)
    )
    await reply(update, f"✅ Warn limit set to <b>{n}</b>.")


@admin_only
async def reset_warns(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")
    db.execute("DELETE FROM warnings WHERE chat_id=? AND user_id=?", (update.effective_chat.id, uid))
    await reply(update, f"✅ Warnings for {mention} have been reset.")


async def warn_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not await is_admin(update, query.from_user.id):
        return await query.answer("❌ Admins only.", show_alert=True)

    _, action, uid_str = query.data.split("_", 2)
    uid = int(uid_str)
    chat_id = update.effective_chat.id

    if action == "remove":
        count, reasons = _get_warns(chat_id, uid)
        if count > 0:
            count -= 1
            reasons = reasons[:-1]
            db.execute(
                "UPDATE warnings SET count=?, reasons=? WHERE chat_id=? AND user_id=?",
                (count, "||".join(reasons), chat_id, uid)
            )
        await query.edit_message_text(f"✅ Warning removed by {query.from_user.mention_html()}.", parse_mode="HTML")
