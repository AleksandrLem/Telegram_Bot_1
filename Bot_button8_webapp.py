from aiogram.types.web_app_info import WebAppInfo
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


# Создаем кнопку
web_app_btn = KeyboardButton(
    text='Start Web App',
    web_app=WebAppInfo(url="https://stepik.org/")
)

# Создаем объект клавиатуры
web_app_keyboard = ReplyKeyboardMarkup(
    keyboard=[[web_app_btn]],
    resize_keyboard=True
)

# Этот хэндлер будет срабатывать на команду "/start"
# и отправлять в чат клавиатуру
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text='Web-приложение',
        reply_markup=web_app_keyboard
                        )


if __name__ == '__main__':
    dp.run_polling(bot)