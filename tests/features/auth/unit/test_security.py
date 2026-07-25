from app.features.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)


class TestSecurity:

    def test_hash_password(self):
        password = "StrongPassword123!"

        hashed_password = hash_password(password)

        assert hashed_password != password
        assert hashed_password.startswith("$argon2")

    def test_verify_password_success(self):
        password = "StrongPassword123!"
        hashed_password = hash_password(password)

        assert verify_password(
            password,
            hashed_password,
        ) is True

    def test_verify_password_wrong_password(self):
        password = "StrongPassword123!"
        wrong_password = "WrongPassword123!"

        hashed_password = hash_password(password)

        assert verify_password(
            wrong_password,
            hashed_password,
        ) is False

    def test_verify_password_invalid_hash(self):
        password = "StrongPassword123!"

        assert verify_password(
            password,
            "invalid_hash",
        ) is False

    def test_create_access_token(self):
        user_id = 1

        token = create_access_token(user_id)

        assert isinstance(token, str)
        assert token.count(".") == 2

    def test_decode_access_token_success(self):
        user_id = 123

        token = create_access_token(user_id)

        result = decode_access_token(token)

        assert result == user_id


    def test_decode_access_token_invalid_token(self):
        result = decode_access_token("invalid.token")

        assert result is None

    def test_decode_access_token_wrong_signature(self):
        token = create_access_token(123)

        parts = token.split(".")
        parts[2] = "invalid_signature"

        invalid_token = ".".join(parts)

        result = decode_access_token(invalid_token)

        assert result is None