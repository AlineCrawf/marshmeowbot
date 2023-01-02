from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton  # for reply keyboard (sends message)

from time import sleep


bot = Bot(token='5918472294:AAGYqlSwmdwbFvnTroam00EyIRfL4tnINDE')
dp = Dispatcher(bot)

answers = []  # store the answers they have given


# sends welcome message after start
@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    await message.answer('Доброго времени суток. Я недоработанный пушистый бот, живущий в облаке GCP')
    
# sends help message
@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.answer('Помощи не ждите :3')


# #### selecting what you need
# @dp.message_handler(regexp='English 👍')
# async def english(message: types.Message):
#     answers.append(message.text)
#     await message.answer('What do you need?', reply_markup = en_options_kb)


# this is the last line
executor.start_polling(dp)