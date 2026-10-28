"""
DRF serializers for MongoEngine documents.

Since our documents aren't Django ORM models, we use plain
serializers.Serializer (not ModelSerializer) and map fields explicitly.
"""
from rest_framework import serializers


class BookSerializer(serializers.Serializer):
    book_id = serializers.CharField(max_length=20)
    title = serializers.CharField(max_length=255)
    author = serializers.CharField(max_length=255)
    isbn = serializers.CharField(max_length=20)
    category = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True)
    cover_image = serializers.CharField(required=False, allow_blank=True)
    total_copies = serializers.IntegerField(min_value=1, default=1)
    available_copies = serializers.IntegerField(read_only=True)


class MemberSerializer(serializers.Serializer):
    member_id = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    membership_type = serializers.CharField(max_length=20, default="standard")
    max_books = serializers.IntegerField(default=5)
    borrowed_book_ids = serializers.ListField(child=serializers.CharField(), read_only=True)
    fines_due = serializers.FloatField(read_only=True)


class BorrowRecordSerializer(serializers.Serializer):
    member_id = serializers.CharField(max_length=20)
    book_id = serializers.CharField(max_length=20)
    borrow_date = serializers.DateTimeField(read_only=True)
    due_date = serializers.DateTimeField(read_only=True)
    return_date = serializers.DateTimeField(read_only=True, allow_null=True)
    status = serializers.CharField(read_only=True)
    remaining_days = serializers.IntegerField(read_only=True)
    days_late = serializers.IntegerField(read_only=True)
    fine_amount = serializers.IntegerField(read_only=True)
