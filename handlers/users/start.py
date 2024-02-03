from aiogram import types

from loader import dp


@dp.message_handler(commands=['start'])
async def bot_start(message: types.Message):
    await message.answer(
        f"Welcome, {message.from_user.full_name}!\nThis bot will resend all calls from Cyber Turtles Shitcoin group into Turtle Calls Private Channel\n"
        f"You have to hold some Turtles to have access to those channel ;)")
