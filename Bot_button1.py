# KeyboardBuilder - строитель клавиатур


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

# Создаем список с кнопками (например, 10 кнопок)
buttons: list[KeyboardButton] = [
    KeyboardButton(text=f'Кнопка моя {i + 1}') for i in range(6)
]

# Методами билдера добавляем в него кнопки (возьмем для примера метод row())
# Распаковываем список с кнопками в билдер, указываем, что
# в одном ряду должно быть 4 кнопки
kb_builder.row(*buttons,  width=3) #  width=4 - количество кнопок в строке

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