from typing import Optional
from collections import UserDict
from models import Contact
from datetime import datetime, timedelta


class ContactBook(UserDict):

    def add_contact(self, contact: Contact):
        key = contact.name.value
        if key not in self.data:
            self.data[key] = contact
            # serialize the whole ContactBook
            # ContactBookStorage.save(self)

    def find_contact_by_name(self, name: str):
        return self.data.get(name)

    def edit_contact(
        self,
        name: str,
        phone_number: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        birthday: Optional[str] = None,
    ):
        contact = self.find_contact_by_name(name)
        if contact:
            contact.edit(phone_number, email, address, birthday)
            # serialize the whole ContactBook

    def delete_by_name(self, name: str):
        if name in self.data:
            self.data.pop(name)
            # serialize the whole ContactBook

    def show_upcoming_birthday_in(self, days: int):
        # to be implemented
        pass

    def get_upcoming_birthdays(self, days: int) -> list:
        upcoming_birthdays = []
        today = datetime.today().date()
        end_date = today + timedelta(days=days)

        for contact in self.data.values():
            # Get user birthday or skip if error
            try:
                birthday_date = datetime.strptime(
                    str(contact.birthday),
                    "%d.%m.%Y"
                ).date()
            except ValueError:
                print(
                    f"Error in date format for {contact.name}: "
                    f"{contact.birthday}"
                )
                continue

            # Transform in this year date
            birthday_this_year = birthday_date.replace(year=today.year)

            # Set next year for a passed birthday
            if birthday_this_year < today:
                birthday_this_year = birthday_date.replace(year=today.year + 1)

            # Check if the birthday is in the upcoming 7 days
            if today <= birthday_this_year < end_date:
                congratulation_date = birthday_this_year

                # In case of skipping the weekends:
                # day_of_week = birthday_this_year.weekday()
                # if day_of_week == 5:
                #     congratulation_date = (
                #         birthday_this_year
                #         + timedelta(days=2)
                #     )
                # elif day_of_week == 6:
                #     congratulation_date = (
                #         birthday_this_year
                #         + timedelta(days=1)
                #     )

                upcoming_birthdays.append({
                    "name": contact.name, "congratulation_date":
                    congratulation_date.strftime("%d.%m.%Y")
                })

        return upcoming_birthdays
