from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
import os

from utils.states import RequestBook
from utils.texts import get_text
from services.request_service import RequestService

requests_router = Router()

@requests_router.message(lambda msg: msg.text and ("Request" in msg.text or "Запросить" in msg.text or "so'rash" in msg.text or "soraw" in msg.text))
async def request_start(message: Message, state: FSMContext, lang: str):
    await message.answer(get_text(lang, 'request_book_prompt'))
    await state.set_state(RequestBook.waiting_for_book_name)

@requests_router.message(RequestBook.waiting_for_book_name)
async def request_finish(message: Message, state: FSMContext, session: AsyncSession, lang: str):
    book_name = message.text
    await RequestService.create_request(session, message.from_user.id, book_name)
    
    await message.answer(get_text(lang, 'request_saved'))
    await state.clear()
    
    admin_ids = os.getenv("ADMIN_IDS", "").split(",")
    admin_text = f"📩 New Request\nUser ID: {message.from_user.id}\nBook: {book_name}"
    for a_id in admin_ids:
        if a_id:
            try:
                await message.bot.send_message(chat_id=int(a_id), text=admin_text)
            except Exception:
                pass
