

class Field:
    def __init__(self, value):
        self.value = value


class Name(Field):
    def __init__(self, name: str):
        super().__init__(name)


class Phone(Field):
    def __init__(self, phone_number: str):
        # validation can be added here
        super().__init__(phone_number)


class Email(Field):
    def __init__(self, email: str):
        # validation can be added here
        super().__init__(email)


class Address(Field):
    def __init__(self, address: str):
        super().__init__(address)


class Birthday(Field):
    def __init__(self, birthday_date: str):
        # validate date format here
        super().__init__(birthday_date)
