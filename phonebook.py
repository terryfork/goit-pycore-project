import pickle
from pathlib import Path
import config

class Contact():
#TODO
    def phone_validator(phone):
#TODO
        return True

    def email_validator(email):
#TODO
        return True

    def DOB_validator(dob):
#TODO
        return True



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


