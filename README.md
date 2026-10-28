# LibraFlow

**Smart Library Management with Overdue Alert System** — EdTech domain.

A full-stack library management system built with **Django 5**, **Django REST
Framework**, and **MongoDB** (via MongoEngine). Librarians manage books,
members, borrowing and returns; a background thread automatically detects
overdue books, logs reports, and notifies members.

## Tech Stack

| Layer      | Technology |
|------------|------------|
| Backend    | Python 3.11+, Django 5, Django REST Framework |
| Database   | MongoDB (via MongoEngine) + SQLite (Django auth/session only) |
| Frontend   | HTML5, CSS3, Bootstrap 5, vanilla JavaScript, Font Awesome |
| Auth       | Django auth + role-based `Profile` (admin / librarian / member) |

## Project Structure

```
LibraFlow/
├── manage.py
├── console_app.py          # Unit 1-2 menu-driven console program (no DB needed)
├── requirements.txt
├── README.md
├── libraflow/               # Django project (settings, urls, wsgi/asgi)
├── core/                    # Framework-independent OOP layer (Unit 3)
│   ├── entities.py          # Book, Member, Person, BorrowRecord classes
│   ├── exceptions.py        # AlreadyBorrowedBookException & friends
│   ├── validators.py        # ISBN / email / phone / member-id regex validation
│   └── threading_jobs.py    # Daily overdue-checker background thread
├── apps/
│   ├── books/                # book_manager.py, MongoEngine model, views, API
│   ├── members/               # member_manager.py, MongoEngine model, views
│   ├── borrow/                 # borrow_manager.py, notifications.py, backup_manager.py
│   ├── dashboard/               # dashboard, landing/about/contact, stats
│   ├── accounts/                 # login/register/logout, role-based Profile
│   └── api/                       # DRF endpoints (/api/books, /borrow, /overdue ...)
├── templates/                # Bootstrap 5 templates for every page
├── static/{css,js}/          # Theme CSS + JS (dark mode, toasts)
├── backups/                  # JSON/CSV/PDF backups & reports land here
├── logs/                     # libraflow.log, notifications.log
└── docs/                     # Setup guides, API docs, diagrams (see docs/)
```

## Quick Start

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start MongoDB locally (see docs/MONGODB_SETUP.md), default
#    connection string is mongodb://localhost:27017

# 4. Run Django migrations (creates the SQLite auth/session tables only)
python manage.py migrate

# 5. Create an admin user
python manage.py createsuperuser

# 6. (Optional) seed demo books & members into MongoDB
python manage.py seed_demo_data

# 7. Run the server
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** for the site and **/admin/** for Django admin
(user/session/role management — library data itself lives in MongoDB and is
managed through the web UI at `/books/`, `/members/`, etc., not the Django
admin, since MongoEngine documents aren't Django ORM models).

## Console App (Units 1–2)

A dependency-free menu-driven program is included for the fundamentals unit:

```bash
python console_app.py
```

It uses plain lists/dicts for the book catalog and borrow records and shares
the same validators/exceptions as the web app.

## REST API

All endpoints are under `/api/` and require an authenticated session or
token (except read-only book listing). See `docs/API_DOCUMENTATION.md`.

```
GET    /api/books/
POST   /api/books/
GET    /api/books/<book_id>/
PUT    /api/books/<book_id>/
DELETE /api/books/<book_id>/
GET    /api/members/
GET    /api/borrow/
POST   /api/borrow/
POST   /api/return/
GET    /api/overdue/
```

## Overdue Alert System

`apps/dashboard/apps.py` starts a daemon thread
(`core/threading_jobs.py::OverdueCheckerThread`) when the server boots. Every
`OVERDUE_CHECK_INTERVAL_HOURS` (default 24, configurable in
`libraflow/settings.py -> LIBRAFLOW`), it:

1. Scans `borrow_records` for anything past its `due_date`
2. Flips status to `overdue` and writes a CSV report to `backups/`
3. Creates a `NotificationDocument` per affected member (simulated email
   alert) and logs it to `logs/notifications.log`

The dashboard displays unread notifications and an overdue badge in the navbar.

## Documentation

See the `docs/` folder for:
- `INSTALLATION.md` — detailed install steps
- `MONGODB_SETUP.md` — MongoDB installation & connection config
- `DJANGO_SETUP.md` — Django project configuration notes
- `API_DOCUMENTATION.md` — full endpoint reference with examples
- `PROJECT_REPORT.md` — architecture overview, ER diagram (text form), use-case/class/sequence outlines, database schema

## Coding Standards

- PEP-8, modular files, business logic separated from views (`*_manager.py`)
- Custom exceptions (`core/exceptions.py`) instead of bare `except:`
- Regex validation for ISBN-10/13, email, phone, member ID
- No duplicate logic between console app, web views, and REST API — all three
  call into the same `*_manager.py` functions
