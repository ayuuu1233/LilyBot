# LilyBot
# 🌹 LilyBot – Telegram Group Management Bot

A full-featured group management bot inspired by MissRose, built with Python & python-telegram-bot.

---

## ✨ Features

| Module | Commands |
|---|---|
| **Admin** | /ban, /unban, /kick, /mute, /unmute, /pin, /unpin, /promote, /demote, /adminlist |
| **Warnings** | /warn, /unwarn, /warns, /warnlimit, /resetwarns |
| **Welcome** | /setwelcome, /setgoodbye, /welcome on\|off, /goodbye on\|off, /resetwelcome |
| **Filters** | /filter, /stop, /filters |
| **Anti-flood** | /antiflood, /flood |
| **General** | /start, /help, /id, /info |

---

## 🚀 Setup

### 1. Clone / download the files
```
rosebot/
├── bot.py
├── config.py
├── database.py
├── helpers.py
├── requirements.txt
└── handlers/
    ├── admin.py
    ├── antispam.py
    ├── filters.py
    ├── warnings.py
    └── welcome.py
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure the bot
Open `config.py` and set:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"   # From @BotFather
OWNER_ID   = 123456789              # Your Telegram user ID
```

To get your **Bot Token**: message [@BotFather](https://t.me/BotFather) → /newbot

To get your **User ID**: message [@userinfobot](https://t.me/userinfobot)

### 4. Run the bot
```bash
python bot.py
```

### 5. Add to a group
- Add the bot to your Telegram group
- Promote it as **Admin** with these permissions:
  - ✅ Delete messages
  - ✅ Ban users
  - ✅ Restrict members
  - ✅ Pin messages
  - ✅ Add new admins (optional, for /promote)

---

## 📝 Welcome Message Variables

Use these placeholders in `/setwelcome` and `/setgoodbye`:

| Variable | Description |
|---|---|
| `{first}` | User's first name |
| `{last}` | User's last name |
| `{username}` | @username (or first name if none) |
| `{mention}` | Clickable mention |
| `{chat}` | Group name |
| `{count}` | Current member count |
| `{id}` | User's ID |

**Example:**
```
/setwelcome Hey {mention}! Welcome to {chat} 🎉 You're member #{count}!
```

---

## ⚙️ Hosting (keep it online 24/7)

### Option A – VPS (recommended)
Use any cheap VPS (DigitalOcean, Hetzner, Oracle Free Tier) and run with:
```bash
nohup python bot.py &
# or with systemd / screen / tmux
```

### Option B – Railway / Render (free tiers)
- Push the folder to GitHub
- Connect to Railway or Render
- Set `BOT_TOKEN` as an environment variable

### Option C – Locally (for testing)
Just run `python bot.py` – works fine for development.

---

## 🗄️ Database
Uses **SQLite** (file: `rosebot.db`) — zero configuration, auto-created on first run.
For production at scale, you can swap `database.py` to use PostgreSQL.

---

## 📜 License
MIT – free to use and modify.
