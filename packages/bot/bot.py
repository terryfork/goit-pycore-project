from repository import ContactBook
from models import Contact


class Bot:
    # Bot functionality:
    # before starting the bot, the ContactBook should be deserialized from file

    def save_contact(args, book: ContactBook):
        name = args[0]
        phone_number = args[1]
        email = args[2] if len(args) > 2 else None
        address = args[3] if len(args) > 3 else None
        birthday_date = args[4] if len(args) > 4 else None

        contact = Contact(name, phone_number, email, address, birthday_date)
        book.add_contact(contact)

    def edit_contact(args, book: ContactBook):
        name = args[0]
        phone_number = args[1]
        email = args[2] if len(args) > 2 else None
        address = args[3] if len(args) > 3 else None
        birthday_date = args[4] if len(args) > 4 else None

        contact = book.find_contact_by_name(name)
        if contact:
            contact.edit(phone_number, email, address, birthday_date)

    def delete_contact(args, book: ContactBook):
        name = args[0]
        book.delete_by_name(name)

    def show_upcoming_birthdays(args, book: ContactBook):
        days = int(args[0])
        return book.show_upcoming_birthday_in(days)

    def search_contact(args, book: ContactBook):
        # args might contain several parameters
        # so we can search by name, phone, email as they should be unique.
        # find_by_phone_number() find_by_email() should be implemented
        name = args[0]
        return book.find_contact_by_name(name)