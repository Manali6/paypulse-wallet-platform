"""Unit tests for auth_service — password hashing and JWT token management."""

from app.services.auth_service import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_access_token,
    verify_password,
    verify_refresh_token,
)


class TestPasswordHashing:
    """Tests for Argon2 password hashing."""

    def test_hash_password_returns_hash(self):
        hashed = hash_password("secure_password_123")
        assert hashed != "secure_password_123"
        assert hashed.startswith("$argon2")

    def test_verify_correct_password(self):
        hashed = hash_password("my_password")
        assert verify_password("my_password", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("my_password")
        assert verify_password("wrong_password", hashed) is False

    def test_different_hashes_for_same_password(self):
        hash1 = hash_password("same_password")
        hash2 = hash_password("same_password")
        # Argon2 uses random salt, so hashes should differ
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password("same_password", hash1) is True
        assert verify_password("same_password", hash2) is True


class TestJWTTokens:
    """Tests for JWT access and refresh token creation/verification."""

    def test_create_and_verify_access_token(self):
        user_id = "test-user-123"
        token = create_access_token(user_id)
        assert token is not None
        assert isinstance(token, str)

        verified_id = verify_access_token(token)
        assert verified_id == user_id

    def test_create_and_verify_refresh_token(self):
        user_id = "test-user-456"
        token = create_refresh_token(user_id)
        assert token is not None

        verified_id = verify_refresh_token(token)
        assert verified_id == user_id

    def test_access_token_cannot_be_used_as_refresh(self):
        token = create_access_token("user-1")
        result = verify_refresh_token(token)
        assert result is None

    def test_refresh_token_cannot_be_used_as_access(self):
        token = create_refresh_token("user-1")
        result = verify_access_token(token)
        assert result is None

    def test_invalid_token_returns_none(self):
        result = verify_access_token("totally.invalid.token")
        assert result is None

    def test_empty_token_returns_none(self):
        result = verify_access_token("")
        assert result is None

    def test_tampered_token_returns_none(self):
        token = create_access_token("user-1")
        # Tamper with the token by modifying a character
        tampered = token[:-5] + "XXXXX"
        result = verify_access_token(tampered)
        assert result is None
