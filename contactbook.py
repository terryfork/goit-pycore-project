import pickle
from pickle import UnpicklingError
from datetime import datetime, date, timedelta
from calendar import calendar
import re
from colorama import Fore, Style
from config import (
    PHONEBOOK_STORAGE,
    DOB_FORMAT,
    PHONE_FORMAT,
    EMAIL_FORMAT,
    MAX_NAME_LEN,
    MAX_ADDR_LEN,
)


class Contact():
    def __init__(self, **kwargs):
        self._data = {}
        fields = ['name', 'addr', 'email', 'phone', 'dob']
        for field in fields:
            if field in kwargs:
                setattr(self, field, kwargs[field])

    @staticmethod
    def name_validator(name):
        return name.isalpha() and len(name) > 0 and len(name) <= MAX_NAME_LEN

    @staticmethod
    def addr_validator(addr):
        return len(addr) <= MAX_ADDR_LEN

    @staticmethod
    def phone_validator(phone: str) -> bool:
        cleaned = re.sub(r'[^\d+]', '', phone)
        if cleaned.count('+') > 1:
            return False
        if '+' in cleaned and not cleaned.startswith('+'):
            return False
        return bool(re.match(PHONE_FORMAT, cleaned))

    @staticmethod
    def email_validator(email: str) -> bool:
        cleaned_email = email.strip().lower()
        if not cleaned_email:
            return False
        return bool(re.fullmatch(EMAIL_FORMAT, cleaned_email))

    @staticmethod
    def dob_validator(dob: str) -> bool:
        try:
            birth_date = datetime.strptime(dob, DOB_FORMAT).date()
            return birth_date <= date.today()
        except (ValueError, AttributeError):
            return False

    @staticmethod
    def phone_normalize(phone):
        pure = re.sub(r"[^\d]", "", phone)
        normalized = "+380"[0:13-len(pure)] + pure
        return normalized

    @property
    def name(self):
        if 'name' in self._data:
            return self._data['name']

    @name.setter
    def name(self, name):
        if self.name_validator(name):
            self._data['name'] = name

    @property
    def addr(self):
        return self._data['addr']

    @addr.setter
    def addr(self, addr):
        if self.addr_validator(addr):
            self._data['addr'] = addr

    @property
    def email(self):
        return self._data['email']

    @email.setter
    def email(self, email):
        if self.email_validator(email):
            self._data['email'] = email

    @property
    def phone(self):
        return self._data['phone']

    @phone.setter
    def phone(self, phone):
        pure_phone = self.phone_normalize(phone)
        if self.phone_validator(pure_phone):
            self._data['phone'] = phone

    @property
    def dob(self):
        return self._data['dob']

    @dob.setter
    def dob(self, dob_str):
        if self.dob_validator(dob_str):
            self._data['dob'] = datetime.strptime(dob_str, DOB_FORMAT)
        else:
            raise ValueError(
                "Invalid date format. Date must be like "
                + date.today().strftime(DOB_FORMAT)
                )


class Contactbook():

    NOT_FOUND = "Contact doesn't exists"

    storage = {}
    last_id = 0

    def __init__(self):
        self.storage = {}
        self.last_id = 0
        phonebook = self._load_data()
        if phonebook:
            self.storage = phonebook

    def _load_data(self):
        try:
            with open(PHONEBOOK_STORAGE, "rb") as f:
                return pickle.load(f)
        except (FileNotFoundError, EOFError, UnpicklingError):
            return {}

    def _save_to_file(self):
        with open(PHONEBOOK_STORAGE, 'wb') as f:
            pickle.dump(self.storage, f)

    def add_contact(self, name):
        suggest = ""
        while True:
            phone = yield (f"{suggest}Enter phone: ")
            if Contact.phone_validator(phone):
                phone = Contact.phone_normalize(phone)
                break
            suggest = ("Invalid phone format."
                       "Phone should by like +380987654321\n")
        suggest = ""
        while True:
            email = yield (f"{suggest}Enter email: ")
            if Contact.email_validator(email):
                break
            suggest = ("Invalid email format."
                       "Email should by like username@domain.tld\n")
        suggest = ""
        while True:
            dob = yield (f"{suggest}Enter date of birthday: ")
            if Contact.dob_validator(dob):
                break
            suggest = (
                "Invalid date of birthday format. "
                "Date of birthday should be like "
                f"{date.today().strftime(DOB_FORMAT)}\n"
            )

        addr = yield ("Enter address: ")
        contact = Contact(
            name=name,
            phone=phone,
            email=email,
            dob=dob,
            addr=addr
            )
        contact_id = 1 if not self.storage else max(self.storage.keys()) + 1
        self.storage[contact_id] = contact
        self.last_id = len(self.storage)
        self._save_to_file()
        return "Contact added"

    def edit_last_contact(self):
        if self.last_id in self.storage:
            return self.edit_by_id(self.last_id)
        return self.NOT_FOUND

    def edit_by_id(self, id):
        contact = self.storage.get(id)
        if not contact:
            return f"No contact found with id: '{id}'"
        return (yield from self.edit_contact(contact))

    def edit_by_name(self, name):
        contacts = self._get_contacts_by_name(name)
        if not contacts:
            return f"No contact found with name '{name}'"

        contact = yield from self._handle_multi_choice(contacts)
        if contact is None:
            return
        return (yield from self.edit_contact(contact=contact))

    def edit_contact(self, contact: Contact):
        # Setting new phone number
        suggest = ""
        while True:
            phone = yield (
                f"{suggest}Current phone: {contact.phone}\n"
                "New phone: "
            )
            if phone == "":
                break
            if Contact.phone_validator(phone):
                contact.phone = Contact.phone_normalize(phone)
                break
            suggest = "Invalid phone format. Example: +380987654321\n"

        # Setting new email
        suggest = ""
        while True:
            email = yield (
                f"{suggest}Current email: {contact.email}\n"
                "New email: "
            )
            if email == "":
                break
            if Contact.email_validator(email):
                contact.email = email
                break
            suggest = "Invalid email format. Example: name@domain.tld\n"

        # Setting new dob
        suggest = ""
        while True:
            dob = yield (
                f"{suggest}Current birthday: {contact.dob}\n"
                "New birthday: "
            )
            if dob == "":
                break
            if Contact.dob_validator(dob):
                contact.dob = dob
                break
            suggest = (
                "Invalid date format. Should be like "
                f"{date.today().strftime(DOB_FORMAT)}\n"
            )

        # Setting new address
        addr = yield (
            f"Current address: {contact.addr}\n"
            "New address: "
        )
        if addr != "":
            contact.addr = addr

        self._save_to_file()
        return "Contact updated"

    def _handle_multi_choice(self, contacts: dict):
        if len(contacts) == 1:
            return next(iter(contacts.values()))

        txt = self.print_contacts(contacts)

        suggest = ""
        while True:
            choice_id = yield (
                f"{suggest}{txt}\n"
                "Enter the id of the contact to update [press enter to skip]: "
            )
            try:
                if choice_id == "":
                    return None
                choice_id = int(choice_id)
                if choice_id in self.storage.keys():
                    return self.storage[choice_id]
                suggest = ("Invalid number. "
                           "Please enter one of the shown numbers.\n")
            except ValueError:
                suggest = "Input must be a number.\n"

    def get_contact(self, name):
        found = self._get_contacts_by_name(name)
        return self.print_contacts(found)

    def _get_contacts_by_name(self, name):
        found = {}
        for id, contact in self.storage.items():
            if contact.name == name:
                found[id] = contact
        return found

    def all_contacts(self):
        return self.print_contacts(self.storage)

    def del_contact(self, name):
        found = self._get_contacts_by_name(name)
        if not found:
            return f"Contact {name} not found"
        elif len(found) == 1:
            return self.del_by_id(next(iter(found)))
        return self.del_all(found)

    def del_all(self, found):
        list = self.print_contacts(found)
        delete_all = yield (f"{list}Found {len(found)} contacts."
                            "Delete all of them(y/N)?")
        if delete_all.lower() == 'y':
            for id in iter(found):
                del self.storage[id]
            self._save_to_file()
            return "Contacts deleted"
        else:
            return (
                "Contact not deleted. You can use command "
                f"{Fore.RED}del_contact_id{Style.RESET_ALL} "
                "to delete contact by its id or command "
                f"{Fore.RED}del_last{Style.RESET_ALL} "
                "to delete last found contact"
            )

    def del_last(self):
        return self.del_by_id(self.last_id)

    def del_by_id(self, id):
        try:
            id = int(id)
        except ValueError:
            return "Invalid id format"
        if id not in self.storage:
            return "Contact doesn't exists"
        confirm_msg = (
            self.print_contacts({self.last_id: self.storage[self.last_id]}) +
            "Are you sure to delete this contact (y/N)?"
        )
        confirm_del = yield (confirm_msg)
        if confirm_del.lower() == 'y':
            del self.storage[self.last_id]
            self._save_to_file()
            return "Contact deleted"
        return "Operation canceled"

    def search_contact(self, needle):
        # TODO
        pass

    def upcoming_birthdays(self, days):
        found = self._get_birthdays(days)
        return (
            f"Contacts having birthdays in {days} days:\n"
            + self.print_contacts(found)
        )

    def _get_birthdays(self, days: int) -> list[Contact]:
        upcoming_birthday_contacts = {}
        today = datetime.now().date()
        end_date = today + timedelta(days=days)

        for id, contact in self.storage.items():
            dob = getattr(contact, "dob", None)
            if not dob:
                continue

            birthday = self._next_birthday(dob, today)

            if today <= birthday.date() < end_date:
                upcoming_birthday_contacts[id] = contact

        return upcoming_birthday_contacts

    def _next_birthday(self, dob: date, today: date):
        year = today.year
        birthday = self._birthday_for_year(dob, year)

        if birthday.date() < today:
            birthday = self._birthday_for_year(dob, year + 1)

        return birthday

    def _birthday_for_year(self, dob: date, year: int):
        if dob.month == 2 and dob.day == 29 and not calendar.isleap(year):
            return dob.replace(year=year, day=28)
        return dob.replace(year=year)

    def print_contacts(self, contacts):
        txt = ""
        for id, contact in contacts.items():
            txt += (
                f"{id}\t"
                f"{contact.name}\t"
                f"{contact.dob.strftime('%Y.%m.%d')}\t"
                f"{contact.email}\t"
                f"{contact.phone}\t"
                f"{contact.addr}\n"
            )
            self.last_id = id

        return txt

    def print_contacts_numbered(self, contacts: dict[int, "Contact"]):
        txt = ""
        id_map = {}
        for i, (contact_id, contact) in enumerate(contacts.items(), start=1):
            txt += (
                f"{i}. {contact.name}\t"
                f"{contact.dob.strftime('%Y.%m.%d')}\t"
                f"{contact.email}\t"
                f"{contact.phone}\t"
                f"{contact.addr}\n"
            )
            id_map[i] = contact_id
        return txt, id_map
