"""
Plain-Python OOP domain classes for LibraFlow (Unit 3: Advanced Python).

These classes are deliberately independent of Django/MongoEngine so they
can be used from the console/menu-driven program (Units 1-2) as well as
wrapped by the MongoEngine Documents in each app's models.py for the web
layer. This keeps business rules in one place instead of duplicated
between the console app and the web app.
"""
from __future__ import annotations
from datetime import date, datetime, timedelta
from core.validators import validate_isbn, validate_member_id, validate_email, validate_phone
from core.exceptions import BookNotAvailableException


class Person:
    """Base class with shared identity fields. Member inherits from it."""

    def __init__(self, name: str, email: str, phone: str):
        self._name = name
        self.email = email        # validated via property setter
        self.phone = phone        # validated via property setter

    # ---- encapsulation: name is read-only after construction ----
    @property
    def name(self) -> str:
        return self._name

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        validate_email(value)
        self._email = value

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str):
        validate_phone(value)
        self._phone = value

    def __str__(self):
        return f"{self.__class__.__name__}({self._name})"


class Member(Person):
    """A library member. Inherits shared contact-info handling from Person."""

    def __init__(self, member_id: str, name: str, email: str, phone: str,
                 membership_type: str = "standard", max_books: int = 5):
        validate_member_id(member_id)
        super().__init__(name, email, phone)
        self.member_id = member_id
        self.membership_type = membership_type
        self.max_books = max_books
        self._borrowed_book_ids: list[str] = []
        self.fines_due: float = 0.0

    @property
    def borrowed_book_ids(self) -> list[str]:
        # return a copy so callers cannot mutate internal state directly
        return list(self._borrowed_book_ids)

    def can_borrow(self) -> bool:
        return len(self._borrowed_book_ids) < self.max_books and self.fines_due <= 0

    def add_borrowed_book(self, book_id: str):
        self._borrowed_book_ids.append(book_id)

    def remove_borrowed_book(self, book_id: str):
        if book_id in self._borrowed_book_ids:
            self._borrowed_book_ids.remove(book_id)

    def to_dict(self) -> dict:
        return {
            "member_id": self.member_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "membership_type": self.membership_type,
            "max_books": self.max_books,
            "borrowed_book_ids": self.borrowed_book_ids,
            "fines_due": self.fines_due,
        }


class Book:
    """A catalog entry. Encapsulates available-copy tracking."""

    def __init__(self, book_id: str, title: str, author: str, isbn: str,
                 category: str, total_copies: int = 1):
        validate_isbn(isbn)
        self.book_id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.category = category
        self._total_copies = total_copies
        self._available_copies = total_copies

    @property
    def available_copies(self) -> int:
        return self._available_copies

    @property
    def total_copies(self) -> int:
        return self._total_copies

    def is_available(self) -> bool:
        return self._available_copies > 0

    def checkout_copy(self):
        if not self.is_available():
            raise BookNotAvailableException(self.title)
        self._available_copies -= 1

    def return_copy(self):
        if self._available_copies < self._total_copies:
            self._available_copies += 1

    def to_dict(self) -> dict:
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "category": self.category,
            "total_copies": self._total_copies,
            "available_copies": self._available_copies,
        }


class BorrowRecord:
    """Tracks a single borrow transaction and computes due/late status."""

    def __init__(self, member_id: str, book_id: str, borrow_date: date = None,
                 loan_period_days: int = 14):
        self.member_id = member_id
        self.book_id = book_id
        self.borrow_date: date = borrow_date or date.today()
        self.due_date: date = self.borrow_date + timedelta(days=loan_period_days)
        self.return_date: date | None = None
        self.status: str = "borrowed"  # borrowed | returned | overdue

    @property
    def remaining_days(self) -> int:
        """Positive = days left, negative = days overdue (only meaningful
        while the book hasn't been returned yet)."""
        return (self.due_date - date.today()).days

    @property
    def days_late(self) -> int:
        reference = self.return_date or date.today()
        late = (reference - self.due_date).days
        return max(late, 0)

    def is_overdue(self) -> bool:
        return self.status == "borrowed" and date.today() > self.due_date

    def mark_returned(self):
        self.return_date = date.today()
        self.status = "returned"

    def refresh_status(self):
        """Called by the background overdue-checker thread."""
        if self.status == "borrowed" and self.is_overdue():
            self.status = "overdue"

    def to_dict(self) -> dict:
        return {
            "member_id": self.member_id,
            "book_id": self.book_id,
            "borrow_date": self.borrow_date.isoformat(),
            "due_date": self.due_date.isoformat(),
            "return_date": self.return_date.isoformat() if self.return_date else None,
            "status": self.status,
            "remaining_days": self.remaining_days,
            "days_late": self.days_late,
        }
