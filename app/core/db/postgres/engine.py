from sqlalchemy.ext.asyncio import create_async_engine
from app.core.settings import settings


engine = create_async_engine(
    settings.db.DB_URL,
    echo=False,  # True in development
    pool_size=10,  # number of connections in the pool
    max_overflow=20,  # additional connections beyond pool_size
    pool_timeout=30,  # seconds to wait for a connection before raising an error
    pool_recycle=1800,  # recycle connections after 30 minutes
    pool_pre_ping=True,  # check if connections are alive before using them
)
