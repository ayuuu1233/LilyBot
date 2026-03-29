# handlers/welcome.py  –  Welcome & Goodbye messages

from telegram import Update, ChatMember
from telegram.ext import ContextTypes

import database as db
from helpers import admin_only, reply

DEFAULT_WELCOME = "👋 Welcome, {mention}! You're member #{count} of {chat}."
DEFAULT_GOODBYE = "👋 {first} has left the group. Goodbye!"


def _get_settings(chat_id: int) -> dict:
    row = db.fetchone("SELECT * FROM welcome_settings WHERE chat_id=?", (chat_id,))
    if row:
        return dict(row)
    return {
        "welcome_enabled": 1,
        "goodbye_enabled": 1,
        "welcome_text": "",
        "goodbye_text": "",
    }


def _format(template: str, user, chat, count: int) -> str:
    return template.format(
        first    = user.first_name,
        last     = user.last_name or "",
        username = f"@{user.username}" if user.username else user.first_name,
        mention  = user.mention_html(),
        chat     = chat.title,
        count    = count,
        id       = user.id,
    )


async def greet_member(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status
    user  = result.new_chat_member.user
    chat  = update.effective_chat

    settings = _get_settings(chat.id)

    # Member joined
    if old_status in (ChatMember.LEFT, ChatMember.BANNED) and new_status == ChatMember.MEMBER:
        if not settings["welcome_enabled"]:
            return
        count = await chat.get_member_count()
        template = settings["welcome_text"] or DEFAULT_WELCOME
        text = _format(template, user, chat, count)
        await ctx.bot.send_message(chat.id, text, parse_mode="HTML")

    # Member left
    elif old_status == ChatMember.MEMBER and new_status in (ChatMember.LEFT, ChatMember.BANNED):
        if not settings["goodbye_enabled"]:
            return
        template = settings["goodbye_text"] or DEFAULT_GOODBYE
        text = _format(template, user, chat, 0)
        await ctx.bot.send_message(chat.id, text, parse_mode="HTML")


@admin_only
async def set_welcome(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        return await reply(update, (
            "Usage: /setwelcome [text]\n\n"
            "Variables: {first} {last} {username} {mention} {chat} {count} {id}"
        ))
    text = " ".join(ctx.args)
    chat_id = update.effective_chat.id
    db.execute(
        "INSERT INTO welcome_settings(chat_id, welcome_text) VALUES(?,?) "
        "ON CONFLICT(chat_id) DO UPDATE SET welcome_text=excluded.welcome_text",
        (chat_id, text)
    )
    await reply(update, f"✅ Welcome message set:\n\n{text}")


@admin_only
async def set_goodbye(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        return await reply(update, "Usage: /setgoodbye [text]\n\nVariables: {first} {last} {username} {mention}")
    text = " ".join(ctx.args)
    chat_id = update.effective_chat.id
    db.execute(
        "INSERT INTO welcome_settings(chat_id, goodbye_text) VALUES(?,?) "
        "ON CONFLICT(chat_id) DO UPDATE SET goodbye_text=excluded.goodbye_text",
        (chat_id, text)
    )
    await reply(update, f"✅ Goodbye message set:\n\n{text}")


@admin_only
async def toggle_welcome(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args or ctx.args[0].lower() not in ("on", "off"):
        return await reply(update, "Usage: /welcome on|off")
    val = 1 if ctx.args[0].lower() == "on" else 0
    chat_id = update.effective_chat.id
    db.execute(
        "INSERT INTO welcome_settings(chat_id, welcome_enabled) VALUES(?,?) "
        "ON CONFLICT(chat_id) DO UPDATE SET welcome_enabled=excluded.welcome_enabled",
        (chat_id, val)
    )
    await reply(update, f"✅ Welcome messages {'enabled' if val else 'disabled'}.")


@admin_only
async def toggle_goodbye(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args or ctx.args[0].lower() not in ("on", "off"):
        return await reply(update, "Usage: /goodbye on|off")
    val = 1 if ctx.args[0].lower() == "on" else 0
    chat_id = update.effective_chat.id
    db.execute(
        "INSERT INTO welcome_settings(chat_id, goodbye_enabled) VALUES(?,?) "
        "ON CONFLICT(chat_id) DO UPDATE SET goodbye_enabled=excluded.goodbye_enabled",
        (chat_id, val)
    )
    await reply(update, f"✅ Goodbye messages {'enabled' if val else 'disabled'}.")


@admin_only
async def reset_welcome(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    db.execute("DELETE FROM welcome_settings WHERE chat_id=?", (update.effective_chat.id,))
    await reply(update, "✅ Welcome/Goodbye settings reset to defaults.")
