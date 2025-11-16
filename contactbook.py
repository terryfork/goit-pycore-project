import pickle
from pathlib import Path
from calendar import calendar
from datetime import datetime, date, timedelta
import config
import re


class Contact():
    _data = {}

    def __init__(self, **kwargs):
        fields = ['name', 'addr', 'email', 'phone', 'dob']
        for field in fields:
            if field in kwargs:
                setattr(self, field, kwargs[field])

    # TODO
    @staticmethod
    def name_validator(phone):
        return True

    # TODO
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
    def DOB_validator(dob: str) -> bool:
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
        if self.email_validator(pure_phone):
            self._data['phone'] = phone

    @property
    def dob(self):
        return self._data['dob']

    @dob.setter
    def dob(self, dob):
        try:
            dob = datetime.strptime(dob, "%Y.%m.%d")
        except ValueError:
            print("Error: invalid date format. Date must be like 2025.11.15.")
            return
        if self.dob_validator(dob):
            self._data['dob'] = dob


class Contactbook():

    phonebook = []
    last_id = 0

    def __init__(self):
        # self.storage_file = config.PHONEBOOK_STORAGE
        # self.phonebook = self._load_from_file()
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
            pickle.dump(self.phonebook, f)

    def add_contact(self, name):
        phone = yield ("Enter phone: ")
        email = yield ("Enter email: ")
        dob = yield ("Enter date of birthday(YYYY.MM.DD): ")
        addr = yield ("Enter address: ")
        contact = Contact(
            name=name,
            phone=phone,
            email=email,
            dob=dob,
            addr=addr
            )
        self.phonebook.append(contact)
        self.last_id = len(self.phonebook)
        return "Contact added"

    def change_contact(self, name, phone):
        # TODO
        if name in self.phonebook:
            self.phonebook[name] = phone
            return "OK"
        else:
            return f"Entry {name} not found"

    def get_contact(self, name):
        found = {}
        for id, contact in enumerate(self.phonebook):
            if contact.name == name:
                found[id] = contact
        if found:
            return self.print_contacts(found)

        return f"Contact {name} not found"

    def all_contacts(self):
        # TODO
        return self.phonebook

    def del_contact(self):
        # TODO
        pass

    def search_contact(self, needle):
        # TODO
        pass

    def get_birthdays(self, days: int) -> list[Contact]:
        upcoming_birthday_contacts = []
        today = datetime.today().date()
        end_date = today + timedelta(days=days)

        for contact in self.phonebook.values():
            dob = getattr(contact, "dob", None)
            if not dob:
                continue

            birthday = self._next_birthday(dob, today)

            if today <= birthday < end_date:
                upcoming_birthday_contacts.append(contact)

        return upcoming_birthday_contacts

    def _next_birthday(self, dob: date, today: date):
        year = today.year
        birthday = self._birthday_for_year(dob, year)

        if birthday < today:
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
                f"{contact.name}\t"
                f"{contact.dob.strftime('%Y.%m.%d')}\t"
                f"{contact.email}\t"
                f"{contact.phone}\t"
                f"{contact.addr}\n"
            )
            self.last_id = id

        return txt
