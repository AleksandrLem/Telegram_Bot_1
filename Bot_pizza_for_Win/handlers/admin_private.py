from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession


from database.orm_query import orm_add_product, orm_get_products, orm_delete_product, orm_get_product, orm_update_product
from filters.chat_types import ChatTypeFilter, IsAdmin
from keyboards.kbd_reply import get_keyboard
from keyboards.kbd_inline import get_callback_btns


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


ADMIN_KB = get_keyboard(
    "Добавить товар",
    "Ассортимент",
    placeholder="Выберите действие",
    sizes=(2,),
)

ADMIN_BACK_NO = get_keyboard(
    "Назад",
    "Отмена",
    placeholder="Жамкай, если надоело",
    sizes=(2,),
)

class AddProduct(StatesGroup):
    # шаги состояний
    name = State()
    description = State()
    price = State()
    image = State()

    product_for_change = None # продукт для изменения

    texts = {
        'AddProduct:name': 'Введите название заново:',
        'AddProduct:description': 'Введите описание заново:',
        'AddProduct:price': 'Введите стоимость заново:',
        'AddProduct:image': 'Этот стейт последний, поэтому...',
    }



@admin_router.message(Command("admin"))
async def add_product(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "Ассортимент")
async def starring_at_product(message: types.Message, session: AsyncSession):
    # проходим циклом по списку всех товаров
    for product in await orm_get_products(session):
        await message.answer_photo(
            product.image,
            caption=f'<strong>{product.name}</strong>\n{product.description}\n\
            Стоимость: {round(product.price, 2)}',
            reply_markup=get_callback_btns(btns={
                'Удалить': f'delete_{product.id}',
                'Изменить': f'change_{product.id}'
            })
        )

    await message.answer("ОК, вот список товаров")

# роутер для удаления товара
@admin_router.callback_query(F.data.startswith('delete_'))
async def delete_product(callback: types.CallbackQuery, session: AsyncSession):
    # id продукта берем из таблицы базы данных с товарами
    product_id = callback.data.split('_')[-1] # последний элемент списка и будет id
    await orm_delete_product(session, int(product_id))
    # чтобы инлайн кнопка на зависала в ожидании, используем следующее:
    await callback.answer('Товар удален', show_alert=True) # show_alert=True подтверждение действия
    # отправляем сообщение, что товар удален
    await callback.message.answer('Товар удален')





# @admin_router.message(F.text == "Изменить товар")
# async def change_product(message: types.Message):
#     await message.answer("ОК, вот список товаров")


# @admin_router.message(F.text == "Удалить товар")
# async def delete_product(message: types.Message):
#     await message.answer("Выберите товар(ы) для удаления")


#Код ниже для машины состояний (FSM)


# Хендлер для изменения товара
# Становимся в состояние ожидания ввода name
@admin_router.callback_query(StateFilter(None), F.data.startswith("change_"))
async def change_product_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    # получаем id товара
    product_id = callback.data.split("_")[-1]
    # получаем сам товар (вся строка из БД по данному товару)
    product_for_change = await orm_get_product(session, int(product_id))
    # сохраняем товар для изменения в словаре
    AddProduct.product_for_change = product_for_change

    await callback.answer()
    await callback.message.answer(
        "Введите название товара", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name)


# Становимся в состояние ожидания ввода name
@admin_router.message(StateFilter(None), F.text == "Добавить товар")
async def add_product(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите название товара", reply_markup=ADMIN_BACK_NO #types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name) # вводим название товара



# Хендлер отмены и сброса состояния должен быть всегда именно хдесь,
# после того как только встали в состояние номер 1 (элементарная очередность фильтров)
@admin_router.message(StateFilter('*'), Command("отмена"))
# StateFilter('*') означает любое состояние машини состояний
@admin_router.message(StateFilter('*'), F.text.casefold() == "отмена")
# метод casefold такой же как lower, т.е. переводит текст в нижний регистр,
# но поддерживает бОльшее количество символов
async def cancel_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state() # берем текущее состояние
    if current_state is None:
        return
    # если отменяеи изменения в товаре, то обнуляем AddProduct.product_for_change
    if AddProduct.product_for_change:
        AddProduct.product_for_change = None
    await state.clear() # очищаем машину стостояний
    await message.answer("Действия отменены", reply_markup=ADMIN_KB)


# Вернутся на шаг назад (на прошлое состояние)
@admin_router.message(StateFilter('*'), Command("назад"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "назад")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    # сначала проверяем нулевой шаг
    current_state = await state.get_state() # берем текущее состояние
    if current_state == AddProduct.name:
        await message.answer('Предыдущего шага нет. Введите название товара или напишите "отмена"')
        return

    previous = None
    # проходим циклом по всей стейтам
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"ок, вы вернулись к прошлому шагу \n {AddProduct.texts[previous.state]}")
            return
        previous = step


# Ловим данные для состояние name и потом меняем состояние на description
# фильтр or_f(F.text, F.text == '.') будет работать и в сценарии, когда админ
# добавляет товар, и в сценарии, когда админ изменяет товар, здесь
# F.text - работает на изменение или добавление названия продукта
# F.text == '.' - пропустить шаг и оставить старое название продукта
# пропускает без изменений (если админ вводит ".")
# вместо '.' можно придумать другую команду или привязать кнопку
@admin_router.message(StateFilter(AddProduct.name), or_f(F.text, F.text == '.'))
async def add_name(message: types.Message, state: FSMContext):
    # если название товара оставляем прежним, то берем название из словаря
    # и сохраняем стейт с этим именем товара (name=AddProduct.product_for_change.name)
    if message.text == ".":
        await state.update_data(name=AddProduct.product_for_change.name)
    #старая запись await state.update_data(name=message.text) # сохраняем название товара
    else:
        # Здесь можно сделать какую либо дополнительную проверку
        # и выйти из хендлера не меняя состояние с отправкой соответствующего сообщения
        # например:
        if len(message.text) >= 100:
            await message.answer(
                "Название товара не должно превышать 100 символов. \n Введите заново"
            )
            return
        # обновляем имя товара, если админ не выбрал команду "пропустить" - '.'
        await state.update_data(name=message.text)
    await message.answer("Введите описание товара")
    await state.set_state(AddProduct.description) # вводим описание товара

# Хендлер для отлова некорректных вводов для состояния name
@admin_router.message(StateFilter(AddProduct.name))
async def add_name(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели недопустимые данные. Введите текст названия товара")


# Ловим данные для состояние description и потом меняем состояние на price
@admin_router.message(AddProduct.description, or_f(F.text, F.text == "."))
async def add_description(message: types.Message, state: FSMContext):
    if message.text == ".":
        await state.update_data(description=AddProduct.product_for_change.description)
    else:
        await state.update_data(description=message.text)
    await message.answer("Введите стоимость товара")
    await state.set_state(AddProduct.price)

# Хендлер для отлова некорректных вводов для состояния description
@admin_router.message(StateFilter(AddProduct.description))
async def add_name(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели недопустимые данные. Введите текст описания товара")


# Ловим данные для состояние price и потом меняем состояние на image
@admin_router.message(AddProduct.price, or_f(F.text, F.text == "."))
async def add_price(message: types.Message, state: FSMContext):
    if message.text == ".":
        await state.update_data(price=AddProduct.product_for_change.price)
    else:
        try:
            float(message.text)
        except ValueError:
            await message.answer("Введите корректное значение цены")
            return

        await state.update_data(price=message.text)
    await message.answer("Загрузите изображение товара")
    await state.set_state(AddProduct.image)

# Хендлер для отлова некорректных ввода для состояния price
@admin_router.message(StateFilter(AddProduct.price))
async def add_price(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели недопустимые данные. Введите стоимость товара")


# Ловим данные для состояние image и потом выходим из состояний
@admin_router.message(AddProduct.image, or_f(F.photo, F.text == "."))
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text and message.text == ".":
        await state.update_data(image=AddProduct.product_for_change.image)

    else:
        await state.update_data(image=message.photo[-1].file_id)
    data = await state.get_data()
    try:
        # если меняем данные по товару, то...
        if AddProduct.product_for_change:
            await orm_update_product(session, AddProduct.product_for_change.id, data)
        else:
        # если добавляем новый товар, то...
            await orm_add_product(session, data)
        await message.answer("Товар добавлен/изменен", reply_markup=ADMIN_KB)
        await state.clear()

    except Exception as e:
        await message.answer(
            f"Ошибка: \n{str(e)}\nОбратись к программеру, он опять денег хочет",
            reply_markup=ADMIN_KB,
        )
        await state.clear()
    # удаляем из словаря товар, который был подгружен из БД для изменения
    AddProduct.product_for_change = None


# Хендлер для отлова некорректных ввода для состояния image
@admin_router.message(StateFilter(AddProduct.image))
async def add_image_err(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели недопустимые данные. Загрузите изображение товара")