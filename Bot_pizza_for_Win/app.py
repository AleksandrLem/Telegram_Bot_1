import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.strategy import FSMStrategy


#----------------------------------
# все записи между #-- работают и при локальной разработке бота
# и при переносе бота на сервер
# find_dotenv - находит файл автоматически
from dotenv import find_dotenv, load_dotenv
# загружаем переменные из файла .env
load_dotenv(find_dotenv())

#from middlewarwes.db import CounterMiddleware
from middlewarwes.db import DataBaseSession
from database.engine import create_db, drop_db, session_maker
from handlers.user_private import user_private_router
from handlers.user_group import user_group_router
from handlers.admin_private import admin_router
from keyboards.set_menu import private



# создаем глобальную переменную, в которую помещаем виды
# апдейтов, которые будет обрабатывать бот
# это нужно для того, чтобы бот не принимал абсолютно все
# апдейты, которые ему прилетают (экономия ресурсов)
ALLOWED_UPDATES = ['message', 'edited_message', 'callback_query']

# пропишем парсмод в bot, чтобы поменять стиль текста,
# который будет отправлять бот пользователю
bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML) # загружаем токен из .env
bot.my_admins_list = [] # список администраторов чата
#----------------------------------------------


dp = Dispatcher() # отвечает за фильтрацию сообщений, обрабатывет update

# регистрируем промежуточный слой, который работает после фильтрации
# admin_router.message.middleware(CounterMiddleware())

# подключаем роутеры к главному роутеру, т.е. к диспетчеру
dp.include_routers(user_private_router, user_group_router, admin_router)

# функция создает таблицу
async def on_startup(bot):
    run_param = False # параметр для примера, невнятное объяснение на 30 мин
    if run_param:
        await drop_db()
    await create_db()

async def on_shoutdown(bot):
    print('бот лег')

# запускаем бота
# это метод бесконечно спрашивет сервер телеграм на наличие обновлений
async def main():
    dp.startup.register(on_startup) # запускается во время старта бота
    dp.shutdown.register(on_shoutdown) # запускается при завершении работы бота

    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    # создает таблицы БД
    # await create_db()
    # удаляем все обновления, пока бот был в offline
    await bot.delete_webhook(drop_pending_updates=True)

    # создаем меню, где commands - это список с кнопками
    # scope - это не обязательный параметр, указывает для кого эти кнопки
    # это либо все пользователи, либо админы, либо только для определенной группы и т.д.
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    # Чтобы удалить все кнопки:
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats)

    # Запуск бота
    # allowed_updates - отвечает за то, какие обновления
    # будет получать бот
    # в allowed_updates передаем либо список ALLOWED_UPDATES, либо resolve_used_update_types
    # resolve_used_update_types - это апдейты, которые выставляются автоматически
    # с учетом того, какие апдейты мы используем при написании бота
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())#ALLOWED_UPDATES)

# теперь запускаем функцию main
asyncio.run(main())