from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy import select
from database.models import User
from database.database import async_session

class I18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = getattr(event, 'from_user', None)
        if not user:
            return await handler(event, data)
        
        async with async_session() as session:
            result = await session.execute(select(User).where(User.telegram_id == user.id))
            db_user = result.scalar_one_or_none()
            
            if not db_user:
                lang = user.language_code if user.language_code in ['en', 'ru', 'uz', 'kaa'] else 'en'
                db_user = User(telegram_id=user.id, language=lang)
                session.add(db_user)
                await session.commit()
                await session.refresh(db_user)
            
            data['user'] = db_user
            data['lang'] = db_user.language
            data['session'] = session
            
            return await handler(event, data)
