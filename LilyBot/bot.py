#!/usr/bin/env python3
"""
LilyBot - A MissRose-style Telegram Group Management Bot
"""

import logging
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ChatMemberHandler, filters, CallbackQueryHandler
)

from config import BOT_TOKEN
from handlers import admin, welcome, filters as filter_handlers, warnings, antispam, notes, rules, locks, owner

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # ── Admin commands ──────────────────────────────────────────────────────
    app.add_handler(CommandHandler("ban",        admin.ban))
    app.add_handler(CommandHandler("unban",      admin.unban))
    app.add_handler(CommandHandler("kick",       admin.kick))
    app.add_handler(CommandHandler("mute",       admin.mute))
    app.add_handler(CommandHandler("unmute",     admin.unmute))
    app.add_handler(CommandHandler("pin",        admin.pin))
    app.add_handler(CommandHandler("unpin",      admin.unpin))
    app.add_handler(CommandHandler("promote",    admin.promote))
    app.add_handler(CommandHandler("demote",     admin.demote))
    app.add_handler(CommandHandler("adminlist",  admin.adminlist))

    # ── Warning system ──────────────────────────────────────────────────────
    app.add_handler(CommandHandler("warn",       warnings.warn))
    app.add_handler(CommandHandler("unwarn",     warnings.unwarn))
    app.add_handler(CommandHandler("warns",      warnings.warns))
    app.add_handler(CommandHandler("warnlimit",  warnings.set_warn_limit))
    app.add_handler(CommandHandler("resetwarns", warnings.reset_warns))

    # ── Welcome / Goodbye ───────────────────────────────────────────────────
    app.add_handler(CommandHandler("setwelcome",   welcome.set_welcome))
    app.add_handler(CommandHandler("setgoodbye",   welcome.set_goodbye))
    app.add_handler(CommandHandler("welcome",      welcome.toggle_welcome))
    app.add_handler(CommandHandler("goodbye",      welcome.toggle_goodbye))
    app.add_handler(CommandHandler("resetwelcome", welcome.reset_welcome))
    app.add_handler(ChatMemberHandler(welcome.greet_member, ChatMemberHandler.CHAT_MEMBER))

    # ── Filters / Auto-reply ────────────────────────────────────────────────
    app.add_handler(CommandHandler("filter",     filter_handlers.add_filter))
    app.add_handler(CommandHandler("stop",       filter_handlers.remove_filter))
    app.add_handler(CommandHandler("filters",    filter_handlers.list_filters))

    # ── Notes ───────────────────────────────────────────────────────────────
    app.add_handler(CommandHandler("save",       notes.save_note))
    app.add_handler(CommandHandler("get",        notes.get_note))
    app.add_handler(CommandHandler("saved",      notes.list_notes))
    app.add_handler(CommandHandler("notes",      notes.list_notes))
    app.add_handler(CommandHandler("clear",      notes.clear_note))

    # ── Rules ───────────────────────────────────────────────────────────────
    app.add_handler(CommandHandler("setrules",   rules.set_rules))
    app.add_handler(CommandHandler("rules",      rules.get_rules))
    app.add_handler(CommandHandler("resetrules", rules.reset_rules))

    # ── Locks ───────────────────────────────────────────────────────────────
    app.add_handler(CommandHandler("lock",       locks.lock))
    app.add_handler(CommandHandler("unlock",     locks.unlock))
    app.add_handler(CommandHandler("locklist",   locks.locklist))

    # ── Anti-spam ───────────────────────────────────────────────────────────
    app.add_handler(CommandHandler("antiflood",  antispam.set_antiflood))
    app.add_handler(CommandHandler("flood",      antispam.flood_status))

    # ── 👑 OWNER ONLY ───────────────────────────────────────────────────────
    app.add_handler(CommandHandler("broadcast",  owner.broadcast))
    app.add_handler(CommandHandler("announce",   owner.announce))
    app.add_handler(CommandHandler("gban",       owner.gban))
    app.add_handler(CommandHandler("ungban",     owner.ungban))
    app.add_handler(CommandHandler("gbanlist",   owner.gban_list))
    app.add_handler(CommandHandler("stats",      owner.stats))
    app.add_handler(CommandHandler("shutdown",   owner.shutdown))
    app.add_handler(CommandHandler("restart",    owner.restart))
    app.add_handler(CommandHandler("iam",        owner.iam))

    # ── General ─────────────────────────────────────────────────────────────
    app.add_handler(CommandHandler("start",      admin.start))
    app.add_handler(CommandHandler("help",       admin.help_cmd))
    app.add_handler(CommandHandler("id",         admin.get_id))
    app.add_handler(CommandHandler("info",       admin.user_info))

    # ── Message handlers ─────────────────────────────────────────────────────
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_handlers.check_filters))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, notes.check_hashtag_note))
    app.add_handler(MessageHandler(filters.ALL  & ~filters.COMMAND, antispam.check_flood))
    app.add_handler(CallbackQueryHandler(warnings.warn_callback, pattern="^warn_"))

    logger.info("🌹 LilyBot is running...")
    app.run_polling(allowed_updates=["message", "chat_member", "callback_query"])


if __name__ == "__main__":
    main()
