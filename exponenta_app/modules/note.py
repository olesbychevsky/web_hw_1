from collections import UserList
from pathlib import Path
import pickle



save_file = Path("notes.bin")


class Notes:
    def __init__(self, title, description, tag):
        self.title = title
        self.description = description
        self.tag = tag


class NoteBook(UserList):
    def __init__(self):
        super().__init__()
        self.load_notes()

    def load_notes(self):
        try:
            with open(save_file, "rb") as file:
                self.data = pickle.load(file)
                print("Notebook succefully load")
        except FileNotFoundError:
            print("Notes file not found. A new notepad has been created.")
        except Exception as e:
            print(f"Error loading notes: {e}")

    def save_notes(self):
        with open(save_file, "wb") as file:
            pickle.dump(self.data, file)
            print("Notes saved successfully")

    def add_note(self, text):
        tags = self.extract_tags(text)
        self.data.append({"text": text, "tags": tags})
        print("The note is added to the notepad")

    def display_all_notes(self):
        print("\n===== All notes from notebook =====")
        for index, note in enumerate(self.data):
            print(f"Note: {index}, Text: {note['text']}, Tags: {note['tags']}")
        print("==============================\n")

    def extract_tags(self, text: str) -> list:
        tags = [word[1:] for word in text.split() if word.startswith("#")]
        return tags

    def search_notes(self, search_text: str):
        matching_notes = []
        for index, note in enumerate(self.data):
            if search_text.lower() in note["text"].lower():
                matching_notes.append((index, note))

        if matching_notes:
            print("Found records:")
            for index, note in matching_notes:
                print(f"Note: {index}, Text: {note['text']}, Tags: {note['tags']}")
        else:
            print("There are no records matching your search query")

    def sort_notes_by_tags(self):
        self.data.sort(key=lambda note: len(note["tags"]))

    def change_note(self, note_index: int, new_text: str):
        if 0 <= note_index < len(self.data):
            tags = self.extract_tags(new_text)
            self.data[note_index] = {"text": new_text, "tags": tags}
            print(f"Record with index {note_index} changed in notebook")
        else:
            print("The specified entry index does not exist")

    def delete_note(self, note_index: int):
        if 0 <= note_index < len(self.data):
            del self.data[note_index]
            print(f"Record with index {note_index} deleted in notenook")
        else:
            print("The specified entry index does not exist")


notebook = NoteBook()


def add(text: list):
    notebook.add_note(" ".join(text))


def show(_: list):
    notebook.display_all_notes()


def sort(_: list):
    notebook.sort_notes_by_tags()
    print("Records sorted")


def find(text: list):
    notebook.search_notes(" ".join(text))


def change(text: list):
    notebook.change_note(int(text[0]), " ".join(text[1:]))


def delete(text: list):
    notebook.delete_note(int(text[0]))


def help(_: list = None):
    print("\n===== Notebook command`s help =====")
    print("add <any string>       - add new record to notebook")
    print("show                   - show all records")
    print("sort                   - sort records by tags")
    print("find <text>            - find records by part")
    print("change <number> <text> - changing a record by its number")
    print("delete <number>        - removing a record by its number")
    print("help                   - notebook commands list")
    print("exit                   - leave notebook")
    print("==============================\n")


COMMANDS = {
    "add": add,
    "show": show,
    "sort": sort,
    "find": find,
    "change": change,
    "delete": delete,
    "help": help,
}


def parser(text: str):
    text = text.strip().split()
    if text[0] in COMMANDS:
        COMMANDS[text[0]](text[1:])
    else:
        print("Wrong command. Please try again.")


def note_main():
    help()
    while True:
        choice = input("Enter your command >>> ")
        if choice.lower().startswith(("exit", "close", "quit")):
            notebook.save_notes()
            break
        parser(choice)


if __name__ == "__main__":
    note_main()