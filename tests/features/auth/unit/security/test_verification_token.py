from app.features.auth.security import hash_password, verify_password


class TestPasswordVerification:
    """Tests for password verification."""
    def test_verify_correct_password(self):
        """Check if password verification works."""
        password = "Password123"
        password_hash = hash_password(password)

        assert verify_password(password, password_hash)

    def test_verify_wrong_password(self):
        """Check if wrong password verification works."""
        password = "Password123"
        wrong_password = "WrongPassword123"
        password_hash = hash_password(password)

        assert not verify_password(wrong_password, password_hash)