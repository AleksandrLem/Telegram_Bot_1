from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                            ReplyKeyboardRemove, KeyboardButtonPollType)
from aiogram.utils.keyboard import ReplyKeyboardBuilder


start_kbd = ReplyKeyboardMarkup(
    keyboard=[
        [
        KeyboardButton(text='Кнопка_1'),
        KeyboardButton(text='Кнопка_2'),
        ],
        [
        KeyboardButton(text='Кнопка_3'),
        KeyboardButton(text='Кнопка_4'),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='жмякни кнопку'
)

del_kbd = ReplyKeyboardRemove()

# создаем кнопки с помощью билдера
start_kbd2 = ReplyKeyboardBuilder() # создаем экземпляр

# добавляем кнопки
start_kbd2.add(
    KeyboardButton(text='Кнопка_11'),
    KeyboardButton(text='Кнопка_12'),
    KeyboardButton(text='Кнопка_13'),
    KeyboardButton(text='Кнопка_14'),
)

# добавляем расположение кнопок
start_kbd2.adjust(2, 2) # две кнопки в ряду, два ряда
# start_kbd2.adjust(2, 1, 1) две кнопки в первом ряду, одна во втором, одна в третьем

# если к клавиауре start_kbd2 мы хотим добавить ещё пару кнопок, но
# не хотим заново прописывать их в новом экземпляре, то делаем так
start_kbd3 = ReplyKeyboardBuilder()
start_kbd3.attach(start_kbd2) # добавляем клавиатуру start_kbd2
# метод row добавляет кнопки в новом ряду
start_kbd3.row(
    KeyboardButton(text='Кнопка_15'),
    KeyboardButton(text='Кнопка_16'),
    KeyboardButton(text='Кнопка_17'),
)


# создаем клавиатуру, где можно запросить лакацию и номер телефона или создать опрос

kbd_location_phone = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Создать опрос', request_poll=KeyboardButtonPollType()),
        ],
        [
            KeyboardButton(text='Отправить номер телефона ☎️', request_contact=True),
            KeyboardButton(text='Отправить локацию 🗺️', request_location=True),
        ],
    ],
    resize_keyboard=True,
)

# функция для формирования клавиатуры, эту функцию можно будет
# применять в любом хендлере
'''
    Parameters request_contact and request_location must be as indexes
    of btns args for buttons you need.
    Example:
    get_keyboard(
            "Меню",
            "О магазине",
            "Варианты оплаты",
            "Варианты доставки",
            "Отправить номер телефона"
            placeholder="Что вас интересует?",
            request_contact=4, это индекс кнопки, где 4 это "Отправить номер телефона"
            sizes=(2, 2, 1)
                )
'''
def get_keyboard(
        *btns: str,
        placeholder: str = None,
        request_contact: int = None,
        request_location: int = None,
        sizes: tuple[int] = (2,),
                ):
        keyboard = ReplyKeyboardBuilder()

        for index, text in enumerate(btns, start=0):
            if request_contact and request_contact == index:
                keyboard.add(KeyboardButton(text=text, request_contact=True))

            elif request_location and request_location == index:
                keyboard.add(KeyboardButton(text=text, request_location=True))

            else:
                keyboard.add(KeyboardButton(text=text))

        return keyboard.adjust(*sizes).as_markup(
            resize_keyboard=True, input_field_placeholder=placeholder)
