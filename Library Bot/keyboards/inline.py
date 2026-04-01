from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.texts import get_text

def get_languages_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="English 🇬🇧", callback_data="lang_en")
    builder.button(text="Русский 🇷🇺", callback_data="lang_ru")
    builder.button(text="O'zbekcha 🇺🇿", callback_data="lang_uz")
    builder.button(text="Qaraqalpaqsha 🇰🇿", callback_data="lang_kaa")
    builder.adjust(2)
    return builder.as_markup()

def get_categories_kb(categories, page: int = 1, total_pages: int = 1, lang: str = 'en') -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for cat in categories:
        builder.button(text=cat.name, callback_data=f"cat_{cat.id}")
        
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text=get_text(lang, 'btn_prev'), callback_data=f"cats_p_{page-1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text=get_text(lang, 'btn_next'), callback_data=f"cats_p_{page+1}"))
        
    builder.adjust(1)
    if nav_buttons:
        builder.row(*nav_buttons)
        
    return builder.as_markup()

def get_books_list_kb(books, category_id: int, page: int = 1, total_pages: int = 1, lang: str = 'en') -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for book in books:
        builder.button(text=book.title, callback_data=f"book_{book.id}")
        
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text=get_text(lang, 'btn_prev'), callback_data=f"b_cat_{category_id}_p_{page-1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text=get_text(lang, 'btn_next'), callback_data=f"b_cat_{category_id}_p_{page+1}"))
        
    builder.adjust(1)
    if nav_buttons:
        builder.row(*nav_buttons)
        
    builder.row(InlineKeyboardButton(text=get_text(lang, 'btn_back'), callback_data="cats_p_1"))
    return builder.as_markup()

def get_book_info_kb(book_id: int, is_favorite: bool, lang: str = 'en') -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.button(text=get_text(lang, 'btn_download'), callback_data=f"download_{book_id}")
    
    if is_favorite:
        builder.button(text=get_text(lang, 'btn_remove_favorite'), callback_data=f"rm_fav_{book_id}")
    else:
        builder.button(text=get_text(lang, 'btn_add_favorite'), callback_data=f"add_fav_{book_id}")
        
    builder.row(InlineKeyboardButton(text=get_text(lang, 'btn_back'), callback_data=f"back_to_cats"))
    return builder.as_markup()
