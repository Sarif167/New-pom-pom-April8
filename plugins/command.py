# =================================================
# 📤 PAYMENT SCREENSHOT RECEIVE
# =================================================

@Client.on_message(filters.photo & filters.private)
async def payment_screenshot_receive(client, message):

    from info import SCREENSHOT_CHANNEL, ADMINS

    user_id = message.from_user.id

    # Ignore Admins
    if user_id in ADMINS:
        return

    caption = f"""
💸 New Payment Screenshot

👤 User : {message.from_user.mention}
🆔 User ID : <code>{user_id}</code>
"""

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ Approve 1 Day",
                callback_data=f"approve_{user_id}"
            )
        ]
    ])

    # =========================================
    # SEND TO ADMINS
    # =========================================

    for admin in ADMINS:

        try:

            await message.copy(
                chat_id=admin,
                caption=caption,
                reply_markup=buttons
            )

        except Exception as e:
            print(e)

    # =========================================
    # AUTO POST TO CHANNEL
    # =========================================

    try:

        await message.copy(
            chat_id=SCREENSHOT_CHANNEL,

            caption=caption,

            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "💎 Buy Premium",
                        url="https://t.me/Adultjon1_bot?start=premium"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "❓ Any Questions",
                        url="https://t.me/premiumuseronly_Bot"
                    )
                ]
            ])
        )

    except Exception as e:
        print(e)

    # =========================================
    # USER MESSAGE
    # =========================================

    await message.reply_text(
        "<blockquote>✅ Screenshot Sent To Admin.\n\n"
        "⏳ Wait For Approval.</blockquote>"
    )


# =================================================
# ✅ APPROVE PREMIUM
# =================================================

@Client.on_callback_query(filters.regex(r"approve_(\\d+)"))
async def approve_premium(client, query):

    from info import ADMINS

    admin_id = query.from_user.id

    if admin_id not in ADMINS:
        return

    user_id = int(query.matches[0].group(1))

    # =========================================
    # ADD 1 DAY PREMIUM
    # =========================================

    expiry_date = datetime.datetime.now() + datetime.timedelta(days=1)

    await db.add_premium(
        user_id,
        expiry_date
    )

    # =========================================
    # USER MESSAGE
    # =========================================

    try:

        await client.send_message(
            chat_id=user_id,

            text="""
<blockquote>
✅ Payment Approved

💎 1 Day Premium Activated Successfully.
⏳ Valid For 1 Day.
</blockquote>
"""
        )

    except Exception as e:
        print(e)

    # =========================================
    # ADMIN MESSAGE
    # =========================================

    await query.message.edit_caption(
        caption=query.message.caption + "\n\n✅ APPROVED"
    )

    await query.answer(
        "Premium Approved Successfully",
        show_alert=True
    )
