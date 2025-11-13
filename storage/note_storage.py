import pickle
from repository import NoteBook

class NoteBookStorage:
    NOTE_BOOK_FILE_NAME = "notes.csv"

    @classmethod
    def save(cls, note_book: NoteBook):
        with open(cls.NOTE_BOOK_FILE_NAME, "wb") as f:
            pickle.dump(note_book, f)
        
    @classmethod
    def load(cls) -> NoteBook:
        try:
            with open(cls.NOTE_BOOK_FILE_NAME, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return NoteBook()