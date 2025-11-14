import pickle
from storage import ContactBook


class ContactRepository:
    FILE_NAME = "contacts.csv"  # to choose the right extension

    @classmethod
    def save(cls, contact_book: ContactBook):
        with open(cls.FILE_NAME, "wb") as f:
            pickle.dump(contact_book, f)

    @classmethod
    def load(cls) -> ContactBook:
        try:
            with open(cls.FILE_NAME, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return ContactBook()
