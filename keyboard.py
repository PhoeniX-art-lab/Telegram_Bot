from telebot import types


def board():
    global markup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Привет!🖐")
    item2 = types.KeyboardButton("Погода🌤")
    item3 = types.KeyboardButton("Настройки⚙")
    item4 = types.KeyboardButton("Уведомления🔔")

    markup.add(item1, item2, item3, item4)
