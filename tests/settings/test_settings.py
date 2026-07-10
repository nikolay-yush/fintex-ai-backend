import os

from app.core.conf import settings


def test_env_loaded():
    print()
    print("ENV_STATE =", os.getenv("ENV_STATE"))
    print("DB_NAME =", settings.db.DB_NAME)