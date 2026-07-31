import os

from app.core.settings import settings


def validate_test_env() -> None:
    """Ensure tests are running only against the test environment."""

    if os.getenv("ENV_STATE") != "test":
        raise RuntimeError(
            "ENV_STATE must be 'test' before running tests."
        )

    if not settings.db.DB_NAME.endswith("_test"):
        raise RuntimeError(
            f"Unsafe database '{settings.db.DB_NAME}'. "
            "Tests may run only on *_test databases."
        )
