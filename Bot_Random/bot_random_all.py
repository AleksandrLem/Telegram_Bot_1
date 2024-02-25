import random

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

BOT_TOKEN = 'token'

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Количество попыток, доступных пользователю в игре
ATTEMPTS = 5

# Словарь, в котором будут храниться данные пользователя
user = {'in_game': False,
        'secret_number': None,
        'attempts': None,
        'total_games': 0,
        'wins': 0}

# Функция, которая возвращает целое число от 1 до 100


def get_random_number() -> int:
    return random.randint(1, 100)

# Этот хендлер будет срабатывать на команду "/start"


@dp.message(CommandStart())
async def process_start_command(message: Message):
    print(message.from_user.id)
    await message.answer(
        f'Привет!\n Давайте сыграем в игру "Угадай число"?\n\n'
        f'Чтобы получить правила игры и список доступных '
        'команд - отправьте команду /help'
    )

# Это хендлер будет срабатывать на команду "/help"


@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(
        f'Правила игры:\n\nЯ загадываю число от 1 до 100, '
        f'а вам нужно его угадать\nУ вас есть {ATTEMPTS} '
        f'попыток\n\nДоступные команды:\n/help - правила '
        f'игры и список команд\n/cancel - выйти из игры\n'
        f'/stat - посмотреть статистику\n\nИграем?'
    )

# Этот хендлер будет срабатывать на команду "/stat"


@dp.message(Command(commands='stat'))
async def process_stat_command(message: Message):
    await message.answer(
        f'Всего игр сыграно: {user["total_games"]}\n'
        f'Игр выиграно: {user["wins"]}'
    )

# Этот хендлер будет срабатывать на команду "/cancel"


@dp.message(Command(commands='cancel'))
async def process_cancel_command(message: Message):
    if user['in_game']:
        user['in_game'] = False
        await message.answer(
            'Вы вышли из игры. Если захотите сыграть '
            'снова - напишите об этом'
        )
    else:
        await message.answer(
            'А мы пока не в игре. '
            'Хотите сыграть?'
        )

# Этот хэндлер будет срабатывать на согласие пользователя сыграть в игру


@dp.message(F.text.lower().in_(['да', 'давай', 'сыграем',
                                'игра', 'играть', 'хочу играть']))
async def process_positive_answer(message: Message):
    if not user['in_game']:
        user['in_game'] = True
        user['secret_number'] = get_random_number()
        user['attempts'] = ATTEMPTS
        await message.answer(
            f'О, да, хорошечно...\n\nЯ загадал число от 1 до 100, '
            f'ну извольте, попробуйте угадать! \nСударь, у Вас {ATTEMPTS} попыток'
        )
    else:
        await message.answer(
            'Пока мы играем в игру я могу '
            'реагировать только на числа от 1 до 100 '
            'и команды /cancel и /stat'
        )

# Этот хэндлер будет срабатывать на отказ пользователя сыграть в игру


@dp.message(F.text.lower().in_(['нет', 'не', 'не хочу', 'не буду']))
async def process_negative_answer(message: Message):
    if not user['in_game']:
        await message.answer(
            'Штош, отнюдь не хорошечно :(\n\nЕсли захотите поиграть - просто '
            'напишите об этом'
        )
    else:
        await message.answer(
            'Мы сейчас с вами играем. Присылайте, '
            'пожалуйста, числа от 1 до 100'
        )

# Этот хэндлер будет срабатывать на отправку пользователем чисел от 1 до 100


@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100)
async def process_number_answer(message: Message):
    if user['in_game']:
        if int(message.text) == user['secret_number']:
            user['in_game'] = False
            user['total_games'] += 1
            user['wins'] += 1
            await message.answer(
                'Ууууииииххаа!!! Мсьё, Вы угадали число!\n\n'
                'Может, сыграем еще?'
            )
        elif int(message.text) > user['secret_number']:
            user['attempts'] -= 1
            await message.answer(f"Мое число меньше. Осталось попыток: {user['attempts']}")
        elif int(message.text) < user['secret_number']:
            user['attempts'] -= 1
            await message.answer(f"Мое число больше. Осталось попыток: {user['attempts']}")

        if user['attempts'] == 0:
            user['in_game'] = False
            user['total_games'] += 1
            await message.answer(
                f'Опаньки, увы и ах, у вас больше не осталось '
                f'попыток. Сэр, Вы продули эту игрульку ; )\n\nМое число '
                f'было {user["secret_number"]}\n\nХочешь?'
                f'Сыграем еще?'
            )
    else:
        await message.answer('Мы еще не играем. Хочешь сыграть?')

# Этот хэндлер будет срабатывать на остальные любые сообщения
dp.message()


async def process_other_answers(message: Message):
    if user['in_game']:
        await message.answer('Мсьё! Мы же сейчас с вами играем. '
                             'Присылайте, пожалуйста, числа от 1 до 100')
    else:
        await message.answer(
            'Сударь, это не простое дело, давайте '
            'просто сыграем в игру?'
        )

if __name__ == '__main__':
    dp.run_polling(bot)
