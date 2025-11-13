from typing import Optional
from collections import UserDict
from models import Contact


class ContactBook(UserDict):
    
    def add_contact(self, contact: Contact):
        key = contact.name.value
        if key not in self.data:
            self.data[key] = contact
            # serialize the whole ContactBook
            # ContactBookStorage.save(self)

    def find_contact_by_name(self, name: str):
        return self.data.get(name)

    def edit_contact(
        self,
        name: str,
        phone_number: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        birthday: Optional[str] = None,
    ):
        contact = self.find_contact_by_name(name)
        if contact:
            contact.edit(phone_number, email, address, birthday)
            #serialize the whole ContactBook

    def delete_by_name(self, name: str):
        if name in self.data:
            self.data.pop(name)
            #serialize the whole ContactBook

    def show_upcoming_birthday_in(self, days: int):
        # to be implemented
        pass


