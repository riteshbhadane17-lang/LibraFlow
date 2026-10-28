from mongoengine import Document, StringField, DateTimeField, IntField, BooleanField
from datetime import datetime, timedelta


class BorrowRecordDocument(Document):
    member_id = StringField(required=True, max_length=20)
    book_id = StringField(required=True, max_length=20)
    borrow_date = DateTimeField(default=datetime.utcnow)
    due_date = DateTimeField(required=True)
    return_date = DateTimeField(null=True)
    status = StringField(choices=["borrowed", "returned", "overdue"], default="borrowed")
    fine_amount = IntField(default=0)

    meta = {
        "collection": "borrow_records",
        "indexes": ["member_id", "book_id", "status", "due_date"],
        "ordering": ["-borrow_date"],
    }

    @property
    def remaining_days(self) -> int:
        return (self.due_date.date() - datetime.utcnow().date()).days

    @property
    def days_late(self) -> int:
        reference = self.return_date or datetime.utcnow()
        late = (reference.date() - self.due_date.date()).days
        return max(late, 0)

    def is_overdue(self) -> bool:
        return self.status in ("borrowed", "overdue") and datetime.utcnow() > self.due_date

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "member_id": self.member_id,
            "book_id": self.book_id,
            "borrow_date": self.borrow_date.isoformat(),
            "due_date": self.due_date.isoformat(),
            "return_date": self.return_date.isoformat() if self.return_date else None,
            "status": self.status,
            "remaining_days": self.remaining_days,
            "days_late": self.days_late,
            "fine_amount": self.fine_amount,
        }

    def __str__(self):
        return f"{self.member_id} -> {self.book_id} [{self.status}]"


class NotificationDocument(Document):
    member_id = StringField(required=True, max_length=20)
    book_id = StringField(required=True, max_length=20)
    message = StringField(required=True, max_length=500)
    notif_type = StringField(choices=["overdue", "due_soon", "return_confirmation", "system"], default="overdue")
    is_read = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "notifications",
        "indexes": ["member_id", "is_read", "-created_at"],
        "ordering": ["-created_at"],
    }

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "member_id": self.member_id,
            "book_id": self.book_id,
            "message": self.message,
            "notif_type": self.notif_type,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat(),
        }
