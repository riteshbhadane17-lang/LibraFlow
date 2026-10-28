"""
borrow_manager.py

Implements the borrow / return workflow, overdue detection queries,
and borrowing statistics. Raises AlreadyBorrowedBookException when a
member tries to borrow a book copy while they already hold one, and
BookNotAvailableException / MemberNotEligibleException for the other
edge cases described in the spec.
"""
from datetime import datetime, timedelta
from django.conf import settings
from apps.borrow.models import BorrowRecordDocument
from apps.books.models import BookDocument
from apps.members.models import MemberDocument
from core.exceptions import (
    AlreadyBorrowedBookException,
    BookNotAvailableException,
    MemberNotEligibleException,
    RecordNotFoundException,
)


class BorrowManager:

    # ---------------- Borrow / Return ----------------

    @staticmethod
    def borrow_book(member_id: str, book_id: str, loan_period_days: int = None) -> BorrowRecordDocument:
        member = MemberDocument.objects(member_id=member_id).first()
        if not member:
            raise RecordNotFoundException(f"Member '{member_id}' not found")

        book = BookDocument.objects(book_id=book_id).first()
        if not book:
            raise RecordNotFoundException(f"Book '{book_id}' not found")

        # Already-borrowed check (this member currently holds this book)
        existing = BorrowRecordDocument.objects(
            member_id=member_id, book_id=book_id, status__in=["borrowed", "overdue"]
        ).first()
        if existing:
            raise AlreadyBorrowedBookException(book.title, member.name)

        if not member.can_borrow():
            raise MemberNotEligibleException(
                f"'{member.name}' has reached their borrow limit or has unpaid fines"
            )

        if not book.is_available():
            raise BookNotAvailableException(book.title)

        period = loan_period_days or settings.LIBRAFLOW["BORROW_PERIOD_DAYS"]
        borrow_date = datetime.utcnow()
        due_date = borrow_date + timedelta(days=period)

        record = BorrowRecordDocument(
            member_id=member_id, book_id=book_id,
            borrow_date=borrow_date, due_date=due_date, status="borrowed",
        )
        record.save()

        book.available_copies -= 1
        book.save()

        member.borrowed_book_ids.append(book_id)
        member.save()

        return record

    @staticmethod
    def return_book(member_id: str, book_id: str) -> BorrowRecordDocument:
        record = BorrowRecordDocument.objects(
            member_id=member_id, book_id=book_id, status__in=["borrowed", "overdue"]
        ).first()
        if not record:
            raise RecordNotFoundException("No active borrow record found for this member/book")

        record.return_date = datetime.utcnow()
        record.status = "returned"

        if record.days_late > 0:
            fine_per_day = settings.LIBRAFLOW["FINE_PER_DAY"]
            record.fine_amount = record.days_late * fine_per_day
        record.save()

        book = BookDocument.objects(book_id=book_id).first()
        if book and book.available_copies < book.total_copies:
            book.available_copies += 1
            book.save()

        member = MemberDocument.objects(member_id=member_id).first()
        if member:
            if book_id in member.borrowed_book_ids:
                member.borrowed_book_ids.remove(book_id)
            if record.fine_amount:
                member.fines_due += record.fine_amount
            member.save()

        return record

    # ---------------- Queries ----------------

    @staticmethod
    def find_overdue():
        now = datetime.utcnow()
        return BorrowRecordDocument.objects(
            status__in=["borrowed", "overdue"], due_date__lt=now
        )

    @staticmethod
    def borrow_history(member_id: str = None, book_id: str = None):
        qs = BorrowRecordDocument.objects
        if member_id:
            qs = qs.filter(member_id=member_id)
        if book_id:
            qs = qs.filter(book_id=book_id)
        return qs.order_by("-borrow_date")

    @staticmethod
    def recently_borrowed(limit: int = 10):
        return BorrowRecordDocument.objects.order_by("-borrow_date").limit(limit)

    @staticmethod
    def most_borrowed_books(limit: int = 10):
        pipeline = [
            {"$group": {"_id": "$book_id", "borrow_count": {"$sum": 1}}},
            {"$sort": {"borrow_count": -1}},
            {"$limit": limit},
        ]
        return list(BorrowRecordDocument.objects.aggregate(pipeline))

    @staticmethod
    def stats_summary() -> dict:
        return {
            "total_books": BookDocument.objects.count(),
            "available_books": BookDocument.objects.filter(available_copies__gt=0).count(),
            "borrowed_books": BorrowRecordDocument.objects.filter(status__in=["borrowed", "overdue"]).count(),
            "total_members": MemberDocument.objects.count(),
            "today_borrow": BorrowRecordDocument.objects.filter(
                borrow_date__gte=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            ).count(),
            "today_return": BorrowRecordDocument.objects.filter(
                return_date__gte=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            ).count(),
            "overdue_books": BorrowManager.find_overdue().count(),
        }
