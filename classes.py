from collections import UserDict
from datetime import datetime, timedelta
import re

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        # Remove spaces and check if value is all digits and has length 10
        name = str(value).strip()
        if not name:
            raise ValueError("Contact name is mandatory and cannot be empty.")
        super().__init__(name)

class Phone(Field):
    def __init__(self, value):
        # Remove spaces and check if value is all digits and has length 10
        phone_str = str(value).strip()
        if not (phone_str.isdigit() and len(phone_str) == 10):
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(phone_str)

class Birthday(Field):
    def __init__(self, value):
        # Validate and standardize birthday format
        birthday_str = self._standardize_date_format(str(value).strip())
        try:
            # Validate the date format
            datetime.strptime(birthday_str, "%Y-%m-%d")
            super().__init__(birthday_str)
        except ValueError:
            raise ValueError("Invalid birthday format. Use YYYY-MM-DD, YYYY.MM.DD, DD.MM.YYYY, or DD-MM-YYYY")
    
    def _standardize_date_format(self, date_string):
        """Convert various date formats to YYYY-MM-DD"""
        # Replace delimiters with dashes
        standardized = re.sub(r'[ \-/\.\\,\t\n\(\)\[\]\{\}]+', '-', date_string).strip('-')
        
        # Try to parse different formats
        formats_to_try = [
            "%Y-%m-%d",  # YYYY-MM-DD
            "%d-%m-%Y",  # DD-MM-YYYY (including DD.MM.YYYY)
            "%m-%d-%Y",  # MM-DD-YYYY
        ]
        
        for fmt in formats_to_try:
            try:
                parsed_date = datetime.strptime(standardized, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        raise ValueError("Unable to parse date format")
    
    def display_format(self):
        """Return birthday in DD.MM.YYYY format for display"""
        try:
            date_obj = datetime.strptime(self.value, "%Y-%m-%d")
            return date_obj.strftime("%d.%m.%Y")
        except ValueError:
            return self.value

class Record: #Describes the one particular contact. Child to AddressBook
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = f", birthday: {self.birthday.display_format()}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"
    
    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        """Add birthday to the contact"""
        self.birthday = Birthday(birthday)

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p

    def edit_phone(self, old_phone, new_phone):
        phone_to_edit = self.find_phone(old_phone)
        if phone_to_edit:
            phone_to_edit.value = new_phone
        else:
            raise ValueError(f"Phone number {old_phone} not found.")
        
    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

class AddressBook(UserDict): #Describes the whole address book. Parent to Record
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        """Get list of contacts with birthdays in the next week"""
        upcoming_birthdays = []
        today = datetime.today()
        
        for name, record in self.data.items():
            if record.birthday:
                try:
                    # Parse birthday
                    birthday = datetime.strptime(record.birthday.value, "%Y-%m-%d")
                    
                    # Set birthday to this year
                    next_birthday = birthday.replace(year=today.year)
                    
                    # If birthday has already passed this year, set to next year
                    if next_birthday < today:
                        next_birthday = next_birthday.replace(year=today.year + 1)
                    
                    # Check if birthday falls on weekend and adjust to Monday
                    if next_birthday.weekday() in [5, 6]:  # Saturday or Sunday
                        days_to_add = 7 - next_birthday.weekday()
                        next_birthday = next_birthday.replace(day=next_birthday.day + days_to_add)
                    
                    # Calculate days until birthday
                    delta = (next_birthday - today).days
                    
                    # If birthday is within next 7 days
                    if 0 <= delta <= 7:
                        upcoming_birthdays.append({
                            "name": name,
                            "birthday": record.birthday.display_format(),
                            "days_until": delta
                        })
                        
                except ValueError:
                    # Skip invalid birthday formats
                    continue
        
        return upcoming_birthdays

if __name__ == "__main__":

    # Створення нової адресної книги
    book = AddressBook()

    # Створення запису для John
    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")
    john_record.add_birthday("1990-06-15")  # Додаємо день народження

    # Додавання запису John до адресної книги
    book.add_record(john_record)

    # Створення та додавання нового запису для Jane
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    jane_record.add_birthday("1985.12.20")  # Додаємо день народження в іншому форматі
    book.add_record(jane_record)

    # Створення запису для Bob з днем народження на цьому тижні
    bob_record = Record("Bob")
    bob_record.add_phone("1112223333")
    # Встановлюємо день народження на завтра (для тестування)
    tomorrow = datetime.today() + timedelta(days=1)
    bob_record.add_birthday(tomorrow.strftime("%Y-%m-%d"))
    book.add_record(bob_record)

    # Виведення всіх записів у книзі
    print("=== Всі контакти ===")
    for name, record in book.data.items():
        print(record)

    # Знаходження та редагування телефону для John
    john = book.find("John")
    john.edit_phone("1234567890", "1112223333")

    print(f"\n=== Після редагування телефону ===")
    print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555, birthday: 1990-06-15

    # Пошук конкретного телефону у записі John
    found_phone = john.find_phone("5555555555")
    print(f"{john.name}: {found_phone}")  # Виведення: 5555555555

    # Тестування функції get_upcoming_birthdays
    print(f"\n=== Майбутні дні народження ===")
    upcoming = book.get_upcoming_birthdays()
    if upcoming:
        for contact in upcoming:
            print(f"Привітання для {contact['name']} з нагоди дня народження {contact['birthday']} (через {contact['days_until']} днів)")
    else:
        print("Немає днів народження на цьому тижні")

    # Тестування валідації
    print(f"\n=== Тестування валідації ===")
    try:
        invalid_phone = Phone("123")  # Неправильний формат
    except ValueError as e:
        print(f"Помилка валідації телефону: {e}")

    try:
        invalid_birthday = Birthday("invalid-date")  # Неправильний формат
    except ValueError as e:
        print(f"Помилка валідації дня народження: {e}")

    # Видалення запису Jane
    book.delete("Jane")
    print(f"\n=== Після видалення Jane ===")
    for name, record in book.data.items():
        print(record)