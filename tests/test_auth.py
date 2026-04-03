from fastapi.testclient import TestClient


def test_register_success(client: TestClient):
    resp = client.post("/auth/register", json={"email": "user@test.com", "password": "pass123"})
    assert resp.status_code == 201
    assert resp.json()["email"] == "user@test.com"
    assert resp.json()["role"] == "viewer"


def test_register_duplicate_email(client: TestClient):
    client.post("/auth/register", json={"email": "dup@test.com", "password": "pass123"})
    resp = client.post("/auth/register", json={"email": "dup@test.com", "password": "pass123"})
    assert resp.status_code == 409


def test_login_success(client: TestClient):
    client.post("/auth/register", json={"email": "login@test.com", "password": "pass123"})
    resp = client.post("/auth/login", json={"email": "login@test.com", "password": "pass123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client: TestClient):
    client.post("/auth/register", json={"email": "bad@test.com", "password": "correct"})
    resp = client.post("/auth/login", json={"email": "bad@test.com", "password": "wrong"})
    assert resp.status_code == 401
