
# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
#     🌸 KAWAII AUTO-REPLY SYSTEM 🌸
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

OWNER_ID         = 5158013355
COOLDOWN_SECONDS = 2 * 60 * 60  # 2 hours


# ✦━━━━━━━━ STATE ━━━━━━━━✦

state = {
    "away":          False,
    "custom_msg":    None,
    "replied_users": {},
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


# ✦━━━━━━━━ HELPERS ━━━━━━━━✦

def get_reply() -> str:
    if state["custom_msg"]:
        return state["custom_msg"]
    return random.choice(DEFAULT_REPLIES)


def is_on_cooldown(user_id: int) -> bool:
    last = state["replied_users"].get(user_id)
    if last is None:
        return False
    return (time.time() - last) < COOLDOWN_SECONDS


def mark_replied(user_id: int):
    state["replied_users"][user_id] = time.time()


def cooldown_remaining_mins(user_id: int) -> int:
    last = state["replied_users"].get(user_id, 0)
    return max(0, int((COOLDOWN_SECONDS - (time.time() - last)) // 60))


# ✦━━━━━━━━ COMMANDS ━━━━━━━━✦

async def cmd_away(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    state["away"] = True
    state["replied_users"] = {}
    await update.message.reply_text(
        "🌙 <b>Away mode ON!</b>\n\n"
        "Auto-reply active for anyone who DMs~ 🌸\n"
        "Use /back when you return.",
        parse_mode=ParseMode.HTML
    )
    logger.info("Away mode ENABLED.")


async def cmd_back(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    state["away"] = False
    await update.message.reply_text(
        "☀️ <b>You're back!</b>\n\n"
        "Auto-reply is now OFF 💕\n"
        "Welcome back, Senpai~ 🫶",
        parse_mode=ParseMode.HTML
    )
    logger.info("Away mode DISABLED.")


async def cmd_setawaymsg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if not ctx.args:
        await update.message.reply_text(
            "📝 Usage: <code>/setawaymsg your message here</code>\n"
            "Reset: <code>/setawaymsg reset</code>",
            parse_mode=ParseMode.HTML
        )
        return
    msg = " ".join(ctx.args).strip()
    if msg.lower() == "reset":
        state["custom_msg"] = None
        await update.message.reply_text("✅ Reset to random replies~ 🎲")
    else:
        state["custom_msg"] = msg
        await update.message.reply_text(
            f"✅ <b>Away message set!</b>\n\n📩 Preview:\n<i>{msg}</i>",
            parse_mode=ParseMode.HTML
        )


async def cmd_awaystatus(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    status   = "🌙 ON" if state["away"] else "☀️ OFF"
    msg_type = "Custom" if state["custom_msg"] else "Random"
    await update.message.reply_text(
        f"📊 <b>Away Mode Status</b>\n\n"
        f"Status: <b>{status}</b>\n"
        f"Message type: <b>{msg_type}</b>\n"
        f"Users replied: <b>{len(state['replied_users'])}</b>\n"
        f"Cooldown: <b>{COOLDOWN_SECONDS // 60} min</b>",
        parse_mode=ParseMode.HTML
    )


# ✦━━━━━━━━ CORE HANDLER ━━━━━━━━✦

async def handle_dm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type != "private":
        return

    user    = update.effective_user
    message = update.message

    if not message:
        return

    logger.info(f"DM received from {user.id} (@{user.username}) — away={state['away']}")

    if user.id == OWNER_ID:
        return

    if not state["away"]:
        return

    if is_on_cooldown(user.id):
        logger.info(f"Skipping {user.id} — cooldown ({cooldown_remaining_mins(user.id)} min left)")
        return

    mark_replied(user.id)

    await asyncio.sleep(random.uniform(2.0, 5.0))

    try:
        await ctx.bot.send_chat_action(
            chat_id=message.chat.id,
            action=ChatAction.TYPING
        )
        await asyncio.sleep(random.uniform(1.5, 2.5))
    except Exception as e:
        logger.warning(f"send_chat_action failed: {e}")

    try:
        await message.reply_text(get_reply())
        logger.info(f"Auto-replied to {user.id} (@{user.username})")
    except Exception as e:
        logger.error(f"Auto-reply failed for {user.id}: {e}")


# ✦━━━━━━━━ REGISTER ━━━━━━━━✦

def register(app):
    app.add_handler(CommandHandler("away",       cmd_away))
    app.add_handler(CommandHandler("back",       cmd_back))
    app.add_handler(CommandHandler("setawaymsg", cmd_setawaymsg))
    app.add_handler(CommandHandler("awaystatus", cmd_awaystatus))

    # ✦ group=0 — sabse pehle fire hoga, groups bilkul ignore ✦
    app.add_handler(MessageHandler(
        filters.ChatType.PRIVATE & ~filters.COMMAND,
        handle_dm
    ), group=0)

    logger.info("🌸 Auto-reply registered — group=0, private only.")
