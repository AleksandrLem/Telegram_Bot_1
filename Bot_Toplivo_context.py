from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, PhotoSize)
from bot_token import token_num

# Вместо BOT TOKEN HERE нужно вставить токен вашего бота,
# полученный у @BotFather
BOT_TOKEN = token_num

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage = MemoryStorage()

# Создаем объекты бота и диспетчера
bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=storage)

# Создаем "базу данных" пользователей
user_dict: dict[int, dict[str, str | int | bool]] = {}


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    mileage = State()        # Состояние ожидания ввода пробега
    price_one_liter = State()  # Состояние ожидания ввода цены за литр топлива
    spent_money = State()      # Состояние ожидания ввода суммы покупки топлива


# Функция возвращающая количество заправленных литров
def total_liters(spent_money, price_per_liter) -> float:
    return round(float(spent_money)/float(price_per_liter), 2)

# Функция возвращающая расход топлива
def fuel_consumption_f(total_litr, mileage) -> float:
    return round((float(total_litr)/float(mileage))*100, 2)

# Этот хэндлер будет срабатывать на команду /start вне состояний
# и предлагать перейти к заполнению анкеты, отправив команду /fillform
@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        text='Этот бот демонстрирует работу FSM\n\n'
             'Чтобы перейти к заполнению анкеты - '
             'отправьте команду /fillform'
    )


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
# и переводить бота в состояние ожидания ввода пробега
@dp.message(Command(commands='fillform'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    await message.answer(text='Пожалуйста, введите ваш пробег (км)\n'
                         'Ожидается целое число от 1 до 1500')
    # Устанавливаем состояние ожидания ввода пробега
    await state.set_state(FSMFillForm.mileage)


# Этот хэндлер будет срабатывать, если введен корректный пробег
# и переводить в состояние ожидания ввода цены за литр топлива
@dp.message(StateFilter(FSMFillForm.mileage),
            lambda x: x.text.isdigit() and 1 <= int(x.text) <= 1500)
async def process_mileage_sent(message: Message, state: FSMContext):
    # Cохраняем введенный пробег в хранилище по ключу "mileage_km"
    await state.update_data(mileage_km=message.text)
    await message.answer(text='Спасибо!\n\nТеперь введите цену за литр топлива\n'
                         'Введите число от 30 до 500')
    # Устанавливаем состояние ожидания ввода цены за литр топлива
    await state.set_state(FSMFillForm.price_one_liter)


# Этот хэндлер будет срабатывать, если во время ввода пробега
# будет введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.mileage))
async def warning_not_mileage(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на пробег\n\n'
             'Пожалуйста, введите пробег (целое число от 1 до 1500)\n\n'
             'Если вы хотите прервать заполнение анкеты - '
             'отправьте команду /cancel'
    )

# Этот хэндлер будет срабатывать, если введена корректная цена
# и переводить в состояние ожидания ввода суммы заправки
@dp.message(StateFilter(FSMFillForm.price_one_liter),
            lambda x: x.text.isdigit() and 30 <= float(x.text) <= 500)
async def process_price_liter_sent(message: Message, state: FSMContext):
    # Cохраняем введенную цену за 1 л в хранилище по ключу "price_liter"
    await state.update_data(price_liter=message.text)
    await message.answer(text='Спасибо!\n\nТеперь введите сумму заправки (руб)\n'
                         'Введите число от 1 до 20 000')
    # Устанавливаем состояние ожидания ввода суммы заправки
    await state.set_state(FSMFillForm.spent_money)


# Этот хэндлер будет срабатывать, если во время ввода цены за литр
# будет введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.price_one_liter))
async def warning_not_price_one_liter(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на цену за литр топлива\n\n'
             'Пожалуйста, введите цену за литр топлива (число от 30 до 500)\n\n'
             'Если вы хотите прервать заполнение анкеты - '
             'отправьте команду /cancel')


# Этот хэндлер будет срабатывать, если введена сумма заправки
@dp.message(StateFilter(FSMFillForm.spent_money),
            lambda x: x.text.isdigit() and 1 <= float(x.text) <= 20_000)
async def process_spent_money_sent(message: Message, state: FSMContext):
    # Cохраняем введенную сумму заправки в хранилище по ключу "price_liter"
    await state.update_data(spent_money_rub=message.text)
    user_dict[message.from_user.id] = await state.get_data()
    sum_money = user_dict[message.from_user.id]["spent_money_rub"]
    price_litr = user_dict[message.from_user.id]["price_liter"]
    await state.update_data(total_liters=total_liters(sum_money, price_litr))
    user_dict[message.from_user.id] = await state.get_data()
    total_litr = user_dict[message.from_user.id]["total_liters"]
    mileage_all = user_dict[message.from_user.id]["mileage_km"]
    await state.update_data(fuel_consumption=fuel_consumption_f(total_litr, mileage_all))
    # Добавляем в "базу данных" анкету пользователя
    # по ключу id пользователя
    user_dict[message.from_user.id] = await state.get_data()
    # Завершаем машину состояний
    await state.clear()
    await message.answer(text='Спасибо!\n\n Данные внесены'
                         'Чтобы посмотреть результат наберите команду /showdata')


# Этот хэндлер будет срабатывать, если во время ввода суммы заправки
# будет введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.spent_money))
async def warning_not_spent_money(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на сумму заправки\n\n'
             'Пожалуйста, введите сумму заправки (число от 1 до 20 000)\n\n'
             'Если вы хотите прервать заполнение анкеты - '
             'отправьте команду /cancel')





# Этот хэндлер будет срабатывать на отправку команды /showdata
# и отправлять в чат данные расчета, либо сообщение об отсутствии данных
@dp.message(Command(commands='showdata'), StateFilter(default_state))
async def process_showdata_command(message: Message):
    # Отправляем пользователю расчет, если он есть в "базе данных"
    if message.from_user.id in user_dict:
        await message.answer(
            f'Пробег: {user_dict[message.from_user.id]["mileage_km"]}\n'
            f'Цена за литр (руб): {user_dict[message.from_user.id]["price_liter"]}\n'
            f'Сумма заправки (руб): {user_dict[message.from_user.id]["spent_money_rub"]}\n'
            f'Всего литров заправлено: {user_dict[message.from_user.id]["total_liters"]}\n'
            f'Расход топлива (л/100км): {user_dict[message.from_user.id]["fuel_consumption"]}'
                           )
    else:
        # Если анкеты пользователя в базе нет - предлагаем заполнить
        await message.answer(
            text='Вы еще не заполняли анкету. Чтобы приступить - '
            'отправьте команду /fillform'
        )


# Этот хэндлер будет срабатывать на любые сообщения, кроме тех
# для которых есть отдельные хэндлеры, вне состояний
@dp.message(StateFilter(default_state))
async def send_echo(message: Message):
    await message.reply(text='Извините, моя твоя не понимать')



# Запускаем поллинг
if __name__ == '__main__':
    dp.run_polling(bot)