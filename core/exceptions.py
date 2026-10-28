"""Custom exceptions used across LibraFlow."""


class LibraFlowException(Exception):
    """Base exception for all LibraFlow-specific errors."""


class AlreadyBorrowedBookException(LibraFlowException):
    """Raised when a member tries to borrow a book that is already
    borrowed by them (or has no available copies left)."""

    def __init__(self, book_title: str, member_name: str = ""):
        self.book_title = book_title
        self.member_name = member_name
        message = f"'{book_title}' is already borrowed"
        if member_name:
            message += f" by {member_name}"
        super().__init__(message)


class BookNotAvailableException(LibraFlowException):
    """Raised when there are zero available copies of a book."""

    def __init__(self, book_title: str):
        super().__init__(f"No available copies of '{book_title}'")


class MemberNotEligibleException(LibraFlowException):
    """Raised when a member has hit their borrow limit or has unpaid fines."""


class InvalidISBNException(LibraFlowException):
    """Raised when an ISBN fails ISBN-10/ISBN-13 validation."""


class InvalidMemberIDException(LibraFlowException):
    """Raised when a member ID fails the expected format."""


class InvalidEmailException(LibraFlowException):
    """Raised when an email fails regex validation."""


class InvalidPhoneException(LibraFlowException):
    """Raised when a phone number fails regex validation."""


class RecordNotFoundException(LibraFlowException):
    """Raised when a book/member/borrow record can't be found."""
