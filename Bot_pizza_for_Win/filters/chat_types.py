from aiogram import Bot
from aiogram.filters import Filter
from aiogram.types import Message

# фильтр, который будет разделять хендлеры самого бота и хендлеры группы
class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: Message) -> bool:
        return message.chat.type in self.chat_types



class IsAdmin(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message, bot: Bot) -> bool:
        return message.from_user.id in bot.my_admins_list