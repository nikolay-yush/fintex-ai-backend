# Alembic in Tests

## Goal

Ensure the test database schema is created using Alembic migrations instead of SQLAlchemy models.

---

## Why not use `create_all()`?

`Base.metadata.create_all()` builds the schema directly from ORM models.

It does **not** verify that Alembic migrations are valid.

As a result, tests may pass while production migrations fail.

---

## Recommended Approach

Before running tests:

```text
Alembic upgrade head

↓

Test Database

↓

Run Tests
```

---

## Benefits

- Tests use the same schema as production.
- Migration errors are detected early.
- Prevents model/schema drift.

---

## Best Practice

- Apply migrations **once per test session**.
- Isolate individual tests using transactions and rollback.
- Do not recreate the schema before every test.