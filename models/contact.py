from typing import Optional
from fields import Name, Phone, Address, Email, Birthday

# This class only holds the contact data, initialized through constructor 
# with the ability to edit the whole data by edit()
# To consider separate setter methods for the fields if there will be 
# the functionality that allows changing a concrete field.


class Contact:
    # Allows initialization with only name and phone number
    def __init__(
        self,
        name: str,
        phone_number: str,
        email: Optional[str] = None,
        address: Optional[str] = None,
        birthday: Optional[str] = None,
    ):
        self.name = Name(name)
        self.phone = Phone(phone_number)
        self.email = Email(email) if email is not None else None
        self.address = Address(address) if address is not None else None
        if birthday is not None:
            self.birthday = Birthday(birthday)
        else:
            self.birthday = None

    def edit(
        self,
        phone_number: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        birthday: Optional[str] = None,
    ):
        if phone_number:
            self.phone = Phone(phone_number)
        if email:
            self.email = Email(email)
        if address:
            self.address = Address(address)
        if birthday:
            self.birthday = Birthday(birthday)
