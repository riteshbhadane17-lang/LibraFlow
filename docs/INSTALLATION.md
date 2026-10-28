# Installation Guide

## Prerequisites
- Python 3.11 or newer
- MongoDB 6.x+ running locally or a MongoDB Atlas connection string
- pip / virtualenv

## Steps

1. Clone/extract the project and `cd LibraFlow`
2. `python -m venv venv && source venv/bin/activate`
3. `pip install -r requirements.txt`
4. Copy environment variables (or export them directly):
   ```bash
   export DJANGO_SECRET_KEY="replace-me-with-a-random-value"
   export DJANGO_DEBUG=True
   export MONGO_DB_NAME=libraflow_db
   export MONGO_HOST=mongodb://localhost:27017
   ```
5. `python manage.py migrate` — creates the SQLite tables Django needs for
   `auth`, `sessions`, and `admin` (library data itself is in MongoDB).
6. `python manage.py createsuperuser`
7. `python manage.py seed_demo_data` (optional demo books & members)
8. `python manage.py runserver`

## Common Issues

- **`mongoengine.connection.ConnectionFailure`** — MongoDB isn't running or
  `MONGO_HOST` is wrong. Verify with `mongosh mongodb://localhost:27017`.
- **`ModuleNotFoundError: No module named 'apps'`** — run manage.py from the
  project root (`LibraFlow/`), not from inside `apps/`.
- **Static files not loading** — run `python manage.py collectstatic` before
  deploying with `DEBUG=False`.
