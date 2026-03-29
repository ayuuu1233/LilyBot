# config.py  –  Edit these before running the bot

# ── Required ────────────────────────────────────────────────────────────────
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"       # Get from @BotFather
OWNER_ID   = 123456789                  # Your Telegram user ID (int)

# ── Optional ────────────────────────────────────────────────────────────────
# Users with these IDs are treated as sudo/dev admins globally
SUDO_USERS = [OWNER_ID]

# Default max warnings before action (groups can override with /warnlimit)
DEFAULT_WARN_LIMIT = 3

# Default anti-flood threshold (messages per 5 s window; 0 = disabled)
DEFAULT_FLOOD_LIMIT = 5

# SQLite database path (auto-created on first run)
DATABASE = "rosebot.db"
