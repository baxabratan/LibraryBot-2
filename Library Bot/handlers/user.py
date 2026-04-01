from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from math import ceil
import os

from database.models import User, Category, Book, favorites
from keyboards.reply import get_main_menu
from keyboards.inline import get_languages_kb, get_categories_kb, get_books_list_kb, get_book_info_kb
from utils.texts import get_text
from services.payment_service import PaymentService
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

user_router = Router()

ITEMS_PER_PAGE = 5

@user_router.message(CommandStart())
async def start_cmd(message: Message, lang: str):
    await message.answer(get_text(lang, 'welcome'), reply_markup=get_main_menu(lang))

@user_router.message(F.text == "⚙️ Language")
@user_router.message(F.text == "⚙️ Язык")
@user_router.message(F.text == "⚙️ Til")
@user_router.message(lambda msg: msg.text and ("Language" in msg.text or "Язык" in msg.text or "Til" in msg.text))
async def lang_menu(message: Message, lang: str):
    await message.answer(get_text(lang, 'select_language'), reply_markup=get_languages_kb())

@user_router.callback_query(F.data.startswith('lang_'))
async def set_lang(callback: CallbackQuery, session: AsyncSession, user: User):
    new_lang = callback.data.split('_')[1]
    user.language = new_lang
    session.add(user)
    await session.commit()
    
    await callback.message.answer(get_text(new_lang, 'language_changed'), reply_markup=get_main_menu(new_lang))
    await callback.answer()

@user_router.message(lambda msg: msg.text and ("Profile" in msg.text or "Профиль" in msg.text or "Profil" in msg.text))
async def profile_info(message: Message, user: User, lang: str):
    d = user.created_at.strftime("%Y-%m-%d") if user.created_at else "Unknown"
    text = get_text(lang, 'profile_info', id=user.id, language=user.language, date=d)
    await message.answer(text)

@user_router.message(lambda msg: msg.text and ("Books" in msg.text or "Книги" in msg.text or "Kitoblar" in msg.text or "Kitaplar" in msg.text))
async def show_categories(message: Message, session: AsyncSession, lang: str):
    result = await session.execute(select(Category))
    categories = result.scalars().all()
    
    if not categories:
        await message.answer(get_text(lang, 'no_results'))
        return
        
    await message.answer(get_text(lang, 'categories_list'), reply_markup=get_categories_kb(categories, 1, 1, lang))

@user_router.callback_query(F.data.startswith('cats_p_'))
async def cats_page(callback: CallbackQuery, session: AsyncSession, lang: str):
    page = int(callback.data.split('_')[2])
    result = await session.execute(select(Category))
    categories = result.scalars().all()
    await callback.message.edit_reply_markup(reply_markup=get_categories_kb(categories, 1, 1, lang))
    await callback.answer()

@user_router.callback_query(F.data.startswith('cat_'))
async def show_books(callback: CallbackQuery, session: AsyncSession, lang: str):
    cat_id = int(callback.data.split('_')[1])
    result = await session.execute(select(Book).where(Book.category_id == cat_id))
    books = result.scalars().all()
    
    if not books:
        await callback.answer(get_text(lang, 'no_results'), show_alert=True)
        return
        
    await callback.message.edit_text(
        get_text(lang, 'books_in_category', category_name="Category"), 
        reply_markup=get_books_list_kb(books, cat_id, 1, 1, lang)
    )

@user_router.callback_query(F.data.startswith('book_'))
async def show_book_info(callback: CallbackQuery, session: AsyncSession, user: User, lang: str):
    book_id = int(callback.data.split('_')[1])
    result = await session.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    
    if not book:
        await callback.answer(get_text(lang, 'error'), show_alert=True)
        return
        
    is_fav = any(b.id == book_id for b in user.saved_books)
    
    text = get_text(lang, 'book_info', title=book.title, author=book.author, description=book.description)
    await callback.message.edit_text(text, reply_markup=get_book_info_kb(book.id, is_fav, lang))

@user_router.callback_query(F.data == 'back_to_cats')
async def back_to_cats(callback: CallbackQuery, session: AsyncSession, lang: str):
    result = await session.execute(select(Category))
    categories = result.scalars().all()
    await callback.message.edit_text(get_text(lang, 'categories_list'), reply_markup=get_categories_kb(categories, 1, 1, lang))

@user_router.callback_query(F.data.startswith('download_'))
async def download_book(callback: CallbackQuery, session: AsyncSession, lang: str):
    book_id = int(callback.data.split('_')[1])
    result = await session.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    
    if book:
        if book.is_paid:
            has_purchased = await PaymentService.has_purchase(session, callback.from_user.id, book.id)
            if not has_purchased:
                price_text = get_text(lang, 'paid_book_msg', price=book.price)
                admin_id = os.getenv("ADMIN_IDS", "").split(",")[0].strip()
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(
                        text=get_text(lang, 'btn_buy_contact'),
                        url=f"tg://user?id={admin_id}"
                    )
                ]])
                await callback.message.answer(price_text, reply_markup=keyboard)
                await callback.answer()
                return
        
        await callback.message.answer_document(book.file_id)
    await callback.answer()

@user_router.callback_query(F.data.startswith('add_fav_'))
async def add_fav(callback: CallbackQuery, session: AsyncSession, user: User, lang: str):
    book_id = int(callback.data.split('_')[2])
    result = await session.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    
    if book and book not in user.saved_books:
        user.saved_books.append(book)
        session.add(user)
        await session.commit()
    
    await callback.message.edit_reply_markup(reply_markup=get_book_info_kb(book_id, True, lang))
    await callback.answer(get_text(lang, 'favorite_added'))

@user_router.callback_query(F.data.startswith('rm_fav_'))
async def rm_fav(callback: CallbackQuery, session: AsyncSession, user: User, lang: str):
    book_id = int(callback.data.split('_')[2])
    book = next((b for b in user.saved_books if b.id == book_id), None)
    
    if book:
        user.saved_books.remove(book)
        session.add(user)
        await session.commit()
        
    await callback.message.edit_reply_markup(reply_markup=get_book_info_kb(book_id, False, lang))
    await callback.answer(get_text(lang, 'favorite_removed'))

@user_router.message(lambda msg: msg.text and ("Favorites" in msg.text or "Избранное" in msg.text or "Sevimlilar" in msg.text or "Tańlamalar" in msg.text))
async def my_favorites(message: Message, user: User, lang: str):
    if not user.saved_books:
        await message.answer(get_text(lang, 'no_favorites'))
        return
        
    text = get_text(lang, 'your_favorites') + "\n"
    for book in user.saved_books:
        text += f"\n- {book.title} (by {book.author})"
    await message.answer(text)

@user_router.message(lambda msg: msg.text and ("Search" in msg.text or "Поиск" in msg.text or "Qidiruv" in msg.text or "Izlew" in msg.text))
async def search_prompt(message: Message, lang: str):
    await message.answer(get_text(lang, 'search_prompt'))

@user_router.message(F.text)
async def search_handler(message: Message, session: AsyncSession, lang: str):
    query = message.text
    if query.startswith('/'):
        return
        
    stmt = select(Book).where(Book.title.ilike(f"%{query}%") | Book.author.ilike(f"%{query}%"))
    result = await session.execute(stmt)
    books = result.scalars().all()
    
    if not books:
        await message.answer(get_text(lang, 'no_results'))
        return
        
    from keyboards.inline import get_books_list_kb
    await message.answer(
        get_text(lang, 'search_results', query=query), 
        reply_markup=get_books_list_kb(books, 0, 1, 1, lang)
    )
