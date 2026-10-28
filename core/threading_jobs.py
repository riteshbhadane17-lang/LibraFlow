"""
Background thread that periodically:
  1. Checks all active borrow records for overdue status
  2. Updates their status to 'overdue' in MongoDB
  3. Generates an overdue report (CSV) in backups/
  4. Sends (simulated) notifications to affected members

Started once from apps.dashboard.apps.DashboardConfig.ready() so it runs
alongside the Django dev/production server without blocking requests.
"""
import threading
import time
import csv
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class OverdueCheckerThread(threading.Thread):
    """Daemon thread — dies automatically when the main process exits."""

    def __init__(self, interval_hours: int = 24, backup_dir: Path = None, run_immediately: bool = True):
        super().__init__(daemon=True, name="OverdueCheckerThread")
        self.interval_seconds = interval_hours * 3600
        self.backup_dir = backup_dir or Path("backups")
        self.run_immediately = run_immediately
        self._stop_event = threading.Event()

    def run(self):
        if self.run_immediately:
            self._check_overdue_books()
        while not self._stop_event.wait(self.interval_seconds):
            self._check_overdue_books()

    def stop(self):
        self._stop_event.set()

    def _check_overdue_books(self):
        # Imported lazily so this module has zero import-time dependency
        # on Django being fully configured (avoids AppRegistryNotReady).
        from apps.borrow.models import BorrowRecordDocument
        from apps.borrow.borrow_manager import BorrowManager
        from apps.borrow.notifications import send_overdue_notification

        logger.info("OverdueCheckerThread: scanning for overdue books...")
        overdue_records = BorrowManager.find_overdue()

        report_rows = []
        for record in overdue_records:
            if record.status != "overdue":
                record.status = "overdue"
                record.save()
            report_rows.append({
                "member_id": record.member_id,
                "book_id": record.book_id,
                "borrow_date": record.borrow_date,
                "due_date": record.due_date,
                "days_late": (datetime.utcnow().date() - record.due_date.date()).days,
            })
            send_overdue_notification(record)

        self._write_report(report_rows)
        logger.info(f"OverdueCheckerThread: {len(report_rows)} overdue record(s) processed.")

    def _write_report(self, rows: list[dict]):
        if not rows:
            return
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        filename = self.backup_dir / f"overdue_report_{datetime.now():%Y%m%d_%H%M%S}.csv"
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        logger.info(f"Overdue report written to {filename}")


_thread_instance: OverdueCheckerThread | None = None


def start_overdue_checker(interval_hours: int = 24, backup_dir: Path = None):
    """Idempotent starter — safe to call multiple times (e.g. autoreload)."""
    global _thread_instance
    if _thread_instance is not None and _thread_instance.is_alive():
        return _thread_instance
    _thread_instance = OverdueCheckerThread(interval_hours=interval_hours, backup_dir=backup_dir)
    _thread_instance.start()
    return _thread_instance
