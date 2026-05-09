import datetime
import asyncio

from pyrogram import Client, filters, enums
from pyrogram.types import *
from pyrogram.errors import *

from Script import script
from database.users_db import db

from info import (
    START_PIC,
    LOG_CHANNEL,
    PREMIUM_LOGS,
    FSUB,
    QR_CODE_IMAGE,
    DAILY_LIMIT,
    PREMIUM_DAILY_LIMIT,
    UPI_ID
)

from utils import temp, is_user_joined
from plugins.verification import verify_user_on_start
from plugins.send_file import send_requested_file
from plugins.refer import refer_on_start


# =================================================
# 🚀 START COMMAND
# =================================================

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):

    user_id = message.from_user.id
    mention = message.from_user.mention
    me2 = (await client.get_me()).mention

    if FSUB and not await is_user_joined(client, message):
        return

    argument = message.command[1] if len(message.command) > 1 else None

    # =========================================
    # VERIFY SYSTEM
    # =========================================

    if argument and argument.startswith('avbotz'):
        await verify_user_on_start(client, message)
        return

    # =========================================
    # PREMIUM PAGE
    # =========================================

    if argument == "premium":

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "💎 Buy 1 Day - ₹5",
                    callback_data="buy_1day"
                )
            ]
        ])

        return await message.reply_text(
            "<blockquote>💎 Premium Plans\n\n"
            "✅ 1 Day Access\n"
            "✅ Unlimited Files\n"
            "✅ Instant Access</blockquote>",
            reply_markup=buttons
        )

    # =========================================
    # TERMS / HELP / ABOUT
    # =========================================

    if argument == "terms":
        await send_legal_text(client, message, script.TERMS_TXT)
        return

    elif argument == "disclaimer":
        await send_legal_text(client, message, script.DISCLAIMER_TXT)
        return

    elif argument == "help":
        await send_legal_text(client, message, script.HELP_TXT)
        return

    elif argument == "about":
        await send_about_text(client, message)
        return

    # =========================================
    # REFERRAL
    # =========================================

    if argument and argument.startswith("reff_"):

        try:
            await refer_on_start(client, message)
            return

        except Exception as e:
            print(f"Referral Error: {e}")

    # =========================================
    # PREMIUM PROTECTED FILE ACCESS
    # =========================================

    if argument:

        is_premium = await db.has_premium_access(user_id)

        # ❌ NOT PREMIUM
        if not is_premium:

            buy_button = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "💎 Buy 1 Day Premium",
                            url="https://t.me/Adultjon1_bot?start=premium"
                        )
                    ]
                ]
            )

            return await message.reply_text(
                "<blockquote>❌ You Need Premium Access To Access This File.\n\n"
                "💎 Buy 1 Day Premium First.</blockquote>",
                reply_markup=buy_button
            )

        # ✅ PREMIUM USER
        message.text = "/getvideo"
        message.command = ["getvideo", argument]

        from plugins.get_video import handle_video_request

        await handle_video_request(client, message)
        return

    # =========================================
    # ADD USER
    # =========================================

    if not await db.is_user_exist(user_id):

        await db.add_user(
            user_id,
            message.from_user.first_name
        )

        try:

            await client.send_message(
                LOG_CHANNEL,
                script.LOG_TEXT.format(
                    me2,
                    user_id,
                    mention
                )
            )

        except Exception:
            pass

    # =========================================
    # MAIN BUTTON
    # =========================================

    reply_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("Get File")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

    # =========================================
    # START MESSAGE
    # =========================================

    await message.reply_photo(
        photo=START_PIC,

        caption=script.START_TXT.format(
            mention,
            temp.U_NAME,
            temp.U_NAME
        ),

        reply_markup=reply_keyboard,
        has_spoiler=True
    )


# =================================================
# 💎 BUY PREMIUM BUTTON
# =================================================

@Client.on_callback_query(filters.regex("buy_1day"))
async def buy_1day_callback(client, query):

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💳 Pay Now",
                callback_data="pay_now"
            )
        ]
    ])

    await query.message.edit_text(
        "<blockquote>💎 1 Day Premium Plan\n\n"
        "💰 Price : ₹5\n"
        "⏳ Duration : 1 Day\n\n"
        "👇 Click Pay Now To Continue.</blockquote>",
        reply_markup=buttons
    )


# =================================================
# 💳 PAY NOW
# =================================================

@Client.on_callback_query(filters.regex("pay_now"))
async def pay_now_callback(client, query):

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📤 Send Screenshot",
                callback_data="send_ss"
            )
        ]
    ])

    await query.message.reply_photo(
        photo=QR_CODE_IMAGE,

        caption=f"""<blockquote>
💎 1 Day Premium Payment

💰 Amount : ₹5
⏳ Duration : 1 Day

💳 UPI ID :
<code>{UPI_ID}</code>

⚠️ Payment Karne Ke Baad
Screenshot Send Kare.

✅ Admin Verify Karega
Uske Baad Premium Activate Hoga.
</blockquote>""",

        reply_markup=buttons
    )


# =================================================
# 📤 SEND SCREENSHOT
# =================================================

@Client.on_callback_query(filters.regex("send_ss"))
async def send_ss_callback(client, query):

    await query.message.reply_text(
        "<blockquote>📤 Ab Payment Screenshot Send Karo.\n\n"
        "✅ Admin Verify Karne Ke Baad\n"
        "Aapko 1 Day Premium Mil Jayega.</blockquote>"
    )


# =================================================
# 📜 DISCLAIMER
# =================================================

@Client.on_message(filters.command("disclaimer") & filters.private)
async def legal_disclaimer(client, message: Message):

    await send_legal_text(
        client,
        message,
        script.DISCLAIMER_TXT
    )


# =================================================
# 📜 TERMS
# =================================================

@Client.on_message(filters.command("terms") & filters.private)
async def legal_terms(client, message: Message):

    await send_legal_text(
        client,
        message,
        script.TERMS_TXT
    )


# =================================================
# 📜 ABOUT
# =================================================

@Client.on_message(filters.command("about") & filters.private)
async def legal_about(client, message: Message):

    await send_about_text(client, message)


# =================================================
# 📜 HELP
# =================================================

@Client.on_message(filters.command("help") & filters.private)
async def legal_help(client, message: Message):

    await send_legal_text(
        client,
        message,
        script.HELP_TXT
    )


# =================================================
# 📜 LEGAL TEXT
# =================================================

async def send_legal_text(client, message, text):

    inline_buttons = [[
        InlineKeyboardButton(
            '• ᴄʟᴏsᴇ •',
            callback_data='close_data'
        )
    ]]

    await message.reply_text(
        text=text,

        reply_markup=InlineKeyboardMarkup(
            inline_buttons
        ),

        disable_web_page_preview=True
    )


# =================================================
# 📜 ABOUT TEXT
# =================================================

async def send_about_text(client, message):

    inline_buttons = [[
        InlineKeyboardButton(
            '• ᴄʟᴏsᴇ •',
            callback_data='close_data'
        )
    ]]

    await message.reply_text(
        text=script.ABOUT_TXT,

        reply_markup=InlineKeyboardMarkup(
            inline_buttons
        ),

        disable_web_page_preview=True
    )
