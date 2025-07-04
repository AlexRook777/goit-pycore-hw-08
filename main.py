from classes import AddressBook, Record
from datetime import datetime
import pickle

def input_error(func):
    """Декоратор для обробки помилок вводу"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"ValueError: {e}"
        except KeyError as e:
            return f"KeyError: {e}"
        except IndexError as e:
            return f"IndexError: {e}"
        except Exception as e:
            return f"Error: {e}"
    return wrapper

def parse_input(user_input):
    """Парсинг введеного користувачем тексту"""
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    """Додати контакт або оновити телефон існуючого контакту"""
    if len(args) < 2:
        raise ValueError("Please provide name and phone number.")
    
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    
    if phone:
        record.add_phone(phone)
    
    return message

@input_error
def change_contact(args, book: AddressBook):
    """Змінити телефонний номер для вказаного контакту"""
    if len(args) < 3:
        raise ValueError("Please provide name, old phone and new phone.")
    
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    
    if record is None:
        raise ValueError(f"Contact {name} not found.")
    
    record.edit_phone(old_phone, new_phone)
    return f"Phone number for {name} changed from {old_phone} to {new_phone}."

@input_error
def show_phone(args, book: AddressBook):
    """Показати телефонні номери для вказаного контакту"""
    if len(args) < 1:
        raise ValueError("Please provide contact name.")
    
    name = args[0]
    record = book.find(name)
    
    if record is None:
        raise ValueError(f"Contact {name} not found.")
    
    if not record.phones:
        return f"Contact {name} has no phone numbers."
    
    phones = "; ".join(phone.value for phone in record.phones)
    return f"Phone numbers for {name}: {phones}"

@input_error
def show_all_contacts(args, book: AddressBook):
    """Показати всі контакти в адресній книзі"""
    if not book.data:
        return "Address book is empty."
    
    result = "All contacts:\n"
    for name, record in book.data.items():
        result += f"{record}\n"
    return result.strip()

@input_error
def add_birthday(args, book: AddressBook):
    """Додати день народження для вказаного контакту"""
    if len(args) < 2:
        raise ValueError("Please provide name and birthday date.")
    
    name, birthday, *_ = args
    record = book.find(name)
    
    if record is None:
        raise ValueError(f"Contact {name} not found.")
    
    record.add_birthday(birthday)
    return f"Birthday {birthday} added for contact {name}."

@input_error
def show_birthday(args, book: AddressBook):
    """Показати день народження для вказаного контакту"""
    if len(args) < 1:
        raise ValueError("Please provide contact name.")
    
    name = args[0]
    record = book.find(name)
    
    if record is None:
        raise ValueError(f"Contact {name} not found.")
    
    if record.birthday is None:
        return f"Contact {name} has no birthday set."
    
    return f"Birthday for {name}: {record.birthday.display_format()}"

@input_error
def show_birthdays(args, book: AddressBook):
    """Показати дні народження, які відбудуться протягом наступного тижня"""
    upcoming = book.get_upcoming_birthdays()
    
    if not upcoming:
        return "No birthdays in the next week."
    
    result = "Upcoming birthdays:\n"
    for contact in upcoming:
        # Convert internal format to display format
        try:
            date_obj = datetime.strptime(contact['birthday'], "%Y-%m-%d")
            display_date = date_obj.strftime("%d.%m.%Y")
        except ValueError:
            display_date = contact['birthday']
        
        result += f"• {contact['name']}: {display_date} (in {contact['days_until']} days)\n"
    return result.strip()

def show_help():
    """Показати список доступних команд"""
    print("Available commands:")
    print("• add [name] [phone] - Add new contact or phone to existing contact")
    print("• change [name] [old_phone] [new_phone] - Change phone number")
    print("• phone [name] - Show phone numbers for contact")
    print("• all - Show all contacts")
    print("• add-birthday [name] [date] - Add birthday (DD.MM.YYYY)")
    print("• show-birthday [name] - Show birthday for contact")
    print("• birthdays - Show upcoming birthdays")
    print("• hello - Get greeting from bot")
    print("• help - Show this help message")
    print("• close/exit - Close program")

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()
    show_help()
    
    while True:
        user_input = input("\nEnter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit", "quit", "q"]:
            save_data(book)
            print("Data saved. Good bye!")
            break

        elif command in ["hi", "hey", "hello", "start", "h"]:
            print("How can I help you?")
        elif command == "help":
            show_help()

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command in ["all","show"] :
            print(show_all_contacts(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(show_birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main() 