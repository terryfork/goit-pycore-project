from models import Note
from repository import NoteRepository


class NoteService:

    def __init__(self):
        self.book = NoteRepository.load()

    def add_note(self, title, content, tags):
        note = Note(title, content, tags)
        self.book.add_note(note)
        NoteRepository.save(self.book)

    # TODO: others methods
