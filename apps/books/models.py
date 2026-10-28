"""
MongoEngine document for the `books` collection.

This wraps the plain-Python core.entities.Book with MongoDB persistence
(schema validation, indexes) while keeping business rules in one place.
"""
from mongoengine import (
    Document, StringField, IntField, DateTimeField, URLField, ListField
)
from datetime import datetime


class BookDocument(Document):
    book_id = StringField(required=True, unique=True, max_length=20)
    title = StringField(required=True, max_length=255)
    author = StringField(required=True, max_length=255)
    isbn = StringField(required=True, unique=True, max_length=20)
    category = StringField(required=True, max_length=100)
    description = StringField(max_length=2000, default="")
    cover_image = StringField(default="")
    total_copies = IntField(required=True, min_value=0, default=1)
    available_copies = IntField(required=True, min_value=0, default=1)
    tags = ListField(StringField(max_length=50), default=list)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "books",
        "indexes": [
            "book_id",
            "isbn",
            "category",
            "title",
            "author",
            {"fields": ["$title", "$author", "$category"],
             "default_language": "english"},
        ],
        "ordering": ["title"],
    }

    def is_available(self) -> bool:
        return self.available_copies > 0

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "category": self.category,
            "description": self.description,
            "cover_image": self.cover_image,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies,
            "tags": self.tags,
        }

    def __str__(self):
        return f"{self.title} ({self.book_id})"
