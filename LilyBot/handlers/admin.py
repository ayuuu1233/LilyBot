# handlers/admin.py  –  Ban, Kick, Mute, Pin, Promote, Info …

from datetime import timedelta
from telegram import Update, ChatPermissions
import re
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from helpers import admin_only, bot_admin_required, reply, resolve_target
from config import SUDO_USERS

HELP_TEXT = """
🌹 <b>LilyBot Commands</b>

<b>Admin Tools</b>
/ban – Ban a user
/unban – Unban a user
/kick – Kick (remove) a user
/mute [time] – Mute a user (e.g. /mute 1h)
/unmute – Unmute a user
/warn [reason] – Warn a user
/unwarn – Remove last warning
/warns – Check warnings
/warnlimit [n] – Set warning limit
/resetwarns – Reset a user's warnings
/promote – Promote to admin
/demote – Demote from admin
/pin – Pin replied message
/unpin – Unpin current pinned message
/adminlist – List group admins

<b>Welcome</b>
/setwelcome [text] – Set welcome message
  Variables: {first}, {last}, {username}, {mention}, {count}
/welcome on|off – Toggle welcome
/setgoodbye [text] – Set goodbye message
/goodbye on|off – Toggle goodbye
/resetwelcome – Reset to default

<b>Filters</b>
/filter [keyword] [reply] – Add a filter
/stop [keyword] – Remove a filter
/filters – List all filters

<b>Anti-Flood</b>
/antiflood [n|off] – Set flood limit (messages/5s)
/flood – Check current flood settings

<b>General</b>
/id – Get chat/user ID
/info – Get user info
/help – Show this message

<b>📝 Notes</b>
/save [name] [text] – Save a note
/get [name] – Get a note (or type #name)
/notes – List all notes
/clear [name] – Delete a note

<b>📜 Rules</b>
/setrules [text] – Set group rules
/rules – Show group rules
/resetrules – Clear rules

<b>🔒 Locks</b>
/lock [type] – Lock message type
/unlock [type] – Unlock message type
/locklist – Show lock status
Types: text, media, polls, invite, pin, info
"""

#content = re.sub(r'HELP_TEXT = """.*?"""', new_help, content, flags=re.DOTALL)

#with open("/home/claude/rosebot/handlers/admin.py", "w") as f:
    #f.write(content)


#async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    #if update.effective_chat.type == "private":
        #await reply(update, (
            #"🌹 <b>Hello! I'm LilyBot</b>\n\n"
            #"Add me to a group and make me admin to get started.\n"
            #"Use /help to see all commands."
        #))
    #else:
        #await reply(update, "🌹 I'm alive! Use /help to see commands.")


#async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    #await reply(update, HELP_TEXT)


# ── Ban ───────────────────────────────────────────────────────────────────────

@admin_only
@bot_admin_required
async def ban(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")

    reason = " ".join(ctx.args[1:]) if ctx.args and not update.message.reply_to_message else " ".join(ctx.args)
    await update.effective_chat.ban_member(uid)
    text = f"🔨 {mention} has been <b>banned</b>."
    if reason:
        text += f"\n📝 Reason: {reason}"
    await reply(update, text)


@admin_only
@bot_admin_required
async def unban(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")
    await update.effective_chat.unban_member(uid)
    await reply(update, f"✅ {mention} has been <b>unbanned</b>.")


# ── Kick ──────────────────────────────────────────────────────────────────────

@admin_only
@bot_admin_required
async def kick(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")
    await update.effective_chat.ban_member(uid)
    await update.effective_chat.unban_member(uid)   # unban immediately = kick
    await reply(update, f"👟 {mention} has been <b>kicked</b>.")


# ── Mute ──────────────────────────────────────────────────────────────────────

def _parse_time(arg: str):
    """Parse '1h', '30m', '2d' → timedelta or None."""
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    if arg and arg[-1] in units and arg[:-1].isdigit():
        return timedelta(seconds=int(arg[:-1]) * units[arg[-1]])
    return None


@admin_only
@bot_admin_required
async def mute(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")

    duration = None
    remaining_args = list(ctx.args)
    if update.message.reply_to_message and ctx.args:
        duration = _parse_time(ctx.args[0])
    elif not update.message.reply_to_message and len(ctx.args) > 1:
        duration = _parse_time(ctx.args[1])

    no_send = ChatPermissions(can_send_messages=False)
    until = None
    if duration:
        from datetime import datetime, timezone
        until = datetime.now(timezone.utc) + duration

    await update.effective_chat.restrict_member(uid, no_send, until_date=until)
    dur_text = f" for {ctx.args[-1]}" if duration else " indefinitely"
    await reply(update, f"🔇 {mention} has been <b>muted</b>{dur_text}.")


@admin_only
@bot_admin_required
async def unmute(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")
    all_perms = ChatPermissions(
        can_send_messages=True, can_send_polls=True,
        can_send_other_messages=True, can_add_web_page_previews=True,
        can_change_info=False, can_invite_users=True, can_pin_messages=False
    )
    await update.effective_chat.restrict_member(uid, all_perms)
    await reply(update, f"🔊 {mention} has been <b>unmuted</b>.")


# ── Pin ───────────────────────────────────────────────────────────────────────

@admin_only
@bot_admin_required
async def pin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await reply(update, "⚠️ Reply to the message you want to pin.")
    loud = "silent" not in (ctx.args or [])
    await update.message.reply_to_message.pin(disable_notification=not loud)
    await reply(update, "📌 Message pinned.")


@admin_only
@bot_admin_required
async def unpin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await ctx.bot.unpin_chat_message(update.effective_chat.id)
    await reply(update, "📌 Message unpinned.")


# ── Promote / Demote ──────────────────────────────────────────────────────────

@admin_only
@bot_admin_required
async def promote(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")
    await update.effective_chat.promote_member(
        uid,
        can_delete_messages=True, can_restrict_members=True,
        can_pin_messages=True, can_invite_users=True
    )
    await reply(update, f"⭐ {mention} has been <b>promoted</b> to admin.")


@admin_only
@bot_admin_required
async def demote(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")
    await update.effective_chat.promote_member(uid)   # empty = strip all rights
    await reply(update, f"🔽 {mention} has been <b>demoted</b>.")


# ── Admin list ────────────────────────────────────────────────────────────────

async def adminlist(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    admins = await update.effective_chat.get_administrators()
    lines = []
    for a in admins:
        name = a.user.full_name
        tag  = " 👑" if a.status == "creator" else ""
        lines.append(f"• {name}{tag}")
    await reply(update, "<b>Admins in this group:</b>\n" + "\n".join(lines))


# ── ID / Info ─────────────────────────────────────────────────────────────────

async def get_id(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    chat_id = update.effective_chat.id
    if msg.reply_to_message:
        uid = msg.reply_to_message.from_user.id
        await reply(update, f"👤 User ID: <code>{uid}</code>\n💬 Chat ID: <code>{chat_id}</code>")
    else:
        await reply(update, f"👤 Your ID: <code>{msg.from_user.id}</code>\n💬 Chat ID: <code>{chat_id}</code>")


async def user_info(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    lines = [
        f"<b>User Info</b>",
        f"• ID: <code>{target.id}</code>",
        f"• Name: {target.full_name}",
    ]
    if target.username:
        lines.append(f"• Username: @{target.username}")
    lines.append(f"• Link: {target.mention_html()}")
    await reply(update, "\n".join(lines))
