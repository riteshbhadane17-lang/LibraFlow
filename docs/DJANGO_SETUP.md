# Django Setup Guide

## Two-database design

LibraFlow deliberately uses **two databases**:

1. **SQLite** (`db.sqlite3`) — only for Django's built-in `auth`, `sessions`,
   and `admin` machinery (usernames, passwords, login sessions, role
   Profiles). Run `python manage.py migrate` for this.
2. **MongoDB** — all library data (books, members, borrow records,
   notifications) via MongoEngine `Document` classes. No migrations needed;
   MongoEngine manages indexes declared in each model's `meta`.

This keeps auth concerns (which Django handles very well out of the box)
separate from library data (which benefits from MongoDB's flexible schema
for things like tags, descriptions, and future fields).

## Apps

| App                | Responsibility |
|--------------------|----------------|
| `apps.accounts`    | Login, register, logout, role-based `Profile` |
| `apps.books`       | Book catalog CRUD + search |
| `apps.members`     | Member registration + management |
| `apps.borrow`      | Borrow/return workflow, overdue queries, notifications, backups |
| `apps.dashboard`   | Landing/about/contact, authenticated dashboard, reports, starts the overdue-checker thread |
| `apps.api`         | DRF REST endpoints |

## Settings of note (`libraflow/settings.py`)

- `LIBRAFLOW` dict — borrow period, fine per day, max books per member,
  overdue-check interval, backup/log directories.
- `mongoengine.connect(...)` is called once at import time using
  `MONGO_DB_NAME` / `MONGO_HOST` environment variables.
- `apps.dashboard.apps.DashboardConfig.ready()` starts the daemon overdue
  thread — guarded by `RUN_MAIN` so it doesn't double-start under the
  autoreloader.
