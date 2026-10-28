"""
backup_manager.py

File I/O utilities (Unit 2):
  - Backup the book catalog / member records to timestamped JSON files
  - Restore a collection from a given backup file
  - Export CSV reports (borrow history, overdue list)
  - Export a simple PDF overdue report (via reportlab)
  - Append structured log lines to logs/
"""
import json
import csv
import logging
from datetime import datetime
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)


def _backup_dir() -> Path:
    d = settings.LIBRAFLOW["BACKUP_DIR"]
    d.mkdir(parents=True, exist_ok=True)
    return d


def backup_books() -> Path:
    from apps.books.models import BookDocument
    data = [b.to_dict() for b in BookDocument.objects.all()]
    path = _backup_dir() / f"books_backup_{datetime.now():%Y%m%d_%H%M%S}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    logger.info(f"Books backed up to {path}")
    return path


def backup_members() -> Path:
    from apps.members.models import MemberDocument
    data = [m.to_dict() for m in MemberDocument.objects.all()]
    path = _backup_dir() / f"members_backup_{datetime.now():%Y%m%d_%H%M%S}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    logger.info(f"Members backed up to {path}")
    return path


def restore_books(backup_path: str):
    from apps.books.book_manager import BookManager
    with open(backup_path) as f:
        records = json.load(f)
    restored = 0
    for r in records:
        try:
            BookManager.add_book(
                book_id=r["book_id"], title=r["title"], author=r["author"],
                isbn=r["isbn"], category=r["category"],
                total_copies=r.get("total_copies", 1),
                description=r.get("description", ""),
                cover_image=r.get("cover_image", ""),
                tags=r.get("tags", []),
            )
            restored += 1
        except Exception as exc:
            logger.warning(f"Skipped restoring {r.get('book_id')}: {exc}")
    return restored


def export_borrow_history_csv(records) -> Path:
    path = _backup_dir() / f"borrow_history_{datetime.now():%Y%m%d_%H%M%S}.csv"
    fieldnames = ["member_id", "book_id", "borrow_date", "due_date",
                  "return_date", "status", "days_late", "fine_amount"]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            row = r.to_dict()
            writer.writerow({k: row.get(k, "") for k in fieldnames})
    return path


def export_overdue_report_pdf(records) -> Path:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet

    path = _backup_dir() / f"overdue_report_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [Paragraph("LibraFlow — Overdue Books Report", styles["Title"])]

    table_data = [["Member ID", "Book ID", "Due Date", "Days Late"]]
    for r in records:
        row = r.to_dict()
        table_data.append([row["member_id"], row["book_id"], row["due_date"][:10], str(row["days_late"])])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563EB")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    elements.append(table)
    doc.build(elements)
    return path
