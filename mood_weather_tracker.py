import aiogram
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.job_queue import JobQueue
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
                          ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton 
from aiogram.utils.callback_data import CallbackData

from google.cloud import bigquery

import datetime
import requests

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=r"C:\Users\Egoiste\marshmeowbot\marshmeowbot\modular-design-373506-8a5d966ec2c3.json"

bot = Bot('5918472294:AAGYqlSwmdwbFvnTroam00EyIRfL4tnINDE')
dp =  Dispatcher(bot)

cb_inline = CallbackData("post", 'action', "data")

#TODO Delete this motherfucker global variable
previous_anxiety_note = None


# %% Weather section    
async def weather_tracker(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = KeyboardButton(text="Send my location", request_location=True)
    keyboard.add(button)
    text = "Please send your location to get the current weather"
    await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard)

@dp.message_handler(content_types=["location"])
async def process_location(message: types.Message):
    lat = message.location.latitude
    lon = message.location.longitude
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={"45bd10a5036ab9086034fac86c62ac73"}'
    response = requests.get(url)
    data = response.json()
    weather = data['weather'][0]['main']
    text = f"The current weather in your location is {weather}."
    await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=ReplyKeyboardRemove())

    # Create a client object
    client = bigquery.Client(project='modular-design-373506')
    # Get the table you want to insert data into
    table = client.get_table('marshmeow_dataset.weather_data')
    # Create a new row
    row = (datetime.datetime.now(),
     message.from_user.id,
     weather, f"lat: {lat}, lon: {lon}")

    try:
        # Insert the row into the table
        client.insert_rows(table, [row])
        await bot.send_message(chat_id=message.from_user.id, text="Data is successfully stored in BigQuery.")
    except Exception as e:
        await bot.send_message(chat_id=message.from_user.id, text=f"An error occurred while storing the data: {e}")

@dp.callback_query_handler(lambda c: c.data == 'weather')
async def process_callback_weather(callback_query: aiogram.types.CallbackQuery):
    await weather_tracker(callback_query.message)

# %%  Mood section
async def mood_tracker(message):
    moods = ["Happy", "Sad", "Excited", "Bored", "Stressed"]
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [InlineKeyboardButton(mood) for mood in moods]
    markup.add(*buttons)
    text = "What's your mood today?"
    await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data == 'mood')
async def process_callback_mood(callback_query: aiogram.types.CallbackQuery):
    await mood_tracker(callback_query.message)

@dp.message_handler(lambda c: c.text in ["Happy", "Sad", "Excited", "Bored", "Stressed"])
async def process_callback_mood_tracker(callback_query: aiogram.types.CallbackQuery):
    mood = callback_query.text
    #bot.send_message(chat_id=callback_query.from_user.id, text=f"{mood}")

    # Create a client object
    client = bigquery.Client(project='modular-design-373506')
    # Get the table you want to insert data into
    table = client.get_table('marshmeow_dataset.mood_data')
    # Create a new row
    row = (datetime.datetime.now(), callback_query.from_user.id, mood)

    try:
        # Insert the row into the table
        client.insert_rows(table, [row])
        await bot.send_message(chat_id=callback_query.from_user.id, text="Data is successfully stored in BigQuery.")
    except Exception as e:
        await bot.send_message(chat_id=callback_query.from_user.id, text=f"An error occurred while storing the data: {e}")

# %%  Anxiety section
async def anxiety_tracker(message):
    anxiety_list = {'chronic_anxiety': 'Chronic anxiety',
                   'fears':'Fears and phobias',
                   'fears':'Fear of failure',
                   'fears':'Fear of the public',
                   'shyness':'Shyness',
                   'panic_attacks':'Panic attacks',
                   'agoraphobia':'Agoraphobia',
                   'obsessions_and_compulsions':'Obsessions and Compulsions',
                   'PTSD':'PTSD',
                   'health_concerns':'Health concerns'}
    keyboard = InlineKeyboardMarkup(resize_keyboard=True,  one_time_keyboard=True)

    for key, value in anxiety_list.items(): 
      keyboard.add(types.InlineKeyboardButton(text=value,
                                            callback_data=key)
      )

    await bot.send_message(chat_id=message.chat.id, 
                    text='Anxiety comes in many forms.'+
                   'Which of the anxiety symptoms listed below do you notice in yourself?',
                    reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data == 'anxiety')
async def process_callback_mood(callback_query: aiogram.types.CallbackQuery):
    await anxiety_tracker(callback_query.message)

@dp.callback_query_handler(lambda c: c.data in ['chronic_anxiety', 'fears', 'shyness', 'panic_attacks', 'agoraphobia', 'obsessions_and_compulsions', 'PTSD', 'health_concerns'])
async def process_callback_anxiety_tracker(callback_query: aiogram.types.CallbackQuery):
    anxiety_type = callback_query.data
    message = callback_query.message
    global previous_anxiety_note
    previous_anxiety_note = anxiety_type
    #await bot.send_message(chat_id=callback_query.from_user.id, text=anxiety_type)
    await message.answer('Describe your feelings right now.'+
     'Please, start with **"I feel"** otherwise you will go to hell',
     parse_mode="Markdown")
    
@dp.message_handler(Text(contains = "I feel"))    
async def process_callback_anxiety_tracker_notes(message: types.Message):   
    global previous_anxiety_note    
    anxiety_note = message.text

    # Create a client object
    client = bigquery.Client(project='modular-design-373506')
    # Get the table you want to insert data into
    table = client.get_table('marshmeow_dataset.anxiety_data')
    # Create a new row
    row = (datetime.datetime.now(),
    message.from_user.id, previous_anxiety_note, anxiety_note )

    try:
        # Insert the row into the table
        client.insert_rows(table, [row])
        await bot.send_message(chat_id=message.from_user.id, text=f"Data is successfully stored in BigQuery.")
    except Exception as e:
        await bot.send_message(chat_id=message.from_user.id, text=f"An error occurred while storing the data: {e}")


job_queue = JobQueue()
dp.job_queue = job_queue

# Schedule the message to be sent at a specific time
async def mood_reminder(context: dict):
    await bot.send_message(chat_id=context["chat_id"], text="Don't forget to track your mood today!")
    

job_queue.run_once(mood_reminder, datetime.datetime.now() + datetime.timedelta(seconds=60), context={"chat_id": message.chat.id})



# %% Main commands section     
@dp.message_handler(commands=['start'])
async def start_command(message: aiogram.types.Message):
    keyboard = InlineKeyboardMarkup()
    weather_button = InlineKeyboardButton('Weather', callback_data='weather')
    mood_button = InlineKeyboardButton('Mood', callback_data='mood')
    moon_button = InlineKeyboardButton('Anxiety', callback_data='anxiety')
    keyboard.add(weather_button, mood_button, moon_button)
    text = "Welcome to the Marshmeowbot! What would you like to track?"

    await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=keyboard)

executor.start_polling(dp)