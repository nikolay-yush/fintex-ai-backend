from app.features.auth.security import hash_password, verify_password


class TestPassword:
    """Tests for password hashing and verification."""

    def test_password_hash(self):
        """Check if password hash is generated."""

        password = "Password123"

        password_hash = hash_password(password)

        assert password_hash
        assert password_hash != password
        assert password_hash.startswith("$argon2")

    def test_hash_password_produces_different_hashes(self):
        """Same password gets different hashes because of unique salt."""

        password = "Password123"

        hash_1 = hash_password(password)
        hash_2 = hash_password(password)

        assert hash_1 != hash_2

