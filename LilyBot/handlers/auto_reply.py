# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
#     🌸 KAWAII AUTO-REPLY SYSTEM 🌸
# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
#
#  SAFE: Bot API only — no userbot, no MTProto
#  SCOPE: Private chats (DM) only
#  ACTION: Read + reply only — never leaves/bans/deletes
#
# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦

import asyncio
import random
import logging
import time

from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
from telegram.constants import ParseMode, ChatAction

logger = logging.getLogger(__name__)


# ✦━━━━━━━━ CONFIG ━━━━━━━━✦

# Paste your Telegram user ID here (get it via @userinfobot)
# Only this person can use /away and /back commands
OWNER_ID = 5158013355  # ← Change this!

# Cooldown in seconds — user won't get a second reply within this time
COOLDOWN_SECONDS = 20 * 60  # 20 minutes


# ✦━━━━━━━━ STATE ━━━━━━━━✦
# Stored in memory — resets on bot restart
# For persistence, replace with a simple JSON/SQLite store

state = {
    "away": False,           # Is away mode ON?
    "custom_msg": None,      # Custom away message (if set)
    "replied_users": {},     # { user_id: timestamp_of_last_reply }
}


# ✦━━━━━━━━ REPLY POOL ━━━━━━━━✦

DEFAULT_REPLIES = [
    "Hiii UwU 💕 I'm not available right now~ I'll reply as soon as I'm back 🥺✨",
    "Anooo~ I'm a bit busy right now 🌸 but I'll text you very soon, okay? 💌",
    "Heyy 😊 I'm currently offline~ please wait a little, I promise I'll reply! 💖",
    "Gomen ne~ I'm away right now 😖 but I'll be back soon and reply to you! 🌷",
    "Kyaa~ not here right now 💤 but don't worry, I'll be back soon! ✨",
    "Uwaa~ I stepped away for a bit 🌙 I'll reply the moment I'm back, Senpai~ 🫶",
    "Ohh noo I missed you 🥺 I'm away right now but I'll text you back very soon 💕",
]


def get_reply(custom_msg: str | None) -> str:
    if custom_msg:
        return custom_msg
    return random.choice(DEFAULT_REPLIES)


def is_on_cooldown(user_id: int) -> bool:
    last = state["replied_users"].get(user_id)
    if last is None:
        return False
    return (time.time() - last) < COOLDOWN_SECONDS


def mark_replied(user_id: int):
    state["replied_users"][user_id] = time.time()


def cooldown_remaining(user_id: int) -> int:
    last = state["replied_users"].get(user_id, 0)
    remaining = COOLDOWN_SECONDS - (time.time() - last)
    return max(0, int(remaining // 60))


# ✦━━━━━━━━ COMMANDS ━━━━━━━━✦

async def cmd_away(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Enable away/auto-reply mode. Owner only."""
    if update.effective_user.id != OWNER_ID:
        return  # Silently ignore non-owners

    state["away"] = True
    state["replied_users"] = {}  # Reset cooldowns on new away session

    await update.message.reply_text(
        "🌙 <b>Away mode ON!</b>\n\n"
        "I'll auto-reply to anyone who DMs you~ 🌸\n"
        "Use /back when you're available again.",
        parse_mode=ParseMode.HTML
    )
    logger.info("Away mode enabled by owner.")


async def cmd_back(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Disable away mode. Owner only."""
    if update.effective_user.id != OWNER_ID:
        return

    state["away"] = False

    await update.message.reply_text(
        "☀️ <b>You're back!</b>\n\n"
        "Auto-reply is now OFF 💕\n"
        "Welcome back, Senpai~ 🫶",
        parse_mode=ParseMode.HTML
    )
    logger.info("Away mode disabled by owner.")


async def cmd_setawaymsg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Set a custom away message. Owner only.
    Usage: /setawaymsg your message here
    """
    if update.effective_user.id != OWNER_ID:
        return

    if not ctx.args:
        await update.message.reply_text(
            "📝 Usage: <code>/setawaymsg your message here</code>\n\n"
            "To reset to random replies, use: <code>/setawaymsg reset</code>",
            parse_mode=ParseMode.HTML
        )
        return

    msg = " ".join(ctx.args).strip()

    if msg.lower() == "reset":
        state["custom_msg"] = None
        await update.message.reply_text(
            "✅ Away message reset to random replies~ 🎲",
            parse_mode=ParseMode.HTML
        )
    else:
        state["custom_msg"] = msg
        await update.message.reply_text(
            f"✅ <b>Away message set!</b>\n\n"
            f"📩 Preview:\n<i>{msg}</i>",
            parse_mode=ParseMode.HTML
        )


async def cmd_awaystatus(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Check current away mode status. Owner only."""
    if update.effective_user.id != OWNER_ID:
        return

    status = "🌙 ON" if state["away"] else "☀️ OFF"
    msg_type = "Custom" if state["custom_msg"] else "Random"
    users_replied = len(state["replied_users"])

    await update.message.reply_text(
        f"📊 <b>Away Mode Status</b>\n\n"
        f"Status: <b>{status}</b>\n"
        f"Message type: <b>{msg_type}</b>\n"
        f"Users replied this session: <b>{users_replied}</b>\n"
        f"Cooldown: <b>{COOLDOWN_SECONDS // 60} minutes</b>",
        parse_mode=ParseMode.HTML
    )


# ✦━━━━━━━━ AUTO-REPLY HANDLER ━━━━━━━━✦

async def handle_dm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Core handler — fires on every private message.
    Safe rules:
      - Only handles private chats (DM)
      - Never acts on group messages
      - Only reads and replies — nothing else
    """
    chat = update.effective_chat
    user = update.effective_user
    message = update.message

    # ── Safety gate 1: Private chats ONLY ──────────
    if chat.type != "private":
        return  # Completely ignore groups/channels

    # ── Safety gate 2: Don't reply to owner's own messages ──
    if user.id == OWNER_ID:
        return

    # ── Safety gate 3: Away mode must be ON ────────
    if not state["away"]:
        return

    # ── Safety gate 4: Cooldown check ──────────────
    if is_on_cooldown(user.id):
        logger.info(
            f"Skipping auto-reply to {user.id} — still on cooldown "
            f"({cooldown_remaining(user.id)} min remaining)"
        )
        return

    # ── Mark as replied BEFORE sending (prevents double-send) ──
    mark_replied(user.id)

    # ── Natural human-like delay: 2–5 seconds ──────
    delay = random.uniform(2.0, 5.0)
    await asyncio.sleep(delay)

    # ── Show "typing..." action ─────────────────────
    try:
        await ctx.bot.send_chat_action(
            chat_id=chat.id,
            action=ChatAction.TYPING
        )
        await asyncio.sleep(random.uniform(1.5, 2.5))  # Realistic typing time
    except Exception as e:
        logger.warning(f"send_chat_action failed: {e}")

    # ── Send the auto-reply ─────────────────────────
    reply_text = get_reply(state["custom_msg"])
    try:
        await message.reply_text(reply_text)
        logger.info(f"Auto-replied to user {user.id} (@{user.username})")
    except Exception as e:
        logger.error(f"Failed to send auto-reply to {user.id}: {e}")


# ✦━━━━━━━━ REGISTER HANDLERS ━━━━━━━━✦
# Call this function from your main bot.py

def register(app):
    """Register all auto-reply handlers into the Application."""

    # Owner commands
    app.add_handler(CommandHandler("away",        cmd_away))
    app.add_handler(CommandHandler("back",        cmd_back))
    app.add_handler(CommandHandler("setawaymsg",  cmd_setawaymsg))
    app.add_handler(CommandHandler("awaystatus",  cmd_awaystatus))

    # DM message handler — private chats only, non-commands
    app.add_handler(MessageHandler(
        filters.ChatType.PRIVATE & ~filters.COMMAND,
        handle_dm
    ))

    logger.info("🌸 Auto-reply system registered.")
