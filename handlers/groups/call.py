import aiohttp
from aiogram import types
from aiogram.dispatcher import FSMContext


import data.config
from filters import IsGroup
from keyboards.inline.call_keyboards import yes_or_no
from loader import dp, bot


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
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        f"https://api.dexscreener.com/latest/dex/tokens/{splitted_args[0]}") as resp:
                    if resp.status != 200:
                        await message.reply(
                            "Please re-check the CA that you've sent\nHaving problems finding this CA")
                        return
                    json_body = await resp.json()
                    token_info = json_body['pairs'][0]
                    symbol = token_info['baseToken']['symbol']
                    mcap = humanize_number(token_info['fdv'])
                    chain = token_info["chainId"]
                    reply_message = await message.reply(
                        f"You sure you want to make a call on {symbol}\n💰 FDV: <code>{mcap}</code>\n{chain}",
                        reply_markup=yes_or_no)
                    state_data[reply_message.message_id] = [message.from_user.id, symbol,
                                                            splitted_args[0], mcap, chain]
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
            chain = state_data[message_id][4]
            if call.data != "no":
                text = f"New {chain} <b>{call.data}</b> call from <b>{call.from_user.first_name}</b>\n<b>${coin_ticker}</b>\n💰 FDV: <code>{mcap}</code>\n<code>{contract}</code>"
                if chain == "solana":
                    text += f"\n<a href='https://t.me/mcqueen_bonkbot?start=ref_o895c_ca_{contract}'>BONK BUY</a> | <a href='https://birdeye.so/token/{contract}?chain=solana'>Birdeye</a>"
                elif chain == "ethereum":
                    text += f"\n<a href='https://t.me/maestro?start=r-da6hki9'>Maestro Bot</a> | <a href='https://dexscreener.com/ethereum/{contract}'>DexScreener</a>"
                else:
                    text += "\n<a href='https://t.me/maestro?start=r-da6hki9'>Maestro Bot</a>"
                await bot.send_message(chat_id=data.config.CHANNEL_ID, text=text)
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
