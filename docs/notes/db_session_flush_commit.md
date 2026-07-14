# Session, Flush and Commit

## Goal

Understand how SQLAlchemy synchronizes ORM objects with the database and how transactions work.

---

## Object Lifecycle

```text
Python Object
      │
      ▼
session.add()
      │
      ▼
Session (NEW)
      │
      ▼
flush()
      │
      ▼
Transaction
      │
      ▼
commit()
      │
      ▼
Database
```

---

## session.add()

Registers the object inside the SQLAlchemy Session.

- No SQL is executed.
- The object exists only in memory.
- The database is unchanged.

Example:

```python
user = User(...)
session.add(user)
```

---

## session.flush()

Synchronizes the Session with the database.

- Executes SQL (`INSERT`, `UPDATE`, `DELETE`).
- Retrieves generated values (e.g., `id`).
- Changes remain inside the current transaction.
- Does **not** permanently save data.

Example:

```python
session.add(user)
await session.flush()

print(user.id)
```

---

## session.commit()

Finalizes the current transaction.

- Automatically performs `flush()`.
- Executes `COMMIT`.
- Makes all changes permanent.
- Changes become visible to other database connections.

Example:

```python
await session.commit()
```

---

## session.rollback()

Cancels the current transaction.

- Undoes all changes made during the transaction.
- Removes all `INSERT`, `UPDATE` and `DELETE` operations.
- Returns the database to its previous state.

Example:

```python
await session.rollback()
```

---

## Difference

| Method | Executes SQL | Saves Changes |
|---------|--------------|---------------|
| `add()` | ❌ No | ❌ No |
| `flush()` | ✅ Yes | ❌ No |
| `commit()` | ✅ Yes | ✅ Yes |
| `rollback()` | ❌ No | Cancels transaction |

---

## Why use flush()?

Typical use case:

```python
user = User(...)

session.add(user)

await session.flush()

wallet = Wallet(user_id=user.id)
```

Without `flush()`, `user.id` is not yet available.

---

## Key Takeaways

- `Session` stores ORM changes.
- `flush()` synchronizes changes with PostgreSQL.
- `commit()` permanently saves the transaction.
- `rollback()` discards the transaction.
- `commit()` automatically performs `flush()`.