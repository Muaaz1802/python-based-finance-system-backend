from fastapi.testclient import TestClient

from tests.conftest import auth_headers, register_and_login


def seed_transactions(client, token):
    txs = [
        {
            "amount": "3000.00",
            "type": "income",
            "category": "Salary",
            "transaction_date": "2024-01-15",
        },
        {
            "amount": "500.00",
            "type": "expense",
            "category": "Food",
            "transaction_date": "2024-01-20",
        },
        {
            "amount": "200.00",
            "type": "expense",
            "category": "Transport",
            "transaction_date": "2024-02-05",
        },
        {
            "amount": "1000.00",
            "type": "income",
            "category": "Freelance",
            "transaction_date": "2024-02-10",
        },
    ]
    for tx in txs:
        client.post("/transactions", json=tx, headers=auth_headers(token))


def test_summary_returns_correct_totals(client: TestClient):
    admin_token = register_and_login(client, "admin@test.com", "pass123", "admin")
    seed_transactions(client, admin_token)

    resp = client.get("/analytics/summary", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert float(data["total_income"]) == 4000.00
    assert float(data["total_expenses"]) == 700.00
    assert float(data["balance"]) == 3300.00


def test_viewer_cannot_access_analytics(client: TestClient):
    token = register_and_login(client, "viewer@test.com", "pass123", "viewer")
    resp = client.get("/analytics/summary", headers=auth_headers(token))
    assert resp.status_code == 403


def test_category_breakdown_returns_groups(client: TestClient):
    admin_token = register_and_login(client, "admin2@test.com", "pass123", "admin")
    seed_transactions(client, admin_token)

    resp = client.get("/analytics/by-category", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    categories = [item["category"] for item in resp.json()]
    assert len(categories) > 0


def test_monthly_totals_structure(client: TestClient):
    token = register_and_login(client, "analyst3@test.com", "pass123", "analyst")
    admin_token = register_and_login(client, "admin3@test.com", "pass123", "admin")
    seed_transactions(client, admin_token)

    resp = client.get("/analytics/monthly", headers=auth_headers(token))
    assert resp.status_code == 200
    for entry in resp.json():
        assert "year" in entry
        assert "month" in entry
        assert "income" in entry
        assert "expenses" in entry
