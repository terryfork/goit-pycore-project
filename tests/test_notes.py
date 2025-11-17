import inspect
import pytest
from datetime import datetime

from notes import Notes
from config import DATETIME_FORMAT


# ---------- ВАЛІДАЦІЯ ПОЛІВ (title, content, tags) ----------
def test_title_validator_valid():
    """Коректний непорожній заголовок має бути валідним."""
    assert Notes.title_validator("Shopping list")


def test_title_validator_invalid_empty_or_too_long():
    """Порожній або занадто довгий заголовок повинен бути невалідним."""
    assert not Notes.title_validator("")
    assert not Notes.title_validator("   ")
    long_title = "x" * 101
    assert not Notes.title_validator(long_title)


def test_content_validator_valid_and_invalid():
    """Контент з непорожнім текстом валідний, порожній/пробіли — ні."""
    assert Notes.content_validator("Some content")
    assert not Notes.content_validator("")
    assert not Notes.content_validator("   ")


def test_normalize_tags_splits_and_trims():
    """
    normalize_tags повинен:
    - розділяти по комі
    - прибирати зайві пробіли
    - сплітити всередині по пробілах для декількох тегів підряд.
    """
    tags = Notes.normalize_tags("tag1,  tag2  ,tag3 tag4")
    assert tags == ["tag1", "tag2", "tag3", "tag4"]


def test_tags_validator_invalid_too_long():
    """
    Тег довжиною > 20 символів не має потрапляти в нормалізований список.
    Тут ми чекаємо, що tags_validator поверне True
    (строка загалом валідна), але normalize_tags відфільтрує тег.
    """
    bad_tag = "x" * 21
    assert Notes.tags_validator(bad_tag)
    assert Notes.normalize_tags(bad_tag) == []


def test_tags_validator_valid_and_empty():
    """Коректні теги та порожній рядок повинні вважатися валідними."""
    assert Notes.tags_validator("tag1, tag2")
    assert Notes.tags_validator("")
    assert Notes.tags_validator("   ")


# ---------- ДОДАВАННЯ / ОТРИМАННЯ / ВИДАЛЕННЯ НОТАТКІВ ----------
def test_add_note_success(empty_notes: Notes):
    """
    Успішне створення нотатки:
    - правильний заголовок, контент і теги,
    - перевіряємо дати created/modified та список тегів.
    """
    msg = empty_notes.add_note("Title", "Content", "tag1, tag2")
    assert msg == "Note created successfully"
    note = empty_notes.notes["Title"]
    datetime.strptime(note["created"], DATETIME_FORMAT)
    datetime.strptime(note["modified"], DATETIME_FORMAT)
    assert note["content"] == "Content"
    assert set(note["tags"]) == {"tag1", "tag2"}


def test_add_note_duplicate_title(empty_notes: Notes):
    """Якщо нотатка з таким заголовком вже існує, друга не створюється."""
    empty_notes.add_note("Title", "Content", "tag1")
    msg = empty_notes.add_note("Title", "Other content", "tag2")
    assert msg == "Note 'Title' already exists"
    assert empty_notes.notes["Title"]["content"] == "Content"


def test_get_note_found(notes_with_one: Notes):
    """get_note повертає детальний текст, якщо нотатка знайдена."""
    txt = notes_with_one.get_note("First")
    assert "Title: First" in txt
    assert "Content: Test content" in txt


def test_get_note_not_found(empty_notes: Notes):
    """Для неіснуючого заголовка повертається відповідне повідомлення."""
    txt = empty_notes.get_note("Unknown")
    assert txt == "Note 'Unknown' not found"


def test_delete_note_success(notes_with_one: Notes):
    """Успішне видалення існуючої нотатки."""
    msg = notes_with_one.delete_note("First")
    assert msg == "Note deleted successfully"
    assert "First" not in notes_with_one.notes


def test_delete_note_not_found(empty_notes: Notes):
    """Спроба видалити неіснуючу нотатку повертає повідомлення not found."""
    msg = empty_notes.delete_note("NoTitle")
    assert msg == "Note 'NoTitle' not found"


def test_add_note_interactive_invalid_content(empty_notes: Notes):
    """Невалідний контент у add_note_interactive повертає помилку формату."""
    empty_notes._save_to_file = lambda self=None: None
    gen = empty_notes.add_note_interactive("Title1")

    prompt = next(gen)
    assert "Enter note content" in prompt

    prompt = gen.send("   ")
    assert "Enter tags" in prompt

    with pytest.raises(StopIteration) as exc_info:
        gen.send("")

    assert exc_info.value.value == "Error: Invalid content format."


# ---------- ІНТЕРАКТИВНЕ ДОДАВАННЯ НОТАТКІВ (ГЕНЕРАТОРИ) ----------
def test_add_note_interactive_valid_flow(empty_notes: Notes):
    """Повний валідний сценарій add_note_interactive з тегами."""
    empty_notes._save_to_file = lambda self=None: None
    gen = empty_notes.add_note_interactive("Title1")

    prompt = next(gen)
    assert "Enter note content" in prompt
    prompt = gen.send("Some content")

    assert "Enter tags" in prompt
    with pytest.raises(StopIteration) as exc_info:
        gen.send("tag1, tag2")

    assert exc_info.value.value == "Note created successfully"
    assert "Title1" in empty_notes.notes
    assert empty_notes.notes["Title1"]["content"] == "Some content"
    assert set(empty_notes.notes["Title1"]["tags"]) == {"tag1", "tag2"}


def test_add_note_fully_interactive_invalid_title(empty_notes: Notes):
    """
    add_note_fully_interactive:
    якщо ввести некоректний заголовок (лише пробіли),
    одразу повертається помилка.
    """
    empty_notes._save_to_file = lambda self=None: None
    gen = empty_notes.add_note_fully_interactive()

    prompt = next(gen)
    assert "Enter note title" in prompt

    with pytest.raises(StopIteration) as exc_info:
        gen.send("   ")

    assert exc_info.value.value == "Error: Invalid title format."


def test_add_note_fully_interactive_valid_flow(empty_notes: Notes):
    """Повний валідний сценарій add_note_fully_interactive з тегами."""
    empty_notes._save_to_file = lambda self=None: None
    gen = empty_notes.add_note_fully_interactive()

    prompt = next(gen)
    assert "Enter note title" in prompt
    prompt = gen.send("Title2")

    assert "Enter note content" in prompt
    prompt = gen.send("Content 2")

    assert "Enter tags" in prompt
    with pytest.raises(StopIteration) as exc_info:
        gen.send("tagX")

    assert exc_info.value.value == "Note created successfully"
    assert "Title2" in empty_notes.notes


# ---------- ІНТЕРАКТИВНЕ РЕДАГУВАННЯ НОТАТКІВ ----------
def test_edit_note_interactive_not_found(empty_notes: Notes):
    """
    edit_note_interactive:
    якщо нотатка з таким title не існує, відразу повертається текст помилки.
    """
    empty_notes._save_to_file = lambda self=None: None
    gen = empty_notes.edit_note_interactive("Unknown")
    with pytest.raises(StopIteration) as exc_info:
        next(gen)
    assert exc_info.value.value == "Note 'Unknown' not found"


def test_edit_note_interactive_change_content_and_tags(notes_with_one: Notes):
    """
    edit_note_interactive:
    змінюємо контент та теги, а заголовок залишаємо тим самим.
    """
    notes_with_one._save_to_file = lambda self=None: None

    gen = notes_with_one.edit_note_interactive("First")

    prompt = next(gen)
    assert "Current title" in prompt
    prompt = gen.send("")

    assert "Current content" in prompt
    prompt = gen.send("New content")

    assert "Current tags" in prompt
    with pytest.raises(StopIteration) as exc_info:
        gen.send("tag3, tag4")

    assert exc_info.value.value == "Note updated successfully"
    key = notes_with_one._find_note_key("First")
    note = notes_with_one.notes[key]
    assert note["content"] == "New content"
    assert set(note["tags"]) == {"tag3", "tag4"}


def test_edit_note_fully_interactive_empty_title(empty_notes: Notes):
    """
    edit_note_fully_interactive:
    якщо користувач нічого не ввів (порожній title),
    повертається помилка про порожній заголовок.
    """
    empty_notes._save_to_file = lambda self=None: None
    gen = empty_notes.edit_note_fully_interactive()

    prompt = next(gen)
    assert "Enter note title to edit" in prompt

    with pytest.raises(StopIteration) as exc_info:
        gen.send("")

    assert exc_info.value.value == "Error: Title cannot be empty."


def test_edit_note_fully_interactive_not_found(empty_notes: Notes):
    """
    edit_note_fully_interactive:
    якщо введений коректний заголовок, але нотатки немає —
    повертається повідомлення 'Note <title> not found'.
    """
    empty_notes._save_to_file = lambda self=None: None
    gen = empty_notes.edit_note_fully_interactive()

    prompt = next(gen)
    assert "Enter note title to edit" in prompt

    with pytest.raises(StopIteration) as exc_info:
        gen.send("Unknown")

    assert exc_info.value.value == "Note 'Unknown' not found"



# ---------- КОМАНДНИЙ ІНТЕРФЕЙС: add_note_from_command / edit_note_from_command ----------
def test_add_note_from_command_no_params_returns_generator(empty_notes: Notes):
    """
    Якщо параметрів немає, add_note_from_command повертає генератор
    для повністю інтерактивного режиму.
    """
    res = empty_notes.add_note_from_command([])
    assert inspect.isgenerator(res)


def test_add_note_from_command_one_invalid_title(empty_notes: Notes):
    """Один параметр з некоректним title — одразу помилка."""
    res = empty_notes.add_note_from_command(["   "])
    assert res == "Error: Invalid title format."


def test_add_note_from_command_invalid_content(empty_notes: Notes):
    """
    Якщо передали заголовок і контент, але контент невалідний,
    повертається підказка з описом команди і полем content як невалідним.
    """
    res = empty_notes.add_note_from_command(["Title", "   "])
    assert "'add_note' command" in res
    assert "Invalid fields: content" in res


def test_add_note_from_command_success_with_tags(empty_notes: Notes):
    """Успішне додавання нотатки через add_note_from_command з тегами."""
    res = empty_notes.add_note_from_command(["Title", "Some content", "tag1,tag2"])
    assert res == "Note created successfully"
    assert "Title" in empty_notes.notes


def test_edit_note_from_command_invalid_title(empty_notes: Notes):
    """Некоректний title у edit_note_from_command повертає помилку."""
    res = empty_notes.edit_note_from_command(["   "])
    assert res == "Error: Invalid title format."


def test_edit_note_from_command_invalid_new_content(empty_notes: Notes):
    """
    Якщо новий контент невалідний (лише пробіли),
    edit_note_from_command повертає usage та помилку по new_content.
    """
    res = empty_notes.edit_note_from_command(["Title", "   "])
    assert "'edit_note' command" in res
    assert "Invalid fields: new_content" in res


# ---------- КОМАНДИ РОБОТИ З ТЕГАМИ: add_tags_from_command / remove_tags_from_command ----------
def test_add_tags_from_command_too_few_params(empty_notes: Notes):
    """
    add_tags_from_command з одним параметром
    повертає usage з прикладом використання.
    """
    res = empty_notes.add_tags_from_command(["OnlyTitle"])
    assert "'add_tags' command" in res
    assert "Command usage: add_tags <title> <tags>" in res


def test_add_tags_from_command_invalid_tags(empty_notes: Notes):
    """
    Якщо теги формально валідні за форматом, але нотатки немає —
    повертається 'Note <title> not found'.
    """
    bad = "x" * 50
    res = empty_notes.add_tags_from_command(["Title", bad])
    assert res == "Note 'Title' not found"


def test_add_tags_from_command_success(empty_notes: Notes):
    """Успішне додавання тегів до існуючої нотатки через команду."""
    empty_notes.add_note("Title", "Body", "")
    res = empty_notes.add_tags_from_command(["Title", "tag1,tag2"])
    assert "Tags updated. Current tags" in res
    assert set(empty_notes.notes["Title"]["tags"]) == {"tag1", "tag2"}


def test_remove_tags_from_command_too_few_params(empty_notes: Notes):
    """
    remove_tags_from_command з недостатньою кількістю параметрів
    повертає usage з правильним форматом.
    """
    res = empty_notes.remove_tags_from_command(["OnlyTitle"])
    assert "'remove_tags' command" in res
    assert "Command usage: remove_tags <title> <tags>" in res


def test_remove_tags_from_command_success(empty_notes: Notes):
    """Успішне видалення частини тегів через команду remove_tags."""
    empty_notes.add_note("Title", "Body", "tag1,tag2")
    res = empty_notes.remove_tags_from_command(["Title", "tag1"])
    assert "Tags removed. Current tags" in res
    tags = set(empty_notes.notes["Title"]["tags"])
    assert "tag1" not in tags


# ---------- КОМАНДА ПОШУКУ ЗА БАГАТЬМА ТЕГАМИ ----------
def test_search_notes_by_tags_from_command_no_params(empty_notes: Notes):
    """
    Якщо не передали жодного параметра для search_notes_by_tags_from_command,
    повертається usage з описом команди.
    """
    res = empty_notes.search_notes_by_tags_from_command([])
    assert "'search_notes_by_tags' command" in res


def test_search_notes_by_tags_from_command_any_vs_all(empty_notes: Notes):
    """
    Перевіряємо різницю між пошуком:
    - за будь-яким з тегів
    - та з усіма тегами (--all).
    """
    empty_notes.add_note("N1", "C1", "tag1, tag2")
    empty_notes.add_note("N2", "C2", "tag2, tag3")

    res_any = empty_notes.search_notes_by_tags_from_command(["tag1", "tag3"])
    assert "Found" in res_any
    assert "N1" in res_any
    assert "N2" in res_any

    res_all = empty_notes.search_notes_by_tags_from_command(["tag1", "tag3", "--all"])
    assert "No notes found with specified tags" in res_all or "Found 0" in res_all



# ---------- ПРЯМА РОБОТА З add_tags / remove_tags ----------
def test_add_tags_not_found(empty_notes: Notes):
    """add_tags повертає помилку, якщо нотатки не існує."""
    res = empty_notes.add_tags("Unknown", "tag1")
    assert res == "Note 'Unknown' not found"


def test_add_tags_and_remove_tags_flow(empty_notes: Notes):
    """
    Повний сценарій:
    - створюємо нотатку з одним тегом
    - додаємо ще два
    - видаляємо частину тегів і перевіряємо результат.
    """
    empty_notes.add_note("Title", "Body", "tag1")
    res = empty_notes.add_tags("Title", "tag2,tag3")
    assert "Tags updated" in res

    tags = set(empty_notes.notes["Title"]["tags"])
    assert tags == {"tag1", "tag2", "tag3"}

    res = empty_notes.remove_tags("Title", "tag1,tag3")
    assert "Tags removed" in res
    tags_after = set(empty_notes.notes["Title"]["tags"])
    assert tags_after == {"tag2"}


# ---------- ПОШУК / СОРТУВАННЯ / СПИСОК НОТАТКІВ ----------
def test_search_notes_by_tag_found(empty_notes: Notes):
    """Пошук за одним тегом: знаходимо лише ті нотатки, що містять цей тег."""
    empty_notes.add_note("T1", "Body1", "tag1")
    empty_notes.add_note("T2", "Body2", "tag2")
    res = empty_notes.search_notes_by_tag("tag1")
    assert "Found 1 note(s) with tag 'tag1':" in res
    assert "T1" in res
    assert "T2" not in res


def test_search_notes_by_tag_not_found(empty_notes: Notes):
    """Якщо жодна нотатка не містить тег — повертається повідомлення про це."""
    res = empty_notes.search_notes_by_tag("no_such_tag")
    assert res == "No notes found with tag 'no_such_tag'"


def test_search_notes_by_tags_any_and_all(empty_notes: Notes):
    """
    search_notes_by_tags:
    - в режимі any достатньо наявності будь-якого з тегів
    - в режимі all всі теги мають бути присутні в нотатці.
    """
    empty_notes.add_note("N1", "C1", "a, b")
    empty_notes.add_note("N2", "C2", "b, c")

    res_any = empty_notes.search_notes_by_tags("a c", match_all=False)
    assert "Found" in res_any
    assert "N1" in res_any
    assert "N2" in res_any

    res_all = empty_notes.search_notes_by_tags("a c", match_all=True)
    assert res_all == "No notes found with specified tags"


def test_list_all_tags_no_tags(empty_notes: Notes):
    """Якщо жодної нотатки з тегами немає — повертається 'No tags found'."""
    res = empty_notes.list_all_tags()
    assert res == "No tags found"


def test_list_all_tags_with_notes(empty_notes: Notes):
    """list_all_tags повертає список усіх тегів з кількістю використань."""
    empty_notes.add_note("N1", "C1", "tag1,tag2")
    empty_notes.add_note("N2", "C2", "tag2,tag3")
    res = empty_notes.list_all_tags()
    assert "All tags:" in res
    assert "tag1" in res
    assert "tag2" in res
    assert "tag3" in res


def test_sort_notes_by_tag_found_and_not_found(empty_notes: Notes):
    """sort_notes_by_tag сортує нотатки з заданим тегом, інші ігнорує."""
    empty_notes.add_note("N1", "C1", "tag1")
    empty_notes.add_note("N2", "C2", "tag1,tag2")

    res = empty_notes.sort_notes_by_tag("tag1")
    assert "Notes with tag 'tag1'" in res
    assert "N1" in res
    assert "N2" in res

    res_none = empty_notes.sort_notes_by_tag("unknown")
    assert res_none == "No notes found with tag 'unknown'"


def test_list_all_notes_empty(empty_notes: Notes):
    """Якщо нотаток немає — list_all_notes повертає 'No notes found'."""
    res = empty_notes.list_all_notes()
    assert res == "No notes found"


def test_list_all_notes_with_notes(empty_notes: Notes):
    """list_all_notes повертає короткий список всіх нот з прев'ю контенту."""
    empty_notes.add_note("N1", "C1", "")
    empty_notes.add_note("N2", "C2", "tagX")
    res = empty_notes.list_all_notes()
    assert "Your notes:" in res
    assert "N1" in res
    assert "N2" in res
