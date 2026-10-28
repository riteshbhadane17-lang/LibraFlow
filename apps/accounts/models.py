"""
Role-based access is layered on top of Django's built-in User model via
a small Profile model (kept in the default SQLite DB alongside auth,
since it's identity/auth data rather than library data).
"""
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("librarian", "Librarian"),
        ("member", "Member"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")
    member_id = models.CharField(max_length=20, blank=True, default="")  # links to MongoDB member doc

    def __str__(self):
        return f"{self.user.username} ({self.role})"
