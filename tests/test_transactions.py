from fastapi.testclient import TestClient

from tests.conftest import auth_headers, register_and_login

VALID_TX = {
    "amount": "1500.00",
    "type": "income",
    "category": "Salary",
    "transaction_date": "2024-06-15",
    "notes": "June salary",
}


def test_admin_can_create_transaction(client: TestClient):
    token = register_and_login(client, "admin@test.com", "pass123", "admin")
    resp = client.post("/transactions", json=VALID_TX, headers=auth_headers(token))
    assert resp.status_code == 201
    assert resp.json()["category"] == "Salary"


def test_viewer_cannot_create_transaction(client: TestClient):
    token = register_and_login(client, "viewer@test.com", "pass123", "viewer")
    resp = client.post("/transactions", json=VALID_TX, headers=auth_headers(token))
    assert resp.status_code == 403


def test_negative_amount_rejected(client: TestClient):
    token = register_and_login(client, "admin2@test.com", "pass123", "admin")
    bad_tx = {**VALID_TX, "amount": "-100.00"}
    resp = client.post("/transactions", json=bad_tx, headers=auth_headers(token))
    assert resp.status_code == 422


def test_viewer_can_list_own_transactions(client: TestClient):
    admin_token = register_and_login(client, "admin3@test.com", "pass123", "admin")
    client.post("/transactions", json=VALID_TX, headers=auth_headers(admin_token))

    viewer_token = register_and_login(client, "viewer2@test.com", "pass123", "viewer")
    resp = client.get("/transactions", headers=auth_headers(viewer_token))
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_admin_can_delete_transaction(client: TestClient):
    token = register_and_login(client, "admin4@test.com", "pass123", "admin")
    create_resp = client.post(
        "/transactions", json=VALID_TX, headers=auth_headers(token)
    )
    tx_id = create_resp.json()["id"]

    del_resp = client.delete(f"/transactions/{tx_id}", headers=auth_headers(token))
    assert del_resp.status_code == 204


def test_filter_by_type(client: TestClient):
    token = register_and_login(client, "admin5@test.com", "pass123", "admin")
    client.post("/transactions", json=VALID_TX, headers=auth_headers(token))
    client.post(
        "/transactions",
        json={**VALID_TX, "type": "expense", "category": "Food"},
        headers=auth_headers(token),
    )

    resp = client.get("/transactions?type=income", headers=auth_headers(token))
    assert resp.status_code == 200
    assert all(tx["type"] == "income" for tx in resp.json()["results"])


def test_pagination(client: TestClient):
    token = register_and_login(client, "admin6@test.com", "pass123", "admin")
    for i in range(5):
        client.post(
            "/transactions",
            json={**VALID_TX, "notes": f"tx {i}"},
            headers=auth_headers(token),
        )

    resp = client.get("/transactions?page=1&page_size=2", headers=auth_headers(token))
    assert resp.json()["total"] == 5
    assert len(resp.json()["results"]) == 2
