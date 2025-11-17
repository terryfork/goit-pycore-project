import pytest

from commands import BotCommands


# ---------- ТЕСТОВІ ЗАГЛУШКИ (STUB) ДЛЯ КНИГИ КОНТАКТІВ ----------
class StubContactbook:
    """
    Спрощена заглушка для Contactbook:
    зберігає тільки виклики методів та повертає передбачувані рядки.
    """
    def __init__(self):
        self.add_contact_called_with = None
        self.search_contacts_called_with = None

    def add_contact(self, name):
        # Запам'ятовуємо, з яким ім'ям викликали метод
        self.add_contact_called_with = name
        return "ADD_CONTACT_OK"

    def upcoming_birthdays(self, days: int):
        return f"UPCOMING_{days}"

    def edit_by_name(self, name):
        return f"EDIT_BY_NAME_{name}"

    def edit_by_id(self, id_):
        return f"EDIT_BY_ID_{id_}"

    def edit_last_contact(self):
        return "EDIT_LAST"

    def search_contacts(self, key, value):
        # Запам'ятовуємо параметри пошуку
        self.search_contacts_called_with = (key, value)
        return f"SEARCH_{key}_{value}"

    def get_contact(self, name):
        return f"GET_{name}"

    def del_contact(self, name):
        return f"DEL_{name}"

    def del_by_id(self, id_):
        return f"DEL_ID_{id_}"

    def del_last(self):
        return "DEL_LAST"

    def all_contacts(self):
        return "ALL_CONTACTS"


class StubNotes:
    """
    Заглушка для Notes:
    ніяких файлів не чіпає, тільки повертає стабільні рядки.
    """
    def __init__(self):
        self.add_from_command_called_with = None

    def add_note_from_command(self, params):
        # Запам'ятовуємо параметри, з якими викликано команду
        self.add_from_command_called_with = params
        return f"ADD_NOTE_{'_'.join(params)}" if params else "ADD_NOTE_INTERACTIVE"

    def get_note(self, title):
        return f"NOTE_{title}"

    def list_all_notes(self):
        return "LIST_NOTES"

    def edit_note_from_command(self, params):
        return f"EDIT_NOTE_{'_'.join(params)}"

    def delete_note(self, title):
        return f"DEL_NOTE_{title}"

    def add_tags_from_command(self, params):
        return f"ADD_TAGS_{'_'.join(params)}"

    def remove_tags_from_command(self, params):
        return f"REMOVE_TAGS_{'_'.join(params)}"

    def search_notes_by_tag(self, tag):
        return f"SEARCH_TAG_{tag}"

    def search_notes_by_tags_from_command(self, params):
        return f"SEARCH_TAGS_{'_'.join(params)}"

    def list_all_tags(self):
        return "LIST_TAGS"

    def sort_notes_by_tag(self, tag):
        return f"SORT_BY_TAG_{tag}"


# ---------- ФІКСТУРА З ПІДМІНЕНИМИ ЗАЛЕЖНОСТЯМИ ДЛЯ BotCommands ----------
@pytest.fixture
def stubbed_bot() -> BotCommands:
    """
    Створює екземпляр BotCommands,
    але підміняє реальні contactbook/notes на заглушки.
    """
    bot = BotCommands()
    bot.contactbook = StubContactbook()
    bot.notes = StubNotes()
    return bot


# ---------- ТЕСТИ ДЛЯ КОМАНД КНИГИ КОНТАКТІВ ----------
def test_add_contact_handler_usage_when_no_params(stubbed_bot: BotCommands):
    """
    Якщо параметри не передані, декоратор input_validator
    повинен повернути рядок з підказкою використання.
    """
    result = stubbed_bot.add_contact_handler([])
    assert "add_contact" in result
    assert "Invalid fields: name" in result


def test_add_contact_handler_calls_contactbook(stubbed_bot: BotCommands):
    """
    При коректному виклику add_contact_handler
    метод contactbook.add_contact повинен бути викликаний з ім'ям.
    """
    result = stubbed_bot.add_contact_handler(["Ivan"])
    assert result == "ADD_CONTACT_OK"
    assert stubbed_bot.contactbook.add_contact_called_with == "Ivan"


def test_search_contact_handler_invalid_field_triggers_usage(stubbed_bot: BotCommands):
    """
    Якщо передати неіснуюче поле пошуку — має повернути usage, а не викликати пошук.
    """
    result = stubbed_bot.search_contact_handler(["invalid_field", "value"])
    assert "search_contact" in result
    assert "Invalid fields: field" in result
    assert "Command usage" in result


def test_search_contact_handler_valid_field_calls_contactbook(stubbed_bot: BotCommands):
    """
    Для валідного поля (наприклад 'name') повинен викликатися search_contacts.
    """
    result = stubbed_bot.search_contact_handler(["name", "Ivan"])
    assert result.startswith("SEARCH_")
    assert stubbed_bot.contactbook.search_contacts_called_with == ("name", "Ivan")


def test_help_handler_lists_commands(stubbed_bot: BotCommands):
    """help_handler має виводити список доступних команд з описами."""
    help_text = stubbed_bot.help_handler([])
    assert "Available comands:" in help_text
    assert "add_contact" in help_text
    assert "add_note" in help_text
    assert "help" in help_text


def test_get_avail_commands_contains_some_handlers(stubbed_bot: BotCommands):
    """
    get_avail_commands повертає список назв команд
    (без суфіксу _handler) і серед них мають бути базові.
    """
    commands = stubbed_bot.get_avail_commands()
    assert "add_contact" in commands
    assert "exit" in commands
    assert "help" in commands
    assert all(not c.endswith("_handler") for c in commands)


def test_find_similar_prefers_close_match(stubbed_bot: BotCommands):
    """
    find_similar повинен підказувати найбільш схожу команду
    для помилково введеного рядка (add_contat → add_contact).
    """
    suggestions = stubbed_bot.find_similar("add_contat")
    assert "add_contact" in suggestions


def test_upcoming_birthdays_handler_invalid_days(stubbed_bot: BotCommands):
    """
    Якщо дні не конвертуються в int — повертається повідомлення про помилку.
    """
    result = stubbed_bot.upcoming_birthdays_handler(["abc"])
    assert result == "Invalid days format"


def test_upcoming_birthdays_handler_valid_days(stubbed_bot: BotCommands):
    """
    Коректні дні повинні передаватися в contactbook.upcoming_birthdays.
    """
    result = stubbed_bot.upcoming_birthdays_handler(["7"])
    assert result == "UPCOMING_7"


def test_edit_contact_id_handler_invalid_id(stubbed_bot: BotCommands):
    """
    Якщо id не число — edit_contact_id_handler повертає помилку формату.
    """
    result = stubbed_bot.edit_contact_id_handler(["abc"])
    assert result == "Invalid id format"


def test_edit_contact_id_handler_valid(stubbed_bot: BotCommands):
    """
    Якщо id валідний, викликається edit_by_id у contactbook.
    """
    result = stubbed_bot.edit_contact_id_handler(["5"])
    assert result == "EDIT_BY_ID_5"


def test_edit_contact_handler_calls_edit_by_name(stubbed_bot: BotCommands):
    """
    Команда edit_contact повинна делегувати в edit_by_name.
    """
    result = stubbed_bot.edit_contact_handler(["Ivan"])
    assert result == "EDIT_BY_NAME_Ivan"


def test_edit_last_contact_handler(stubbed_bot: BotCommands):
    """
    edit_last_contact_handler просто викликає contactbook.edit_last_contact.
    """
    result = stubbed_bot.edit_last_contact_handler([])
    assert result == "EDIT_LAST"


def test_get_contact_handler(stubbed_bot: BotCommands):
    """
    get_contact_handler делегує в contactbook.get_contact.
    """
    result = stubbed_bot.get_contact_handler(["Ivan"])
    assert result == "GET_Ivan"


def test_del_contact_handler(stubbed_bot: BotCommands):
    """
    del_contact_handler видаляє контакт за ім'ям через contactbook.del_contact.
    """
    result = stubbed_bot.del_contact_handler(["Ivan"])
    assert result == "DEL_Ivan"


def test_del_contact_id_handler(stubbed_bot: BotCommands):
    """
    del_contact_id_handler видаляє контакт за id через contactbook.del_by_id.
    """
    result = stubbed_bot.del_contact_id_handler(["5"])
    assert result == "DEL_ID_5"


def test_del_last_contact_handler(stubbed_bot: BotCommands):
    """
    del_last_contact_handler делегує в contactbook.del_last.
    """
    result = stubbed_bot.del_last_contact_handler([])
    assert result == "DEL_LAST"


def test_all_contacts_handler(stubbed_bot: BotCommands):
    """
    all_contacts_handler повинен повернути рядок зі StubContactbook.all_contacts.
    """
    result = stubbed_bot.all_contacts_handler([])
    assert result == "ALL_CONTACTS"


# ---------- ТЕСТИ ДЛЯ КОМАНД З НОТАТКАМИ ----------
def test_add_note_handler_delegates_to_notes(stubbed_bot: BotCommands):
    """
    add_note_handler має передати параметри далі в notes.add_note_from_command.
    """
    result = stubbed_bot.add_note_handler(["Title", "content", "tag1"])
    assert result == "ADD_NOTE_Title_content_tag1"
    assert stubbed_bot.notes.add_from_command_called_with == [
        "Title",
        "content",
        "tag1",
    ]


def test_show_note_handler_valid_title(stubbed_bot: BotCommands):
    """
    Для валідного title команда show_note повертає результат notes.get_note.
    """
    result = stubbed_bot.show_note_handler(["MyTitle"])
    assert result == "NOTE_MyTitle"


def test_show_note_handler_invalid_title_triggers_usage(stubbed_bot: BotCommands):
    """
    Порожній title повинен викликати валідацію input_validator і повернути usage.
    """
    result = stubbed_bot.show_note_handler([""])
    assert "show_note" in result
    assert "Invalid fields: title" in result
    assert "Command usage" in result


def test_list_notes_handler(stubbed_bot: BotCommands):
    """
    list_notes_handler просто делегує в notes.list_all_notes.
    """
    result = stubbed_bot.list_notes_handler([])
    assert result == "LIST_NOTES"


def test_edit_note_handler_valid_title(stubbed_bot: BotCommands):
    """
    При валідному title edit_note_handler викликає notes.edit_note_from_command.
    """
    result = stubbed_bot.edit_note_handler(["Title", "new content"])
    assert result == "EDIT_NOTE_Title_new content"


def test_edit_note_handler_invalid_title(stubbed_bot: BotCommands):
    """
    Порожній title в edit_note_handler повинен повернути повідомлення про помилку.
    """
    result = stubbed_bot.edit_note_handler([""])
    assert "edit_note" in result
    assert "Invalid fields: title" in result


def test_delete_note_handler(stubbed_bot: BotCommands):
    """
    delete_note_handler делегує видалення в notes.delete_note.
    """
    result = stubbed_bot.delete_note_handler(["Title"])
    assert result == "DEL_NOTE_Title"


def test_add_tags_handler(stubbed_bot: BotCommands):
    """
    add_tags_handler викликає notes.add_tags_from_command з усіма параметрами.
    """
    result = stubbed_bot.add_tags_handler(["Title", "tag1", "tag2"])
    assert result == "ADD_TAGS_Title_tag1_tag2"


def test_remove_tags_handler(stubbed_bot: BotCommands):
    """
    remove_tags_handler делегує виклик у notes.remove_tags_from_command.
    """
    result = stubbed_bot.remove_tags_handler(["Title", "tag1"])
    assert result == "REMOVE_TAGS_Title_tag1"


def test_search_notes_by_tag_handler(stubbed_bot: BotCommands):
    """
    search_notes_by_tag_handler передає тег у notes.search_notes_by_tag.
    """
    result = stubbed_bot.search_notes_by_tag_handler(["tag1"])
    assert result == "SEARCH_TAG_tag1"


def test_search_notes_by_tags_handler(stubbed_bot: BotCommands):
    """
    search_notes_by_tags_handler делегує в notes.search_notes_by_tags_from_command.
    """
    result = stubbed_bot.search_notes_by_tags_handler(["tag1", "tag2"])
    assert result == "SEARCH_TAGS_tag1_tag2"


def test_list_all_tags_handler(stubbed_bot: BotCommands):
    """
    list_all_tags_handler повертає результат notes.list_all_tags.
    """
    result = stubbed_bot.list_all_tags_handler([])
    assert result == "LIST_TAGS"


def test_sort_notes_by_tag_handler(stubbed_bot: BotCommands):
    """
    sort_notes_by_tag_handler сортує нотатки через notes.sort_notes_by_tag.
    """
    result = stubbed_bot.sort_notes_by_tag_handler(["tag1"])
    assert result == "SORT_BY_TAG_tag1"


# ---------- ЗАГАЛЬНІ КОМАНДИ (exit/close/help/find_similar) ----------      
def test_close_handler_uses_exit_handler(stubbed_bot: BotCommands):
    """
    close_handler повинен виставити прапорець done в True
    і повернути рядок 'Bye!'.
    """
    assert stubbed_bot.done is False
    msg = stubbed_bot.close_handler([])
    assert msg == "Bye!"
    assert stubbed_bot.done is True


def test_find_similar_returns_empty_for_too_short_query(stubbed_bot: BotCommands):
    """
    Якщо строка запиту занадто коротка — підказки не повертаються.
    """
    suggestions = stubbed_bot.find_similar("x")
    assert suggestions == []
