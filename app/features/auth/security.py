import jwt
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from jwt import InvalidTokenError
from datetime import datetime, timedelta, timezone
from app.core.settings import settings


ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(
    password: str,
    hashed_password: str,
) -> bool:
    try:
        return password_hasher.verify(
            hashed_password,
            password,
        )
    except (VerificationError, InvalidHashError):
        return False


def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)

    expire = now + timedelta(
        minutes=settings.jwt.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    payload = {
        "sub": str(user_id),
        "type": ACCESS_TOKEN_TYPE,
        "iat": now,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.jwt.JWT_SECRET_KEY,
        algorithm=settings.jwt.JWT_ALGORITHM,
    )

def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(
            token,
            settings.jwt.JWT_SECRET_KEY,
            algorithms=[settings.jwt.JWT_ALGORITHM],
        )

        user_id = payload.get("sub")
        token_type = payload.get("type")

        if user_id is None:
            return None

        if token_type != ACCESS_TOKEN_TYPE:
            return None

        return int(user_id)

    except (
        InvalidTokenError,
        ValueError,
        TypeError,
    ):
        return None

def create_email_verification_token() -> str:
    """Generate a secure email verification token."""

    return secrets.token_urlsafe(32)

def create_refresh_token(
    user_id: int,
) -> str:
    now = datetime.now(timezone.utc)

    expire = now + timedelta(
        days=settings.jwt.JWT_REFRESH_TOKEN_EXPIRE_DAYS,
    )

    payload = {
        "sub": str(user_id),
        "type": REFRESH_TOKEN_TYPE,
        "iat": now,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.jwt.JWT_SECRET_KEY,
        algorithm=settings.jwt.JWT_ALGORITHM,
    )

def decode_refresh_token(
    token: str,
) -> int | None:
    try:
        payload = jwt.decode(
            token,
            settings.jwt.JWT_SECRET_KEY,
            algorithms=[settings.jwt.JWT_ALGORITHM],
        )

        user_id = payload.get("sub")
        token_type = payload.get("type")

        if user_id is None:
            return None

        if token_type != REFRESH_TOKEN_TYPE:
            return None

        return int(user_id)

    except (
        InvalidTokenError,
        ValueError,
        TypeError,
    ):
        return None