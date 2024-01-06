import asyncio

import aiohttp
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils.exceptions import ChatNotFound

import data.config
from filters import IsGroup
from keyboards.inline.call_keyboards import yes_or_no
from loader import dp, db, bot


@dp.message_handler(IsGroup(), commands=['call'])
async def check_call(message: types.Message, state: FSMContext):
    arguments = message.get_args()
    state_data = await state.get_data()
    if len(arguments) == 0:
        await message.reply("You have to put Contract address after /call")
    else:
        splitted_args = arguments.split(" ")
        if len(splitted_args) > 1:
            await message.reply("You have to put ONLY CA after /call")
        else:
            headers = {
                "X-BLOBR-KEY": f"{data.config.DEXTOOLS}"
            }
            symbol = ""
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(
                        f"https://open-api.dextools.io/free/v2/token/solana/{splitted_args[0]}") as resp:
                    json_body = await resp.json()
                    if json_body["statusCode"] != 200:
                        await message.reply(
                            "Please re-check the CA that you've sent\nHaving problems finding this CA on solana blockchain")
                        return
                    else:
                        symbol = json_body['data']['symbol']
                async with session.get(
                        f"https://open-api.dextools.io/free/v2/token/solana/{splitted_args[0]}/info") as resp:
                    json_data = await resp.json()
                    if json_data['data']['fdv'] is None:
                        print(json_data)
                        mcap = "None"
                    else:
                        mcap = humanize_number(json_data['data']['fdv'])
                    reply_message = await message.reply(
                        f"You sure you want to make a call on ${symbol}\n💰 FDV: <code>{mcap}</code>",
                        reply_markup=yes_or_no)
                    state_data[reply_message.message_id] = [message.from_user.id, symbol,
                                                            splitted_args[0], mcap]
                    await state.update_data(state_data)


@dp.callback_query_handler()
async def send_call(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    state_data = await state.get_data()
    message_id = call.message.message_id
    if message_id in state_data:
        if state_data[message_id][0] == call.from_user.id:
            coin_ticker = state_data[message_id][1]
            contract = state_data[message_id][2]
            mcap = state_data[message_id][3]
            if call.data != "no":
                users = await db.select_all_users()
                coros = []
                for user in users:
                    coros.append(bot.send_message(chat_id=user['telegram_id'],
                                                  text=f"New Solana <b>{call.data}</b> call from <b>{call.from_user.first_name}</b>\n<b>${coin_ticker}</b>\n💰 FDV: <code>{mcap}</code>\n<code>{contract}</code>\n<a href='https://t.me/mcqueen_bonkbot?start=ref_o895c_ca_{contract}'>BONK BUY</a> | <a href='https://birdeye.so/token/{contract}?chain=solana'>Birdeye</a>"))

                await asyncio.gather(*coros, return_exceptions=True)
                await call.message.edit_reply_markup(reply_markup=None)
                await call.message.reply(f"{call.data} call have been made")
                del state_data[message_id]
                await state.update_data(state_data)
            else:
                await call.message.edit_reply_markup(reply_markup=None)
                await call.message.reply("Call cancelled")
                del state_data[message_id]
                await state.update_data(state_data)


def humanize_number(value, fraction_point=1):
    powers = [10 ** x for x in (12, 9, 6, 3, 0)]
    human_powers = ('T', 'B', 'M', 'K', '')
    is_negative = False
    if not isinstance(value, float):
        value = float(value)
    if value < 0:
        is_negative = True
        value = abs(value)
    for i, p in enumerate(powers):
        if value >= p:
            return_value = str(round(value / (p / (10.0 ** fraction_point))) /
                               (10 ** fraction_point)) + human_powers[i]
            break
    if is_negative:
        return_value = "-" + return_value

    return return_value
