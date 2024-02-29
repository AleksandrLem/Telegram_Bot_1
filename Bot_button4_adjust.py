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

# Инициализируем билдер
kb_builder = ReplyKeyboardBuilder()

# Создаем первый список с кнопками
buttons_1: list[KeyboardButton] = [
    KeyboardButton(text=f'Кнопка {i + 1}') for i in range(8)
]
# Распаковываем список с кнопками методом add
kb_builder.add(*buttons_1)

# Явно сообщаем билдеру сколько хотим видеть кнопок в 1-м и 2-м рядах
# По сути мы задаем количество кнопок в 1-й строке (это 1), затем
# все последующие строки заполняем строками по 3 кнопки, а в последней строке
# будет 1 кнопка, т.к. для этой строки осталась только одна кнопка, если количество
# кнопок будет 9, то для последней строки останется 2 кнопки
kb_builder.adjust(1, 3)
# Ну, вот, как мы и хотели - в первом ряду одна кнопка, во втором - 3.
# В третьем тоже 3, потому что оставшиеся кнопки не могут в одном
# ряду превышать в своем количестве значения последнего
# переданного аргумента в adjust, ну и на 4-й ряд перешла
# последняя оставшаяся кнопка.




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