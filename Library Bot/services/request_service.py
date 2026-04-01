from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Request

class RequestService:
    @staticmethod
    async def create_request(session: AsyncSession, user_id: int, book_name: str) -> Request:
        req = Request(user_id=user_id, book_name=book_name)
        session.add(req)
        await session.commit()
        return req
        
    @staticmethod
    async def get_pending_requests(session: AsyncSession):
        stmt = select(Request).where(Request.status == 'pending')
        result = await session.execute(stmt)
        return result.scalars().all()
        
    @staticmethod
    async def update_status(session: AsyncSession, request_id: int, status: str) -> bool:
        stmt = select(Request).where(Request.id == request_id)
        result = await session.execute(stmt)
        req = result.scalar_one_or_none()
        if req:
            req.status = status
            await session.commit()
            return True
        return False
