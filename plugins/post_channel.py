import asyncio
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from pyrogram.errors import FloodWait

from info import (
    VIDEO_CHANNEL,
    BRAZZER_CHANNEL,
    NO_IMG,
    POST_CHANNEL,
    SEND_POST
)

from database.users_db import db
from utils import (
    temp,
    generate_weird_name,
    generate_thumbnail
)

# -----------------------
# BRAZZERS INDEX
# -----------------------
@Client.on_message(filters.video & filters.chat(BRAZZER_CHANNEL))
async def index_brazzers_videos(_, m: Message):

    file_id = m.video.file_id
    file_unique_id = m.video.file_unique_id

    await db.add_brazzers_video(
        file_unique_id,
        file_id
    )

# -----------------------
# NORMAL VIDEO INDEX
# -----------------------
@Client.on_message(filters.video & filters.chat(VIDEO_CHANNEL))
async def index_normal_videos(client, m: Message):

    try:
        file_id = m.video.file_id
        file_unique_id = m.video.file_unique_id

        # RANDOM FILE NAME
        file_name = generate_weird_name() + ".mp4"

        # SAVE DATABASE
        status = await db.add_video(
            file_unique_id,
            file_id
        )

        if status:
            print(
                f"✅ New Video Added: "
                f"{file_name} (Msg ID: {m.id})"
            )

        else:
            print(
                f"♻️ Duplicate Found: {file_name}"
            )

        # SEND POST CHECK
        if not SEND_POST:
            return

        # BOT USERNAME CACHE
        if not temp.U_NAME:
            me = await client.get_me()
            temp.U_NAME = me.username

        # -----------------------
        # DIRECT BOT LINK
        # -----------------------
        btn = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "📂 ɢᴇᴛ ᴠɪᴅᴇᴏ 📂",
                    url=(
                        f"https://t.me/"
                        f"{temp.U_NAME}"
                        f"?start=avx-{file_unique_id}"
                    )
                )
            ]
        ])

        caption = (
            f"<b>{file_name}</b>\n\n"
            f"<i>Click the button below "
            f"to watch the video.</i>"
        )

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
                try:
                    video_path = await m.download()

                    gen_thumb = await generate_thumbnail(
                        video_path
                    )

                    if gen_thumb:
                        thumb_to_send = gen_thumb

                except Exception as e:
                    print(
                        "⚠️ Thumbnail Generate Error:",
                        e
                    )

        except Exception as e:
            print(
                "⚠️ Thumbnail handling error:",
                e
            )

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

            print(
                "📸 Post sent with thumbnail"
            )

            # ANTI FLOOD
            await asyncio.sleep(2)

        except FloodWait as e:

            print(
                f"⚠️ FloodWait: "
                f"Sleeping for {e.value} seconds"
            )

            await asyncio.sleep(e.value)

            try:
                await client.send_photo(
                    chat_id=POST_CHANNEL,
                    photo=thumb_to_send,
                    caption=caption,
                    reply_markup=btn
                )

            except Exception as er:
                print(
                    "❌ Retry Failed:",
                    er
                )

        except Exception as e:

            print(
                "⚠️ Thumb failed, "
                "sending NO_IMG:",
                e
            )

            try:

                await client.send_photo(
                    chat_id=POST_CHANNEL,
                    photo=NO_IMG,
                    caption=caption,
                    reply_markup=btn
                )

                await asyncio.sleep(2)

            except FloodWait as fw:

                print(
                    f"⚠️ FloodWait NO_IMG: "
                    f"{fw.value} sec"
                )

                await asyncio.sleep(fw.value)

            except Exception as er:
                print(
                    "❌ NO_IMG Failed:",
                    er
                )

    except FloodWait as e:

        print(
            f"⚠️ Global FloodWait: "
            f"{e.value} seconds"
        )

        await asyncio.sleep(e.value)

    except Exception as e:

        print(
            f"❌ Error in Auto Index: {e}"
        )
