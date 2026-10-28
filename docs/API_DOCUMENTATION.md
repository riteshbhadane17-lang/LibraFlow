# API Documentation

Base URL: `/api/`
Auth: Django session auth (log in via the web UI) or DRF Token auth.

## Books

### `GET /api/books/`
Query params: `q` (search title/author/isbn), `category`
```json
[
  {"book_id": "BK-0001", "title": "Clean Code", "author": "Robert C. Martin",
   "isbn": "9780132350884", "category": "Software Engineering",
   "total_copies": 3, "available_copies": 3}
]
```

### `POST /api/books/`
```json
{"book_id": "BK-0006", "title": "Deep Work", "author": "Cal Newport",
 "isbn": "9781455586691", "category": "Self-Help", "total_copies": 2}
```
→ `201 Created`

### `GET /api/books/<book_id>/`
### `PUT /api/books/<book_id>/` — partial field update
### `DELETE /api/books/<book_id>/` → `204 No Content`

## Members

### `GET /api/members/?q=<search>`
Requires authentication.

## Borrow / Return

### `GET /api/borrow/?member_id=&book_id=`
Returns borrow history, optionally filtered.

### `POST /api/borrow/`
```json
{"member_id": "LIB-2026-0001", "book_id": "BK-0001"}
```
Errors: `400` with `{"detail": "..."}` on `AlreadyBorrowedBookException`,
`BookNotAvailableException`, or `MemberNotEligibleException`.

### `POST /api/return/`
```json
{"member_id": "LIB-2026-0001", "book_id": "BK-0001"}
```

## Overdue

### `GET /api/overdue/`
Returns all currently overdue borrow records with `days_late`.
