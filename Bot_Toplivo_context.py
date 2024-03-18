from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.types import (Message, BotCommand)
from bot_token import token_num

# Вместо BOT TOKEN HERE нужно вставить токен вашего бота,
# полученный у @BotFather
BOT_TOKEN = token_num

# Инициализируем Redis
redis = Redis(host='localhost')

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage = RedisStorage(redis=redis)

# Создаем объекты бота и диспетчера
bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=storage)

# Создаем асинхронную функцию
async def set_main_menu(bot: Bot):
    # Создаем список с командами и их описанием для кнопки menu
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Запуск бота'),
        BotCommand(command='/help',
                   description='Справка'),
        BotCommand(command='/calculation',
                   description='Сделать расчеты'),
        BotCommand(command='/result',
                   description='Результаты расчетов'),
        BotCommand(command='/cancel',
                   description='Отмена действий')
    ]
    await bot.set_my_commands(main_menu_commands)

# Регистрируем асинхронную функцию в диспетчере,
# которая будет выполняться на старте бота
dp.startup.register(set_main_menu)


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

# Этот хэндлер будет срабатывать на команду "/help"
@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(
        'Этот бот делает расчет расхода топлива\n\n'
        'На ввод принимаются ЦЕЛЫЕ числа либо числа с ТОЧКОЙ\n'
        'Для расчетов будут нужны следующие данные:\n\n'
        ' - Пробег;\n'
        ' - Цена за 1 литр топлива;\n'
        ' - Сумма заправки;\n\n'
        'Итоги расчетов будут предоставлены примерно в таком виде:\n\n'
        'Пробег: 321 км\n'
        'Цена за 1 литр топлива: 53.3 руб.\n'
        'Сумма заправки: 1050.5 руб.\n'
        'Всего литров заправлено: 19.71\n'
        'Расход топлива: 6.14 л/100км\n\n'
        'Данные вводятся пошагово, а в итоге по команде result\n'
        'выводятся результаты расчетов\n\n'
        'Пожалуйста, при вводе данных следуйте указаниям инструкции на'
        ' каждом шаге!\n'
        'Чтобы перейти к расчетам, отправьте команду /calculation'
        )


# Этот хэндлер будет срабатывать на команду /start вне состояний
# и предлагать перейти к заполнению анкеты, отправив команду /calculation
@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        text='Этот бот поможет сделать расчет расхода топлива\n\n'
            'Для спавки отправьте команду /help\n'
            'Чтобы перейти к расчетам - '
            'отправьте команду /calculation'
    )


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию и сообщать, что эта команда работает внутри машины состояний
@dp.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text='Отменять нечего. Сейчас расчет не ведется\n\n'
             'Чтобы перейти к расчетам - '
             'отправьте команду /calculation'
    )


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@dp.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Вы прервали проведение расчетов\n\n'
             'Чтобы снова перейти к заполнению данных - '
             'отправьте команду /calculation'
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


# Этот хэндлер будет срабатывать на команду /calculation
# и переводить бота в состояние ожидания ввода пробега
@dp.message(Command(commands='calculation'), StateFilter(default_state))
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
                         'Ожидается целое число или число с ТОЧКОЙ от 30 до 500')
    # Устанавливаем состояние ожидания ввода цены за литр топлива
    await state.set_state(FSMFillForm.price_one_liter)


# Этот хэндлер будет срабатывать, если во время ввода пробега
# будет введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.mileage))
async def warning_not_mileage(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на пробег\n\n'
             'Пожалуйста, введите пробег (целое число от 1 до 1500)\n\n'
             'Если вы хотите прервать заполнение данных - '
             'отправьте команду /cancel'
    )

# Этот хэндлер будет срабатывать, если введена корректная цена
# и переводить в состояние ожидания ввода суммы заправки
@dp.message(StateFilter(FSMFillForm.price_one_liter),
            lambda x: x.text[0]!='.' and (all(map(lambda el: el in '0123456789', x.text.replace('.', '')))) and 30 <= float(x.text) <= 500)
async def process_price_liter_sent(message: Message, state: FSMContext):
    # Cохраняем введенную цену за 1 л в хранилище по ключу "price_liter"
    await state.update_data(price_liter=message.text)
    await message.answer(text='Спасибо!\n\nТеперь введите сумму заправки (руб)\n'
                         'Ожидается целое число или число с ТОЧКОЙ от 100 до 20 000')
    # Устанавливаем состояние ожидания ввода суммы заправки
    await state.set_state(FSMFillForm.spent_money)


# Этот хэндлер будет срабатывать, если во время ввода цены за литр
# будет введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.price_one_liter))
async def warning_not_price_one_liter(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на цену за литр топлива\n\n'
             'Пожалуйста, введите цену за литр топлива\n'
             'Ожидается целое число или число с ТОЧКОЙ от 30 до 500)\n\n'
             'Если вы хотите прервать заполнение данных - '
             'отправьте команду /cancel')


# Этот хэндлер будет срабатывать, если введена сумма заправки
@dp.message(StateFilter(FSMFillForm.spent_money),
            lambda x: x.text[0]!='.' and (all(map(lambda el: el in '0123456789', x.text.replace('.', '')))) and 100 <= float(x.text) <= 20_000)
async def process_spent_money_sent(message: Message, state: FSMContext):
    # Cохраняем введенную сумму заправки в хранилище по ключу "price_liter"
    await state.update_data(spent_money_rub=message.text)
    user_dict[message.from_user.id] = await state.get_data()
    sum_money = user_dict[message.from_user.id]["spent_money_rub"]
    price_litr = user_dict[message.from_user.id]["price_liter"]
    # Сохраняем количество всего заправленных литров
    await state.update_data(total_liters=total_liters(sum_money, price_litr))
    user_dict[message.from_user.id] = await state.get_data()
    total_litr = user_dict[message.from_user.id]["total_liters"]
    mileage_all = user_dict[message.from_user.id]["mileage_km"]
    # Сохраняем расход топлива
    await state.update_data(fuel_consumption=fuel_consumption_f(total_litr, mileage_all))
    # Сохраняем дату и время расчетов
    await state.update_data(date_time=datetime.now().strftime('%d.%m.%Y || %H:%M:%S'))
    # Добавляем в "базу данных" анкету пользователя
    # по ключу id пользователя
    user_dict[message.from_user.id] = await state.get_data()
    # Завершаем машину состояний
    await state.clear()
    await message.answer(text='Спасибо!\n\n Данные внесены\n'
                         'Чтобы посмотреть результат отправьте команду /result')


# Этот хэндлер будет срабатывать, если во время ввода суммы заправки
# будет введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.spent_money))
async def warning_not_spent_money(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на сумму заправки\n\n'
             'Пожалуйста, введите сумму заправки\n'
             'Ожидается целое число или число с ТОЧКОЙ от 100 до 20 000)\n\n'
             'Если вы хотите прервать заполнение анкеты - '
             'отправьте команду /cancel')





# Этот хэндлер будет срабатывать на отправку команды /result
# и отправлять в чат данные расчета, либо сообщение об отсутствии данных
@dp.message(Command(commands='result'), StateFilter(default_state))
async def process_showdata_command(message: Message):
    # Отправляем пользователю расчет, если он есть в "базе данных"
    if message.from_user.id in user_dict:
        await message.answer(
            f'Дата, время: {user_dict[message.from_user.id]["date_time"]}\n'
            f'Пробег: {user_dict[message.from_user.id]["mileage_km"]} км\n'
            f'Цена за литр: {user_dict[message.from_user.id]["price_liter"]} руб.\n'
            f'Сумма заправки: {user_dict[message.from_user.id]["spent_money_rub"]} руб.\n'
            f'Всего литров заправлено: {user_dict[message.from_user.id]["total_liters"]}\n'
            f'Расход топлива: {user_dict[message.from_user.id]["fuel_consumption"]} л/100км'
                           )
    else:
        # Если анкеты пользователя в базе нет - предлагаем заполнить
        await message.answer(
            text='Вы еще не заполняли данные. Чтобы приступить - '
            'отправьте команду /calculation'
        )


# Этот хэндлер будет срабатывать на любые сообщения, кроме тех
# для которых есть отдельные хэндлеры, вне состояний
@dp.message(StateFilter(default_state))
async def send_echo(message: Message):
    await message.reply(text='Извините, моя твоя не понимать')



# Запускаем поллинг
if __name__ == '__main__':
    dp.run_polling(bot)