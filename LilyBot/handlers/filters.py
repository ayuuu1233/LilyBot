# handlers/filters.py  –  Keyword filters & auto-replies

from telegram import Update
from telegram.ext import ContextTypes

import database as db
from helpers import admin_only, reply


@admin_only
async def add_filter(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if len(ctx.args) < 2:
        return await reply(update, "Usage: /filter [keyword] [response text]")
    keyword  = ctx.args[0].lower()
    response = " ".join(ctx.args[1:])
    chat_id  = update.effective_chat.id
    db.execute(
        "INSERT INTO filters(chat_id,keyword,response) VALUES(?,?,?) "
        "ON CONFLICT(chat_id,keyword) DO UPDATE SET response=excluded.response",
        (chat_id, keyword, response)
    )
    await reply(update, f"✅ Filter <code>{keyword}</code> saved.")


@admin_only
async def remove_filter(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        return await reply(update, "Usage: /stop [keyword]")
    keyword = ctx.args[0].lower()
    chat_id = update.effective_chat.id
    db.execute("DELETE FROM filters WHERE chat_id=? AND keyword=?", (chat_id, keyword))
    await reply(update, f"✅ Filter <code>{keyword}</code> removed.")


async def list_filters(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    rows = db.fetchall("SELECT keyword FROM filters WHERE chat_id=?", (update.effective_chat.id,))
    if not rows:
        return await reply(update, "No filters set in this group.")
    keywords = [r["keyword"] for r in rows]
    await reply(update, "<b>Active filters:</b>\n" + "\n".join(f"• <code>{k}</code>" for k in keywords))


async def check_filters(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return
    text    = msg.text.lower()
    chat_id = update.effective_chat.id
    rows    = db.fetchall("SELECT keyword, response FROM filters WHERE chat_id=?", (chat_id,))
    for row in rows:
        if row["keyword"] in text:
            await msg.reply_text(row["response"], parse_mode="HTML")
            break
