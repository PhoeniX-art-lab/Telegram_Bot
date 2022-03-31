import config
import telebot
from pyowm import OWM
import pyowm
from telebot import types
import schedule
from threading import Thread
import time

owm = OWM('')   # your OWM token

places = ['Могилёв', 'Минск', 'Москва', 'Санкт-Петербург']
place = ""
temp = ""
w = ""
i = -1
words_list = []
flag = 0
permission = 0
favourite_time = '12:38'

bot = telebot.TeleBot(config.TOKEN)
id1 = None


def board():
    global markup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Привет!🖐")
    item2 = types.KeyboardButton("Погода🌤")
    item3 = types.KeyboardButton("Настройки⚙")
    item4 = types.KeyboardButton("Уведомления🔔")

    markup.add(item1, item2, item3, item4)


@bot.message_handler(commands=['start', 'help'])
def starting_dialog(message):
    # keyboard
    board()

    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, бот, который покажет "
                     "тебе погоду в любом городе.".format(
                         message.from_user, bot.get_me()),
                     parse_mode='html', reply_markup=markup)
    global id1  # идея с рассылкой погоды в определенное время
    # bot.send_message(id1, id1)


@bot.message_handler(content_types=["text"])
def weather_forecast_func(message):
    global i
    if message.text == 'Привет!🖐':
        bot.send_message(message.from_user.id, 'Привет!')

    elif message.text == 'Погода🌤':
        # temp keyboard
        markup1 = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        item1_def = types.KeyboardButton(places[0])
        item2_def = types.KeyboardButton(places[1])
        item3_def = types.KeyboardButton(places[2])
        item4_def = types.KeyboardButton(places[3])
        markup1.add(item1_def, item2_def, item3_def, item4_def)

        bot.send_message(message.from_user.id, 'Укажи свой город', reply_markup=markup1)
        bot.register_next_step_handler(message, placy)

    elif message.text.lower() == 'ок':
        bot.send_message(message.from_user.id, 'Ну ок, так ок')

    elif message.text == 'Настройки⚙':
        i = -1
        # keyboard
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Продолжить➡")
        item2 = types.KeyboardButton("Назад⬅")

        markup.add(item1, item2)

        bot.send_message(message.from_user.id, 'Вы можете настроить города для быстрого доступа к ним',
                         reply_markup=markup)
        bot.register_next_step_handler(message, switch)

    elif message.text == 'Уведомления🔔':
        # keyboard
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Продолжить➡")
        item2 = types.KeyboardButton("Назад⬅")

        markup.add(item1, item2)

        bot.send_message(message.from_user.id, 'Вы можете настроить уведомления, чтобы каждый день в определенное '
                                               'время получать информацию о погоде в избранном городе',
                         reply_markup=markup)
        bot.register_next_step_handler(message, switch_notifications)

    else:
        bot.send_message(message.from_user.id, 'Я не знаю такой команды')


def switch_notifications(message):
    global id1, markup
    # keyboard
    board()

    if message.text == 'Продолжить➡':
        bot.send_message(message.from_user.id, 'Укажите город, в котором вы хотите получать погоду')
        id1 = message.from_user.id  # запоминаем id юзера, на который и будет отправляться рассылка
        bot.register_next_step_handler(message, switch_notifications_city)
    elif message.text == 'Назад⬅':
        bot.send_message(message.from_user.id, 'Вы вышли из настроек', reply_markup=markup)
    else:
        bot.send_message(message.from_user.id, 'Я не знаю такой команды', reply_markup=markup)


def switch_notifications_city(message):
    global favourite_place, markup
    # keyboard
    board()

    favourite_place = message.text
    # проверка, существует ли такой город?
    try:
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(favourite_place)
    except pyowm.commons.exceptions.NotFoundError:
        for letter in favourite_place:
            try:
                if letter == 'е':
                    favourite_place = favourite_place.replace('е', 'ё', 1)
                    mgr = owm.weather_manager()
                    observation = mgr.weather_at_place(favourite_place)
                    bot.send_message(message.from_user.id, f'Возможно вы имели в виду {favourite_place}')
                    bot.send_message(message.from_user.id, 'Укажите время, в которое хотите получать погоду в формате '
                                                           '"часы:минуты"')
                    bot.register_next_step_handler(message, switch_notifications_time)
                    return
            except pyowm.commons.exceptions.NotFoundError:
                bot.send_message(message.from_user.id, 'Вы ввели несуществующий город', reply_markup=markup)
                return
        bot.send_message(message.from_user.id, 'Вы ввели несуществующий город', reply_markup=markup)
        return
    bot.send_message(message.from_user.id, 'Укажите время, в которое хотите получать погоду в формате '
                                           '"часы:минуты"')
    bot.register_next_step_handler(message, switch_notifications_time)


def switch_notifications_time(message):
    global favourite_time, markup, permission
    # keyboard
    board()

    favourite_time = message.text
    permission = 1


def placy(message):
    try:
        # keyboard
        board()

        global place
        global temp, w, flag
        place = message.text
        # bot.send_message(message.from_user.id, place)
        try:
            mgr = owm.weather_manager()
            observation = mgr.weather_at_place(place)
            w = observation.weather

            temp = w.temperature('celsius')["temp"]
            bot.send_message(message.from_user.id, f'В городе {place} сейчас {temp} градусов по Цельсию',
                             reply_markup=markup)
            bot.send_message(message.from_user.id, f'В городе {place} сейчас {w.detailed_status}')
        except pyowm.commons.exceptions.NotFoundError:
            flag = 0
            for j in place:
                try:
                    if j == 'е':
                        flag = 1
                        place = place.replace('е', 'ё', 1)

                        mgr = owm.weather_manager()
                        observation = mgr.weather_at_place(place)
                        w = observation.weather

                        temp = w.temperature('celsius')["temp"]
                        bot.send_message(message.from_user.id, f'Возможно вы имели в виду {place}')
                        bot.send_message(message.from_user.id, f'В городе {place} сейчас {temp} градусов по Цельсию',
                                         reply_markup=markup)
                        bot.send_message(message.from_user.id, f'В городе {place} сейчас {w.detailed_status}')
                except pyowm.commons.exceptions.NotFoundError:
                    bot.send_message(message.from_user.id, 'Я не знаю такого города😭', reply_markup=markup)
            if flag == 0:
                bot.send_message(message.from_user.id, 'Я не знаю такого города😭', reply_markup=markup)
    except:
        bot.reply_to(message, 'ooops!!\n Возникла какая-та ошибка, попробуйте ввести "/help"')


def switch(message):
    try:
        global i, markup
        if message.text == 'Продолжить➡':
            i += 1
            bot.send_message(message.from_user.id, f'Введите {i + 1} город')
            bot.register_next_step_handler(message, settings)
        elif message.text == 'Назад⬅':
            # keyboard
            board()
            bot.send_message(message.from_user.id, 'Вы вышли из настроек', reply_markup=markup)
        else:
            # keyboard
            board()
            bot.send_message(message.from_user.id, 'Неизвестная команда!', reply_markup=markup)
    except:
        bot.reply_to(message, 'ooops!!\n Возникла какая-та ошибка, попробуйте ввести "/help"')


def settings(message):
    try:
        global i, markup
        # keyboard
        board()

        temporary = message.text
        try:
            mgr = owm.weather_manager()
            observation = mgr.weather_at_place(temporary)
        except pyowm.commons.exceptions.NotFoundError:
            for j in temporary:
                try:
                    if j == 'е':
                        temporary = temporary.replace('е', 'ё', 1)
                        mgr = owm.weather_manager()
                        observation = mgr.weather_at_place(temporary)
                        places[i] = temporary
                        bot.send_message(message.from_user.id, 'Принято')
                        bot.send_message(message.from_user.id, f'{places[i]} добавлен в список ваших городов')
                        if i == 3:
                            bot.send_message(message.from_user.id, 'Вы успешно закончили настройку',
                                             reply_markup=markup)
                            return
                        bot.send_message(message.from_user.id, 'Хотите продолжить?')
                        bot.register_next_step_handler(message, switch)
                        return
                except pyowm.commons.exceptions.NotFoundError:
                    bot.send_message(message.from_user.id, 'Вы ввели несуществующий город', reply_markup=markup)
                    return
            bot.send_message(message.from_user.id, 'Вы ввели несуществующий город', reply_markup=markup)
            return
        places[i] = temporary
        bot.send_message(message.from_user.id, 'Принято', reply_markup=None)
        bot.send_message(message.from_user.id, f'{places[i]} добавлен в список ваших городов')
        if i == 3:
            # keyboard
            board()

            bot.send_message(message.from_user.id, 'Вы успешно закончили настройку', reply_markup=markup)
            return
        bot.send_message(message.from_user.id, 'Хотите продолжить?')
        bot.register_next_step_handler(message, switch)
    except:
        bot.reply_to(message, 'ooops!!\n Возникла какая-та ошибка, попробуйте ввести "/help"')


def planing_message():
    global favourite_place

    mgr = owm.weather_manager()
    observation = mgr.weather_at_place(favourite_place)
    w = observation.weather
    temp = w.temperature('celsius')["temp"]
    bot.send_message(id1, f'В городе {favourite_place} сейчас {temp} градусов по Цельсию')
    bot.send_message(id1, f'В городе {favourite_place} сейчас {w.detailed_status}')


# RUN
def do_schedule():
    global markup
    # keyboard
    board()

    global permission
    try:
        schedule.every().day.at(favourite_time).do(planing_message)
        if permission == 2:
            bot.send_message(id1, 'Вы успешно настроили уведомления', reply_markup=markup)
    except schedule.ScheduleValueError:
        bot.send_message(id1, 'Не верный формат времени!', reply_markup=markup)

    while True:
        schedule.run_pending()
        time.sleep(1)
        if permission == 1:
            permission = 2
            break
    do_schedule()


def main_loop():
    thread = Thread(target=do_schedule)
    thread.start()

    bot.polling(True)


if __name__ == '__main__':
    try:
        main_loop()
    except:
        main_loop()
