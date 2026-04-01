import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from database.database import init_models
from middlewares.i18n import I18nMiddleware
from middlewares.rate_limit import RateLimitMiddleware

from handlers.user import user_router
from handlers.admin import admin_router
from handlers.paid_books import paid_books_router
from handlers.requests import requests_router
from handlers.support import support_router

logging.basicConfig(level=logging.INFO)

async def main():
    await init_models()
    
    bot = Bot(
        token=os.getenv("BOT_TOKEN"),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(I18nMiddleware())
    dp.callback_query.middleware(I18nMiddleware())
    
    dp.include_router(admin_router)
    dp.include_router(paid_books_router)
    dp.include_router(requests_router)
    dp.include_router(support_router)
    dp.include_router(user_router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
