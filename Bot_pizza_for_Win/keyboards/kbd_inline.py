from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# функция для создания инлайн кнопок
def get_callback_btns(
    *, # * - это автоматический запрет на передачу неименованных аргументов
    btns: dict[str, str], # текст на кнопке, строка с данными, которые отправляются боту
    sizes: tuple[int] = (2,)): # как будут размещаться кнопки (например, две в ряду)

    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():

        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()

# функция для генерации инлайн-кнопок с url-ссылками куда-нибудь
def get_url_btns(
    *,
    btns: dict[str, str],
    sizes: tuple[int] = (2,)):

    keyboard = InlineKeyboardBuilder()

    for text, url in btns.items():

        keyboard.add(InlineKeyboardButton(text=text, url=url))

    return keyboard.adjust(*sizes).as_markup()


#Создать микс из CallBack и URL кнопок
def get_inlineMix_btns(
    *,
    btns: dict[str, str],
    sizes: tuple[int] = (2,)):

    keyboard = InlineKeyboardBuilder()

    for text, value in btns.items():
        if '://' in value:
            keyboard.add(InlineKeyboardButton(text=text, url=value))
        else:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=value))

    return keyboard.adjust(*sizes).as_markup()