from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageNotModified

from database.users_db import db
from Script import script

# =========================================
# START COMMAND
# =========================================

@Client.on_message(filters.command("start"))
async def start(client, message):

    user_id = message.from_user.id
    mention = message.from_user.mention

    if len(message.command) > 1:
        argument = message.command[1]
    else:
        argument = None

    # =========================================
    # PREMIUM PAGE
    # =========================================

    if argument == "premium":

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "💳 Buy 1 Day - ₹5",
                    url="https://t.me/Adultjon1_bot?start=buy"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔥 Premium Features",
                    callback_data="premium_features"
                )
            ],
            [
                InlineKeyboardButton(
                    "👑 Admin",
                    url="https://t.me/premiumuseronly_Bot"
                )
            ]
        ])

        return await message.reply_text(
            "<blockquote>💎 Premium Plans\n\n"
            "✅ 1 Day Access\n"
            "✅ Unlimited Files\n"
            "✅ Instant Access\n"
            "✅ Premium Locked Content\n"
            "✅ Fast Download Speed\n\n"
            "🔥 Best Premium Experience Available.</blockquote>",
            reply_markup=buttons
        )

    # =========================================
    # BUY PAGE DIRECT OPEN
    # =========================================

    elif argument == "buy":

        from plugins.premium import buy_handler

        return await buy_handler(client, message)

    # =========================================
    # TERMS / HELP / ABOUT
    # =========================================

    elif argument == "terms":
        return await message.reply_text(script.TERMS_TXT)

    elif argument == "disclaimer":
        return await message.reply_text(script.DISCLAIMER_TXT)

    elif argument == "help":
        return await message.reply_text(script.HELP_TXT)

    elif argument == "about":
        return await message.reply_text(script.ABOUT_TXT)

    # =========================================
    # REFERRAL
    # =========================================

    elif argument and argument.startswith("reff_"):

        try:
            from plugins.referral import refer_on_start
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
                            url="https://t.me/Adultjon1_bot?start=buy"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "👑 Admin",
                            url="https://t.me/premiumuseronly_Bot"
                        )
                    ]
                ]
            )

            return await message.reply_text(
                "<blockquote>❌ You Need Premium Access To Access This File.\n\n"
                "💎 Buy 1 Day Premium First.\n"
                "⚡ Get Instant Unlimited Access.</blockquote>",
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

    # =========================================
    # NORMAL START MESSAGE
    # =========================================

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💎 Buy Premium",
                url="https://t.me/Adultjon1_bot?start=buy"
            )
        ],
        [
            InlineKeyboardButton(
                "👑 Admin",
                url="https://t.me/premiumuseronly_Bot"
            )
        ]
    ])

    await message.reply_text(
        "<blockquote>👋 Welcome To Premium Bot\n\n"
        "🚀 Get Premium Access To Unlock Unlimited Files.\n"
        "⚡ Fast Download Speed & Instant Delivery.\n"
        "🔓 Access Premium Locked Content Easily.\n\n"
        "💎 Buy Premium To Enjoy All Features.</blockquote>",
        reply_markup=buttons
    )


# =========================================
# BUY 1 DAY CALLBACK
# =========================================

@Client.on_callback_query(filters.regex("^buy_1day$"))
async def buy_1day_callback(client, query):

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💳 Open Payment Page",
                url="https://t.me/Adultjon1_bot?start=buy"
            )
        ],
        [
            InlineKeyboardButton(
                "🔥 Premium Features",
                callback_data="premium_features"
            )
        ],
        [
            InlineKeyboardButton(
                "👑 Admin",
                url="https://t.me/premiumuseronly_Bot"
            )
        ]
    ])

    text = (
        "<blockquote>💎 1 Day Premium Plan\n\n"
        "💰 Price: ₹5\n"
        "⏳ Validity: 1 Day\n"
        "📥 Unlimited File Access\n"
        "⚡ Fast Download\n"
        "🔓 Premium Locked Files Access\n"
        "🔥 Instant Delivery\n\n"
        "👇 Click Below To Open Payment Page.</blockquote>"
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


# =========================================
# PREMIUM FEATURES CALLBACK
# =========================================

@Client.on_callback_query(filters.regex("^premium_features$"))
async def premium_features(client, query):

    text = (
        "<blockquote>🔥 Premium Features\n\n"
        "✅ Unlimited File Access\n"
        "✅ No Daily Download Limit\n"
        "✅ Instant File Delivery\n"
        "✅ Access Premium Locked Content\n"
        "✅ Ultra Fast Server Speed\n"
        "✅ 24x7 Non-Stop Access\n"
        "✅ Auto Verified Access\n"
        "✅ Priority Support\n"
        "✅ Latest Movies & Series First\n"
        "✅ Ads Free Experience\n\n"
        "⚡ Why Choose Our Bot?\n"
        "• Easy To Use Interface\n"
        "• Safe & Secure Downloads\n"
        "• Daily New Content Updates\n"
        "• High Quality Files Available\n\n"
        "💎 Buy Premium To Unlock All Features.</blockquote>"
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💎 Buy Now",
                url="https://t.me/Adultjon1_bot?start=buy"
            )
        ],
        [
            InlineKeyboardButton(
                "👑 Admin",
                url="https://t.me/premiumuseronly_Bot"
            )
        ]
    ])

    try:

        await query.message.edit_text(
            text=text,
            reply_markup=buttons
        )

    except Exception as e:
        print(e)
