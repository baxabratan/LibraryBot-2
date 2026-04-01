from aiogram.fsm.state import StatesGroup, State

class AdminAddCategory(StatesGroup):
    waiting_for_name = State()

class AdminAddBook(StatesGroup):
    waiting_for_title = State()
    waiting_for_author = State()
    waiting_for_description = State()
    waiting_for_category = State()
    waiting_for_file = State()

class AdminDeleteBook(StatesGroup):
    waiting_for_id = State()

class RequestBook(StatesGroup):
    waiting_for_book_name = State()

class ContactAdmin(StatesGroup):
    waiting_for_message = State()

