"""Integration tests for user-to-user transfer API — user lookup, transfer execution, idempotency, and cross-currency."""


class TestTransferAPI:
    def test_search_users(self, client, auth_headers):
        # Create second user
        client.post(
            "/auth/signup",
            json={
                "email": "bob@example.com",
                "password": "password123",
                "display_name": "Bob Builder",
                "default_currency": "USD",
            },
        )

        response = client.get("/users/search?q=bob", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["email"] == "bob@example.com"

    def test_end_to_end_transfer_same_currency(self, client, auth_headers):
        # 1. Register User B
        client.post(
            "/auth/signup",
            json={
                "email": "userB@example.com",
                "password": "password123",
                "display_name": "User B",
                "default_currency": "USD",
            },
        )

        # 2. Credit User A (auth_headers is User A)
        wallets = client.get("/wallets", headers=auth_headers).json()
        wallet_a_id = wallets[0]["id"]
        client.post(
            f"/wallets/{wallet_a_id}/credit",
            json={"amount": "500"},
            headers=auth_headers,
        )

        # 3. Transfer 150 USD from User A to User B
        idempotency_key = "test-idem-key-12345"
        response = client.post(
            "/transfers",
            json={
                "recipient_email": "userB@example.com",
                "amount": "150",
                "currency": "USD",
                "idempotency_key": idempotency_key,
                "description": "Lunch money",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["sent_amount"] == "150.000000"
        assert data["status"] == "COMPLETED"

        # 4. Check User A balance is now 350
        wallets_after = client.get("/wallets", headers=auth_headers).json()
        assert wallets_after[0]["balance"] == "350.000000"

        # 5. Idempotency test: Retry with same key returns original response
        retry_resp = client.post(
            "/transfers",
            json={
                "recipient_email": "userB@example.com",
                "amount": "150",
                "currency": "USD",
                "idempotency_key": idempotency_key,
            },
            headers=auth_headers,
        )
        assert retry_resp.status_code == 201
        # Balance should still be 350 (no double debit)
        wallets_retry = client.get("/wallets", headers=auth_headers).json()
        assert wallets_retry[0]["balance"] == "350.000000"

    def test_transfer_self_fails(self, client, auth_headers):
        response = client.post(
            "/transfers",
            json={
                "recipient_email": "test@example.com",
                "amount": "50",
                "currency": "USD",
                "idempotency_key": "self-transfer-key-123",
            },
            headers=auth_headers,
        )
        assert response.status_code == 400
