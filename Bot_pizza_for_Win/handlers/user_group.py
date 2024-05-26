from string import punctuation
from aiogram import F, types, Router, Bot
from filters.chat_types import ChatTypeFilter
from aiogram.filters import Command

user_group_router = Router()
user_group_router.message.filter(ChatTypeFilter(['group', 'supergroup']))

restricted_words = {'кабан', 'свинья', 'бык'}

# функция удаляет все знаки пунктуации
def clean_text(text: str):
    return text.translate(str.maketrans('', '', punctuation))

@user_group_router.message(Command('admin'))
async def get_admins(message: types.Message, bot: Bot):
    # достаем chat_id, чтобы понимать из какого чато пришло сообщение
    chat_id = message.chat.id
    # с помощью метода бота get_chat_administrators создаем список участников
    # группы с правами админа или creator
    admins_list = await bot.get_chat_administrators(chat_id)
    # можно посмотреть все данные полученных объектов
    # print(admins_list)
    admins_list = [member.user.id for member in admins_list
                   if member.status == 'creator' or member.status == 'administrator']
    # обновляем список администраторов чата
    bot.my_admins_list = admins_list
    # удаляем секретную команду admin из чата
    if message.from_user.id in admins_list:
        await message.delete()
    print(admins_list)


# этот хендлер удаляет ненормативную лексику из чата группы
@user_group_router.edited_message()
@user_group_router.message()
async def cleaner(message: types.Message):
    if restricted_words.intersection(clean_text(message.text.lower()).split()):
        await message.delete()
        # можно забанить матершиника
        # await message.chat.ban(message.from_user.id)
        await message.answer(f'{message.from_user.first_name}! Не ругайся!!!')
