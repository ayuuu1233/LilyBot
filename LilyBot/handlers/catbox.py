from telegram import Update
from telegram.ext import ContextTypes
from helpers import reply
import requests
import os
import asyncio
import time

async def catbox(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    if not msg.reply_to_message:
        return await reply(update, "🌸 Reply to a file/image/video senpai~ 💕")

    media = msg.reply_to_message

    file = None
    filename = None

    if media.photo:
        file = await media.photo[-1].get_file()
        filename = f"kawaii_{int(time.time())}.jpg"
    elif media.video:
        file = await media.video.get_file()
        filename = f"kawaii_{int(time.time())}.mp4"
    elif media.document:
        file = await media.document.get_file()
        filename = media.document.file_name or f"kawaii_{int(time.time())}"
    else:
        return await reply(update, "❌ Unsupported media type baka~")

    # 🎀 Initial message
    status = await reply(update, "🌸 <b>Uploading to Catbox...</b>\n\n📥 Downloading file...")

    file_path = filename
    await file.download_to_drive(file_path)

    # 💖 Fake progress animation
    steps = [
        "📦 Preparing file...",
        "🔄 Processing data...",
        "☁️ Uploading to Catbox...",
        "✨ Almost done..."
    ]

    for step in steps:
        await asyncio.sleep(1)
        try:
            await status.edit_text(f"🌸 <b>Uploading to Catbox...</b>\n\n{step}")
        except:
            pass

    try:
        with open(file_path, "rb") as f:
            res = requests.post(
                "https://catbox.moe/user/api.php",
                data={"reqtype": "fileupload"},
                files={"fileToUpload": (filename, f)}
            )

        link = res.text.strip()

        # 🎉 Final message
        await status.edit_text(
            f"🎀 <b>Upload Complete!</b>\n\n"
            f"👤 Uploaded by: {update.effective_user.mention_html()}\n"
            f"📎 File: <code>{filename}</code>\n\n"
            f"🔗 <b>Link:</b>\n{link}\n\n"
            f"(≧◡≦) ♡ Enjoy senpai~ 💕",
            parse_mode="HTML"
        )

    except Exception as e:
        await status.edit_text(
            f"❌ <b>Upload Failed</b>\n\n<code>{e}</code>",
            parse_mode="HTML"
        )

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
