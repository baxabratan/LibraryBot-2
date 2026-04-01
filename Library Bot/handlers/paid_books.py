from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
import os

from services.payment_service import PaymentService

paid_books_router = Router()

def is_admin(user_id: int) -> bool:
    admin_ids = os.getenv("ADMIN_IDS", "").split(",")
    return str(user_id) in admin_ids

@paid_books_router.message(Command("purchase"))
async def admin_purchase(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
        
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Usage: /purchase <user_id> <book_id>")
        return
        
    try:
        user_id = int(parts[1])
        book_id = int(parts[2])
        has_purchased = await PaymentService.has_purchase(session, user_id, book_id)
        if has_purchased:
            await message.answer("User already has access to this book.")
            return
            
        await PaymentService.create_purchase(session, user_id, book_id)
        await message.answer(f"Purchase granted for user {user_id} on book {book_id}")
    except ValueError:
        await message.answer("Invalid ID format.")
