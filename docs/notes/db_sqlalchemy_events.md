# SQLAlchemy Events

## Goal

Understand how SQLAlchemy events work and why they are used in testing.

---

## What is an Event?

An Event is a notification emitted by SQLAlchemy when a specific action occurs.

Example events:

- Connection opened
- Transaction started
- Transaction ended
- Commit
- Rollback
- Flush

---

## Listening for Events

Use the `event.listens_for()` decorator.

```python
@event.listens_for(target, "event_name")
```

This registers a callback that is executed whenever the specified event occurs.

---

## Event Used in Testing

```python
after_transaction_end
```

Triggered every time a transaction finishes.

---

## Why is it used?

After a `SAVEPOINT` is committed, it no longer exists.

To continue supporting `session.commit()` inside tests, SQLAlchemy automatically creates a new `SAVEPOINT`.

Flow:

```text
commit()

↓

SAVEPOINT ends

↓

after_transaction_end

↓

begin_nested()

↓

New SAVEPOINT
```

---

## Key Takeaways

- SQLAlchemy emits events during ORM operations.
- `event.listens_for()` subscribes to those events.
- `after_transaction_end` is commonly used in test fixtures.
- It allows automatic recreation of `SAVEPOINT`s after each `commit()`.