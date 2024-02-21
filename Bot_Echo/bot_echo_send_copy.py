from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

BOT_TOKEN = 'token'

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Этот хэндлер будет срабатывать на команду "/start"


@dp.message(Command(commands='start'))
async def process_start_command(message: Message):
    await message.answer('   Привет! \n Это Эхо-Бот \n Напишите что-нибудь')

# Этот хэндлер будет срабатывать на команду "/help"


@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer('Напишите что-нибудь и в ответ я пришлю вам ваше сообщение)')

# Этот хэндлер будет срабатывать на любые ваши сообщения,
# кроме команд "/start" и "/help"


@dp.message()
async def send_echo(message: Message):
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.reply(taxt='Данный тип апдейтов не поддерживается методом send_copy')

if __name__ == '__main__':
    dp.run_polling(bot)
