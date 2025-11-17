import pytest
from datetime import date, datetime

from contactbook import Contact, Contactbook
from config import MAX_NAME_LEN, MAX_ADDR_LEN, DOB_FORMAT


# ---------- ТЕСТИ ВАЛІДАЦІЇ ПОЛІВ Contact ----------
def test_name_validator_valid():
    """Ім'я з літерами (латиниця/кірилиця) вважається валідним."""
    assert Contact.name_validator("Ivan")
    assert Contact.name_validator("Іван")


def test_name_validator_invalid_empty_or_nonalpha():
    """Порожні або не з букв символи не проходять валідацію імені."""
    assert not Contact.name_validator("")
    assert not Contact.name_validator("  ")
    assert not Contact.name_validator("Ivan123")
    assert not Contact.name_validator("!@#$")


def test_name_validator_too_long():
    """Дуже довге ім'я має вважатися невалідним."""
    long_name = "A" * (MAX_NAME_LEN + 50)
    assert not Contact.name_validator(long_name)


def test_addr_validator_valid_and_too_long():
    """Адреса в межах ліміту валідна, довша за ліміт — ні."""
    assert Contact.addr_validator("Some address, Kyiv")

    long_addr = "X" * (MAX_ADDR_LEN + 1)
    assert not Contact.addr_validator(long_addr)


def test_phone_validator_valid_and_invalid():
    """Перевірка різних форматів телефону: валідні та явно невалідні."""
    assert Contact.phone_validator("+380501234567")
    assert Contact.phone_validator("050 123 45 67")
    assert Contact.phone_validator("+38(050)123-45-67")

    assert not Contact.phone_validator("++380501234567")
    assert not Contact.phone_validator("380+501234567")


def test_email_validator_valid_and_invalid():
    """Валідні email-и проходять, неправильні формати — ні."""
    assert Contact.email_validator("user@example.com")
    assert Contact.email_validator("user.name+tag@sub.domain.co.uk")

    assert not Contact.email_validator("")
    assert not Contact.email_validator("just_text")
    assert not Contact.email_validator("user@@example.com")
    assert not Contact.email_validator("user@")
    assert not Contact.email_validator("@example.com")


def test_dob_validator_past_date_ok():
    """Дата народження в минулому повинна бути валідною."""
    today = date.today()
    past = today.replace(year=today.year - 20).strftime(DOB_FORMAT)
    assert Contact.dob_validator(past)


def test_dob_validator_future_date_invalid():
    """Дата народження в майбутньому повинна бути невалідною."""
    today = date.today()
    future = today.replace(year=today.year + 1).strftime(DOB_FORMAT)
    assert not Contact.dob_validator(future)


def test_dob_validator_invalid_format():
    """Невірний формат дати або випадковий текст — невалідні."""
    assert not Contact.dob_validator("31-02-2000")
    assert not Contact.dob_validator("abracadabra")


def test_phone_normalize_to_ukraine_format():
    """phone_normalize приводить номер до формату +380XXXXXXXXX."""
    normalized = Contact.phone_normalize("050 123-45-67")
    assert normalized.startswith("+380")
    assert len(normalized) == 13
    assert normalized[-9:] == "501234567"


def test_field_validator_known_and_unknown_field():
    """field_validator повертає True лише для відомих полів моделі Contact."""
    assert Contact.field_validator("name")
    assert Contact.field_validator("dob")
    assert not Contact.field_validator("unknown_field")



# ---------- ТЕСТИ РОБОТИ СЕТТЕРІВ ТА ЗБЕРІГАННЯ ДАНИХ В Contact ----------
def test_contact_setters_store_valid_values():
    """При ініціалізації валідні значення зберігаються у внутрішньому словнику."""
    today_str = date.today().strftime(DOB_FORMAT)
    c = Contact(
        name="Ivan",
        phone="050 123-45-67",
        email="ivan@example.com",
        dob=today_str,
        addr="Kyiv",
    )

    assert c.name == "Ivan"
    assert c.phone == "050 123-45-67"
    assert isinstance(c.dob, datetime)
    assert c.dob.strftime(DOB_FORMAT) == today_str
    assert c.email == "ivan@example.com"
    assert c.addr == "Kyiv"


def test_contact_setters_ignore_invalid_values():
    """Сеттери мають ігнорувати невалідні значення та залишати старі."""
    today_str = date.today().strftime(DOB_FORMAT)
    c = Contact(
        name="Ivan",
        phone="050 123-45-67",
        email="ivan@example.com",
        dob=today_str,
        addr="Kyiv",
    )

    c.name = "123"
    c.email = "wrong_email"
    c.phone = "абракадабра"

    assert c.name == "Ivan"
    assert c.email == "ivan@example.com"
    assert c.phone == "050 123-45-67"


def test_dob_setter_invalid_raises_value_error():
    """Сеттер dob повинен піднімати ValueError при невалідній даті."""
    today_str = date.today().strftime(DOB_FORMAT)
    c = Contact(
        name="Ivan",
        phone="+380501234567",
        email="ivan@example.com",
        dob=today_str,
        addr="Kyiv",
    )
    with pytest.raises(ValueError):
        c.dob = "31-02-2000"


# ---------- ТЕСТИ ДЛЯ Contactbook: ПОШУК ТА ВИВІД ----------
def test_get_contact_found(book_with_one_contact: Contactbook):
    """get_contact повертає рядок з даними, якщо контакт знайдений."""
    txt = book_with_one_contact.get_contact("Ivan")
    assert "Ivan" in txt


def test_get_contact_not_found(empty_book: Contactbook):
    """Для неіснуючого імені get_contact повертає порожній рядок."""
    txt = empty_book.get_contact("NoName")
    assert txt == ""



# ---------- ТЕСТИ: ДОДАВАННЯ КОНТАКТУ (ГЕНЕРАТОР add_contact) ----------
def test_add_contact_happy_path(empty_book: Contactbook):
    """
    Повний щасливий сценарій add_contact:
    послідовно вводимо телефон, email, дату народження, адресу.
    """
    empty_book._save_to_file = lambda self=None: None

    gen = empty_book.add_contact("Ivan")

    prompt = next(gen)
    assert "Enter phone" in prompt
    prompt = gen.send("+380501234567")

    assert "Enter email" in prompt
    prompt = gen.send("ivan@example.com")

    assert "Enter date of birthday" in prompt
    today_str = date.today().strftime(DOB_FORMAT)
    prompt = gen.send(today_str)

    assert "Enter address" in prompt
    with pytest.raises(StopIteration) as exc_info:
        gen.send("Kyiv")

    assert exc_info.value.value == "Contact added"
    assert len(empty_book.storage) == 1



# ---------- ТЕСТИ: РЕДАГУВАННЯ КОНТАКТУ ----------
def test_edit_by_id_change_only_phone(book_with_one_contact: Contactbook):
    """
    edit_by_id через генератор edit_contact змінює тільки телефон,
    інші поля пропускаємо (порожні відповіді).
    """
    book_with_one_contact._save_to_file = lambda self=None: None

    gen = book_with_one_contact.edit_by_id(1)

    prompt = next(gen)
    assert "Current phone" in prompt
    prompt = gen.send("+380671234567")

    assert "Current email" in prompt
    prompt = gen.send("")

    assert "Current birthday" in prompt
    prompt = gen.send("")

    assert "Current address" in prompt
    with pytest.raises(StopIteration) as exc_info:
        gen.send("")

    assert exc_info.value.value == "Contact updated"
    contact = book_with_one_contact.storage[1]
    assert contact.phone == "+380671234567"


def test_edit_by_id_not_found(empty_book: Contactbook):
    """
    Якщо контакту з таким id немає — edit_by_id має повернути
    відповідний рядок (тут ми очікуємо його через StopIteration.value).
    """
    gen = empty_book.edit_by_id(1)
    with pytest.raises(StopIteration) as exc_info:
        next(gen)
    assert exc_info.value.value == "No contact found with id: '1'"


def test_edit_last_contact_not_found(empty_book: Contactbook):
    """edit_last_contact повертає константу NOT_FOUND, якщо last_id відсутній."""
    empty_book.last_id = 999
    result = empty_book.edit_last_contact()
    assert result == Contactbook.NOT_FOUND


# ---------- ТЕСТИ: ПОШУК ТА ВИДАЛЕННЯ КОНТАКТІВ ----------
def test_search_contacts_found(book_with_one_contact: Contactbook):
    """search_contacts знаходить контакт за частиною email-а."""
    result = book_with_one_contact.search_contacts("email", "ivan@")
    assert "Ivan" in result


def test_search_contacts_not_found(book_with_one_contact: Contactbook):
    """Якщо збігів немає — повертається текстове повідомлення."""
    result = book_with_one_contact.search_contacts("email", "other@")
    assert result == "No contacts found matching the given criteria."


def test_del_by_id_invalid_id_format(empty_book: Contactbook):
    """del_by_id має відреагувати на нечисловий id помилкою формату."""
    gen = empty_book.del_by_id("abc")
    with pytest.raises(StopIteration) as exc_info:
        next(gen)
    assert exc_info.value.value == "Invalid id format"


def test_del_by_id_contact_not_exists(empty_book: Contactbook):
    """Для коректного id, якого немає у storage, повертається повідомлення."""
    gen = empty_book.del_by_id("1")
    with pytest.raises(StopIteration) as exc_info:
        next(gen)
    assert exc_info.value.value == "Contact doesn't exists"


def test_del_by_id_confirm_yes(book_with_one_contact: Contactbook):
    """
    При підтвердженні 'y' контакт повинен видалятися зі storage,
    а метод повертає 'Contact deleted'.
    """
    book_with_one_contact._save_to_file = lambda self=None: None

    gen = book_with_one_contact.del_by_id(1)

    prompt = next(gen)
    assert "Are you sure to delete this contact" in prompt

    with pytest.raises(StopIteration) as exc_info:
        gen.send("y")

    assert exc_info.value.value == "Contact deleted"
    assert book_with_one_contact.storage == {}


def test_del_by_id_operation_canceled(book_with_one_contact: Contactbook):
    """
    Якщо користувач відповідає не 'y' (наприклад 'n'),
    контакт залишається і повертається 'Operation canceled'.
    """
    book_with_one_contact._save_to_file = lambda self=None: None

    gen = book_with_one_contact.del_by_id(1)

    next(gen)
    with pytest.raises(StopIteration) as exc_info:
        gen.send("n")

    assert exc_info.value.value == "Operation canceled"
    assert 1 in book_with_one_contact.storage


def test_del_contact_not_found(empty_book: Contactbook):
    """del_contact повертає повідомлення, якщо контакт з таким ім'ям відсутній."""
    result = empty_book.del_contact("Ivan")
    assert result == "Contact Ivan not found"


def test_del_contact_single_found_uses_del_by_id(book_with_one_contact: Contactbook):
    """
    Якщо знайдено рівно один контакт, del_contact повинен викликати del_by_id.
    Тут підміняємо del_by_id фейковою функцією.
    """
    called_with = {}

    def fake_del_by_id(id_):
        called_with["id"] = id_
        return "OK"

    book_with_one_contact.del_by_id = fake_del_by_id  # type: ignore[assignment]
    result = book_with_one_contact.del_contact("Ivan")
    assert result == "OK"
    assert called_with["id"] == 1


# ---------- ТЕСТИ: ДНІ НАРОДЖЕННЯ ----------
def test_upcoming_birthdays_includes_today_birthday(book_with_one_contact: Contactbook):
    """
    Якщо вказати days=1 і день народження сьогодні,
    контакт має бути включений у результат.
    """
    today = date.today()
    contact = book_with_one_contact.storage[1]
    dob_str = today.replace(year=today.year - 20).strftime(DOB_FORMAT)
    contact.dob = dob_str

    result = book_with_one_contact.upcoming_birthdays(1)
    assert "Contacts having birthdays in 1 days:" in result
    assert "Ivan" in result


def test_birthday_for_year_feb_29_to_feb_28_on_non_leap_year(empty_book: Contactbook):
    """
    Для дати 29 лютого на невисокосний рік
    _birthday_for_year повинен повернути 28 лютого.
    """
    dob = datetime(2000, 2, 29)
    bday = empty_book._birthday_for_year(dob, 2021)
    assert bday.year == 2021
    assert bday.month == 2
    assert bday.day == 28
