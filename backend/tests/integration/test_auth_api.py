"""Integration tests for the auth API — signup, login, refresh, and profile."""


class TestSignup:
    def test_signup_success(self, client):
        response = client.post(
            "/auth/signup",
            json={
                "email": "new@example.com",
                "password": "password123",
                "display_name": "New User",
                "default_currency": "USD",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_signup_duplicate_email(self, client, auth_headers):
        # auth_headers fixture already creates test@example.com
        response = client.post(
            "/auth/signup",
            json={
                "email": "test@example.com",
                "password": "password123",
                "display_name": "Duplicate",
                "default_currency": "USD",
            },
        )
        assert response.status_code == 409

    def test_signup_invalid_currency(self, client):
        response = client.post(
            "/auth/signup",
            json={
                "email": "bad@example.com",
                "password": "password123",
                "display_name": "Bad Currency",
                "default_currency": "XYZ",
            },
        )
        assert response.status_code == 400

    def test_signup_short_password(self, client):
        response = client.post(
            "/auth/signup",
            json={
                "email": "short@example.com",
                "password": "short",
                "display_name": "Short Pass",
                "default_currency": "USD",
            },
        )
        assert response.status_code == 422  # Pydantic validation error


class TestLogin:
    def test_login_success(self, client, auth_headers):
        response = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "securepassword123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_wrong_password(self, client, auth_headers):
        response = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_email(self, client):
        response = client.post(
            "/auth/login",
            json={"email": "nobody@example.com", "password": "password123"},
        )
        assert response.status_code == 401


class TestRefresh:
    def test_refresh_success(self, client):
        # First signup to get tokens
        signup_resp = client.post(
            "/auth/signup",
            json={
                "email": "refresh@example.com",
                "password": "password123",
                "display_name": "Refresh User",
                "default_currency": "USD",
            },
        )
        refresh_token = signup_resp.json()["refresh_token"]

        # Use refresh token
        response = client.post(
            "/auth/refresh", json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_invalid_token(self, client):
        response = client.post(
            "/auth/refresh", json={"refresh_token": "invalid.token.here"}
        )
        assert response.status_code == 401


class TestGetProfile:
    def test_get_profile_success(self, client, auth_headers):
        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["display_name"] == "Test User"
        assert data["default_currency"] == "USD"

    def test_get_profile_no_auth(self, client):
        response = client.get("/auth/me")
        assert response.status_code == 403  # No Bearer token
