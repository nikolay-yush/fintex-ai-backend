# 03. SQLAlchemy

## Overview

The project uses **SQLAlchemy 2.x** with **AsyncIO** as the ORM layer.

---

## Why SQLAlchemy

* Mature and stable ORM
* Modern 2.x API
* Native async support
* Excellent PostgreSQL integration
* Strong typing support

---

# Install
uv add sqlalchemy
uv add asyncpg

## Components

* SQLAlchemy ORM
* Async Engine
* Async Session
* Declarative Base
* AsyncPG driver

---

## DB Components

```text
core/db/postgres
|-- base.py
|-- session.py
|-- engine.py
|-- models.py
```

Models are organized inside feature modules and registered for Alembic migrations.

---

## Architecture

Database access follows the Repository pattern.

```text
Router
   │
Service
   │
Repository
   │
SQLAlchemy
   │
PostgreSQL
```

Services do not communicate with the database directly.

---

## Conventions

* One `AsyncSession` per request.
* Models inherit from a shared `Base`.
* Database logic belongs to repositories.
* Business logic belongs to services.

---
