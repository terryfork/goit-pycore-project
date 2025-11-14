
from models import Contact
from repository import ContactRepository


class ContactService:

    def __init__(self):
        self.book = ContactRepository.load()

    def add_contact(self,
                    name,
                    phone=None,
                    email=None,
                    address=None,
                    birthday=None
                    ):
        contact = Contact(name, phone, email, address, birthday)
        self.book.add_contact(contact)
        ContactRepository.save(self.book)

    def edit_contact(self, name, **kwargs):
        self.book.edit_contact(name, **kwargs)
        ContactRepository.save(self.book)

    def delete_contact(self, name):
        self.book.delete_by_name(name)
        ContactRepository.save(self.book)

    def show_upcoming_birthday_in(self, days: int):
        return self.book.get_upcoming_birthdays(days)
