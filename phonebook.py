def phonebook_keeper():

    phones={}

    def add_phone(name, phone):
        nonlocal phones
        if name not in phones:
            phones[name] = phone
            return "OK"
        else:
            return f"Entry {name} already exists"

    def change_phone(name, phone):
        nonlocal phones
        if name in phones:
            phones[name] = phone
            return "OK"
        else:
            return f"Entry {name} not found"

    def get_phone(name):
        if name in phones:
            return phones[name]
        else:
            return f"Entry {name} not found"

    def all_phones():
        return phones

    return add_phone, change_phone, get_phone, all_phones

add_phone, change_phone, get_phone, all_phones = phonebook_keeper()
