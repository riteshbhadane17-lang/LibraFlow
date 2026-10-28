from mongoengine import Document, StringField, IntField, FloatField, DateTimeField, ListField
from datetime import datetime


class MemberDocument(Document):
    member_id = StringField(required=True, unique=True, max_length=20)   # LIB-YYYY-NNNN
    name = StringField(required=True, max_length=255)
    email = StringField(required=True, unique=True, max_length=255)
    phone = StringField(required=True, max_length=20)
    membership_type = StringField(choices=["standard", "premium", "student"], default="standard")
    max_books = IntField(default=5)
    borrowed_book_ids = ListField(StringField(), default=list)
    fines_due = FloatField(default=0.0)
    is_active = StringField(choices=["active", "suspended"], default="active")
    joined_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "members",
        "indexes": ["member_id", "email"],
        "ordering": ["name"],
    }

    def can_borrow(self) -> bool:
        return (
            self.is_active == "active"
            and len(self.borrowed_book_ids) < self.max_books
            and self.fines_due <= 0
        )

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "member_id": self.member_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "membership_type": self.membership_type,
            "max_books": self.max_books,
            "borrowed_book_ids": self.borrowed_book_ids,
            "fines_due": self.fines_due,
            "is_active": self.is_active,
        }

    def __str__(self):
        return f"{self.name} ({self.member_id})"
