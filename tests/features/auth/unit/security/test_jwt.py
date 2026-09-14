from datetime import datetime, timedelta, timezone

import jwt

from app.core.settings import settings
from app.features.auth.security import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    create_access_token,
    decode_access_token,
    create_refresh_token,
    decode_refresh_token,
)


class TestAccessToken:

    def test_create_access_token(self):
        token = create_access_token(user_id=1)

        assert token

    def test_decode_access_token(self):
        token = create_access_token(user_id=1)

        user_id = decode_access_token(token)

        assert user_id == 1

    def test_access_token_payload(self):
        token = create_access_token(user_id=1)

        payload = jwt.decode(
            token,
            settings.jwt.JWT_SECRET_KEY,
            algorithms=[settings.jwt.JWT_ALGORITHM],
        )

        assert payload["sub"] == "1"
        assert payload["type"] == ACCESS_TOKEN_TYPE
        assert "iat" in payload
        assert "exp" in payload
        assert "jti" in payload

    def test_invalid_access_token(self):
        assert decode_access_token("invalid-token") is None

    def test_refresh_token_is_not_access_token(self):
        token = create_refresh_token(user_id=1)

        assert decode_access_token(token) is None

    
    def test_expired_access_token(self):
        now = datetime.now(timezone.utc)

        payload = {
            "sub": "1",
            "type": ACCESS_TOKEN_TYPE,
            "iat": now - timedelta(minutes=10),
            "exp": now - timedelta(minutes=5),
            "jti": "test-jti",
        }

        token = jwt.encode(
            payload,
            settings.jwt.JWT_SECRET_KEY,
            algorithm=settings.jwt.JWT_ALGORITHM,
        )

        assert decode_access_token(token) is None

    def test_invalid_access_token_signature(self):
        token = create_access_token(user_id=1)

        payload = jwt.decode(
            token,
            settings.jwt.JWT_SECRET_KEY,
            algorithms=[settings.jwt.JWT_ALGORITHM],
        )

        forged_token = jwt.encode(
            payload,
            "wrong_secret_key_that_is_long_enough_32_bytes",
            algorithm=settings.jwt.JWT_ALGORITHM,
        )

        assert decode_access_token(forged_token) is None

    def test_access_token_with_wrong_type(self):
        now = datetime.now(timezone.utc)

        payload = {
            "sub": "1",
            "type": REFRESH_TOKEN_TYPE,
            "iat": now,
            "exp": now + timedelta(minutes=30),
            "jti": "test-jti",
        }

        token = jwt.encode(
            payload,
            settings.jwt.JWT_SECRET_KEY,
            algorithm=settings.jwt.JWT_ALGORITHM,
        )

        assert decode_access_token(token) is None

    def test_access_token_without_sub(self):
        now = datetime.now(timezone.utc)

        payload = {
            "type": ACCESS_TOKEN_TYPE,
            "iat": now,
            "exp": now + timedelta(minutes=30),
            "jti": "test-jti",
        }

        token = jwt.encode(
            payload,
            settings.jwt.JWT_SECRET_KEY,
            algorithm=settings.jwt.JWT_ALGORITHM,
        )

        assert decode_access_token(token) is None


class TestRefreshToken:

    def test_create_refresh_token(self):
        token = create_refresh_token(user_id=1)

        assert token

    def test_decode_refresh_token(self):
        token = create_refresh_token(user_id=1)

        user_id = decode_refresh_token(token)

        assert user_id == 1

    def test_refresh_token_payload(self):
        token = create_refresh_token(user_id=1)

        payload = jwt.decode(
            token,
            settings.jwt.JWT_SECRET_KEY,
            algorithms=[settings.jwt.JWT_ALGORITHM],
        )

        assert payload["sub"] == "1"
        assert payload["type"] == REFRESH_TOKEN_TYPE
        assert "iat" in payload
        assert "exp" in payload
        assert "jti" in payload

    def test_invalid_refresh_token(self):
        assert decode_refresh_token("invalid-token") is None

    def test_access_token_is_not_refresh_token(self):
        token = create_access_token(user_id=1)

        assert decode_refresh_token(token) is None

    def test_expired_refresh_token(self):
        now = datetime.now(timezone.utc)

        payload = {
            "sub": "1",
            "type": REFRESH_TOKEN_TYPE,
            "iat": now - timedelta(days=2),
            "exp": now - timedelta(days=1),
            "jti": "test-jti",
        }

        token = jwt.encode(
            payload,
            settings.jwt.JWT_SECRET_KEY,
            algorithm=settings.jwt.JWT_ALGORITHM,
        )

        assert decode_refresh_token(token) is None

    def test_invalid_refresh_token_signature(self):
        token = create_refresh_token(user_id=1)

        payload = jwt.decode(
            token,
            settings.jwt.JWT_SECRET_KEY,
            algorithms=[settings.jwt.JWT_ALGORITHM],
        )

        forged_token = jwt.encode(
            payload,
            "wrong_secret_key_that_is_long_enough_32_bytes",
            algorithm=settings.jwt.JWT_ALGORITHM,
        )

        assert decode_refresh_token(forged_token) is None

    def test_refresh_token_with_wrong_type(self):
        now = datetime.now(timezone.utc)

        payload = {
            "sub": "1",
            "type": ACCESS_TOKEN_TYPE,
            "iat": now,
            "exp": now + timedelta(days=30),
            "jti": "test-jti",
        }

        token = jwt.encode(
            payload,
            settings.jwt.JWT_SECRET_KEY,
            algorithm=settings.jwt.JWT_ALGORITHM,
        )

        assert decode_refresh_token(token) is None

    def test_refresh_token_without_sub(self):
        now = datetime.now(timezone.utc)

        payload = {
            "type": REFRESH_TOKEN_TYPE,
            "iat": now,
            "exp": now + timedelta(days=30),
            "jti": "test-jti",
        }

        token = jwt.encode(
            payload,
            settings.jwt.JWT_SECRET_KEY,
            algorithm=settings.jwt.JWT_ALGORITHM,
        )

        assert decode_refresh_token(token) is None