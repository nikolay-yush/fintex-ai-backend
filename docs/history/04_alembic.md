# 04. Alembic

## Overview

Alembic is used to manage database schema migrations and keep the PostgreSQL schema synchronized with SQLAlchemy models.

### Features

* Database schema versioning
* Automatic migration generation
* Safe upgrades and rollbacks
* Consistent schema across all environments

---

## Installation

# Command                                   |   Description                                      
-----------------------------------------   |   ------------------------------------------------ 
`uv add alembic`                            |   Install Alembic.                                 
`uv run alembic init -t async migrations`   |   Initialize the migration environment (run once). 

---

## Migration Commands

# Command                                                      |   Description                                  
------------------------------------------------------------   |   -------------------------------------------- 
`uv run alembic revision --autogenerate -m "migration_name"`   |   Generate a new migration from model changes. 
`uv run alembic upgrade head`                                  |   Apply all pending migrations.                
`uv run alembic downgrade -1`                                  |   Roll back the last migration.                
`uv run alembic downgrade base`                                |   Roll back all migrations.                    
`uv run alembic current`                                       |   Display the current migration version.       

---

# Project Configuration

The default Alembic configuration was adapted to match the project's asynchronous architecture.

---

## 1. Database URL

### Configuration

```python
config.set_main_option("sqlalchemy.url", settings.db.DB_URL)
```

### Purpose

Uses the application's centralized configuration instead of a hardcoded connection string in `alembic.ini`.

---

## 2. Project Metadata

### Configuration

```python
from app.core.db.postgres.base import Base
import app.core.db.postgres.models

target_metadata = Base.metadata
```

### Purpose

Registers all SQLAlchemy models through a shared metadata object, allowing Alembic to detect schema changes automatically.

---

## 3. Offline Migration Mode

### Function

```python
run_migrations_offline()
```

### Purpose

Generates SQL migration scripts without connecting to the database.

### Configuration

* `url` — database connection string
* `target_metadata` — project metadata
* `literal_binds=True` — embeds values directly into SQL
* `dialect_opts` — database-specific SQL generation options

---

## 4. Online Migration Mode

### Function

```python
run_migrations_online()
```

### Purpose

Main migration entry point.

Creates an asynchronous event loop and starts the migration process using the project configuration.

Used by:

```text
alembic upgrade head
alembic downgrade
alembic revision --autogenerate
```

---

## 5. Async Engine

### Function

```python
run_async_migrations()
```

### Purpose

Creates an `AsyncEngine`, establishes a temporary database connection, and prepares the migration environment.

### Configuration

* Application database URL
* `asyncpg` driver
* `NullPool` connection pool
* Automatic connection cleanup

---

## 6. Migration Context

### Function

```python
do_run_migrations()
```

### Purpose

Configures the migration context and executes all pending operations within a database transaction.

### Configuration

* `connection` — active database connection
* `target_metadata` — project metadata
* `compare_type=True` — detect column type changes

---

## Execution Flow

```text
Alembic CLI
      │
      ▼
run_migrations_online()
      │
      ▼
run_async_migrations()
      │
      ▼
AsyncEngine
      │
      ▼
Database Connection
      │
      ▼
do_run_migrations()
      │
      ▼
Migration Transaction
      │
      ▼
PostgreSQL
```

---

## Result

* Asynchronous migration support
* Automatic model discovery
* Automatic schema comparison
* Transaction-safe migrations
* Shared application configuration
