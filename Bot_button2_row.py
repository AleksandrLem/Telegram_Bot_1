# KeyboardBuilder - строитель клавиатур
# Автоматическое размещение сначала 6-ти кнопок с
# параметром width=4, а затем еще 4-х кнопок с параметром width=3

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
    KeyboardButton(text=f'Кнопка {i + 1}') for i in range(6)
]
# Создаем второй список с кнопками
buttons_2: list[KeyboardButton] = [
    KeyboardButton(text=f'Кнопка {i + 7}') for i in range(4)
]

# Распаковываем список с кнопками в билдер, указываем, что
# в одном ряду должно быть 4 кнопки
kb_builder.row(*buttons_1, width=4)

# Еще раз распаковываем список с кнопками в билдер, указываем, что
# теперь в одном ряду должно быть 3 кнопки
kb_builder.row(*buttons_2, width=3)

# Методом as_markup() передаем клавиатуру как аргумент туда, где она требуется
# await message.answer(
#     text='Вот такая получается клавиатура',
#     reply_markup=kb_builder.as_markup()
# )

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