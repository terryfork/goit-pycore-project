from contact_service import ContactService
from note_service import NoteService
from models import Contact


class BotService:

    def __init__(self):
        self.contact_service = ContactService()
        self.note_service = NoteService()

    def save_contact(self, args):
        name = args[0]
        phone_number = args[1]
        email = args[2] if len(args) > 2 else None
        address = args[3] if len(args) > 3 else None
        birthday_date = args[4] if len(args) > 4 else None

        contact = Contact(name, phone_number, email, address, birthday_date)
        self.contact_service.add_contact(contact)

    def edit_contact(self, args):
        name = args[0]
        phone_number = args[1]
        email = args[2] if len(args) > 2 else None
        address = args[3] if len(args) > 3 else None
        birthday_date = args[4] if len(args) > 4 else None

        contact = self.contact_service.find_contact_by_name(name)
        if contact:
            contact.edit(phone_number, email, address, birthday_date)

    def delete_contact(self, args):
        name = args[0]
        self.contact_service.delete_by_name(name)

    def show_upcoming_birthdays(self, args):
        days = int(args[0])
        return self.contact_service.show_upcoming_birthday_in(days)

    def search_contact(self, args):
        # args might contain several parameters
        # so we can search by name, phone, email as they should be unique.
        # find_by_phone_number() find_by_email() should be implemented
        name = args[0]
        return self.contact_service.find_contact_by_name(name)
