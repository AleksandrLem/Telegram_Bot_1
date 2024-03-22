from aiogram import Router
from aiogram.types import Message

router = Router

# Этот хэндлер будет реагировать на любые сообщения пользователя,
# не предусмотренные логикой работы бота
@router.message()
async def send_echo(message: Message):
    await message.answer(f'Вот Вы говорите: "{message.text}"\n'
                         f'Мне ли не знать, как это не просто...'
                         f'Но чтение книг - всё же хорошее дело'
                         f'Команда /help может дать ответ на Ваш запрос')