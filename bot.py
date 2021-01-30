import telebot
from pyowm import OWM
import pyowm
from telebot import types

TOKEN = '1663190341:AAF5wIHIud9cB1u8NL6ucN6-W96G11d4qOQ'
owm = OWM('f15abce18b3cdc239ede82805377767e')

# place = input('Введите город:')
place = ""
temp = ""
w = ""

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def starting_dialog(message):
    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Привет!🖐")
    item2 = types.KeyboardButton("Погода🌤")

    markup.add(item1, item2)

    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, бот, который покажет "
                     "тебе погоду в любом городе.".format(
                         message.from_user, bot.get_me()),
                     parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=["text"])
def weather_forecast_func(message):
    if message.text == 'Привет!🖐':
        bot.send_message(message.from_user.id, 'Привет!')
    elif message.text == 'Погода🌤':
        bot.send_message(message.from_user.id, 'Укажи свой город')
        bot.register_next_step_handler(message, placy)
    else:
        bot.send_message(message.from_user.id, 'Я не знаю такой команды')


def placy(message):
    global place
    global temp, w
    place = message.text
    # bot.send_message(message.from_user.id, place)
    try:
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(place)
        w = observation.weather

        temp = w.temperature('celsius')["temp"]
        bot.send_message(message.from_user.id, f'В городе {place} сейчас {temp} градусов по Цельсию')
        bot.send_message(message.from_user.id, f'В городе {place} сейчас {w.detailed_status}')
    except pyowm.commons.exceptions.NotFoundError:
        bot.send_message(message.from_user.id, 'Я не знаю такого города😭')


# RUN
bot.polling(none_stop=True)
