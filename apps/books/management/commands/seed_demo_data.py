"""
Usage: python manage.py seed_demo_data

Populates MongoDB with a handful of demo books and members so the
dashboard, catalog, and API endpoints have data to show immediately
after setup.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed demo books and members into MongoDB"

    def handle(self, *args, **options):
        from apps.books.book_manager import BookManager
        from apps.members.member_manager import MemberManager

        demo_books = [
            dict(book_id="BK-0001", title="Clean Code", author="Robert C. Martin",
                 isbn="9780132350884", category="Software Engineering", total_copies=3),
            dict(book_id="BK-0002", title="The Pragmatic Programmer", author="Andrew Hunt",
                 isbn="9780135957059", category="Software Engineering", total_copies=2),
            dict(book_id="BK-0003", title="Sapiens", author="Yuval Noah Harari",
                 isbn="9780062316097", category="History", total_copies=4),
            dict(book_id="BK-0004", title="Atomic Habits", author="James Clear",
                 isbn="9780735211292", category="Self-Help", total_copies=5),
            dict(book_id="BK-0005", title="Django for Professionals", author="William S. Vincent",
                 isbn="9781735467221", category="Software Engineering", total_copies=2),
        ]

        demo_members = [
            dict(member_id="LIB-2026-0001", name="Aditi Sharma", email="aditi@example.com",
                 phone="+91-9876543210", membership_type="premium"),
            dict(member_id="LIB-2026-0002", name="Rohan Verma", email="rohan@example.com",
                 phone="+91-9876500000", membership_type="standard"),
        ]

        created_books = 0
        for b in demo_books:
            try:
                BookManager.add_book(**b)
                created_books += 1
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f"Skipped {b['book_id']}: {exc}"))

        created_members = 0
        for m in demo_members:
            try:
                MemberManager.register_member(**m)
                created_members += 1
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f"Skipped {m['member_id']}: {exc}"))

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {created_books} book(s) and {created_members} member(s)."
        ))
