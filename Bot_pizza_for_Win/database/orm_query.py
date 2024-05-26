from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Product


# функция для добавления данных в БД
async def orm_add_product(session: AsyncSession, data: dict):
    # добавляем в БД данные из словаря
    obj = Product(
        name = data['name'],
        description = data['description'],
        price = float(data['price']),
        image = data['image'],
        )
    session.add(obj)
    # сохряняем изменения в сессии
    await session.commit()


# функция, которая выдает список всех товаров, которые есть
async def orm_get_products(session: AsyncSession):
    query = select(Product) # выбираем все записи из БД
    result = await session.execute(query) # execute - выполнить запрос
    return result.scalars().all()

# функция, которая будет выбирать отдельный продукт
async def orm_get_product(session: AsyncSession, product_id: int):
    query = select(Product).where(Product.id == product_id)
    result = await session.execute(query)
    return result.scalar()

# функция для обновления конкретной записи (продукта)
async def orm_update_product(session: AsyncSession, product_id: int, data):
    query = update(Product).where(Product.id == product_id).values(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        image=data["image"],)
    await session.execute(query)
    await session.commit()

# функция для удаления конкретной записи (товара)
async def orm_delete_product(session: AsyncSession, product_id: int):
    query = delete(Product).where(Product.id == product_id)
    await session.execute(query)
    await session.commit()