from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from bot_token import token

BOT_TOKEN = token

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Создаем асинхронную функцию
async def set_main_menu(bot: Bot):
    # Создаем список с командами и их описанием для кнопки menu
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Запуск бота'),
        BotCommand(command='/help',
                   description='Справка'),
        BotCommand(command='/support',
                   description='Техподдержка')
    ]
    await bot.set_my_commands(main_menu_commands)

# Регистрируем асинхронную функцию в диспетчере,
# которая будет выполняться на старте бота
dp.startup.register(set_main_menu)
# Запускаем поллинг
dp.run_polling(bot)
