from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (KeyboardButton, Message,
                           ReplyKeyboardMarkup, ReplyKeyboardRemove,
                           KeyboardButtonPollType)
from bot_token import token_num

BOT_TOKEN = token_num

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Инициализируем билдер
kb_builder = ReplyKeyboardBuilder()

# Создаем кнопки
poll_btn = KeyboardButton(
    text='Создать опрос',
    request_poll=KeyboardButtonPollType(type='regular')
)
quiz_btn = KeyboardButton(
    text='Создать викторину',
    request_poll=KeyboardButtonPollType(type='quiz')
)

# Добавляем кнопки в билдер
kb_builder.row(poll_btn, quiz_btn, width=1)

# Создаем объект клавиатуры
keyboard: ReplyKeyboardMarkup = kb_builder.as_markup(
    resize_keyboard=True,
    one_time_keyboard=True
)


# Этот хэндлер будет срабатывать на команду "/start"
# и отправлять в чат клавиатуру
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text='Специальные кнопки',
        reply_markup=keyboard
                        )


if __name__ == '__main__':
    dp.run_polling(bot)