"""Smoke tests — verify the app boots and core endpoints respond.

These are deliberately minimal; deep tests land in phases 1+.
"""


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Smart Logistics" in r.json()["message"]


def test_generate_token_default_role(client):
    r = client.post("/generate-token", json={})
    assert r.status_code == 200
    body = r.json()
    assert body["role"] == "user"
    assert body["token_type"] == "bearer"
    assert body["access_token"]
