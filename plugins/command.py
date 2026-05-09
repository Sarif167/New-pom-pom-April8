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
    message.text = f"/getvideo {argument}"
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
