# handlers/rules.py  –  Group rules management

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import database as db
from helpers import admin_only, reply


@admin_only
async def set_rules(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        return await reply(update, "Usage: /setrules [rules text]")
    rules = " ".join(ctx.args)
    db.execute(
        "INSERT INTO rules(chat_id, content) VALUES(?,?) ON CONFLICT(chat_id) DO UPDATE SET content=excluded.content",
        (update.effective_chat.id, rules)
    )
    await reply(update, "✅ Rules updated!")


async def get_rules(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    row = db.fetchone("SELECT content FROM rules WHERE chat_id=?", (update.effective_chat.id,))
    if not row or not row["content"]:
        return await reply(update, "❌ No rules set for this group. Admins can set rules with /setrules")

    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("📜 Rules", callback_data="rules_show")
    ]])
    await reply(update, f"📜 <b>Group Rules</b>\n\n{row['content']}", reply_markup=kb)


@admin_only
async def reset_rules(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    db.execute("DELETE FROM rules WHERE chat_id=?", (update.effective_chat.id,))
    await reply(update, "✅ Rules cleared.")
