import pickle
from storage import NoteBook


class NoteRepository:
    FILE_NAME = "notes.csv"

    @classmethod
    def save(cls, note_book: NoteBook):
        with open(cls.FILE_NAME, "wb") as f:
            pickle.dump(note_book, f)

    @classmethod
    def load(cls) -> NoteBook:
        try:
            with open(cls.FILE_NAME, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return NoteBook()
