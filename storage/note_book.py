from models import Note


class NoteBook:

    def __init__(self):
        self.notes = []

    def add_note(self, note: Note):
        self.notes.append(note)

    def remove_note(self, note: Note):
        self.notes.remove(note)

    def find_by_title(self, title: str):
        return [note for note in self.notes if note.title == title]

    def find_by_content(self, search_text: str):
        search_text = search_text.lower()
        for note in self.notes:
            if search_text in note.content.lower():
                return note

    def find_by_value(self, value: str):
        self.find_by_title(value)
        self.find_by_content(value)
        pass

    def find_by_tag(self, tag: str):
        for note in self.notes:
            if tag in note.tags:
                return note
