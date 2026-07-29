"""Integration tests for the wallet API — create, list, credit, debit, and transactions."""


class TestWalletCreate:
    def test_create_wallet_success(self, client, auth_headers):
        response = client.post(
            "/wallets", json={"currency": "EUR"}, headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["currency"] == "EUR"
        assert data["balance"] == "0.000000"
        assert data["is_active"] is True

    def test_create_duplicate_wallet(self, client, auth_headers):
        # Default USD wallet was created on signup
        response = client.post(
            "/wallets", json={"currency": "USD"}, headers=auth_headers
        )
        assert response.status_code == 409

    def test_create_wallet_invalid_currency(self, client, auth_headers):
        response = client.post(
            "/wallets", json={"currency": "XYZ"}, headers=auth_headers
        )
        assert response.status_code == 400


class TestWalletList:
    def test_list_wallets(self, client, auth_headers):
        response = client.get("/wallets", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Should have the default USD wallet from signup
        assert len(data) >= 1
        assert data[0]["currency"] == "USD"


class TestWalletCredit:
    def test_credit_success(self, client, auth_headers):
        # Get the default wallet
        wallets = client.get("/wallets", headers=auth_headers).json()
        wallet_id = wallets[0]["id"]

        response = client.post(
            f"/wallets/{wallet_id}/credit",
            json={"amount": "100.50", "description": "Test credit"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "CREDIT"
        assert data["amount"] == "100.500000"
        assert data["balance_after"] == "100.500000"
        assert data["description"] == "Test credit"

    def test_credit_zero_amount(self, client, auth_headers):
        wallets = client.get("/wallets", headers=auth_headers).json()
        wallet_id = wallets[0]["id"]

        response = client.post(
            f"/wallets/{wallet_id}/credit",
            json={"amount": "0"},
            headers=auth_headers,
        )
        assert response.status_code == 422  # Pydantic: gt=0


class TestWalletDebit:
    def test_debit_success(self, client, auth_headers):
        wallets = client.get("/wallets", headers=auth_headers).json()
        wallet_id = wallets[0]["id"]

        # Credit first
        client.post(
            f"/wallets/{wallet_id}/credit",
            json={"amount": "200"},
            headers=auth_headers,
        )

        # Then debit
        response = client.post(
            f"/wallets/{wallet_id}/debit",
            json={"amount": "75", "description": "Withdrawal"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "DEBIT"
        assert data["amount"] == "75.000000"
        assert data["balance_after"] == "125.000000"

    def test_debit_insufficient_funds(self, client, auth_headers):
        wallets = client.get("/wallets", headers=auth_headers).json()
        wallet_id = wallets[0]["id"]

        response = client.post(
            f"/wallets/{wallet_id}/debit",
            json={"amount": "999999"},
            headers=auth_headers,
        )
        assert response.status_code == 422  # InsufficientFundsError


class TestTransactions:
    def test_list_transactions_empty(self, client, auth_headers):
        response = client.get("/transactions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["transactions"] == []
        assert data["total"] == 0

    def test_list_transactions_after_operations(self, client, auth_headers):
        wallets = client.get("/wallets", headers=auth_headers).json()
        wallet_id = wallets[0]["id"]

        # Credit
        client.post(
            f"/wallets/{wallet_id}/credit",
            json={"amount": "500"},
            headers=auth_headers,
        )
        # Debit
        client.post(
            f"/wallets/{wallet_id}/debit",
            json={"amount": "100"},
            headers=auth_headers,
        )

        response = client.get("/transactions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["transactions"]) == 2
        # Most recent first
        assert data["transactions"][0]["type"] == "DEBIT"
        assert data["transactions"][1]["type"] == "CREDIT"

    def test_list_transactions_pagination(self, client, auth_headers):
        wallets = client.get("/wallets", headers=auth_headers).json()
        wallet_id = wallets[0]["id"]

        # Create 3 transactions
        for i in range(3):
            client.post(
                f"/wallets/{wallet_id}/credit",
                json={"amount": "10"},
                headers=auth_headers,
            )

        # Page 1, size 2
        response = client.get("/transactions?page=1&page_size=2", headers=auth_headers)
        data = response.json()
        assert len(data["transactions"]) == 2
        assert data["total"] == 3
        assert data["has_next"] is True

        # Page 2, size 2
        response = client.get("/transactions?page=2&page_size=2", headers=auth_headers)
        data = response.json()
        assert len(data["transactions"]) == 1
        assert data["has_next"] is False

    def test_list_transactions_filter_by_wallet(self, client, auth_headers):
        # Create a second wallet
        client.post("/wallets", json={"currency": "EUR"}, headers=auth_headers)
        wallets = client.get("/wallets", headers=auth_headers).json()

        usd_wallet_id = next(w["id"] for w in wallets if w["currency"] == "USD")
        eur_wallet_id = next(w["id"] for w in wallets if w["currency"] == "EUR")

        # Credit both
        client.post(
            f"/wallets/{usd_wallet_id}/credit",
            json={"amount": "100"},
            headers=auth_headers,
        )
        client.post(
            f"/wallets/{eur_wallet_id}/credit",
            json={"amount": "50"},
            headers=auth_headers,
        )

        # Filter by USD wallet
        response = client.get(
            f"/transactions?wallet_id={usd_wallet_id}", headers=auth_headers
        )
        data = response.json()
        assert data["total"] == 1
        assert data["transactions"][0]["currency"] == "USD"
