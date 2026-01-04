from abc import ABC, abstractmethod
from typing import List, Optional


# --------------------------- Abstraction ---------------------------

class Person(ABC):
    """Abstract class representing a person in the system."""
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def get_role(self) -> str:
        """Must be implemented by subclasses to return the role name."""
        pass


# --------------------------- Encapsulation + Inheritance ---------------------------

class Member(Person):
    """Base member class. Demonstrates encapsulation with private ID."""
    def __init__(self, name: str, member_id: int):
        super().__init__(name)
        self.__member_id = member_id       # encapsulated (private) attribute
        self.borrowed_books: List["Book"] = []

    # Getter demonstrates controlled access to private data
    def get_member_id(self) -> int:
        return self.__member_id

    def get_role(self) -> str:
        return "Member"

    def borrow_book(self, book: "Book") -> bool:
        """Default borrow behavior; overridden in subclasses for policy."""
        if book.is_available:
            book.is_available = False
            self.borrowed_books.append(book)
            print(f"{self.name} borrowed '{book.title}'.")
            return True
        else:
            print(f"'{book.title}' is not available.")
            return False

    def return_book(self, book_id: int) -> bool:
        """Return a book by its ID."""
        for b in self.borrowed_books:
            if b.get_book_id() == book_id:
                b.is_available = True
                self.borrowed_books.remove(b)
                print(f"{self.name} returned '{b.title}'.")
                return True
        print(f"{self.name} does not have a book with ID {book_id}.")
        return False

    def list_borrowed(self) -> None:
        if not self.borrowed_books:
            print(f"{self.name} has no borrowed books.")
            return
        print(f"Borrowed by {self.name}:")
        for b in self.borrowed_books:
            print(f"  - {b}")


class StudentMember(Member):
    """Student policy: can borrow up to 3 books, 7-day implied rule."""
    MAX_BORROW = 3

    def get_role(self) -> str:
        return "Student"

    # --------------------------- Polymorphism (overriding) ---------------------------
    def borrow_book(self, book: "Book") -> bool:
        if len(self.borrowed_books) >= self.MAX_BORROW:
            print(f"{self.name} (Student) reached limit of {self.MAX_BORROW} books.")
            return False
        if not book.is_available:
            print(f"'{book.title}' is not available.")
            return False
        book.is_available = False
        self.borrowed_books.append(book)
        print(f"{self.name} (Student) borrowed '{book.title}' for 7 days.")
        return True


class FacultyMember(Member):
    """Faculty policy: can borrow up to 10 books, 30-day implied rule."""
    MAX_BORROW = 10

    def get_role(self) -> str:
        return "Faculty"

    # --------------------------- Polymorphism (overriding) ---------------------------
    def borrow_book(self, book: "Book") -> bool:
        if len(self.borrowed_books) >= self.MAX_BORROW:
            print(f"{self.name} (Faculty) reached limit of {self.MAX_BORROW} books.")
            return False
        if not book.is_available:
            print(f"'{book.title}' is not available.")
            return False
        book.is_available = False
        self.borrowed_books.append(book)
        print(f"{self.name} (Faculty) borrowed '{book.title}' for 30 days.")
        return True


# --------------------------- Encapsulation + Method overriding ---------------------------

class Book:
    """Book class demonstrating encapsulation and __str__ overriding."""
    def __init__(self, title: str, author: str, book_id: int):
        self.title = title
        self.author = author
        self.__book_id = book_id        # private
        self.is_available = True

    def get_book_id(self) -> int:
        return self.__book_id

    # --------------------------- Method overriding ---------------------------
    def __str__(self) -> str:
        status = "Available" if self.is_available else "Borrowed"
        return f"[{self.__book_id}] {self.title} by {self.author} - {status}"


# --------------------------- Library + Operator overloading ---------------------------

class Library:
    """Library holds books and manages members."""
    def __init__(self, name: str):
        self.name = name
        self.books: List[Book] = []
        self.members: List[Member] = []

    # --------------------------- CRUD for books ---------------------------
    def add_book(self, book: Book) -> None:
        self.books.append(book)
        print(f"Added '{book.title}' to {self.name}.")

    def remove_book(self, book_id: int) -> bool:
        for b in self.books:
            if b.get_book_id() == book_id and b.is_available:
                self.books.remove(b)
                print(f"Removed '{b.title}' from {self.name}.")
                return True
        print(f"Book ID {book_id} not found or currently borrowed; cannot remove.")
        return False

    def find_book(self, book_id: int) -> Optional[Book]:
        for b in self.books:
            if b.get_book_id() == book_id:
                return b
        return None

    def show_books(self) -> None:
        print(f"\nBooks in {self.name}:")
        if not self.books:
            print("  No books found.")
            return
        for book in self.books:
            print(f"  - {book}")

    # --------------------------- Members management ---------------------------
    def add_member(self, member: Member) -> None:
        self.members.append(member)
        print(f"Registered {member.get_role()} '{member.name}' (ID: {member.get_member_id()}).")

    def get_member_by_id(self, member_id: int) -> Optional[Member]:
        for m in self.members:
            if m.get_member_id() == member_id:
                return m
        return None

    # --------------------------- Borrow/Return operations ---------------------------
    def borrow(self, member_id: int, book_id: int) -> bool:
        member = self.get_member_by_id(member_id)
        book = self.find_book(book_id)
        if not member:
            print(f"No member with ID {member_id}.")
            return False
        if not book:
            print(f"No book with ID {book_id}.")
            return False
        return member.borrow_book(book)

    def return_book(self, member_id: int, book_id: int) -> bool:
        member = self.get_member_by_id(member_id)
        if not member:
            print(f"No member with ID {member_id}.")
            return False
        return member.return_book(book_id)

    # --------------------------- Operator overloading ---------------------------
    def __add__(self, other: "Library") -> "Library":
        """Merge two libraries into a new one; combines books and members."""
        merged = Library(f"{self.name} & {other.name}")
        # Avoid duplicates by book_id; keep first occurrence
        seen_ids = set()
        for b in self.books + other.books:
            if b.get_book_id() not in seen_ids:
                merged.books.append(b)
                seen_ids.add(b.get_book_id())

        # Merge members by member_id; avoid duplicates
        seen_member_ids = set()
        for m in self.members + other.members:
            if m.get_member_id() not in seen_member_ids:
                merged.members.append(m)
                seen_member_ids.add(m.get_member_id())

        print(f"Merged libraries into '{merged.name}'.")
        return merged

    # --------------------------- Destructor ---------------------------
    def __del__(self):
        # Note: __del__ timing depends on Python's garbage collector
        print(f"Library '{self.name}' is being cleaned up.")

def seed_demo_data():
    """Create two libraries with sample data."""
    lib1 = Library("Central Library")
    lib1.add_book(Book("Python Basics", "Guido van Rossum", 101))
    lib1.add_book(Book("Data Structures", "N. Wirth", 102))
    lib1.add_member(StudentMember("Alice", 1))
    lib1.add_member(FacultyMember("Dr. Bob", 2))

    lib2 = Library("AI Library")
    lib2.add_book(Book("AI: A Modern Approach", "Russell & Norvig", 201))
    lib2.add_book(Book("Deep Learning", "Goodfellow et al.", 202))
    lib2.add_member(StudentMember("Charlie", 3))
    lib2.add_member(FacultyMember("Prof. Dana", 4))

    return lib1, lib2


def print_menu():
    print("\n--- Library Menu ---")
    print("1. Show books")
    print("2. Register member")
    print("3. Add book")
    print("4. Remove book")
    print("5. Borrow book")
    print("6. Return book")
    print("7. Show member borrowed books")
    print("8. Merge with another library")
    print("9. Switch active library")
    print("0. Exit")


def run_cli():
    lib1, lib2 = seed_demo_data( )
    libraries = [lib1, lib2]
    active_idx = 0

    print(f"\nActive library: {libraries[active_idx].name}")
    while True:
        print_menu()
        try:
            choice = int(input("Choose an option: ").strip())
        except ValueError:
            print("Please enter a valid number.")
            continue

        active_lib = libraries[active_idx]

        if choice == 1:
            active_lib.show_books()

        elif choice == 2:
            name = input("Member name: ").strip()
            role = input("Role (student/faculty): ").strip().lower()
            try:
                member_id = int(input("Member ID (int): ").strip())
            except ValueError:
                print("Invalid ID.")
                continue

            if role == "student":
                active_lib.add_member(StudentMember(name, member_id))
            elif role == "faculty":
                active_lib.add_member(FacultyMember(name, member_id))
            else:
                print("Unknown role. Use 'student' or 'faculty'.")

        elif choice == 3:
            title = input("Book title: ").strip()
            author = input("Author: ").strip()
            try:
                book_id = int(input("Book ID (int): ").strip())
            except ValueError:
                print("Invalid book ID.")
                continue
            if active_lib.find_book(book_id):
                print("A book with this ID already exists.")
                continue
            active_lib.add_book(Book(title, author, book_id))

        elif choice == 4:
            try:
                book_id = int(input("Book ID to remove: ").strip())
            except ValueError:
                print("Invalid book ID.")
                continue
            active_lib.remove_book(book_id)

        elif choice == 5:
            try:
                member_id = int(input("Member ID: ").strip())
                book_id = int(input("Book ID: ").strip())
            except ValueError:
                print("Invalid input.")
                continue
            active_lib.borrow(member_id, book_id)

        elif choice == 6:
            try:
                member_id = int(input("Member ID: ").strip())
                book_id = int(input("Book ID: ").strip())
            except ValueError:
                print("Invalid input.")
                continue
            active_lib.return_book(member_id, book_id)

        elif choice == 7:
            try:
                member_id = int(input("Member ID: ").strip())
            except ValueError:
                print("Invalid input.")
                continue
            member = active_lib.get_member_by_id(member_id)
            if member:
                member.list_borrowed()
            else:
                print("Member not found.")

        elif choice == 8:
            other_idx = 1 - active_idx
            merged = active_lib + libraries[other_idx]
            libraries.append(merged)
            active_idx = len(libraries) - 1
            print(f"Switched to merged library: {libraries[active_idx].name}")

        elif choice == 9:
            print("Available libraries:")
            for i, lib in enumerate(libraries):
                print(f"{i}: {lib.name}")
            try:
                new_idx = int(input("Select index: ").strip())
            except ValueError:
                print("Invalid index.")
                continue
            if 0 <= new_idx < len(libraries):
                active_idx = new_idx
                print(f"Now using: {libraries[active_idx].name}")
            else:
                print("Index out of range.")

        elif choice == 0:
            print("Goodbye!")
            break

        else:
            print("Unknown option.")


if __name__ == "__main__":

    run_cli()

