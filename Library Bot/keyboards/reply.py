from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.texts import get_text

def get_main_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_text(lang, 'btn_books')),
                KeyboardButton(text=get_text(lang, 'btn_search'))
            ],
            [
                KeyboardButton(text=get_text(lang, 'btn_favorites')),
                KeyboardButton(text=get_text(lang, 'btn_profile'))
            ],
            [
                KeyboardButton(text=get_text(lang, 'btn_request')),
                KeyboardButton(text=get_text(lang, 'btn_contact_admin'))
            ],
            [
                KeyboardButton(text=get_text(lang, 'btn_language'))
            ]
        ],
        resize_keyboard=True
    )
