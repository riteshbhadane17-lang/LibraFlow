# MongoDB Setup Guide

## Option A — Local MongoDB

```bash
# macOS (Homebrew)
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0

# Ubuntu/Debian
sudo apt-get install -y mongodb
sudo systemctl start mongodb

# Windows — download the MSI installer from mongodb.com/try/download/community
```

Default connection string: `mongodb://localhost:27017`

## Option B — MongoDB Atlas (cloud, free tier)

1. Create a cluster at https://www.mongodb.com/cloud/atlas
2. Add your IP to the network access list
3. Create a database user
4. Copy the connection string, e.g.
   `mongodb+srv://<user>:<password>@cluster0.mongodb.net`
5. Set it as `MONGO_HOST` before running the server:
   ```bash
   export MONGO_HOST="mongodb+srv://<user>:<password>@cluster0.mongodb.net"
   export MONGO_DB_NAME=libraflow_db
   ```

## Collections

LibraFlow creates these collections automatically on first write (no manual
schema step needed, since MongoEngine defines the schema in `models.py`):

| Collection       | Defined in                     |
|------------------|---------------------------------|
| `books`          | `apps/books/models.py`         |
| `members`        | `apps/members/models.py`       |
| `borrow_records` | `apps/borrow/models.py`        |
| `notifications`  | `apps/borrow/models.py`        |

## Verifying the Connection

```bash
python manage.py shell -c "from apps.books.models import BookDocument; print(BookDocument.objects.count())"
```
