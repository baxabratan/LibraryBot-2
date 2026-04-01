import os
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database.models import User, Category, Book
from utils.states import AdminAddCategory, AdminAddBook, AdminDeleteBook
from utils.texts import get_text
from keyboards.inline import get_categories_kb

admin_router = Router()

def is_admin(user_id: int) -> bool:
    admin_ids = os.getenv("ADMIN_IDS", "").split(",")
    return str(user_id) in admin_ids

@admin_router.message(Command("admin"))
async def admin_panel(message: Message, lang: str):
    if not is_admin(message.from_user.id):
        return await message.answer(get_text(lang, 'not_admin'))
    await message.answer(get_text(lang, 'admin_panel'))

@admin_router.message(Command("add_category"))
async def add_cat_start(message: Message, state: FSMContext, lang: str):
    if not is_admin(message.from_user.id):
        return
    await message.answer(get_text(lang, 'enter_category_name'))
    await state.set_state(AdminAddCategory.waiting_for_name)

@admin_router.message(AdminAddCategory.waiting_for_name)
async def add_cat_finish(message: Message, state: FSMContext, session: AsyncSession, lang: str):
    category = Category(name=message.text)
    session.add(category)
    await session.commit()
    await message.answer(get_text(lang, 'category_added'))
    await state.clear()

@admin_router.message(Command("add_book"))
async def add_book_start(message: Message, state: FSMContext, lang: str):
    if not is_admin(message.from_user.id):
        return
    await message.answer(get_text(lang, 'enter_book_title'))
    await state.set_state(AdminAddBook.waiting_for_title)

@admin_router.message(AdminAddBook.waiting_for_title)
async def add_book_title(message: Message, state: FSMContext, lang: str):
    await state.update_data(title=message.text)
    await message.answer(get_text(lang, 'enter_book_author'))
    await state.set_state(AdminAddBook.waiting_for_author)

@admin_router.message(AdminAddBook.waiting_for_author)
async def add_book_author(message: Message, state: FSMContext, lang: str):
    await state.update_data(author=message.text)
    await message.answer(get_text(lang, 'enter_book_description'))
    await state.set_state(AdminAddBook.waiting_for_description)

@admin_router.message(AdminAddBook.waiting_for_description)
async def add_book_desc(message: Message, state: FSMContext, session: AsyncSession, lang: str):
    await state.update_data(description=message.text)
    result = await session.execute(select(Category))
    categories = result.scalars().all()
    
    if not categories:
        await message.answer("No categories exist! Add one first.")
        await state.clear()
        return
        
    await message.answer(get_text(lang, 'select_book_category'), reply_markup=get_categories_kb(categories, 1, 1, lang))
    await state.set_state(AdminAddBook.waiting_for_category)

@admin_router.callback_query(AdminAddBook.waiting_for_category, F.data.startswith("cat_"))
async def add_book_cat(callback: CallbackQuery, state: FSMContext, lang: str):
    cat_id = int(callback.data.split("_")[1])
    await state.update_data(category_id=cat_id)
    await callback.message.answer(get_text(lang, 'send_book_file'))
    await state.set_state(AdminAddBook.waiting_for_file)
    await callback.answer()

@admin_router.message(AdminAddBook.waiting_for_file, F.document)
async def add_book_file(message: Message, state: FSMContext, session: AsyncSession, lang: str):
    data = await state.get_data()
    book = Book(
        title=data['title'],
        author=data['author'],
        description=data['description'],
        category_id=data['category_id'],
        file_id=message.document.file_id
    )
    session.add(book)
    await session.commit()
    await message.answer(get_text(lang, 'book_added'))
    await state.clear()

@admin_router.message(Command("delete_book"))
async def del_book_start(message: Message, state: FSMContext, lang: str):
    if not is_admin(message.from_user.id):
        return
    await message.answer(get_text(lang, 'enter_delete_book_id'))
    await state.set_state(AdminDeleteBook.waiting_for_id)

@admin_router.message(AdminDeleteBook.waiting_for_id)
async def del_book_finish(message: Message, state: FSMContext, session: AsyncSession, lang: str):
    try:
        book_id = int(message.text)
        result = await session.execute(select(Book).where(Book.id == book_id))
        book = result.scalar_one_or_none()
        if book:
            await session.delete(book)
            await session.commit()
            await message.answer(get_text(lang, 'book_deleted'))
        else:
            await message.answer(get_text(lang, 'error'))
    except ValueError:
        await message.answer(get_text(lang, 'error'))
    await state.clear()

@admin_router.message(Command("stats"))
async def bot_stats(message: Message, session: AsyncSession, lang: str):
    if not is_admin(message.from_user.id):
        return
    
    u_count = await session.scalar(select(func.count(User.id)))
    c_count = await session.scalar(select(func.count(Category.id)))
    b_count = await session.scalar(select(func.count(Book.id)))
    
    text = get_text(lang, 'stats', users=u_count, categories=c_count, books=b_count)
    await message.answer(text)

@admin_router.message(Command("requests"))
async def list_requests(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
        
    from services.request_service import RequestService
    requests = await RequestService.get_pending_requests(session)
    if not requests:
        await message.answer("No pending requests.")
        return
        
    text = "📩 Pending Requests:\n"
    for r in requests:
        text += f"ID: {r.id} | User: {r.user_id} | Book: {r.book_name}\n"
    await message.answer(text)

@admin_router.message(Command("done"))
async def request_done(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
        
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Usage: /done <id>")
        return
        
    try:
        req_id = int(parts[1])
        from services.request_service import RequestService
        success = await RequestService.update_status(session, req_id, 'done')
        if success:
            await message.answer(f"Request {req_id} marked as done.")
        else:
            await message.answer("Request not found.")
    except ValueError:
        await message.answer("Invalid ID.")

@admin_router.message(Command("reject"))
async def request_reject(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
        
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Usage: /reject <id>")
        return
        
    try:
        req_id = int(parts[1])
        from services.request_service import RequestService
        success = await RequestService.update_status(session, req_id, 'rejected')
        if success:
            await message.answer(f"Request {req_id} marked as rejected.")
        else:
            await message.answer("Request not found.")
    except ValueError:
        await message.answer("Invalid ID.")

