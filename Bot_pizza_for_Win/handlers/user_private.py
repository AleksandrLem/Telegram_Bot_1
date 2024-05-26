from aiogram import F, Bot, types, Router
from aiogram.filters import CommandStart, Command, or_f
from aiogram.utils.formatting import as_list, as_marked_section, Bold
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import orm_get_products
from filters.chat_types import ChatTypeFilter
from keyboards.kbd_reply import (start_kbd, del_kbd,
                                 start_kbd2, start_kbd3,
                                 kbd_location_phone, get_keyboard)


user_private_router = Router()
# отделяем роутеры бота от роутеров чата
user_private_router.message.filter(ChatTypeFilter(['private']))



# хендлер для старта
@user_private_router.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer('Да, чувак, мы стартанули)')


@user_private_router.message(or_f(Command("menu"), (F.text.lower() == "меню")))
async def menu_cmd(message: types.Message, session: AsyncSession):
    for product in await orm_get_products(session):
        await message.answer_photo(
            product.image,
            caption=f"<strong>{product.name}\
                    </strong>\n{product.description}\nСтоимость: {round(product.price, 2)}",
        )
    await message.answer("Вот меню:")



# хендлер эхо, можно несколько роутеров повесить
# @user_private_router.message(F.text.lower().contains('меню'))
# @user_private_router.message(Command('menu'))
# async def start_menu(message: types.Message):
#     # Ответ с упоминание автора сообщения
#     # Это меню... делаем жирным через parse_mode
#     await message.reply(f'<b>Это меню...</b>')

# Магический фильтр F. Комбинация нескольких фильтров
@user_private_router.message((F.text.lower().contains('ком')) | (F.text.lower() == 'фильтры'))
async def filter_func(message: types.Message):
    await message.answer('F-фильтр комбинация')



# Магический фильтр F
@user_private_router.message(F.text.lower() == 'одиночный фильтр')
async def filter_func(message: types.Message):
    await message.answer('F-филтр работает нормально')


# Магический фильтр F добавим клавиатуру
@user_private_router.message(F.text.lower() == 'клава и функция')
async def filter_kbd(message: types.Message):
    await message.answer('А вот и клава-функция',
                         reply_markup=get_keyboard('Раз кнопка',
                                                    'Два кнопка',
                                                    'Три кнопка',
                                                    placeholder='жмякни кнопку',
                                                    sizes=(1, 2)))

# Магический фильтр F добавим клавиатуру
@user_private_router.message(F.text.lower() == 'клавиатура')
async def filter_kbd(message: types.Message):
    await message.answer('Добавил клавиатуру', reply_markup=start_kbd)


# Магический фильтр F добавим клавиатуру
@user_private_router.message(F.text.lower() == 'клавиатура2')
async def filter_kbd(message: types.Message):
    await message.answer('Добавил клавиатуру2',
                         reply_markup=start_kbd2.as_markup(
                            resize_keyboard=True,
                            input_field_placeholder='жмякни кнопку'
                         ))


# Магический фильтр F добавим клавиатуру
@user_private_router.message(F.text.lower() == 'клавиатура3')
async def filter_kbd(message: types.Message):
    await message.answer('Добавил клавиатуру3',
                         reply_markup=start_kbd3.as_markup(
                            resize_keyboard=True,
                            input_field_placeholder='жмякни кнопку'
                         ))


# Магический фильтр F добавим клавиатуру
@user_private_router.message(F.text.lower() == 'локация')
async def filter_kbd(message: types.Message):
    await message.answer('Добавил клавиатуру', reply_markup=kbd_location_phone)



# Магический фильтр F убираем клавиатуру
@user_private_router.message(F.text.lower() == 'убрать клаву')
async def filter_kbd(message: types.Message):
    await message.answer('Убрал клаву', reply_markup=del_kbd)


# отлавливаем контакт
@user_private_router.message(F.contact)
async def get_contact(message: types.Message):
    await message.answer('номер получен')
    await message.answer(str(message.contact))

# отлавливаем локацию
@user_private_router.message(F.location)
async def get_location(message: types.Message):
    await message.answer('локация получена')
    await message.answer(str(message.location))


# для вариантов оплаты делаем часть текста жирным
# делаем также маркировку пунктов
@user_private_router.message(F.text.lower() == 'варианты оплаты')
@user_private_router.message(Command('payment'))
async def payment_cmd(message: types.Message):

    txt = as_marked_section(
        Bold('Варианты оплаты:'), # Bold делает текст жирным, это оглавление
        'Картой в боте',
        'Оплаты при получении (карта/наличные)',
        'В заведении',
        marker='✅ ' # маркируем пункты таким значком
    )
    await message.answer(txt.as_html())



# варианты доставки тоже маркируем
@user_private_router.message(
        (F.text.lower().contains('доставк')) | (F.text.lower() == 'варианты доставки'))
@user_private_router.message(Command('shipping'))
async def shipping(message: types.Message):

    txts = as_list(
        as_marked_section(
            Bold('Вариант доставки:'),
            'Курьер',
            'Самовывоз',
            'Поедим у вас',
            marker='✅ '
        ),
        as_marked_section(
            Bold('Нельзя:'),
            'Почта',
            'Голуби',
            marker='❌ '

        ),
        sep='\n--------------------\n'
        )
    await message.answer(txts.as_html())



# Магический фильтр F
# @user_private_router.message(F.photo)
# async def filter_photo(message: types.Message):
#     await message.answer('Фото принято')

# @user_private_router.message()
# async def start_others(message: types.Message, bot: Bot):
#     # ответ через метод бота
#     await bot.send_message(message.from_user.id, text='Опа, ага')
#     # Ответ с упоминание автора сообщения
#     await message.reply(f'Ти пишешь: {message.text}. \n Ну допустим...')
#     text: str | None = message.text
#     if text in ['Hi', 'Hello', 'Привет']:
#         await message.answer(f'Приветики!! Тута хорошечно')
#     elif text in ['Пока', 'покедова', 'до свидосы', 'bay']:
#         await message.answer(f'Довай, покедова)))')
#     else:
#         await message.answer(f'Ты написал мне: {message.text},\n Я скажу, что это для меня легко')
