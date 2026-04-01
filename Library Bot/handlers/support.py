from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import os

from utils.states import ContactAdmin
from utils.texts import get_text

support_router = Router()

@support_router.message(lambda msg: msg.text and ("Contact" in msg.text or "Связаться" in msg.text or "yozish" in msg.text or "baylanısıw" in msg.text))
async def support_start(message: Message, state: FSMContext, lang: str):
    await message.answer(get_text(lang, 'support_prompt'))
    await state.set_state(ContactAdmin.waiting_for_message)

@support_router.message(ContactAdmin.waiting_for_message)
async def support_finish(message: Message, state: FSMContext, lang: str):
    user_text = message.text
    await message.answer(get_text(lang, 'support_msg_sent'))
    await state.clear()
    
    admin_ids = os.getenv("ADMIN_IDS", "").split(",")
    admin_msg = f"📩 New Message\nUser ID: {message.from_user.id}\nMessage: {user_text}"
    for a_id in admin_ids:
        if a_id:
            try:
                await message.bot.send_message(chat_id=int(a_id), text=admin_msg)
            except Exception:
                pass

@support_router.message(lambda msg: msg.reply_to_message and "User ID:" in msg.reply_to_message.text)
async def admin_reply(message: Message):
    admin_ids = os.getenv("ADMIN_IDS", "").split(",")
    if str(message.from_user.id) not in admin_ids:
        return
        
    try:
        original_text = message.reply_to_message.text
        for line in original_text.split('\n'):
            if line.startswith("User ID:"):
                user_id = int(line.split(":")[1].strip())
                await message.bot.send_message(chat_id=user_id, text=f"👨‍💻 Admin reply:\n\n{message.text}")
                await message.answer("Reply sent to user!")
                break
    except Exception:
        await message.answer("Could not send reply")
