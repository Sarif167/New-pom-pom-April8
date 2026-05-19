import asyncio
import logging
import random
import string
import pytz
from datetime import datetime, timedelta
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import enums
from info import (
    VERIFIED_LOG, TIMEZONE, VERIFY_IMG,
    TUTORIAL_LINK, IS_VERIFY,
    ADMIN_USERNAME, PREMIUM_LINK
)
from database.users_db import db
from utils import temp, get_shortlink_av, auto_delete_message
from Script import script
from plugins.send_file import send_requested_file

logger = logging.getLogger(__name__)

# =========================================================
# MAIN VERIFICATION CHECKER
# =========================================================
async def av_x_verification(client, message):
    user_id = message.from_user.id

    # PREMIUM BYPASS
    if await db.has_premium_access(user_id):
        return True

    # VERIFY OFF
    if not IS_VERIFY:
        return True

    # =====================================================
    # 24 HOURS CHECK
    # =====================================================
    user_data = await db.get_user(user_id)

    if user_data:
        last_verified = user_data.get("last_verified")
        is_verified = user_data.get("is_verified", False)

        if last_verified and is_verified:
            ist = pytz.timezone(TIMEZONE)
            now = datetime.now(ist)

            # VERIFIED WITHIN 24 HOURS
            if (now - last_verified) < timedelta(hours=24):
                return True

    # =====================================================
    # GENERATE VERIFY LINK
    # =====================================================
    file_id = None

    if message.command and len(message.command) > 1:
        file_id = message.command[1]

    verify_id = ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=7
        )
    )

    await db.create_verify_id(
        user_id,
        verify_id,
        file_id
    )

    long_url = (
        f"https://telegram.me/"
        f"{temp.U_NAME}?start=avbotz_{user_id}_{verify_id}"
    )

    verify_url = await get_shortlink_av(long_url)

    buttons = [
        [
            InlineKeyboardButton(
                text="⚠️ ᴠᴇʀɪғʏ ⚠️",
                url=verify_url
            ),
            InlineKeyboardButton(
                text="❗ ʜᴏᴡ ᴛᴏ ᴠᴇʀɪғʏ ❗",
                url=TUTORIAL_LINK
            )
        ],
        [
            InlineKeyboardButton(
                text="💎 ᴘʀᴇᴍɪᴜᴍ 💎",
                callback_data="premium"
            ),
            InlineKeyboardButton(
                text="📞 ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ 📞",
                url=f"https://t.me/{ADMIN_USERNAME}"
            )
        ]
    ]

    user_name = message.from_user.first_name

    try:
        bin_text = script.VERIFICATION_TEXT.format(
            user_name,
            "1/1"
        )
    except:
        bin_text = script.VERIFICATION_TEXT.format(user_name)

    dlt = await message.reply_text(
        text=bin_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )

    asyncio.create_task(
        auto_delete_message(message, dlt)
    )

    return False


# =========================================================
# VERIFY SUCCESS HANDLER
# =========================================================
async def verify_user_on_start(client, message):
    try:
        if not message.command or len(message.command) < 2:
            return False

        argument = message.command[1]

        # =====================================================
        # FIRST TIME CLICK FROM CHANNEL POST
        # =====================================================
        if argument.startswith("avx-"):

            check = await av_x_verification(client, message)

            # NOT VERIFIED
            if not check:
                return True

            # VERIFIED → SEND FILE
            search_id = argument.replace("avx-", "")

            await send_requested_file(
                client,
                message,
                message.from_user.id,
                search_id
            )

            return True

        # =====================================================
        # VERIFY LINK CLICK
        # =====================================================
        data = argument.split("_")

        if len(data) < 3:
            return False

        user_id = int(data[1])
        verify_id = data[2]

        if message.from_user.id != user_id:
            await message.reply(
                "<b>This link is not for you!</b>"
            )
            return True

        verify_id_info = await db.get_verify_id_info(
            user_id,
            verify_id
        )

        if (
            not verify_id_info or
            verify_id_info["verified"]
        ):
            await message.reply(
                "<b>Lɪɴᴋ Exᴘɪʀᴇᴅ "
                "ᴏʀ Aʟʀᴇᴀᴅʏ Usᴇᴅ...</b>"
            )
            return True

        ist = pytz.timezone(TIMEZONE)
        current_time = datetime.now(tz=ist)

        # =====================================================
        # SAVE VERIFIED STATUS
        # =====================================================
        await db.update_notcopy_user(
            user_id,
            {
                "last_verified": current_time,
                "is_verified": True
            }
        )

        await db.update_verify_id_info(
            user_id,
            verify_id,
            {
                "verified": True
            }
        )

        stored_file_id = verify_id_info.get("file_id")

        if stored_file_id:
            search_id = stored_file_id.replace("avx-", "")

            # DIRECT FILE SEND AFTER VERIFY
            await send_requested_file(
                client,
                message,
                user_id,
                search_id
            )

        txt = script.VERIFY_COMPLETE_TEXT

        if VERIFIED_LOG:
            try:
                await client.send_message(
                    VERIFIED_LOG,
                    script.VERIFIED_TXT.format(
                        message.from_user.mention,
                        user_id,
                        datetime.now(ist).strftime(
                            '%d_%B_%Y'
                        ),
                        "1"
                    )
                )
            except Exception as e:
                logger.warning(
                    f"Failed to send log: {e}"
                )

        # SUCCESS MESSAGE
        try:
            if VERIFY_IMG:
                await message.reply_photo(
                    photo=VERIFY_IMG,
                    caption=txt.format(
                        message.from_user.mention
                    ),
                    parse_mode=enums.ParseMode.HTML
                )

            else:
                await message.reply_text(
                    text=txt.format(
                        message.from_user.mention
                    ),
                    parse_mode=enums.ParseMode.HTML
                )

        except Exception as e:
            logger.error(f"Verify Error: {e}")

            await message.reply_text(
                text=(
                    f"✅ {message.from_user.mention}, "
                    f"verification complete!"
                ),
                parse_mode=enums.ParseMode.HTML
            )

        return True

    except Exception as e:
        logger.error(f"Verify Error: {e}")
        return False
