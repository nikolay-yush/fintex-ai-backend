from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.postgres.engine import engine


# Path to the Alembic configuration file.
ROOT_DIR = Path(__file__).resolve().parents[2]
ALEMBIC_INI = ROOT_DIR / "alembic.ini"


@pytest.fixture(scope="session", autouse=True)
def apply_migrations() -> Generator[None, None, None]:
    """Apply all database migrations before running the test suite."""

    config = Config(str(ALEMBIC_INI))
    command.upgrade(config, "head")

    yield


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an isolated database session for each test."""

    connection = await engine.connect()

    transaction = await connection.begin()

    session = AsyncSession(
        bind=connection,
        expire_on_commit=False,
    )

    await session.begin_nested()

    @event.listens_for(session.sync_session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        """Automatically recreate the savepoint after each commit."""
        if transaction.nested and not transaction.parent.nested:
            session.begin_nested()

    try:
        yield session

    finally:
        event.remove(
            session.sync_session,
            "after_transaction_end",
            restart_savepoint,
        )

        if transaction.is_active:
            await transaction.rollback()

        await session.close()

        await connection.close()