import os
import sys
from datetime import date

import pytest

# Визначаємо кореневу директорію проєкту (на рівень вище за папку tests)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Додаємо корінь проєкту в sys.path, щоб імпорти config/contactbook/notes
# працювали коректно при запуску тестів
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from config import DOB_FORMAT  # noqa: E402
from contactbook import Contact, Contactbook  # noqa: E402
from notes import Notes  # noqa: E402
from commands import BotCommands  # noqa: E402


# ---------- ФІКСТУРИ ДЛЯ КНИГИ КОНТАКТІВ ----------
@pytest.fixture
def empty_book(monkeypatch) -> Contactbook:
    """
    Повертає порожню книгу контактів.

    _load_data та _save_to_file замінюємо на заглушки, щоб:
    - не читати реальний файл з диска
    - не записувати нічого під час тестів
    """
    monkeypatch.setattr(Contactbook, "_load_data", lambda self: {})
    monkeypatch.setattr(Contactbook, "_save_to_file", lambda self: None)
    return Contactbook()


@pytest.fixture
def book_with_one_contact(empty_book: Contactbook) -> Contactbook:
    """
    Книга контактів з одним тестовим контактом 'Ivan'.

    Використовується в тестах, де потрібен хоча б один запис
    у телефонній книзі.
    """
    today_str = date.today().strftime(DOB_FORMAT)
    c = Contact(
        name="Ivan",
        phone="+380501234567",
        email="ivan@example.com",
        dob=today_str,
        addr="Kyiv",
    )
    empty_book.storage[1] = c
    empty_book.last_id = 1
    return empty_book


# ---------- ФІКСТУРИ ДЛЯ НОТАТОК ----------
@pytest.fixture
def empty_notes(monkeypatch) -> Notes:
    """
    Повертає порожній об'єкт Notes.

    _load_from_file та _save_to_file замінюємо на заглушки, щоб
    ізолювати тести від файлової системи.
    """
    monkeypatch.setattr(Notes, "_load_from_file", lambda self: {})
    monkeypatch.setattr(Notes, "_save_to_file", lambda self: None)
    return Notes()


@pytest.fixture
def notes_with_one(empty_notes: Notes) -> Notes:
    """
    Об'єкт Notes з однією тестовою нотаткою 'First'.

    Використовується у тестах, де потрібна вже існуюча нотатка.
    """
    empty_notes.notes["First"] = {
        "content": "Test content",
        "created": "2025-01-01 10:00",
        "modified": "2025-01-01 10:00",
        "tags": ["test", "demo"],
    }
    return empty_notes


# ---------- ФІКСТУРА ДЛЯ BotCommands ----------
@pytest.fixture
def bot() -> BotCommands:
    """
    Повертає реальний екземпляр BotCommands.

    У тестах, де треба підмінити notes/contactbook,
    можна замокати ці атрибути окремо.
    """
    return BotCommands()
