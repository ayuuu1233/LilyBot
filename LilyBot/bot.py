#!/usr/bin/env python3
"""
LilyBot - A MissRose-style Telegram Group Management Bot
"""

import logging
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ChatMemberHandler, filters, CallbackQueryHandler
)
from telegram.request import HTTPXRequest
from telegram.error import NetworkError, TimedOut

from config import BOT_TOKEN
from handlers import (
    admin, welcome,
    filters as filter_handlers,
    warnings, antispam, notes, rules, locks, owner,
    start as start_handler,
    auto_reply,
)
from handlers.start import help_command

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, ctx):
    error = ctx.error
    if isinstance(error, (NetworkError, TimedOut)):
        logger.warning(f"Network hiccup (auto-retrying): {error}")
        return
    logger.error("Unexpected error:", exc_info=error)


def main():

    request = HTTPXRequest(
        connect_timeout=30,
        read_timeout=30,
        write_timeout=30,
        pool_timeout=30,
        http_version="1.1",
    )

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .request(request)
        .build()
    )

    app.add_error_handler(error_handler)

    # ── Admin ───────────────────────────────────────
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

    # ── Warnings ────────────────────────────────────
    app.add_handler(CommandHandler("warn",       warnings.warn))
    app.add_handler(CommandHandler("unwarn",     warnings.unwarn))
    app.add_handler(CommandHandler("warns",      warnings.warns))
    app.add_handler(CommandHandler("warnlimit",  warnings.set_warn_limit))
    app.add_handler(CommandHandler("resetwarns", warnings.reset_warns))

    # ── Welcome ─────────────────────────────────────
    app.add_handler(CommandHandler("setwelcome",   welcome.set_welcome))
    app.add_handler(CommandHandler("setgoodbye",   welcome.set_goodbye))
    app.add_handler(CommandHandler("welcome",      welcome.toggle_welcome))
    app.add_handler(CommandHandler("goodbye",      welcome.toggle_goodbye))
    app.add_handler(CommandHandler("resetwelcome", welcome.reset_welcome))
    app.add_handler(ChatMemberHandler(welcome.greet_member, ChatMemberHandler.CHAT_MEMBER))

    # ── Filters ─────────────────────────────────────
    app.add_handler(CommandHandler("filter",     filter_handlers.add_filter))
    app.add_handler(CommandHandler("stop",       filter_handlers.remove_filter))
    app.add_handler(CommandHandler("filters",    filter_handlers.list_filters))

    # ── Notes ───────────────────────────────────────
    app.add_handler(CommandHandler("save",       notes.save_note))
    app.add_handler(CommandHandler("get",        notes.get_note))
    app.add_handler(CommandHandler("saved",      notes.list_notes))
    app.add_handler(CommandHandler("notes",      notes.list_notes))
    app.add_handler(CommandHandler("clear",      notes.clear_note))

    # ── Rules ───────────────────────────────────────
    app.add_handler(CommandHandler("setrules",   rules.set_rules))
    app.add_handler(CommandHandler("rules",      rules.get_rules))
    app.add_handler(CommandHandler("resetrules", rules.reset_rules))

    # ── Locks ───────────────────────────────────────
    app.add_handler(CommandHandler("lock",       locks.lock))
    app.add_handler(CommandHandler("unlock",     locks.unlock))
    app.add_handler(CommandHandler("locklist",   locks.locklist))

    # ── Anti-spam ───────────────────────────────────
    app.add_handler(CommandHandler("antiflood",  antispam.set_antiflood))
    app.add_handler(CommandHandler("flood",      antispam.flood_status))

    # ── Owner ───────────────────────────────────────
    app.add_handler(CommandHandler("broadcast",  owner.broadcast))
    app.add_handler(CommandHandler("announce",   owner.announce))
    app.add_handler(CommandHandler("gban",       owner.gban))
    app.add_handler(CommandHandler("ungban",     owner.ungban))
    app.add_handler(CommandHandler("gbanlist",   owner.gban_list))
    app.add_handler(CommandHandler("stats",      owner.stats))
    app.add_handler(CommandHandler("shutdown",   owner.shutdown))
    app.add_handler(CommandHandler("restart",    owner.restart))
    app.add_handler(CommandHandler("iam",        owner.iam))

    # ── General ─────────────────────────────────────
    app.add_handler(CommandHandler("start",      start_handler.start))
    app.add_handler(CommandHandler("help",       help_command))
    app.add_handler(CommandHandler("id",         admin.get_id))
    app.add_handler(CommandHandler("info",       admin.user_info))

    # ── Callbacks ───────────────────────────────────
    app.add_handler(CallbackQueryHandler(start_handler.start_callback, pattern="^(help|back)$"))
    app.add_handler(CallbackQueryHandler(warnings.warn_callback,       pattern="^warn_"))

    # ✦ AUTO-REPLY — group=0, fires BEFORE message handlers ✦
    auto_reply.register(app)

    # ── Message handlers — group=1 ───────────────────
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        filter_handlers.check_filters
    ), group=1)
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        notes.check_hashtag_note
    ), group=1)
    app.add_handler(MessageHandler(
        filters.ALL & ~filters.COMMAND,
        antispam.check_flood
    ), group=1)

    logger.info("🌸 LilyBot is running...")

    app.run_polling(
        allowed_updates=["message", "chat_member", "callback_query"],
        drop_pending_updates=True,
        timeout=20,
        read_timeout=30,
        write_timeout=30,
        connect_timeout=30,
        pool_timeout=30,
    )


if __name__ == "__main__":
    main()
