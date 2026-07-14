# Savepoints (Nested Transactions)

## Goal

Understand what a Savepoint is, why it is needed, and how it is used in SQLAlchemy tests.

---

## What is a Savepoint?

A **Savepoint** is a checkpoint inside an existing transaction.

It allows rolling back only part of the transaction without canceling the entire transaction.

---

## Transaction Structure

```text
BEGIN (Outer Transaction)
│
├── SQL
│
├── SAVEPOINT
│      │
│      ├── SQL
│      ├── SQL
│      └── SQL
│
└── COMMIT / ROLLBACK
```

The Savepoint is **not** a separate transaction.

It is a nested checkpoint inside the current transaction.

---

## Why use Savepoints?

Without a Savepoint:

```text
BEGIN

INSERT User
INSERT Wallet
ERROR

ROLLBACK
```

Result:

```text
✖ User
✖ Wallet
```

Everything is lost.

---

With a Savepoint:

```text
BEGIN

INSERT User

SAVEPOINT

INSERT Wallet

ERROR

ROLLBACK TO SAVEPOINT

COMMIT
```

Result:

```text
✔ User
✖ Wallet
```

Only the operations after the Savepoint are reverted.

---

## SQLAlchemy

Create a nested transaction:

```python
await session.begin_nested()
```

or

```python
await connection.begin_nested()
```

SQLAlchemy executes:

```sql
SAVEPOINT;
```

---

## Savepoints in Testing

Typical test transaction hierarchy:

```text
Engine
    │
    ▼
Connection
    │
    ▼
Outer Transaction
    │
    ▼
SAVEPOINT
    │
    ▼
Session
```

The Session works inside the Savepoint.

After the test:

```python
await transaction.rollback()
```

The outer transaction is rolled back, removing every database change made during the test.

---

## Why use Savepoints in tests?

Some application code performs:

```python
await session.commit()
```

Without a Savepoint:

- The transaction is committed.
- Test data remains in the database.
- Tests affect each other.

With a Savepoint:

- `session.commit()` releases the current Savepoint.
- The outer transaction remains active.
- After the test, a single `ROLLBACK` removes all changes.

---

## When to use Savepoints?

Use Savepoints when:

- Testing application code that calls `session.commit()`.
- Partially rolling back complex business operations.
- Creating nested transactions.
- Building reliable integration tests.

---

## Key Takeaways

- A Savepoint is a nested checkpoint inside a transaction.
- It allows partial rollback without canceling the outer transaction.
- SQLAlchemy creates Savepoints using `begin_nested()`.
- Production test suites commonly use:
  - one outer transaction;
  - one Savepoint per test;
  - rollback of the outer transaction after the test.