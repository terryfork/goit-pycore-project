import pickle
from pathlib import Path
import config
from re import fullmatch, sub, match
from datetime import datetime, date

class Contact():
    @staticmethod
    def phone_validator(phone: str) -> bool:
        if not isinstance(phone, str):
            return False
        cleaned = sub(r'[^\d+]', '', phone)
        if cleaned.count('+') > 1:
            return False
        if '+' in cleaned and not cleaned.startswith('+'):
            return False
        return bool(match(config.PHONE_FORMAT, cleaned))

    @staticmethod
    def email_validator(email: str) -> bool:
        if not isinstance(email, str):
            return False
        cleaned_email = email.strip().lower()
        if not cleaned_email:
            return False
        return bool(fullmatch(config.EMAIL_FORMAT, cleaned_email))

    @staticmethod
    def DOB_validator(dob: str) -> bool:
        if not isinstance(dob, str):
            return False
        try:
            birth_date = datetime.strptime(dob, config.DOB_FORMAT).date()
            return birth_date <= date.today()
        except (ValueError, AttributeError):
            return False



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


    def add_contact(self, name, phone):
#TODO
        if name not in self.phonebook:
            self.phonebook[name] = phone
            return "OK"
        else:
            return f"Entry {name} already exists"

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


