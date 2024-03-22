from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon import LEXICON

# Функция, генерирующая клавиатуру для страницы книги
def create_pagination_keyboard(*buttons: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_bilder = InlineKeyboardBuilder()
    # Добавляем в билдер ряд с кнопками
    kb_bilder.row(*[InlineKeyboardBuilder(
        text=LEXICON[button] if button in LEXICON else button,
        callback_data=button) for button in buttons])
    # Возвращаем объект инлайн-клавиатуры
    return kb_bilder.as_markup()