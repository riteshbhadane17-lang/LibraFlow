# LibraFlow — Project Report

## 1. Overview
LibraFlow is a library management system that lets librarians manage a book
catalog, member registry, and the borrow/return lifecycle, with automatic
overdue detection and member notifications. Built with Django 5 + DRF for
the web/API layer and MongoDB (via MongoEngine) for persistence of library
data, with Django's own auth system layered on top for login/roles.

## 2. ER Diagram (entity-relationship, text form)

```
┌───────────────┐        ┌──────────────────┐        ┌───────────────┐
│     Member     │        │   BorrowRecord    │        │      Book      │
├───────────────┤        ├──────────────────┤        ├───────────────┤
│ member_id (PK)│───┐    │ id (PK)           │    ┌───│ book_id (PK)   │
│ name           │   └───│ member_id (FK)     │───┘    │ title          │
│ email          │        │ book_id (FK)      │        │ author         │
│ phone          │        │ borrow_date        │        │ isbn           │
│ membership_type│        │ due_date           │        │ category       │
│ max_books      │        │ return_date        │        │ total_copies   │
│ borrowed_book_ids       │ status             │        │ available_copies│
│ fines_due      │        │ fine_amount        │        └───────────────┘
└───────────────┘        └──────────────────┘
        │                          │
        │                          │
        │                 ┌──────────────────┐
        └────────────────│   Notification    │
                           ├──────────────────┤
                           │ id (PK)           │
                           │ member_id (FK)    │
                           │ book_id (FK)      │
                           │ message           │
                           │ notif_type        │
                           │ is_read           │
                           │ created_at        │
                           └──────────────────┘
```
Relationships: one Member ⟶ many BorrowRecords; one Book ⟶ many
BorrowRecords; one Member ⟶ many Notifications. All FKs are logical
(string references to `member_id`/`book_id`) since MongoDB is schema-flexible
and these are separate collections rather than SQL foreign keys.

## 3. Use Case Diagram (text form)

```
                    ┌─────────────────────────────┐
   Librarian ──────▶│ Add / Edit / Delete Book     │
   Librarian ──────▶│ Register / Delete Member     │
   Librarian ──────▶│ Process Borrow / Return      │
   Librarian ──────▶│ View Reports & Overdue List  │
   Member    ──────▶│ Search / Browse Catalog      │
   Member    ──────▶│ View Own Borrow History      │
   System    ──────▶│ Daily Overdue Check (thread) │
   System    ──────▶│ Send Notification            │
                    └─────────────────────────────┘
```

## 4. Class Diagram (text form)

```
Person (base)
 ├─ name, email, phone
 └─ Member(Person)
     ├─ member_id, membership_type, max_books, fines_due
     ├─ can_borrow()
     ├─ add_borrowed_book() / remove_borrowed_book()

Book
 ├─ book_id, title, author, isbn, category, total_copies, available_copies
 ├─ is_available()
 ├─ checkout_copy() / return_copy()

BorrowRecord
 ├─ member_id, book_id, borrow_date, due_date, return_date, status
 ├─ remaining_days / days_late (properties)
 ├─ is_overdue() / mark_returned() / refresh_status()

Custom Exceptions (LibraFlowException base)
 ├─ AlreadyBorrowedBookException
 ├─ BookNotAvailableException
 ├─ MemberNotEligibleException
 ├─ InvalidISBNException / InvalidMemberIDException / InvalidEmailException / InvalidPhoneException
 └─ RecordNotFoundException
```
See `core/entities.py` and `core/exceptions.py` for the full implementation
(this is the framework-independent layer shared by the console app, web
views, and REST API).

## 5. Sequence Diagram — Borrow a Book (text form)

```
Librarian → BorrowView: POST /borrow/new (member_id, book_id)
BorrowView → BorrowManager: borrow_book(member_id, book_id)
BorrowManager → MemberDocument: find member, check can_borrow()
BorrowManager → BookDocument: find book, check is_available()
BorrowManager → BorrowRecordDocument: check existing active record
  alt already borrowed
    BorrowManager --> BorrowView: raise AlreadyBorrowedBookException
  else eligible
    BorrowManager → BorrowRecordDocument: create + save (status=borrowed)
    BorrowManager → BookDocument: available_copies -= 1, save
    BorrowManager → MemberDocument: append book_id, save
    BorrowManager --> BorrowView: return BorrowRecordDocument
  end
BorrowView --> Librarian: success message + due date
```

## 6. Sequence Diagram — Daily Overdue Check (text form)

```
OverdueCheckerThread (daemon, runs every 24h)
  → BorrowManager.find_overdue(): query due_date < now, status in [borrowed, overdue]
  loop each overdue record
    → set status = "overdue", save
    → notifications.send_overdue_notification(record): create NotificationDocument, log line
  end
  → backup_manager: write CSV overdue report to backups/
```

## 7. Database Schema (MongoDB collections)

### `books`
| Field | Type | Notes |
|---|---|---|
| book_id | string | unique, indexed |
| title | string | text-indexed |
| author | string | text-indexed |
| isbn | string | unique, indexed |
| category | string | indexed |
| description | string | |
| cover_image | url string | |
| total_copies / available_copies | int | |
| tags | list[string] | |
| created_at / updated_at | datetime | |

### `members`
| Field | Type | Notes |
|---|---|---|
| member_id | string | unique, format `LIB-YYYY-NNNN` |
| name, email, phone | string | email unique |
| membership_type | enum | standard / premium / student |
| max_books | int | |
| borrowed_book_ids | list[string] | |
| fines_due | float | |
| is_active | enum | active / suspended |

### `borrow_records`
| Field | Type | Notes |
|---|---|---|
| member_id, book_id | string | indexed |
| borrow_date, due_date, return_date | datetime | |
| status | enum | borrowed / returned / overdue |
| fine_amount | int | |

### `notifications`
| Field | Type | Notes |
|---|---|---|
| member_id, book_id | string | |
| message | string | |
| notif_type | enum | overdue / due_soon / return_confirmation / system |
| is_read | bool | |
| created_at | datetime | |

## 8. Architecture Notes
- **MVC mapping**: MongoEngine `Document` classes = Model, Django templates
  = View, Django view functions + `*_manager.py` = Controller (business
  logic deliberately kept out of `views.py` so it's reusable by the console
  app and the REST API).
- **Auth DB split**: Django's relational DB (SQLite by default) holds only
  `auth`/`session`/`Profile` data; everything library-related is in MongoDB.
- **Background processing**: a daemon thread (not Celery, to keep the stack
  simple) handles the daily overdue sweep — see `core/threading_jobs.py`.
