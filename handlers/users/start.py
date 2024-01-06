from aiogram import types
from aiogram.dispatcher import FSMContext
from asyncpg import UniqueViolationError
from loader import dp, db


@dp.message_handler(commands=['start'])
async def bot_start(message: types.Message):
    try:
        await db.save_user(message.from_user.id)
    except UniqueViolationError:
        pass
    await message.answer(
        f"Welcome, {message.from_user.full_name}!\nThis bot will resend all calls from Cyber Turtles Shitcoin group\n"
        f"They are automatically turned on and for now you won't be able to turn them off\nWait for new updates")
