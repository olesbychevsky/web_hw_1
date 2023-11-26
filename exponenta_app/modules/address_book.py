from abc import ABC, abstractmethod
from collections import UserDict
from pathlib import Path
from datetime import date, datetime
from itertools import islice
import re
import pickle
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit import prompt

save_file = Path("phone_book.bin")

help_message = """Use next commands:
    <add> 'name' 'phone'                - add name and phone number (10 digits) to the dictionary
    <add_birthday> 'name' 'birthday'    - add birthday date to the name in the dictionary
    <add_phone> 'name' 'phone'          - add phone number (10 digits) to the name in the dictionary
    <add_adress> 'name' 'adress'        - add adress to the name in dictionary
    <change> 'name' 'phone' 'new_phone' - change phone number (10 digits) for this name
    <days_to_birthday> 'name'           - return number days to birhday
    <birthday> 'num'                    - return records with birthday date in 'num' days
    <delete_record> 'name'              - delete record for this name from the dictionary
    <delete_adr> 'name'                 - remove adress for this name
    <delete_phone> 'name' 'phone'       - remove phone for this name
    <find> 'info'                       - find all records including 'info' in Name or Phone
    <search> 'str': min 3 symbols       - find all records including 'str' in Name or Phone or Adress
    <hello>                             - greeting
    <email> 'name' [email@domain.com]   - add OR change email for specified Name
    <phone> 'name'                      - show phone number for this name
    <adress> 'name'                     - show address for this name
    <remove_phone> 'name' 'phone'       - remove phone for this name
    <show_all>                          -  show all records in the dictionary
    <show_all> 'N'                      - show records by N records on page
    <exit> or <close> or <good_bye>     - exit from module"""

greeting_message = """Welcome to Address Book.
Type command or 'help' for more information."""


class GeneralInterface(ABC):
    @abstractmethod
    def show_data(self, data: str) -> None:
        pass


class UserInterface(GeneralInterface):
    def show_data(self, output: str = None) -> None:
        print(output)


class DateError(Exception):
    ...


class PhoneError(Exception):
    ...


class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    ...


class Adress(Field):
    ...


class Email(Field):
    def __init__(self, email: str):
        self.__email = None
        self.email = email

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, email: str):
        if re.match(r"[A-z.]+\w+@[A-z]+\.[A-Za-z]{2,}", email):
            self.__email = email
        else:
            raise ValueError(
                "Wrong email format. Use pattern <name@domain.com> for email"
            )

    def __str__(self):
        return f"{self.__email}"


class Birthday(Field):
    def __init__(self, birthday) -> None:
        self.__birthday = None
        self.birthday = birthday

    @property
    def birthday(self):
        return self.__birthday

    @birthday.setter
    def birthday(self, birthday):
        if isinstance(birthday, datetime):
            self.birthday = birthday
        else:
            raise DateError()

    def __str__(self):
        return f"Days to birthday: {self.days_to_birthday}"


class Phone(Field):
    def __init__(self, phone: str):
        self.__phone = None
        self.phone = phone

    @property
    def phone(self):
        return self.__phone

    @phone.setter
    def phone(self, phone: str):
        if re.match(r"[0-9]{10}", phone):
            self.__phone = phone
        else:
            raise ValueError("Wrong phone format. It must contains 10 digits")


class Record:
    def __init__(
        self,
        name,
        phone: str = None,
        birthday_date: Birthday = None,
        email: str = None,
        adress: str = None,
    ):
        self.name = Name(name)
        self.phones: list(Phone) = []
        self.birthday = None
        self.email = None
        self.adress = None
        if phone:
            self.phones.append(Phone(phone))
        if birthday_date:
            self.birthday = birthday_date
        if email:
            self.email = Email(email)

    def add_phone(self, phone: str) -> str:
        self.phones.append(Phone(phone))
        return f"Added phone {phone} to contact {self.name}"


    def add_adress(self, adress: str):
        self.adress = Adress(adress)

    def show_adress(self) -> str:
        if self.adress:
            return f"{self.name}'s adress: {self.adress}"
        else:
            return f"{self.name}'s adress is empty"

    def del_adress(self) -> None:
        self.adress = None


    def add_birthday(self, bd_date) -> None:
        self.birthday = bd_date

    def find_phone(self, phone: str) -> Phone:
        result = None
        for p in self.phones:
            if phone in p.phone:
                result = p
        return result

    def find_adress(self, adress: str) -> Adress:
        result = None
        if adress.lower() in str(self.adress):
            result = self.adress
        return result

    def remove_phone(self, phone: str) -> str:
        search = self.find_phone(phone)
        if search in self.phones:
            self.phones.remove(search)
            return f"Removed phone {phone} from contact {self.name}."
        else:
            raise PhoneError

    def edit_phone(self, phone: str, new_phone: str) -> str:
        edit_check = False
        for i in range(len(self.phones)):
            if self.phones[i].value == phone:
                edit_check = True
                self.phones[i] = Phone(new_phone)
                return f"Changed phone {phone} for contact {self.name} to {new_phone}"
        if not edit_check:
            raise ValueError

    def days_to_birthday(self) -> int:
        if self.birthday:
            now_date = date.today()
            future_bd = self.birthday
            future_bd = future_bd.replace(year=now_date.year)
            if future_bd > now_date:
                return (future_bd - now_date).days
            else:
                future_bd = future_bd.replace(year=future_bd.year + 1)
                return (future_bd - now_date).days
        else:
            raise DateError()

    def add_change_email(self, email: str = None) -> str:
        if email:
            self.email = Email(email)
            return (
                f"Email for contact {self.name} was succefully changed to {self.email}"
            )
        if not email:
            return f"{self.name.value} has an email {self.email}"

    def __str__(self):
        phones = "; ".join(p.phone for p in self.phones)
        return (
            "Contact name: {}, birthday: {}, phones: {}, email: {}, adress: {}".format(
                self.name, self.birthday, phones, self.email, self.adress
            )
        )


class AddressBook(UserDict):
    def __init__(self, data=None):
        super().__init__(data)
        self.counter = 0

    def add_record(self, rec: Record):
        if rec.name.value not in self.data.keys():
            self.data[rec.name.value] = rec
        else:
            raise ValueError

    def find(self, name: str) -> Record:
        for k in self.data.keys():
            if name in k:
                return self.data.get(name)
        else:
            return None

    def delete(self, name: str):
        if name in self.data.keys():
            return self.data.pop(name)

    def iterator(self, quantity=None) -> list:
        self.counter = 0
        values = list(map(str, islice(self.data.values(), None)))
        while self.counter < len(values):
            if quantity:
                yield values[self.counter : self.counter + quantity]
                self.counter += quantity
            else:
                yield values
                break

    def save_book(self) -> str:
        with open(save_file, "wb") as file:
            pickle.dump(self.data, file)
        return f"Phonebook saved. Good bye!"

    def load_book(self) -> str:
        with open(save_file, "rb") as file:
            data = file.read()
            self.data = pickle.loads(data)
        return f"Phonebook loaded"


def input_error(func):
    def inner(*args):
        try:
            return func(*args)
        except TypeError:
            return "Not enough params. Try again"
        except KeyError:
            return "Unknown name. Try again"
        except ValueError:
            return "Wrong format. Try again"  
        except DateError:
            return "Birthday date error or no birthday data"
        except IndexError:
            return "Not enough params. Try again"
        except PhoneError:
            return "This phone number doesn't exist in the dictionary."

    return inner


def greeting():
    return greeting_message


def help():
    return help_message


@input_error
def add_birhday(*args) -> str:
    name = args[0]
    try:
        birhday = datetime.strptime(args[1], "%d/%m/%Y")
    except:
        raise DateError()
    rec = phone_book.get(name)
    if rec:
        rec.add_birthday(birhday.date())
        return f"{args[0].capitalize()}'s birthday added {args[1]}"
    else:
        raise KeyError()


@input_error
def days_to_birthday(*args) -> str:
    name = args[0]
    rec = phone_book.get(name)
    if rec:
        days = rec.days_to_birthday()
        return f"{days} days to {name.capitalize()}'s birthday"
    else:
        raise DateError()


@input_error
def birthday_in(*args) -> str:
    num_days = int(args[0])
    for name in phone_book:
        rec = phone_book.get(name)
        try:
            days = rec.days_to_birthday()
            if days <= num_days:
                print(f"{rec} birthday in {days} days")
        except DateError:
            continue
    return f"Our birthday people in {num_days} days"


phone_book = AddressBook()


def find_name(args: str) -> str:
    name = ""
    idx = 0
    for item in args:
        if item.isalpha() or item == " ":
            name += f"{item}"
            idx += 1
        else:
            name = name.strip()
            break
    return name, args[idx:]


@input_error
def add_record(name: str, *phone: list) -> str:
    x = name + " " + " ".join(phone)
    name, phone = find_name(x)
    global phone_book
    record = Record(name, phone.strip())
    phone_book.add_record(record)
    return f"{record}"


@input_error
def change_record(name: str, phone: str, new_phone: str) -> str:
    global phone_book
    rec: Record = phone_book.find(name)
    if rec:
        return rec.edit_phone(phone, new_phone)


@input_error
def delete_record(*args):
    name, _ = find_name(" ".join(args))
    if phone_book.get(name):
        phone_book.delete(name)
        return f"Record with name {name} deleted."
    else:
        raise KeyError()


@input_error
def add_change_email(name: str, email: str = None):
    global phone_book
    rec: Record = phone_book.find(name)
    if rec:
        return rec.add_change_email(email)
    return f"Contact {name} wasn`t found"


@input_error
def add_phone(*args):
    name = args[0]
    new_phone = args[1]
    rec = phone_book.get(name)
    if rec:
        rec.add_phone(new_phone)
        return f"{args[0].capitalize()}'s phone added another one {args[1]}"
    else:
        raise KeyError()


@input_error
def remove_phone(*args):
    name = args[0]
    phone = args[1]
    rec = phone_book.get(name)
    if rec:
        rec.remove_phone(phone)
        return f"{phone} deleted."
    else:
        raise PhoneError()


@input_error
def find(search: str) -> str:
    rec = []
    if search.isdigit():
        for k, v in phone_book.items():
            if v.find_phone(search) or search.lower() in str(
                v.find_adress(search.lower())
            ):
                rec.append(phone_book[k])
    else:
        for k, v in phone_book.items():
            if search.lower() in k.lower() or search.lower() in str(
                v.find_adress(search.lower())
            ):
                rec.append(phone_book[k])
    if rec:
        result = "\n".join(list(map(str, rec)))
        return f"Finded \n{result}"
    else:
        return f"Nothing was found for your request."


def show_all(*args):
    try:
        if args[0]:
            for rec in phone_book.iterator(int(args[0])):
                UserInterface().show_data("\n".join([str(r) for r in rec]))
                input("Press Enter for next records")
    except:
        for rec in phone_book.iterator():
            UserInterface().show_data("\n".join([str(r) for r in rec]))


def save_book() -> str:
    return phone_book.save_book()


def load_book() -> str:
    return phone_book.load_book()


@input_error
def add_adress(name, *args):
    adress: str = " ".join(args).replace(name, "", 1)
    rec: Record = phone_book.get(name)
    if rec:
        rec.add_adress(adress)
        return f"{name.capitalize()}'s added adress {adress}"
    else:
        raise KeyError()


def show_adress(*args):
    name = args[0]
    rec: Record = phone_book.get(name)
    if rec:
        return rec.show_adress()
    else:
        raise KeyError()


def remove_adr(*args):
    name = args[0]
    rec: Record = phone_book.get(name)
    if rec:
        rec.del_adress()
        return f"{rec.name}'s del adress"
    else:
        raise KeyError()


def stop_command(*_):
    return phone_book.save_book()


def unknown(*args):
    return "Unknown command. Try again."


COMMANDS = {
    greeting: "hello",
    add_birhday: "add_birthday",
    add_record: "add",
    add_phone: "add_phone",
    add_adress: "add_adress",
    show_adress: "adress",
    birthday_in: "birthday",
    change_record: "change",
    delete_record: "delete_record",
    days_to_birthday: "days_to_birthday",
    find: "find",
    help: "help",
    show_all: "show_all",
    save_book: "save",
    load_book: "load",
    remove_phone: "delete_phone",
    remove_adr: "delete_adr",
    stop_command: ("good_bye", "close", "exit", "stop"),
    add_change_email: "email",
}


def parcer(text: str):
    for func, kw in COMMANDS.items():
        command = text.rstrip().split()
        if text.lower().startswith(kw) and command[0].lower() in kw:
            return func, text[len(kw) :].strip().split()
    return unknown, []


def addressbook_main():
    try:
        if all([save_file.exists(), save_file.stat().st_size > 0]):
            print(phone_book.load_book())
    except:
        ...

    greeting()
    menu_completer = NestedCompleter.from_nested_dict(
        {
            "add": {"name phone": None},
            "add_phone": {"name phone(10 digits)": None},
            "add_birthday": {"name dd/mm/YYYY"},
            "birthday": {"num_days": None},
            "add_adress": {"name adress"},
            "adress": {"name": None},
            "change": {"name phone new_phone": None},
            "days_to_birthday": {"name": None},
            "delete_adr": {"name": None},
            "delete_phone": {"name phone"},
            "delete_record": {"name": None},
            "email": {"name email@": None},
            "find": {"anything": None},
            "hello": None,
            "help": None,
            "show_all": {"20"},
            "exit": None,
            "close": None,
            "good_buy": None,
        }
    )
    while True:
        user_input = prompt(
            "\nEnter command or 'help' for help: ", completer=menu_completer
        )

        func, data = parcer(user_input)
        result = func(*data)
        user_interface = UserInterface()
        user_interface.show_data(result)
        if result == "Phonebook saved. Good bye!":
            break


if __name__ == "__main__":
    addressbook_main()