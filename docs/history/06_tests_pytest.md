# Pytest

# Ibstallation
uv add --dev pytest
uv add --dev pytest-asyncio
uv add --dev httpx
uv add --dev pytest-cov


# Transactional Test Session

## Goal

Create an isolated SQLAlchemy session for each test and automatically rollback all changes after the test finishes.

---

## Why

Without transactions:

- Tests affect each other.
- Data remains in the database.
- Tests become order-dependent.

With transactions:

- Every test starts with a clean database.
- All changes are rolled back automatically.
- Tests are isolated and repeatable.

---

## SQLAlchemy Architecture

```text
Engine
    │
    ▼
Connection
    │
    ▼
Transaction
    │
    ▼
Session
```

### Components

- **Engine** — manages the connection pool.
- **Connection** — physical connection to PostgreSQL.
- **Transaction** — groups SQL operations into a single unit.
- **Session** — ORM interface working through a Connection.

---

## Transaction Lifecycle

```text
BEGIN

INSERT
UPDATE
DELETE

COMMIT
```

or

```text
BEGIN

INSERT
UPDATE
DELETE

ROLLBACK
```

- `COMMIT` saves all changes.
- `ROLLBACK` discards all changes.

---

## Testing Strategy

Instead of creating a Session directly:

```python
async_session_local()
```

Create resources manually:

```python
connection = await engine.connect()

transaction = await connection.begin()

session = AsyncSession(bind=connection)
```

This allows the test to fully control the transaction lifecycle.

---

## Fixture Lifecycle

```text
Setup
    │
    ▼
Create Connection
    │
    ▼
Begin Transaction
    │
    ▼
Create Session
    │
    ▼
yield session
    │
    ▼
Run Test
    │
    ▼
Close Session
    │
    ▼
Rollback Transaction
    │
    ▼
Close Connection
```

---

## Key Takeaways

- Engine creates Connections.
- Session works through a Connection.
- Transactions isolate database changes.
- Tests should own the Connection.
- Always rollback after every test.