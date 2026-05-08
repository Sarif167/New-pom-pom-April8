from os import environ
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from database.users_db import db
from info import PROTECT_CONTENT, FSUB
import asyncio
from plugins.ban_manager import ban_manager
from utils import temp, auto_delete_message, is_user_joined


@Client.on_message(filters.command("getvideo") | filters.regex(r"(?i)get file"))
async def handle_video_request(client, m: Message):

    # Safety check
    if not m.from_user:
        return

    # Force subscribe check
    if FSUB and not await is_user_joined(client, m):
        return

    user_id = m.from_user.id
    username = m.from_user.username or m.from_user.first_name or "Unknown"

    # Ban check
    if await ban_manager.check_ban(client, m):
        return

    # ------------------------------------------------
    # GET VIDEO
    # ------------------------------------------------

    file_unique_id = None

    # Start se specific video
    if m.command and len(m.command) > 1:
        file_unique_id = m.command[1]

    if file_unique_id:
        file_data = await db.videos.find_one({"file_unique_id": file_unique_id})

        if not file_data:
            return await m.reply("❌ Video not found.")

        video_id = file_data["file_id"]

    else:
        # Random video
        video_id = await db.get_unseen_video(user_id)

        if not video_id:
            try:
                video_id = await db.get_random_video()
            except Exception as e:
                print(f"[Random Video Error] {e}")
                return

        if not video_id:
            return await m.reply("❌ No videos found in database.")

    # ------------------------------------------------
    # SEND VIDEO
    # ------------------------------------------------

    try:
        sent = await client.send_video(
            chat_id=m.chat.id,
            video=video_id,
            protect_content=PROTECT_CONTENT,
            caption=(
                f"𝘗𝘰𝘸𝘦𝘳𝘦𝘥 𝘉𝘺: {temp.B_LINK}

"
                "<blockquote>"
                "ᴛʜɪꜱ ꜰɪʟᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ 10 ᴍɪɴᴜᴛᴇꜱ.
"
                "ᴘʟᴇᴀꜱᴇ ꜰᴏʀᴡᴀʀᴅ ᴛʜɪꜱ ꜰɪʟᴇ ꜱᴏᴍᴇᴡʜᴇʀᴇ ᴇʟꜱᴇ "
                "ᴏʀ ꜱᴀᴠᴇ ɪɴ ꜱᴀᴠᴇᴅ ᴍᴇꜱꜱᴀɢᴇꜱ."
                "</blockquote>"
            ),
            reply_to_message_id=m.id
        )

        await db.increase_video_count(user_id, username)
        asyncio.create_task(auto_delete_message(m, sent))

    except Exception as e:
        await m.reply(f"❌ Failed to send video: {str(e)}")
