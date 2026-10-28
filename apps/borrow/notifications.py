"""
notifications.py

Simulates an email-alert system: rather than integrating a real SMTP
provider, it writes structured notification records into MongoDB
(`notifications` collection) and appends a line to logs/notifications.log.
The Django dashboard reads unread notifications to show the "overdue
alert popup".
"""
import logging
from pathlib import Path
from django.conf import settings
from apps.borrow.models import NotificationDocument

logger = logging.getLogger(__name__)


def _log_line(message: str):
    log_dir = settings.LIBRAFLOW["LOG_DIR"]
    log_dir.mkdir(parents=True, exist_ok=True)
    with open(log_dir / "notifications.log", "a") as f:
        f.write(message + "\n")


def send_overdue_notification(record) -> NotificationDocument:
    message = (
        f"Book '{record.book_id}' borrowed by member '{record.member_id}' "
        f"is overdue by {record.days_late} day(s). Please return it as soon as possible."
    )
    notif = NotificationDocument(
        member_id=record.member_id, book_id=record.book_id,
        message=message, notif_type="overdue",
    )
    notif.save()
    _log_line(f"[OVERDUE] {message}")
    logger.info(message)
    return notif


def send_due_soon_notification(record) -> NotificationDocument:
    message = (
        f"Reminder: book '{record.book_id}' is due in {record.remaining_days} day(s)."
    )
    notif = NotificationDocument(
        member_id=record.member_id, book_id=record.book_id,
        message=message, notif_type="due_soon",
    )
    notif.save()
    _log_line(f"[DUE SOON] {message}")
    return notif


def send_return_confirmation(record) -> NotificationDocument:
    message = f"Thank you for returning '{record.book_id}'."
    notif = NotificationDocument(
        member_id=record.member_id, book_id=record.book_id,
        message=message, notif_type="return_confirmation",
    )
    notif.save()
    _log_line(f"[RETURNED] {message}")
    return notif


def unread_notifications(member_id: str = None, limit: int = 20):
    qs = NotificationDocument.objects.filter(is_read=False)
    if member_id:
        qs = qs.filter(member_id=member_id)
    return qs.order_by("-created_at").limit(limit)


def mark_all_read(member_id: str = None):
    qs = NotificationDocument.objects.filter(is_read=False)
    if member_id:
        qs = qs.filter(member_id=member_id)
    qs.update(is_read=True)
