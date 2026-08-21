from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def test_postgres_connection(db_session: AsyncSession):
    result = await db_session.execute(text("SELECT 1"))

    assert result.scalar() == 1


async def test_postgres_write_and_read(db_session: AsyncSession):
    await db_session.execute(
        text("SELECT 1")
    )

    result = await db_session.execute(
        text("SELECT current_database()")
    )

    assert result.scalar() == "fintex_ai_test"