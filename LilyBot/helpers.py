# helpers.py  –  Shared utilities & decorators

import functools
from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from config import SUDO_USERS


# ── Permission checks ────────────────────────────────────────────────────────

async def is_admin(update: Update, user_id: int) -> bool:
    member = await update.effective_chat.get_member(user_id)
    return member.status in (ChatMember.ADMINISTRATOR, ChatMember.OWNER)


def admin_only(func):
    """Decorator: only group admins (or sudo users) may run this command."""
    @functools.wraps(func)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id in SUDO_USERS:
            return await func(update, ctx)
        if not await is_admin(update, user.id):
            await update.message.reply_text("❌ You must be an admin to use this command.")
            return
        return await func(update, ctx)
    return wrapper


def bot_admin_required(func):
    """Decorator: check that the bot itself is an admin."""
    @functools.wraps(func)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        bot_member = await update.effective_chat.get_member(ctx.bot.id)
        if bot_member.status not in (ChatMember.ADMINISTRATOR, ChatMember.OWNER):
            await update.message.reply_text("⚠️ I need to be an admin to do that!")
            return
        return await func(update, ctx)
    return wrapper


# ── Reply helpers ────────────────────────────────────────────────────────────

async def reply(update, text, **kwargs):
    return await update.message.reply_text(text, parse_mode="HTML", **kwargs)

# ── Target resolution ─────────────────────────────────────────────────────────

async def resolve_target(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Return (user_id, mention_html) from reply or first arg."""
    msg = update.message
    if msg.reply_to_message:
        u = msg.reply_to_message.from_user
        return u.id, u.mention_html()
    if ctx.args:
        arg = ctx.args[0]
        if arg.lstrip("-").isdigit():
            uid = int(arg)
            return uid, f"<code>{uid}</code>"
        # username
        username = arg.lstrip("@")
        try:
            chat = await ctx.bot.get_chat(f"@{username}")
            return chat.id, f"@{username}"
        except Exception:
            pass
    return None, None
