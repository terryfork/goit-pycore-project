# contact_book/storage.py
import pickle
from repository import ContactBook


class ContactBookStorage:
    CONTACT_BOOK_FILE_NAME = "contacts.csv"

    @classmethod
    def save(cls, contact_book: ContactBook):
        with open(cls.CONTACT_BOOK_FILE_NAME, "wb") as f:
            pickle.dump(contact_book, f)

    @classmethod
    def load(cls) -> ContactBook:
        try:
            with open(cls.CONTACT_BOOK_FILE_NAME, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return ContactBook()
