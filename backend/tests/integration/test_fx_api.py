"""Integration tests for FX API endpoints — rate listing, wallet conversion, and conversion history."""


class TestFXAPI:
    def test_get_exchange_rates(self, client):
        response = client.get("/fx/rates?base=USD")
        assert response.status_code == 200
        data = response.json()
        assert data["base_currency"] == "USD"
        assert "EUR" in data["rates"]
        assert "GBP" in data["rates"]

    def test_convert_currency_end_to_end(self, client, auth_headers):
        # 1. Get USD wallet and credit 500 USD
        wallets = client.get("/wallets", headers=auth_headers).json()
        usd_wallet = next(w for w in wallets if w["currency"] == "USD")
        client.post(
            f"/wallets/{usd_wallet['id']}/credit",
            json={"amount": "500"},
            headers=auth_headers,
        )

        # 2. Convert 100 USD to EUR
        idempotency_key = "convert-test-key-999"
        response = client.post(
            "/fx/convert",
            json={
                "from_currency": "USD",
                "to_currency": "EUR",
                "amount": "100",
                "idempotency_key": idempotency_key,
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["from_currency"] == "USD"
        assert data["to_currency"] == "EUR"
        assert data["from_amount"] == "100.000000"

        # 3. Verify EUR wallet was created and credited
        updated_wallets = client.get("/wallets", headers=auth_headers).json()
        eur_wallet = next(w for w in updated_wallets if w["currency"] == "EUR")
        assert float(eur_wallet["balance"]) > 0

        # 4. List conversion audit history
        conversions = client.get("/fx/conversions", headers=auth_headers).json()
        assert len(conversions) >= 1
        assert conversions[0]["idempotency_key"] == idempotency_key
