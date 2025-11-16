import pickle
from pathlib import Path
from datetime import datetime, date
import config
import re

class Contact():
    _data = {}

    def __init__(self, **kwargs):
        fields = ['name', 'addr', 'email', 'phone', 'dob']
        for field in fields:
            if field in kwargs:
                setattr(self, field, kwargs[field])

#TODO
    @staticmethod
    def name_validator(phone):
        return True

#TODO
    @staticmethod
    def addr_validator(phone):
        return True

    @staticmethod
    def phone_validator(phone: str) -> bool:
        cleaned = re.sub(r'[^\d+]', '', phone)
        if cleaned.count('+') > 1:
            return False
        if '+' in cleaned and not cleaned.startswith('+'):
            return False
        return bool(re.match(config.PHONE_FORMAT, cleaned))

    @staticmethod
    def email_validator(email: str) -> bool:
        cleaned_email = email.strip().lower()
        if not cleaned_email:
            return False
        return bool(re.fullmatch(config.EMAIL_FORMAT, cleaned_email))

    @staticmethod
    def dob_validator(dob: str) -> bool:
        try:
            birth_date = datetime.strptime(dob, config.DOB_FORMAT).date()
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
            self._data['dob'] = datetime.strptime(dob_str, config.DOB_FORMAT)
        else:
            raise ValueError("Invalid date format. Date must be like " + date.today().strftime(config.DOB_FORMAT))


class Contactbook():

    storage = []
    last_id = 0


    def __init__(self):
#        self.storage_file = config.PHONEBOOK_STORAGE
#        self.phonebook = self._load_from_file()
        pass

    def _load_from_file(self):
        if Path(self.storage_file).exists():
            try:
                with open(self.storage_file, 'rb') as f:
                    return pickle.load(f)
            except pickle.UnpicklingError:
                return {}
        return {}

    def _save_to_file(self):
        with open(self.storage_file, 'wb') as f:
            pickle.dump(self.storage, f)


    def add_contact(self, name):
        phone = yield("Enter phone: ")
        email = yield("Enter email: ")
        dob = yield("Enter date of birthday(YYYY.MM.DD): ")
        addr = yield("Enter address: ")
        contact = Contact(name=name, phone=phone, email=email, dob=dob, addr=addr)
        self.storage.append(contact)
        self.last_id = len(self.storage)
        return "Contact added"


    def change_contact(self, name, phone):
#TODO
        if name in self.storage:
            self.storage[name] = phone
            return "OK"
        else:
            return f"Entry {name} not found"


    def get_contact(self, name):
        found = self.get_contacts_by_name(name)
        if found:
            return self.print_contacts(found)

        return f"Contact {name} not found"


    def get_contacts_by_name(self, name):
        found = {}
        for id, contact in enumerate(self.storage):
            if contact.name == name:
                found[id] = contact
        return found


    def all_contacts(self):
        return self.print_contacts(dict(enumerate(self.storage)))


    def del_contact(self, name):
        found = self.get_contacts_by_name(name)
        if not found:
            return f"Contact {name} not found"
        elif len(found) > 1:
            list = self.print_contacts(found)
            delete_all = yield(f"{list}Found {len(found)} contacts with name '{name}'. Delete all of them(y/N)?")
            if delete_all.lower() == 'y':
#TODO
                pass
                return f"All contacts with name '{name}' deleted"
            else:
                return f"Contact not deleted. You can use command {Fore.RED}del_contact_id{Style.RESET_ALL} to delete contact by it's id or command {Fore.RED}del_last{Style.RESET_ALL} to delete last found contact"
        else:
#TODO
            pass
            return "Contact deleted"


    def search_contact(self, needle):
#TODO
        pass


    def get_birthdays(self, days: int) -> list[Contact]:
        today = date.today()
        list_of_birthday_people = []

        for contact in self.storage.values():
            dob = getattr(contact, "dob", None)
            if not dob:
                continue

            birthday_this_year = self._safe_birthday(today.year, dob.month, dob.day)
            if birthday_this_year is None:
                continue

            next_birthday = (self._safe_birthday(today.year + 1, dob.month, dob.day)
                             if birthday_this_year < today
                             else birthday_this_year)
            if next_birthday and (next_birthday - today).days <= days:
                list_of_birthday_people.append(contact)

        return list_of_birthday_people


    def _safe_birthday(self, year: int, month: int, day: int) -> date | None:
        try:
            return date(year, month, day)
        except ValueError:
            if month == 2 and day == 29:
                return date(year, 2, 28)
            return None


    def print_contacts(self, contacts):
        txt = ""
        for id, contact in contacts.items():
            txt += f"{contact.name}\t{contact.dob.strftime('%Y.%m.%d')}\t{contact.email}\t{contact.phone}\t{contact.addr}\n"
            self.last_id = id

        return txt
