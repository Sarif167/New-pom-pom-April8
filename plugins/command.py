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
        ],
        [
            InlineKeyboardButton(
                "🛠 Admin Help",
                url="https://t.me/premiumuseronly_Bot"
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

elif argument == "terms":
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

elif argument and argument.startswith("reff_"):

    try:
        await refer_on_start(client, message)
        return

    except Exception as e:
        print(f"Referral Error: {e}")

# =========================================
# PREMIUM PROTECTED FILE ACCESS
# =========================================

elif argument:

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
    message.text = f"/getvideo {argument}"
    message.command = ["getvideo", argument]

    from plugins.get_video import handle_video_request

    try:
        await handle_video_request(client, message)

    except Exception as e:
        print(f"Video Request Error: {e}")

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

    except Exception as e:
        print(f"Log Error: {e}")



# =========================================
# BUY 1 DAY CALLBACK FIX
# =========================================

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageNotModified


@Client.on_callback_query(filters.regex("^buy_1day$"))
async def buy_1day_callback(client, query):

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💳 Pay Now",
                url="https://t.me/Adultjon1_bot?start=premium"
            )
        ]
    ])

    text = (
        "<blockquote>💎 1 Day Premium Plan\n\n"
        "💰 Price: ₹5\n"
        "⏳ Validity: 1 Day\n"
        "📥 Unlimited File Access\n\n"
        "Click Below To Buy.</blockquote>"
    )

    try:

        await query.message.edit_text(
            text=text,
            reply_markup=buttons
        )

    except MessageNotModified:

        await query.answer(
            "Already Opened ✅",
            show_alert=False
        )

    except Exception as e:
        print(f"Buy 1 Day Error: {e}")
