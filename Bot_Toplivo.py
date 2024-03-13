from bot_token import token_num

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, PhotoSize)


BOT_TOKEN = token_num

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage = MemoryStorage()

# Создаем объекты бота и диспетчера
bot = Bot(token = BOT_TOKEN)
dp = Dispatcher()



# Создаем "базу данных" пользователей
user_dict: dict[int, dict[str, str | int | bool]] = {}

# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    mileage = State()        # Состояние ожидания ввода пробега
    price_per_liter = State()  # Состояние ожидания ввода цены за литр топлива
    spent_money = State()      # Состояние ожидания ввода суммы покупки топлива



# Функция возвращающая количество заправленных литров
def total_liters(spent_money, price_per_liter) -> float:
    return round(spent_money/price_per_liter, 2)

# Функция возвращающая расход топлива
def fuel_consumption(total_litr, mileage) -> float:
    return round((total_litr/mileage)*100, 2)

# Этот хэндлер будет срабатывать на команду /start вне состояний
# и предлагать перейти к заполнению анкеты, отправив команду /fillform
@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        text='Этот бот поможет сделать расчет расхода топлива\n\n'
             'Чтобы начать расчет - '
             'отправьте команду /fillform'
    )

    # Если пользователь только запустил бота и его нет в словаре '
    # 'users - добавляем его в словарь
    if message.from_user.id not in users:
        users[message.from_user.id] = {
            'in_game': False,
            'in_probeg': False,
            'in_cena_1l': False,
            'in_summa_rub': False,
            'probeg': 1,
            'cena_1_litr': 1,
            'summa_deneg': 1,
            'summa_litrov': 1,
            'rashod_topliva': 1
        }

# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию и сообщать, что эта команда работает внутри машины состояний
@dp.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text='Отменять нечего. Вы вне машины состояний\n\n'
             'Чтобы перейти к заполнению анкеты - '
             'отправьте команду /fillform'
    )

# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@dp.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Вы вышли из машины состояний\n\n'
             'Чтобы снова перейти к заполнению анкеты - '
             'отправьте команду /fillform'
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


# Этот хэндлер будет срабатывать на команду /fillform
# и переводить бота в состояние ожидания ввода имени
@dp.message(Command(commands='fillform'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    await message.answer(text='Пожалуйста, введите значение пробега')
    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(FSMFillForm.mileage)

# Этот хэндлер будет срабатывать, если введено корректное имя
# и переводить в состояние ожидания ввода возраста
@dp.message(StateFilter(FSMFillForm.mileage), F.text.idigit())
async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введенное имя в хранилище по ключу "mileage"
    await state.update_data(mileage=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите ваш возраст')
    # Устанавливаем состояние ожидания ввода возраста
    await state.set_state(FSMFillForm.fill_age)







# Этот хэндлер будет срабатывать на команду "/help"
@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(
        f'Этот бот рассчитает расход топлива в (л/100км)'
        f'Вводите значение пробега целыми числавми в диапазоне'
        f'от 1 до 10_000_000'
        f'Цена за литр(руб) и сумма заправки(руб) - положительные числа'
        f'Для вывода расчетов отправьте команду /stat'
    )

# Этот хэндлер будет срабатывать на команду "/stat"
@dp.message(Command(commands='stat'))
async def process_stat_command(message: Message):
    await message.answer(
        f'Данные по пробегу и топливу: \n'
        f'Пробег: {users[message.from_user.id]["probeg"]}\n'
        f'Цена за 1 литр: {users[message.from_user.id]["cena_1_litr"]}\n'
        f'Сумма заправки в руб. : {users[message.from_user.id]["summa_deneg"]}\n'
        f'Всего литров заправлено: {users[message.from_user.id]["summa_litrov"]}\n'
        f'Расход топлива (л/100км): {users[message.from_user.id]["rashod_topliva"]}'
    )


# Этот хэндлер будет срабатывать на команду "/cancel"
@dp.message(Command(commands='cancel'))
async def process_cancel_command(message: Message):
    if users[message.from_user.id]['in_game']:
        users[message.from_user.id]['in_game'] = False
        await message.answer(
            'Вы вышли из расчетов. Если захотите сделать расчет '
            'снова - напишите об этом'
        )
    else:
        await message.answer(
            'расчеты сейчас не проводятся'
        )

# Этот хэндлер будет срабатывать на согласие пользователя сделать расчет
@dp.message(F.text.lower().in_(['да', 'расчет']))
async def process_positive_answer(message: Message):
    if not users[message.from_user.id]['in_game']:
        users[message.from_user.id]['in_game'] = True
        await message.answer(
            'Начинаем расчет...\n'
            'Введите значение пробега в км...'
        )
    else:
        await message.answer(
            'Пока идет расчет я могу '
            'реагировать только на числа от 1 до 10_000_000 '
            'и команды /cancel и /stat'
        )

# Этот хэндлер будет срабатывать на отказ пользователя сыграть в игру
@dp.message(F.text.lower().in_(['нет', 'не', 'не хочу', 'не буду']))
async def process_negative_answer(message: Message):
    if not users[message.from_user.id]['in_game']:
        await message.answer(
            'Жаль :(\n\nЕсли захотите поиграть - просто '
            'напишите об этом'
        )
    else:
        await message.answer(
            'Мы же сейчас с вами играем. Присылайте, '
            'пожалуйста, числа от 1 до 100'
        )

# Этот хэндлер будет срабатывать на отправку пользователем чисел от 1 до 10_0000_000
# и здесь же вносим значение пробега
@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 10_0000_000)
async def process_numbers_answer(message: Message):
    if users[message.from_user.id]['in_game']:
        users[message.from_user.id]['in_probeg'] = True
        users[message.from_user.id]['probeg'] = int(message.text)
        await message.answer(f'Ок, пробег равен: {users[message.from_user.id]["probeg"]}')
    else:
        await message.answer('Мы еще не играем. Хотите сыграть?')


# Этот хэндлер будет срабатывать на отправку пользователем чисел от 1 до 300
# и здесь же вносим значение цены за литр
@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 300 and users[message.from_user.id]['in_probeg']==True)
async def process_numbers_answer(message: Message):
    if users[message.from_user.id]['in_game'] and users[message.from_user.id]['in_probeg']:
        await message.answer(f'Введите цену за 1 литр топлива: ')
        users[message.from_user.id]['in_cena_1l'] = True
        users[message.from_user.id]['in_cena_1l'] = int(message.text)
        await message.answer(f'Ок, цена за 1 литр топлива равна: {users[message.from_user.id]["cena_1_litr"]}')
    else:
        await message.answer('Мы еще не играем. Хотите сыграть?')


# Этот хэндлер будет срабатывать на остальные любые сообщения
@dp.message()
async def process_other_answers(message: Message):
    if users[message.from_user.id]['in_game']:
        await message.answer(
            'Сейчас идет процесс расчета. '
            'Присылайте, пожалуйста, числа от 1 до 10_000_000'
        )
    else:
        await message.answer(
            'Я довольно ограниченный бот, давайте '
            'просто сыграем в игру?'
        )


if __name__ == '__main__':
    dp.run_polling(bot)