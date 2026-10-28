"""
book_manager.py

All CRUD + search/query logic for the `books` MongoDB collection lives
here, separated from Django views so it can be reused by the console
app, the web views, and the DRF API layer alike.
"""
from mongoengine.queryset.visitor import Q
from apps.books.models import BookDocument
from core.exceptions import RecordNotFoundException
from core.validators import validate_isbn


class BookManager:

    # ---------------- CRUD ----------------

    @staticmethod
    def add_book(book_id, title, author, isbn, category, total_copies=1,
                 description="", cover_image="", tags=None) -> BookDocument:
        validate_isbn(isbn)
        book = BookDocument(
            book_id=book_id,
            title=title,
            author=author,
            isbn=isbn,
            category=category,
            description=description,
            cover_image=cover_image,
            total_copies=total_copies,
            available_copies=total_copies,
            tags=tags or [],
        )
        book.save()
        return book

    @staticmethod
    def update_book(book_id: str, **fields) -> BookDocument:
        book = BookManager.get_book(book_id)
        for key, value in fields.items():
            if hasattr(book, key) and value is not None:
                setattr(book, key, value)
        book.save()
        return book

    @staticmethod
    def delete_book(book_id: str) -> bool:
        book = BookManager.get_book(book_id)
        book.delete()
        return True

    @staticmethod
    def get_book(book_id: str) -> BookDocument:
        book = BookDocument.objects(book_id=book_id).first()
        if not book:
            raise RecordNotFoundException(f"Book '{book_id}' not found")
        return book

    @staticmethod
    def list_books(page: int = 1, page_size: int = 20):
        skip = (page - 1) * page_size
        return BookDocument.objects.order_by("title").skip(skip).limit(page_size)

    # ---------------- Search ----------------

    @staticmethod
    def search(query: str = "", category: str = "", author: str = "",
               isbn: str = "", available_only: bool = False):
        qs = BookDocument.objects
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(author__icontains=query) | Q(isbn__icontains=query))
        if category:
            qs = qs.filter(category__iexact=category)
        if author:
            qs = qs.filter(author__icontains=author)
        if isbn:
            qs = qs.filter(isbn=isbn)
        if available_only:
            qs = qs.filter(available_copies__gt=0)
        return qs

    @staticmethod
    def available_books():
        return BookDocument.objects.filter(available_copies__gt=0)

    @staticmethod
    def categories() -> list:
        return BookDocument.objects.distinct("category")
