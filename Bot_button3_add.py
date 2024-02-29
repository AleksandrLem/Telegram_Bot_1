# KeyboardBuilder - строитель клавиатур

# В отличие от метода row() метод add() добавляет кнопки с
# нового ряда только если в предыдущем ряду для новых кнопок
# уже нет места. Причем, методу add все равно какой там у вас
# был параметр width до этого. Кнопки будут добавляться в ряд пока
# их там не станет 10 и только потом начнут заполнять новый ряд.
# Тоже до 10 штук.

# Создадим клавиатуру, в которую добавим 5 кнопок
# методом row с параметром width=4, а затем
# добавим еще 16 кнопок методом add.

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (KeyboardButton, Message,
                           ReplyKeyboardMarkup, ReplyKeyboardRemove)
from bot_token import token_num

BOT_TOKEN = token_num

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Инициализируем объект билдера
kb_builder = ReplyKeyboardBuilder()

# Создаем первый список с кнопками
buttons_1: list[KeyboardButton] = [
    KeyboardButton(text=f'Btn {i + 1}') for i in range(5)
]
# Создаем второй список с кнопками
buttons_2: list[KeyboardButton] = [
    KeyboardButton(text=f'Btn {i + 6}') for i in range(16)
]

# Распаковываем список с кнопками в билдер, указываем, что
# в одном ряду должно быть 4 кнопки
kb_builder.row(*buttons_1, width=4)

# Распаковываем второй список с кнопками методом add
kb_builder.add(*buttons_2)


# Этот хэндлер будет срабатывать на команду "/start"
# и отправлять в чат клавиатуру
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text='Вот такая получается клавиатура',
        reply_markup=kb_builder.as_markup(resize_keyboard=True)

    )

if __name__ == '__main__':
    dp.run_polling(bot)