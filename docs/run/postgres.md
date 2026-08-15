# Connect to Postgres
sudo docker exec -it fintex_ai_db psql -U <USER> -d <DB NAME>

# PostgreSQL CLI — Quick Reference

## Connection

| Command | Purpose |
|---|---|
| `psql` | Connect using default settings |
| `psql -U <user> -d <database>` | Connect as user to database |
| `psql -h <host> -p <port> -U <user> -d <database>` | Connect using host, port, user, and database |
| `psql "<connection_string>"` | Connect using PostgreSQL connection string |
| `\q` | Exit `psql` |

### Examples

```bash
psql -U postgres -d fintex_ai

psql -h localhost -p 5432 -U postgres -d fintex_ai
```

Docker:

```bash
docker exec -it <container> psql -U postgres -d fintex_ai
```

---

# Database

| Command | Purpose |
|---|---|
| `\l` | List databases |
| `\c <database>` | Connect to database |
| `\conninfo` | Show current connection |
| `CREATE DATABASE <name>;` | Create database |
| `DROP DATABASE <name>;` | Delete database |

### Examples

```sql
\l

\c fintex_ai

\conninfo
```

> `DROP DATABASE` permanently deletes the database. Use carefully.

---

# Schemas

| Command | Purpose |
|---|---|
| `\dn` | List schemas |
| `CREATE SCHEMA <name>;` | Create schema |
| `DROP SCHEMA <name>;` | Delete schema |

### Example

```sql
CREATE SCHEMA billing;
```

---

# Tables

| Command | Purpose |
|---|---|
| `\dt` | List tables |
| `\dt *.*` | List tables in all schemas |
| `\d <table>` | Describe table |
| `\d+ <table>` | Detailed table information |
| `CREATE TABLE` | Create table |
| `DROP TABLE` | Delete table |
| `TRUNCATE TABLE` | Delete all rows |

### Examples

```sql
\dt

\d users

\d+ users
```

Create table:

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

---

# INSERT

Insert a row:

```sql
INSERT INTO users (
    email,
    full_name
)
VALUES (
    'alex@example.com',
    'Alex'
);
```

Insert and return created row:

```sql
INSERT INTO users (
    email,
    full_name
)
VALUES (
    'alex@example.com',
    'Alex'
)
RETURNING *;
```

Insert specific fields:

```sql
INSERT INTO users (email)
VALUES ('alex@example.com');
```

---

# SELECT

Get all rows:

```sql
SELECT *
FROM users;
```

Select specific columns:

```sql
SELECT
    id,
    email,
    full_name
FROM users;
```

Get one row:

```sql
SELECT *
FROM users
WHERE id = 1;
```

Limit results:

```sql
SELECT *
FROM users
LIMIT 10;
```

---

# WHERE

| Operator | Purpose |
|---|---|
| `=` | Equal |
| `!=` / `<>` | Not equal |
| `>` | Greater than |
| `<` | Less than |
| `>=` | Greater or equal |
| `<=` | Less or equal |
| `IN` | Match multiple values |
| `BETWEEN` | Range |
| `LIKE` | Pattern matching |
| `ILIKE` | Case-insensitive pattern |
| `IS NULL` | Check NULL |
| `IS NOT NULL` | Check not NULL |

### Examples

```sql
SELECT *
FROM users
WHERE id = 10;
```

```sql
SELECT *
FROM users
WHERE id IN (1, 2, 3);
```

```sql
SELECT *
FROM users
WHERE created_at BETWEEN '2026-01-01' AND '2026-12-31';
```

```sql
SELECT *
FROM users
WHERE email ILIKE '%gmail.com';
```

```sql
SELECT *
FROM users
WHERE full_name IS NOT NULL;
```

---

# AND / OR / NOT

```sql
SELECT *
FROM users
WHERE is_active = TRUE
  AND is_banned = FALSE;
```

```sql
SELECT *
FROM users
WHERE role = 'admin'
   OR role = 'moderator';
```

```sql
SELECT *
FROM users
WHERE NOT is_banned;
```

Use parentheses when combining conditions:

```sql
SELECT *
FROM users
WHERE is_active = TRUE
  AND (
      role = 'admin'
      OR role = 'moderator'
  );
```

---

# ORDER BY

Ascending:

```sql
SELECT *
FROM users
ORDER BY created_at ASC;
```

Descending:

```sql
SELECT *
FROM users
ORDER BY created_at DESC;
```

Multiple fields:

```sql
SELECT *
FROM users
ORDER BY is_active DESC, created_at DESC;
```

---

# Pagination

Offset pagination:

```sql
SELECT *
FROM users
ORDER BY id
LIMIT 20
OFFSET 40;
```

Concept:

```text
LIMIT  → number of rows
OFFSET → number of rows to skip
```

For large datasets, cursor/keyset pagination is usually preferable:

```sql
SELECT *
FROM users
WHERE id > 1000
ORDER BY id
LIMIT 20;
```

---

# UPDATE

Update one row:

```sql
UPDATE users
SET full_name = 'Alex Smith'
WHERE id = 1;
```

Update multiple fields:

```sql
UPDATE users
SET
    full_name = 'Alex Smith',
    is_active = TRUE
WHERE id = 1;
```

Return updated row:

```sql
UPDATE users
SET full_name = 'Alex Smith'
WHERE id = 1
RETURNING *;
```

> Always verify the `WHERE` condition before running `UPDATE`.

---

# DELETE

Delete one row:

```sql
DELETE FROM users
WHERE id = 1;
```

Return deleted row:

```sql
DELETE FROM users
WHERE id = 1
RETURNING *;
```

> `DELETE` without `WHERE` deletes every row.

---

# COUNT / Aggregation

Count rows:

```sql
SELECT COUNT(*)
FROM users;
```

Count active users:

```sql
SELECT COUNT(*)
FROM users
WHERE is_active = TRUE;
```

Group by:

```sql
SELECT
    role,
    COUNT(*)
FROM users
GROUP BY role;
```

Filter groups:

```sql
SELECT
    role,
    COUNT(*)
FROM users
GROUP BY role
HAVING COUNT(*) > 10;
```

Common aggregate functions:

```text
COUNT()
SUM()
AVG()
MIN()
MAX()
```

---

# DISTINCT

Get unique values:

```sql
SELECT DISTINCT role
FROM users;
```

Multiple columns:

```sql
SELECT DISTINCT role, is_active
FROM users;
```

---

# JOIN

## INNER JOIN

Return matching rows:

```sql
SELECT
    users.id,
    users.email,
    wallets.name
FROM users
INNER JOIN wallets
    ON wallets.user_id = users.id;
```

## LEFT JOIN

Return all users even without wallets:

```sql
SELECT
    users.id,
    users.email,
    wallets.name
FROM users
LEFT JOIN wallets
    ON wallets.user_id = users.id;
```

Common joins:

```text
INNER JOIN
LEFT JOIN
RIGHT JOIN
FULL JOIN
CROSS JOIN
```

---

# Subqueries

Example:

```sql
SELECT *
FROM users
WHERE id IN (
    SELECT user_id
    FROM wallets
    WHERE balance > 1000
);
```

---

# Common Table Expressions

```sql
WITH active_users AS (
    SELECT *
    FROM users
    WHERE is_active = TRUE
)
SELECT *
FROM active_users
WHERE role = 'admin';
```

---

# Transactions

Start transaction:

```sql
BEGIN;
```

Commit:

```sql
COMMIT;
```

Rollback:

```sql
ROLLBACK;
```

Example:

```sql
BEGIN;

UPDATE wallets
SET balance = balance - 100
WHERE id = 1;

UPDATE wallets
SET balance = balance + 100
WHERE id = 2;

COMMIT;
```

If something goes wrong:

```sql
ROLLBACK;
```

---

# Row Locking

Lock selected rows:

```sql
SELECT *
FROM wallets
WHERE id = 1
FOR UPDATE;
```

Common locking modes:

```sql
FOR UPDATE
FOR NO KEY UPDATE
FOR SHARE
FOR KEY SHARE
```

`FOR UPDATE` is commonly used when a transaction must safely modify a selected row.

---

# Constraints

Common constraints:

```sql
PRIMARY KEY
FOREIGN KEY
UNIQUE
NOT NULL
CHECK
DEFAULT
```

Example:

```sql
CREATE TABLE wallets (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL,

    name VARCHAR(100) NOT NULL,

    balance NUMERIC(20, 2) NOT NULL DEFAULT 0,

    CONSTRAINT fk_wallet_user
        FOREIGN KEY (user_id)
        REFERENCES users(id),

    CONSTRAINT positive_balance
        CHECK (balance >= 0)
);
```

---

# Indexes

Create index:

```sql
CREATE INDEX idx_users_email
ON users(email);
```

Unique index:

```sql
CREATE UNIQUE INDEX idx_users_email_unique
ON users(email);
```

Composite index:

```sql
CREATE INDEX idx_users_status_created
ON users(is_active, created_at);
```

List indexes:

```sql
\di
```

Drop index:

```sql
DROP INDEX idx_users_email;
```

---

# EXPLAIN

Show query execution plan:

```sql
EXPLAIN
SELECT *
FROM users
WHERE email = 'alex@example.com';
```

Show actual execution statistics:

```sql
EXPLAIN ANALYZE
SELECT *
FROM users
WHERE email = 'alex@example.com';
```

For detailed analysis:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM users
WHERE email = 'alex@example.com';
```

> `EXPLAIN ANALYZE` actually executes the query. Be careful with `UPDATE`, `DELETE`, and other modifying statements.

---

# Users & Roles

List roles:

```sql
\du
```

Create user:

```sql
CREATE USER app_user
WITH PASSWORD 'password';
```

Create role:

```sql
CREATE ROLE app_user
LOGIN
PASSWORD 'password';
```

Grant database access:

```sql
GRANT CONNECT
ON DATABASE fintex_ai
TO app_user;
```

Grant schema access:

```sql
GRANT USAGE
ON SCHEMA public
TO app_user;
```

Grant table permissions:

```sql
GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA public
TO app_user;
```

> Do not use the PostgreSQL superuser for the application in production.

---

# Current Connection

Show connection:

```sql
\conninfo
```

Current database:

```sql
SELECT current_database();
```

Current user:

```sql
SELECT current_user;
```

Server version:

```sql
SELECT version();
```

---

# Useful psql Commands

| Command | Purpose |
|---|---|
| `\l` | List databases |
| `\c <db>` | Connect to database |
| `\conninfo` | Current connection |
| `\dt` | List tables |
| `\d <table>` | Describe table |
| `\d+ <table>` | Detailed table information |
| `\di` | List indexes |
| `\dn` | List schemas |
| `\du` | List roles/users |
| `\df` | List functions |
| `\dv` | List views |
| `\q` | Exit `psql` |
| `\?` | psql commands help |
| `\h <SQL>` | SQL command help |

Example:

```sql
\h SELECT
```

---

# Docker

Connect to PostgreSQL container:

```bash
docker exec -it <container> psql \
    -U <user> \
    -d <database>
```

Example:

```bash
docker exec -it postgres \
    psql -U postgres -d fintex_ai
```

Check PostgreSQL:

```bash
docker exec postgres \
    pg_isready -U postgres
```

---

# Backup & Restore

Create database dump:

```bash
pg_dump \
    -U postgres \
    -d fintex_ai \
    > backup.sql
```

Restore:

```bash
psql \
    -U postgres \
    -d fintex_ai \
    < backup.sql
```

Docker:

```bash
docker exec postgres \
    pg_dump -U postgres -d fintex_ai \
    > backup.sql
```

---

# Dangerous Commands

| Command | Risk |
|---|---|
| `DROP DATABASE` | Deletes entire database |
| `DROP TABLE` | Deletes table and its data |
| `TRUNCATE` | Deletes all rows |
| `DELETE FROM table` | Deletes all rows if no `WHERE` |
| `UPDATE table SET ...` | Updates all rows if no `WHERE` |
| `DROP SCHEMA ... CASCADE` | Can delete dependent objects |

Always check the target before destructive operations:

```sql
SELECT *
FROM users
WHERE id = 100;
```

Then perform the operation:

```sql
DELETE FROM users
WHERE id = 100;
```

---

# Most Used Commands

### Connect

```bash
psql -U postgres -d fintex_ai
```

### Inspect

```sql
\dt
\d users
\conninfo
```

### Read

```sql
SELECT *
FROM users
LIMIT 20;
```

### Filter

```sql
SELECT *
FROM users
WHERE is_active = TRUE;
```

### Insert

```sql
INSERT INTO users (email, full_name)
VALUES ('alex@example.com', 'Alex')
RETURNING *;
```

### Update

```sql
UPDATE users
SET full_name = 'Alex Smith'
WHERE id = 1
RETURNING *;
```

### Delete

```sql
DELETE FROM users
WHERE id = 1
RETURNING *;
```

### Transaction

```sql
BEGIN;

-- operations

COMMIT;
```

Rollback:

```sql
ROLLBACK;
```

### Analyze

```sql
EXPLAIN ANALYZE
SELECT *
FROM users
WHERE email = 'alex@example.com';
```