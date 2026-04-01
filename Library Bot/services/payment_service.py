from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Purchase

class PaymentService:
    @staticmethod
    async def has_purchase(session: AsyncSession, user_id: int, book_id: int) -> bool:
        stmt = select(Purchase).where(Purchase.user_id == user_id, Purchase.book_id == book_id)
        result = await session.execute(stmt)
        purchase = result.scalar_one_or_none()
        return purchase is not None

    @staticmethod
    async def create_purchase(session: AsyncSession, user_id: int, book_id: int) -> Purchase:
        purchase = Purchase(user_id=user_id, book_id=book_id)
        session.add(purchase)
        await session.commit()
        return purchase
