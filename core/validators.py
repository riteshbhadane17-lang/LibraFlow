"""
Regex-based validators for LibraFlow.

These are plain functions (no Django/Mongo dependency) so they can be
unit-tested in isolation and reused by both the console app (Units 1-3)
and the Django web layer (Units 4-5).
"""
import re
from core.exceptions import (
    InvalidISBNException,
    InvalidMemberIDException,
    InvalidEmailException,
    InvalidPhoneException,
)

# ISBN-10: 9 digits + check digit (0-9 or X)
ISBN_10_REGEX = re.compile(r"^(?:\d[- ]?){9}[\dX]$")
# ISBN-13: 13 digits, optionally hyphen/space separated in 978/979-x-xx-xxxxxx-x groups
ISBN_13_REGEX = re.compile(r"^(?:97[89][- ]?)(?:\d[- ]?){9}\d$")

# LIB-YYYY-NNNN e.g. LIB-2026-0001
MEMBER_ID_REGEX = re.compile(r"^LIB-\d{4}-\d{4,6}$")

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

# Accepts +country code, spaces, dashes; 10-15 digits total
PHONE_REGEX = re.compile(r"^\+?\d{1,3}?[-.\s]?\(?\d{3,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}$")


def _clean_isbn(isbn: str) -> str:
    return isbn.replace("-", "").replace(" ", "")


def validate_isbn(isbn: str) -> bool:
    """Validate ISBN-10 or ISBN-13 format and checksum. Raises
    InvalidISBNException on failure, else returns True."""
    if not isbn or not (ISBN_10_REGEX.match(isbn) or ISBN_13_REGEX.match(isbn)):
        raise InvalidISBNException(f"'{isbn}' is not a valid ISBN-10/13 format")

    digits = _clean_isbn(isbn)

    if len(digits) == 10:
        total = 0
        for i, ch in enumerate(digits):
            val = 10 if ch.upper() == "X" else int(ch)
            total += (10 - i) * val
        if total % 11 != 0:
            raise InvalidISBNException(f"'{isbn}' failed ISBN-10 checksum")
    elif len(digits) == 13:
        total = 0
        for i, ch in enumerate(digits):
            weight = 1 if i % 2 == 0 else 3
            total += int(ch) * weight
        if total % 10 != 0:
            raise InvalidISBNException(f"'{isbn}' failed ISBN-13 checksum")
    else:
        raise InvalidISBNException(f"'{isbn}' has an invalid length")

    return True


def validate_member_id(member_id: str) -> bool:
    if not member_id or not MEMBER_ID_REGEX.match(member_id):
        raise InvalidMemberIDException(
            f"'{member_id}' is not a valid member ID (expected format LIB-YYYY-NNNN)"
        )
    return True


def validate_email(email: str) -> bool:
    if not email or not EMAIL_REGEX.match(email):
        raise InvalidEmailException(f"'{email}' is not a valid email address")
    return True


def validate_phone(phone: str) -> bool:
    if not phone or not PHONE_REGEX.match(phone):
        raise InvalidPhoneException(f"'{phone}' is not a valid phone number")
    return True
