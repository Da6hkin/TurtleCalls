from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

yes_or_no = InlineKeyboardMarkup(inline_keyboard=[

    [
        InlineKeyboardButton(text="Yes ✅", callback_data="yes"),
    ],
[
        InlineKeyboardButton(text="No ⛔️", callback_data="no"),
    ]
])
