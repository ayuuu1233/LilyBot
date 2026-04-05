# handlers/admin.py  –  Ban, Kick, Mute, Pin, Promote, Info …

from datetime import timedelta
from telegram import ChatPermissions
import re
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from helpers import admin_only, bot_admin_required, reply, resolve_target
from config import OWNER_ID, SUDO_USERS
from handlers.admin import HELP_TEXT

LOG_CHANNEL_ID = -1001945969614  # log channel ID

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

import asyncio
from telegram.constants import ChatAction

async def kawaii_typing(update):
    try:
        await update.effective_chat.send_action(ChatAction.TYPING)
        await asyncio.sleep(1.5)  # delay feel
    except:
        pass

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
    #await reply(update, HELP_TEXT)) 
     

# ── Ban ───────────────────────────────────────────────────────────────────────

@admin_only
@bot_admin_required
async def ban(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")

    reason = " ".join(ctx.args)
    await update.effective_chat.ban_member(uid)

    import random

    messages = [
        f"🌸 <b>Ban Event ~ UwU</b>\n\n👤 {mention}\n🔨 Status: Banned 🚫\n\n💖 By: {update.effective_user.mention_html()}\n\n(｡•̀︿•̀｡) Rules are rules~",

        f"⚡ <b>Kawaii Justice!</b>\n\n👤 {mention} has been removed 💀\n🚪 Access denied!\n\n✨ Admin: {update.effective_user.mention_html()}\n\nBehave next time baka~ 😏",

        f"🔥 <b>Ban Hammer Activated!</b>\n\n👤 {mention} got yeeted 🚫\n💥 Chaos eliminated!\n\n💖 By: {update.effective_user.mention_html()}",

        f"🎀 <b>System Action</b>\n\n👤 {mention} is no longer here ✨\n🔒 Permanently banned!\n\n💖 {update.effective_user.mention_html()}\n\nAra ara~ too naughty 😈"
    ]

    text = random.choice(messages)

    if reason:
        text += f"\n\n📝 <b>Reason:</b> {reason}"

    await reply(update, text, parse_mode=ParseMode.HTML)



from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import random
from datetime import datetime

@admin_only
@bot_admin_required
async def unban(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await kawaii_typing(update)

    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")

    await update.effective_chat.unban_member(uid)

    time_now = datetime.now().strftime("%H:%M")

    # 💖 Kawaii Messages
    messages = [
        f"🌸 <b>Unban Event ~ UwU</b>\n\n👤 {mention}\n🔓 Ban lifted ✨\n\n💖 By: {update.effective_user.mention_html()}\n⏰ {time_now}\n\nWelcome back senpai~ 💕",

        f"🎀 <b>Second Chance Granted!</b>\n\n👤 {mention} is free again 💬✨\n🚪 Door opened!\n\n💖 Admin: {update.effective_user.mention_html()}",

        f"✨ <b>Kawaii Mercy Activated!</b>\n\n👤 {mention} has been unbanned 🎉\n\n(｡•̀ᴗ-)✧ behave nicely this time 😏"
    ]

    # 😈 Inline Button
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Kick Again 👟", callback_data=f"kick_{uid}")]
    ])

    await reply(
        update,
        random.choice(messages),
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )

    # 📜 LOG CHANNEL
    if LOG_CHANNEL_ID:
        try:
            await ctx.bot.send_message(
                LOG_CHANNEL_ID,
                f"🔓 <b>Unban Log</b>\n\n👤 User: {mention}\n👮 Admin: {update.effective_user.mention_html()}\n💬 Chat: {update.effective_chat.title}",
                parse_mode=ParseMode.HTML
            )
        except:
            pass

# ── Kick ──────────────────────────────────────────────────────────────────────

@admin_only
@bot_admin_required
async def kick(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")

    await update.effective_chat.ban_member(uid)
    await update.effective_chat.unban_member(uid)   # kick logic

    import random

    messages = [
        f"🌸 <b>Kick Event ~ UwU</b>\n\n👤 {mention}\n👟 Status: Kicked 🚪\n\n💖 By: {update.effective_user.mention_html()}\n\nCome back nicely senpai~ 💕",

        f"🎀 <b>Kawaii Push!</b>\n\n👤 {mention} has been removed 💨\n🚪 Out you go!\n\n✨ Admin: {update.effective_user.mention_html()}\n\nBehave next time baka~ 😏",

        f"⚡ <b>Quick Remove!</b>\n\n👤 {mention} got kicked 👟\n💥 Chaos controlled!\n\n💖 By: {update.effective_user.mention_html()}",

        f"🌷 <b>System Action</b>\n\n👤 {mention} is out for now ✨\n🚪 Temporary removal complete!\n\n💖 {update.effective_user.mention_html()}\n\nAra ara~ try again later 😈"
    ]

    await reply(update, random.choice(messages), parse_mode=ParseMode.HTML)

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

    import random
    dur_text = f" for {ctx.args[-1]}" if duration else " indefinitely"

    messages = [
        f"🌸 <b>Mute Event ~ UwU</b>\n\n👤 {mention}\n🔇 Status: Muted{dur_text} 🤫\n\n💖 By: {update.effective_user.mention_html()}\n\nShhh~ be quiet senpai 💕",

        f"🎀 <b>Silence Mode Activated!</b>\n\n👤 {mention} can't talk{dur_text} 💬❌\n\n✨ Admin: {update.effective_user.mention_html()}\n\n(｡-_-｡) Peace restored~",

        f"⚡ <b>Mute Spell Cast!</b>\n\n👤 {mention} lost voice{dur_text} 💀\n\n💖 By: {update.effective_user.mention_html()}\n\nNo talking allowed baka~ 😏",

        f"🌷 <b>System Action</b>\n\n👤 {mention} is now silenced{dur_text} ✨\n🔇 Chat restricted!\n\n💖 {update.effective_user.mention_html()}\n\nAra ara~ too noisy 😈"
    ]

    await reply(update, random.choice(messages), parse_mode=ParseMode.HTML)



@admin_only
@bot_admin_required
async def unmute(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await kawaii_typing(update)

    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")

    all_perms = ChatPermissions(
        can_send_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_change_info=False,
        can_invite_users=True,
        can_pin_messages=False
    )

    await update.effective_chat.restrict_member(uid, all_perms)

    import random
    from datetime import datetime
    time_now = datetime.now().strftime("%H:%M")

    messages = [
        f"🌸 <b>Unmute Event ~ UwU</b>\n\n👤 {mention}\n🔊 Voice restored ✨\n\n💖 By: {update.effective_user.mention_html()}\n⏰ {time_now}",
        f"🎀 <b>Kawaii Freedom!</b>\n\n👤 {mention} can talk again 💬✨\n🔓 Spell broken!",
        f"✨ <b>Voice Returned!</b>\n\n👤 {mention} is unmuted 🎉"
    ]

    # 😈 Inline Button
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Warn Again 😈", callback_data=f"warn_{uid}")]
    ])

    msg = await reply(update, random.choice(messages), parse_mode=ParseMode.HTML, reply_markup=keyboard)

    # 📜 LOG CHANNEL MESSAGE
    if LOG_CHANNEL_ID:
        try:
            await ctx.bot.send_message(
                LOG_CHANNEL_ID,
                f"🔊 <b>Unmute Log</b>\n\n👤 User: {mention}\n👮 Admin: {update.effective_user.mention_html()}\n💬 Chat: {update.effective_chat.title}",
                parse_mode=ParseMode.HTML
            )
        except:
            pass

# ── Pin ───────────────────────────────────────────────────────────────────────

@admin_only
@bot_admin_required
async def pin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await reply(update, "⚠️ Reply to the message you want to pin.")

    loud = "silent" not in (ctx.args or [])
    await update.message.reply_to_message.pin(disable_notification=not loud)

    import random

    messages = [
        f"🌸 <b>Pin Event ~ UwU</b>\n\n📌 Message pinned successfully ✨\n\n💖 By: {update.effective_user.mention_html()}\n\nKeep it safe senpai~ 💕",

        f"🎀 <b>Kawaii Pin!</b>\n\n📌 This message is now important 💬✨\n\n✨ Admin: {update.effective_user.mention_html()}\n\nDon't ignore it baka~ 😏",

        f"⚡ <b>Highlight Activated!</b>\n\n📌 Message pinned at the top 🔝\n\n💖 By: {update.effective_user.mention_html()}\n\nNotice it properly 👀",

        f"🌷 <b>System Action</b>\n\n📌 Message secured ✨\n🔝 Now visible for everyone!\n\n💖 {update.effective_user.mention_html()}\n\nAra ara~ important info 😈"
    ]

    await reply(update, random.choice(messages), parse_mode=ParseMode.HTML)


@admin_only
@bot_admin_required
async def unpin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await ctx.bot.unpin_chat_message(update.effective_chat.id)

    import random

    messages = [
        f"🌸 <b>Unpin Event ~ UwU</b>\n\n📌 Message unpinned ✨\n\n💖 By: {update.effective_user.mention_html()}\n\nAll clear now senpai~ 💕",

        f"🎀 <b>Kawaii Update!</b>\n\n📌 Message removed from top 💬\n\n✨ Admin: {update.effective_user.mention_html()}\n\nNo longer important baka~ 😏",

        f"⚡ <b>Pin Released!</b>\n\n📌 Message is no longer pinned 🔓\n\n💖 By: {update.effective_user.mention_html()}",

        f"🌷 <b>System Action</b>\n\n📌 Highlight removed ✨\n🔽 Back to normal chat\n\n💖 {update.effective_user.mention_html()}\n\nAra ara~ done 😈"
    ]

    await reply(update, random.choice(messages), parse_mode=ParseMode.HTML)


# ── Promote / Demote ──────────────────────────────────────────────────────────

@admin_only
@bot_admin_required
async def promote(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")

    await update.effective_chat.promote_member(
        uid,
        can_delete_messages=True,
        can_restrict_members=True,
        can_pin_messages=True,
        can_invite_users=True
    )

    import random

    messages = [
        f"👑 <b>Promotion Event ~ UwU</b>\n\n👤 {mention}\n⭐ Status: Promoted to Admin ✨\n\n💖 By: {update.effective_user.mention_html()}\n\nWelcome to the elite ranks senpai~ 💕",

        f"🌸 <b>Kawaii Power Up!</b>\n\n👤 {mention} is now an admin ⚡\n🔐 Authority granted!\n\n✨ By: {update.effective_user.mention_html()}\n\nUse your powers wisely baka~ 😏",

        f"⚡ <b>Rank Upgrade!</b>\n\n👤 {mention} leveled up 👑\n💥 New powers unlocked!\n\n💖 Admin: {update.effective_user.mention_html()}",

        f"🎀 <b>System Promotion</b>\n\n👤 {mention} has ascended ✨\n👑 Admin role granted!\n\n💖 {update.effective_user.mention_html()}\n\nAra ara~ big responsibility 😈"
    ]

    await reply(update, random.choice(messages), parse_mode=ParseMode.HTML)


@admin_only
@bot_admin_required
async def demote(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, mention = await resolve_target(update, ctx)
    if not uid:
        return await reply(update, "⚠️ Reply to a user or provide a username/ID.")

    await update.effective_chat.promote_member(uid)  # remove all rights

    import random

    messages = [
        f"🔽 <b>Demotion Event ~ UwU</b>\n\n👤 {mention}\n💔 Status: Demoted\n\n💖 By: {update.effective_user.mention_html()}\n\nPower removed senpai~ 😔",

        f"🌸 <b>Kawaii Downgrade!</b>\n\n👤 {mention} lost admin powers ⚡\n🔓 Authority revoked!\n\n✨ By: {update.effective_user.mention_html()}\n\nBetter luck next time baka~ 😏",

        f"⚡ <b>Rank Lost!</b>\n\n👤 {mention} has been demoted 💀\n📉 Powers removed!\n\n💖 Admin: {update.effective_user.mention_html()}",

        f"🎀 <b>System Update</b>\n\n👤 {mention} is no longer an admin ✨\n🔽 Back to normal user\n\n💖 {update.effective_user.mention_html()}\n\nAra ara~ responsibility was too much 😈"
    ]

    await reply(update, random.choice(messages), parse_mode=ParseMode.HTML)

# ── Admin list ────────────────────────────────────────────────────────────────

async def adminlist(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    admins = await update.effective_chat.get_administrators()

    owner = None
    admins_list = []

    for a in admins:
        user = a.user
        mention = user.mention_html()
        name = user.full_name

        if a.status == "creator":
            owner = f"👑 <b>Owner :</b> {mention}"
        else:
            # 💖 Role detection
            if a.can_promote_members:
                role = "𝐂𝐎-𝐎𝐖𝐍𝐄𝐑 ⚡"
            elif a.can_restrict_members:
                role = "𝐀𝐃𝐌𝐈𝐍 🔰"
            elif a.can_delete_messages:
                role = "𝐌𝐎𝐃 🛡️"
            else:
                role = "𝐄𝐋𝐈𝐓𝐄 💎"

            admins_list.append(f"• 『 {name} 』 - {role}")

    text = (
        "👮 <b>Admin List</b>:\n\n"
        f"{owner if owner else ''}\n\n"
        + "\n".join(admins_list)
    )

    await reply(update, text, parse_mode=ParseMode.HTML)


# ── ID / Info ─────────────────────────────────────────────────────────────────

async def get_id(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    chat_id = update.effective_chat.id

    if msg.reply_to_message:
        user = msg.reply_to_message.from_user
        text = (
            f"🌸 <b>ID Lookup ~ UwU</b>\n\n"
            f"👤 <b>User:</b> {user.mention_html()}\n"
            f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
            f"💬 <b>Chat ID:</b> <code>{chat_id}</code>\n\n"
            f"(｡•̀ᴗ-)✧ Found successfully!"
        )
    else:
        user = msg.from_user
        text = (
            f"🌸 <b>Your Info ~ UwU</b>\n\n"
            f"👤 <b>You:</b> {user.mention_html()}\n"
            f"🆔 <b>Your ID:</b> <code>{user.id}</code>\n"
            f"💬 <b>Chat ID:</b> <code>{chat_id}</code>\n\n"
            f"💖 Keep it safe senpai~"
        )

    await reply(update, text, parse_mode=ParseMode.HTML)

async def user_info(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user

    import random

    headers = [
        "🌸 <b>User Profile ~ UwU</b>",
        "🎀 <b>Kawaii Info Card</b>",
        "✨ <b>User Data Loaded!</b>",
        "🌷 <b>Profile Scan Complete</b>"
    ]

    text = [
        random.choice(headers),
        "",
        f"👤 <b>Name:</b> {target.full_name}",
        f"🆔 <b>ID:</b> <code>{target.id}</code>"
    ]

    if target.username:
        text.append(f"📛 <b>Username:</b> @{target.username}")
    else:
        text.append(f"📛 <b>Username:</b> <i>None</i>")

    text.append(f"🔗 <b>Profile Link:</b> {target.mention_html()}")

    # 💖 Extra flavor line
    extras = [
        "(≧◡≦) ♡ Looking cool senpai~",
        "UwU such a mysterious user~ 😏",
        "✨ Data looks clean and powerful!",
        "Ara ara~ interesting profile 👀"
    ]

    text.append("")
    text.append(random.choice(extras))

    await reply(update, "\n".join(text), parse_mode=ParseMode.HTML)

#----------- warn --------------------------------------------------------
from telegram.ext import CallbackQueryHandler

async def warn_button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("warn_"):
        return

    uid = int(query.data.split("_")[1])

    await query.edit_message_text(
        f"⚠️ User warned!\nID: <code>{uid}</code>\n\n(｡•̀︿•̀｡) behave please!",
        parse_mode=ParseMode.HTML
    )
