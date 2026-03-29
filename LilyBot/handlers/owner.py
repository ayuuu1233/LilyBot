# handlers/owner.py  –  👑 OWNER ONLY COMMANDS  👑
# These commands are EXCLUSIVE to the bot owner. No admin can touch these.

import os
import sys
import time
import logging
from datetime import datetime

from telegram import Update, Bot
from telegram.ext import ContextTypes

import database as db
from config import OWNER_ID, BOT_TOKEN
from helpers import reply

logger = logging.getLogger(__name__)

# Track bot start time for uptime
BOT_START_TIME = time.time()


# ── Owner-only decorator ──────────────────────────────────────────────────────

def owner_only(func):
    import functools
    @functools.wraps(func)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != OWNER_ID:
            await reply(update,
                "👑 <b>OWNER ONLY</b>\n\n"
                "Bhai ye command sirf owner ke liye hai.\n"
                "Teri aukat nahi hai ye use karne ki. 💀"
            )
            return
        return await func(update, ctx)
    return wrapper


# ── Broadcast ─────────────────────────────────────────────────────────────────

@owner_only
async def broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Send a message to ALL groups the bot is in."""
    if not ctx.args:
        return await reply(update,
            "👑 Usage: /broadcast [message]\n"
            "Sends your message to every group this bot is in."
        )

    msg_text = " ".join(ctx.args)
    broadcast_text = f"📢 <b>Broadcast from Owner</b>\n\n{msg_text}"

    # Get all unique chat IDs from DB tables
    chats = set()
    for table in ["welcome_settings", "warn_settings", "flood_settings", "locks", "rules"]:
        try:
            rows = db.fetchall(f"SELECT chat_id FROM {table}")
            for r in rows:
                chats.add(r["chat_id"])
        except Exception:
            pass

    if not chats:
        return await reply(update, "⚠️ No groups found in database yet.")

    sent, failed = 0, 0
    status_msg = await update.message.reply_html(f"📡 Broadcasting to {len(chats)} groups...")

    for chat_id in chats:
        try:
            await ctx.bot.send_message(chat_id, broadcast_text, parse_mode="HTML")
            sent += 1
        except Exception as e:
            logger.warning(f"Broadcast failed for {chat_id}: {e}")
            failed += 1

    await status_msg.edit_text(
        f"✅ Broadcast complete!\n\n"
        f"• Sent: {sent}\n• Failed: {failed}",
        parse_mode="HTML"
    )


# ── Global Ban (GBan) ─────────────────────────────────────────────────────────

@owner_only
async def gban(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Globally ban a user from ALL groups."""
    from helpers import resolve_target
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")

    reason = " ".join(ctx.args[1:]) if ctx.args else "No reason provided"

    # Save to gban list
    db.execute(
        "INSERT OR REPLACE INTO gbans(user_id, reason, banned_by, date) VALUES(?,?,?,?)",
        (uid, reason, OWNER_ID, datetime.now().isoformat())
    )

    # Get all chats and ban
    chats = _get_all_chats()
    banned, failed = 0, 0
    status_msg = await update.message.reply_html(f"🌍 GBanning {mention} from {len(chats)} groups...")

    for chat_id in chats:
        try:
            await ctx.bot.ban_chat_member(chat_id, uid)
            banned += 1
        except Exception:
            failed += 1

    await status_msg.edit_text(
        f"🔨 <b>Global Ban Executed</b>\n\n"
        f"• User: {mention}\n"
        f"• Reason: {reason}\n"
        f"• Banned from: {banned} groups\n"
        f"• Failed: {failed}",
        parse_mode="HTML"
    )


@owner_only
async def ungban(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Remove global ban from a user."""
    from helpers import resolve_target
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")

    row = db.fetchone("SELECT * FROM gbans WHERE user_id=?", (uid,))
    if not row:
        return await reply(update, f"❌ {mention} is not globally banned.")

    db.execute("DELETE FROM gbans WHERE user_id=?", (uid,))

    chats = _get_all_chats()
    unbanned = 0
    for chat_id in chats:
        try:
            await ctx.bot.unban_chat_member(chat_id, uid)
            unbanned += 1
        except Exception:
            pass

    await reply(update, f"✅ {mention} has been <b>globally unbanned</b> from {unbanned} groups.")


@owner_only
async def gban_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    rows = db.fetchall("SELECT user_id, reason, date FROM gbans ORDER BY date DESC LIMIT 20")
    if not rows:
        return await reply(update, "📋 GBan list is empty.")
    lines = ["<b>🌍 Globally Banned Users:</b>"]
    for r in rows:
        lines.append(f"• <code>{r['user_id']}</code> — {r['reason']}")
    await reply(update, "\n".join(lines))


# ── Stats ─────────────────────────────────────────────────────────────────────

@owner_only
async def stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Full bot statistics — owner eyes only."""
    uptime_sec = int(time.time() - BOT_START_TIME)
    h, m, s    = uptime_sec // 3600, (uptime_sec % 3600) // 60, uptime_sec % 60

    total_warns   = db.fetchone("SELECT COUNT(*) as c FROM warnings")["c"]
    total_filters = db.fetchone("SELECT COUNT(*) as c FROM filters")["c"]
    total_notes   = db.fetchone("SELECT COUNT(*) as c FROM notes")["c"]
    total_gbans   = db.fetchone("SELECT COUNT(*) as c FROM gbans")["c"]
    total_groups  = len(_get_all_chats())

    await reply(update,
        f"📊 <b>Bot Statistics</b> — Owner View\n\n"
        f"⏱ Uptime: <code>{h}h {m}m {s}s</code>\n"
        f"👥 Groups: <code>{total_groups}</code>\n"
        f"⚠️ Active Warnings: <code>{total_warns}</code>\n"
        f"🔍 Filters: <code>{total_filters}</code>\n"
        f"📝 Notes: <code>{total_notes}</code>\n"
        f"🌍 GBanned Users: <code>{total_gbans}</code>\n\n"
        f"👑 Only you can see this, boss."
    )


# ── Shutdown ──────────────────────────────────────────────────────────────────

@owner_only
async def shutdown(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await reply(update, "💤 Shutting down... Goodbye, boss. 👑")
    logger.info("Bot shutdown by owner.")
    os.kill(os.getpid(), 9)


# ── Restart ───────────────────────────────────────────────────────────────────

@owner_only
async def restart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await reply(update, "🔄 Restarting bot...")
    logger.info("Bot restart triggered by owner.")
    os.execv(sys.executable, [sys.executable] + sys.argv)


# ── Announce (like broadcast but with bold formatting) ────────────────────────

@owner_only
async def announce(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Send a styled announcement to ALL groups."""
    if not ctx.args:
        return await reply(update, "Usage: /announce [message]")

    text = " ".join(ctx.args)
    announcement = (
        f"📣 <b>ANNOUNCEMENT</b>\n"
        f"{'─' * 25}\n\n"
        f"{text}\n\n"
        f"{'─' * 25}\n"
        f"<i>— Bot Owner</i>"
    )

    chats = _get_all_chats()
    sent = 0
    for chat_id in chats:
        try:
            await ctx.bot.send_message(chat_id, announcement, parse_mode="HTML")
            sent += 1
        except Exception:
            pass

    await reply(update, f"📣 Announcement sent to {sent} groups.")


# ── Owner info (flex command) ─────────────────────────────────────────────────

@owner_only
async def iam(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await reply(update,
        f"👑 <b>OWNER IDENTIFIED</b>\n\n"
        f"Name: {user.full_name}\n"
        f"ID: <code>{user.id}</code>\n"
        f"Username: @{user.username or 'N/A'}\n\n"
        f"🔱 You have <b>FULL CONTROL</b> over this bot.\n"
        f"No one else can touch owner commands. 💀\n\n"
        f"<i>Main commands:\n"
        f"/broadcast – Message all groups\n"
        f"/announce – Styled announcement\n"
        f"/gban – Global ban a user\n"
        f"/ungban – Remove global ban\n"
        f"/gbanlist – View all gbans\n"
        f"/stats – Full bot stats\n"
        f"/restart – Restart bot\n"
        f"/shutdown – Kill the bot</i>"
    )


# ── Helper ────────────────────────────────────────────────────────────────────

def _get_all_chats() -> list:
    chats = set()
    for table in ["welcome_settings", "warn_settings", "flood_settings", "locks", "rules", "notes"]:
        try:
            rows = db.fetchall(f"SELECT chat_id FROM {table}")
            for r in rows:
                if r["chat_id"] < 0:   # negative IDs = groups/channels
                    chats.add(r["chat_id"])
        except Exception:
            pass
    return list(chats)
