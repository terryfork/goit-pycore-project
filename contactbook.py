import pickle
from pathlib import Path
from datetime import datetime, date
import config
import re
from colorama import Fore, Style

class Contact():
    def __init__(self, **kwargs):
        self._data = {}
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

    storage = {}
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
        suggest = ""
        while True:
            phone = yield(f"{suggest}Enter phone: ")
            if Contact.phone_validator(phone):
                phone = Contact.phone_normalize(phone)
                break
            suggest = "Invalid phone format. Phone should by like +380987654321\n"
        suggest = ""
        while True:
            email = yield(f"{suggest}Enter email: ")
            if Contact.email_validator(email):
                break
            suggest = "Invalid email format. Email should by like username@domain.tld\n"
        suggest = ""
        while True:
            dob = yield(f"{suggest}Enter date of birthday: ")
            if Contact.dob_validator(dob):
                break
            suggest = f"Invalid date of birthday format. Date of birthday should by like {date.today().strftime(config.DOB_FORMAT)}\n"
        addr = yield("Enter address: ")
        contact = Contact(name=name, phone=phone, email=email, dob=dob, addr=addr)
        contact_id = 0 if not self.storage else max(self.storage.keys()) + 1
        self.storage[contact_id] = contact
        self.last_id = contact_id
        return "Contact added"


    def change_contact(self, name, phone):
#TODO
        if name in self.storage:
            self.storage[name] = phone
            return "OK"
        else:
            return f"Entry {name} not found"


    def get_contact(self, name):
        found = self._get_contacts_by_name(name)
        if found:
            return self.print_contacts(found)

        return f"Contact {name} not found"


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
        elif len(found) > 1:
            list = self.print_contacts(found)
            delete_all = yield(f"{list}Found {len(found)} contacts with name '{name}'. Delete all of them(y/N)?")
            if delete_all.lower() == 'y':
                for id in iter(found):
                    del self.storage[id]
                    return f"All contacts with name '{name}' deleted"
            else:
                return f"Contact not deleted. You can use command {Fore.RED}del_contact_id{Style.RESET_ALL} to delete contact by it's id or command {Fore.RED}del_last{Style.RESET_ALL} to delete last found contact"
        else:
            del self.storage[next(iter(found))]
            return "Contact deleted"

    def del_last(self):
        if self.last_id not in self.storage:
            return "Contact doesn't exists"
        confirm_msg = self.print_contacts({self.last_id: self.storage[self.last_id]}) + "Are you sure to delete this contact (y/N)?"
        confirm_del = yield(confirm_msg)
        if confirm_del.lower() == 'y':
            del self.storage[self.last_id]
            return "Contact deleted"
        return "Operation canceled"


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
