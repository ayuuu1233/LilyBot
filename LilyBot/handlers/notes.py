# handlers/notes.py  –  Save & retrieve notes per group

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import database as db
from helpers import admin_only, reply


@admin_only
async def save_note(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if len(ctx.args) < 2:
        return await reply(update, "Usage: /save [name] [content]\nOr reply to a message with /save [name]")

    name    = ctx.args[0].lower()
    content = " ".join(ctx.args[1:])

    # If replying to a message, use that as content
    if update.message.reply_to_message and len(ctx.args) == 1:
        content = update.message.reply_to_message.text or ""

    chat_id = update.effective_chat.id
    db.execute(
        "INSERT INTO notes(chat_id, name, content) VALUES(?,?,?) "
        "ON CONFLICT(chat_id, name) DO UPDATE SET content=excluded.content",
        (chat_id, name, content)
    )
    await reply(update, f"📝 Note <code>#{name}</code> saved!")


async def get_note(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        return await reply(update, "Usage: /get [name]  or just type  #notename")
    name = ctx.args[0].lower().lstrip("#")
    row  = db.fetchone("SELECT content FROM notes WHERE chat_id=? AND name=?",
                       (update.effective_chat.id, name))
    if not row:
        return await reply(update, f"❌ Note <code>#{name}</code> not found.")
    await reply(update, f"📌 <b>#{name}</b>\n\n{row['content']}")


async def list_notes(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    rows = db.fetchall("SELECT name FROM notes WHERE chat_id=?", (update.effective_chat.id,))
    if not rows:
        return await reply(update, "No notes saved in this group.")
    names = [f"• <code>#{r['name']}</code>" for r in rows]
    await reply(update, "<b>📋 Saved Notes:</b>\n" + "\n".join(names) +
                "\n\n<i>Use /get [name] or type #name to retrieve.</i>")


@admin_only
async def clear_note(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        return await reply(update, "Usage: /clear [name]")
    name = ctx.args[0].lower().lstrip("#")
    db.execute("DELETE FROM notes WHERE chat_id=? AND name=?", (update.effective_chat.id, name))
    await reply(update, f"🗑 Note <code>#{name}</code> deleted.")


async def check_hashtag_note(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Auto-respond when someone types #notename"""
    msg = update.message
    if not msg or not msg.text:
        return
    words = msg.text.split()
    for word in words:
        if word.startswith("#") and len(word) > 1:
            name = word[1:].lower()
            row  = db.fetchone("SELECT content FROM notes WHERE chat_id=? AND name=?",
                               (update.effective_chat.id, name))
            if row:
                await msg.reply_html(f"📌 <b>#{name}</b>\n\n{row['content']}")
                break
