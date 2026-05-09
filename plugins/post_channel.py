from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from info import VIDEO_CHANNEL, BRAZZER_CHANNEL, NO_IMG, POST_CHANNEL, POST_SHORTLINK, SEND_POST
from database.users_db import db
from utils import temp, get_shortlink, generate_thumbnail

# -----------------------
# BRAZZERS INDEX
# -----------------------
@Client.on_message(filters.video & filters.chat(BRAZZER_CHANNEL))
async def index_brazzers_videos(_, m: Message):

    file_id = m.video.file_id
    file_unique_id = m.video.file_unique_id

    await db.add_brazzers_video(file_unique_id, file_id)

# -----------------------
# NORMAL VIDEO INDEX
# -----------------------
@Client.on_message(filters.video & filters.chat(VIDEO_CHANNEL))
async def index_normal_videos(client, m: Message):

    try:

        file_id = m.video.file_id
        file_unique_id = m.video.file_unique_id

        # ORIGINAL FILE NAME
        file_name = m.video.file_name

        # DB SAVE
        status = await db.add_video(file_unique_id, file_id)

        if status:
            print(f"✅ New Video Added: {file_name} (Msg ID: {m.id})")
        else:
            print(f"♻️ Duplicate Found: {file_name}")

        # SEND_POST CHECK
        if not SEND_POST:
            return

        # BOT USERNAME
        if not temp.U_NAME:
            me = await client.get_me()
            temp.U_NAME = me.username

        link = f"https://t.me/{temp.U_NAME}?start={file_unique_id}"

        # SHORTLINK
        if POST_SHORTLINK:
            try:
                shortlink = await get_shortlink(link)
            except Exception as e:
                print("Shortlink Error:", e)
                shortlink = link
        else:
            shortlink = link

        # CLEAN FILE NAME
        clean_name = (
            file_name
            .replace(".", " ")
            .replace("_", " ")
            .replace("1080p", "")
            .replace("720p", "")
            .replace("480p", "")
            .replace("WEB-DL", "")
            .replace("HDRip", "")
            .replace("BluRay", "")
        )

        # CAPTION
        caption = (
            f"🎬 <b>{clean_name}</b>\n\n"
            f"⭐ IMDb: 8.5\n"
            f"📥 Paid Content\n\n"
            f"<i>Click below button to buy this file.</i>"
        )

        # BUTTON
        btn = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "💳 Buy File",
                    url=link
                )
            ]
        ])

        # -----------------------
        # THUMBNAIL SYSTEM
        # -----------------------
        thumb_to_send = NO_IMG

        try:

            # TELEGRAM THUMB
            if m.video.thumbs:

                thumb_file = await client.download_media(
                    m.video.thumbs[0].file_id
                )

                if thumb_file:
                    thumb_to_send = thumb_file

            else:

                # GENERATE THUMB
                video_path = await m.download()

                gen_thumb = await generate_thumbnail(video_path)

                if gen_thumb:
                    thumb_to_send = gen_thumb

        except Exception as e:
            print("Thumbnail Error:", e)

        # -----------------------
        # SEND POST
        # -----------------------
        try:

            await client.send_photo(
                chat_id=POST_CHANNEL,
                photo=thumb_to_send,
                caption=caption,
                reply_markup=btn
            )

            print("📸 Post Sent Successfully")

        except Exception as e:

            print("⚠️ Thumbnail Failed:", e)

            await client.send_photo(
                chat_id=POST_CHANNEL,
                photo=NO_IMG,
                caption=caption,
                reply_markup=btn
            )

    except Exception as e:
        print(f"❌ Error in Auto Index: {e}")
