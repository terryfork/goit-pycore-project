import pickle
from pathlib import Path
from datetime import datetime
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

#TODO
    @staticmethod
    def phone_validator(phone):
        return True

#TODO
    @staticmethod
    def email_validator(email):
        return True

#TODO
    @staticmethod
    def dob_validator(dob):
        return True


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



class Phonebook():
    def __init__(self):
        self.storage_file = config.PHONEBOOK_STORAGE
        self.phonebook = self._load_from_file()

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
        phone = yield("Enter phone: ")
        email = yield("Enter email: ")
        dob = yield("Enter date of birthday(YYYY.MM.DD): ")
        addr = yield("Enter address: ")
        contact = Contact(name=name, phone=phone, email=email, dob=dob, addr=addr)
        return "Contact added"

    def change_contact(self, name, phone):
#TODO
        if name in self.phonebook:
            self.phonebook[name] = phone
            return "OK"
        else:
            return f"Entry {name} not found"


    def get_contact(self, name):
#TODO
        if name in self.phonebook:
            return self.phonebook[name]
        else:
            return f"Entry {name} not found"


    def all_contacts(self):
#TODO
        return self.phonebook

    def del_contact(self):
#TODO
        pass


    def search_contact(self, needle):
#TODO
        pass


    def get_birthdays(self, days):
#TODO
        pass


