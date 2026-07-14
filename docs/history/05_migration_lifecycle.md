# Migration Lifecycle

## Initial Project Setup (One Time)

```bash
uv add alembic

uv run alembic init -t async migrations
```

---

## Daily Development Workflow

### 1. Modify SQLAlchemy models

```text
User
Wallet
Category
Transaction
...
```

↓

### 2. Generate a migration

```bash
uv run alembic revision --autogenerate -m "add wallets table"
```

↓

### 3. Review the generated migration

Check:

- Table names
- Column types
- Constraints
- Indexes
- Foreign keys

↓

### 4. Apply migration

```bash
uv run alembic upgrade head
```

↓

### 5. Verify the application

- Run the project
- Run tests
- Check database schema

↓

### 6. Commit changes

Commit:

- SQLAlchemy models
- Alembic migration
- Related code

---

## Production Deployment

```text
Deploy New Version

↓

Update Source Code

↓

Install Dependencies

↓

Run Alembic

↓

Start / Restart Application
```

Example:

```bash
git pull

uv sync

uv run alembic upgrade head

systemctl restart fintexai
```

---

## Test Environment

```text
Create Test Database

↓

alembic upgrade head

↓

Run Tests

↓

Rollback Between Tests
```