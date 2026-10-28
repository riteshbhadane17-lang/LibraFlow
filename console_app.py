"""
console_app.py

Standalone menu-driven console program covering Unit 1 & Unit 2 of the
spec: lists for the book catalog, dictionaries for borrow records,
loops for overdue detection, functions, and file I/O backups -- with
no Django/MongoDB dependency, so it runs with just `python console_app.py`.

This mirrors the same business rules as the web app (see core/entities.py)
but keeps its own in-memory list/dict structures, exactly as Unit 1 asks
for, before Unit 4 upgrades storage to MongoDB.
"""
import json
from datetime import date, timedelta
from pathlib import Path

from core.exceptions import AlreadyBorrowedBookException, LibraFlowException
from core.validators import validate_isbn, validate_email, validate_phone

# ---- Unit 1: in-memory data structures ----
book_catalog: list[dict] = []          # list of book dicts
borrow_records: dict = {}              # {member_id: {book_id, borrow_date, due_date, status}}

BACKUP_DIR = Path("backups")


def find_book(book_id: str) -> dict | None:
    return next((b for b in book_catalog if b["book_id"] == book_id), None)


def add_book(book_id, title, author, isbn, category, available_copies=1):
    validate_isbn(isbn)
    book_catalog.append({
        "book_id": book_id, "title": title, "author": author, "isbn": isbn,
        "category": category, "available_copies": available_copies,
    })
    print(f"✔ Added '{title}'")


def borrow_book(member_id, book_id, loan_days=14):
    if member_id in borrow_records and borrow_records[member_id].get("book_id") == book_id \
            and borrow_records[member_id]["status"] == "borrowed":
        raise AlreadyBorrowedBookException(book_id, member_id)

    book = find_book(book_id)
    if not book or book["available_copies"] <= 0:
        print(f"✘ '{book_id}' is not available.")
        return

    book["available_copies"] -= 1
    borrow_date = date.today()
    due_date = borrow_date + timedelta(days=loan_days)
    borrow_records[member_id] = {
        "book_id": book_id, "borrow_date": borrow_date.isoformat(),
        "due_date": due_date.isoformat(), "status": "borrowed",
    }
    print(f"✔ '{book['title']}' borrowed by {member_id}, due {due_date}")


def return_book(member_id):
    record = borrow_records.get(member_id)
    if not record or record["status"] != "borrowed":
        print("✘ No active borrow record for this member.")
        return
    record["status"] = "returned"
    book = find_book(record["book_id"])
    if book:
        book["available_copies"] += 1
    print(f"✔ Book returned by {member_id}")


def detect_overdue() -> list[dict]:
    """Loop through borrow_records and flag anything past its due date."""
    overdue = []
    today = date.today()
    for member_id, record in borrow_records.items():
        if record["status"] == "borrowed":
            due = date.fromisoformat(record["due_date"])
            if today > due:
                record["status"] = "overdue"
                overdue.append({"member_id": member_id, **record, "days_late": (today - due).days})
    return overdue


def backup_catalog():
    BACKUP_DIR.mkdir(exist_ok=True)
    path = BACKUP_DIR / "console_books_backup.json"
    with open(path, "w") as f:
        json.dump(book_catalog, f, indent=2)
    print(f"✔ Catalog backed up to {path}")


def print_menu():
    print("""
============================
   LibraFlow Console (Unit 1-2)
============================
1. Add Book
2. List Books
3. Borrow Book
4. Return Book
5. Detect Overdue Books
6. Backup Catalog
0. Exit
""")


def main():
    while True:
        print_menu()
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                add_book(
                    input("Book ID: "), input("Title: "), input("Author: "),
                    input("ISBN: "), input("Category: "),
                    int(input("Available copies: ") or 1),
                )
            elif choice == "2":
                for b in book_catalog:
                    print(f"  {b['book_id']} | {b['title']} by {b['author']} ({b['available_copies']} available)")
            elif choice == "3":
                borrow_book(input("Member ID: "), input("Book ID: "))
            elif choice == "4":
                return_book(input("Member ID: "))
            elif choice == "5":
                for o in detect_overdue():
                    print(f"  ⚠ {o['member_id']} -> {o['book_id']} is {o['days_late']} day(s) late")
            elif choice == "6":
                backup_catalog()
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Invalid option.")
        except LibraFlowException as exc:
            print(f"✘ {exc}")


if __name__ == "__main__":
    main()
