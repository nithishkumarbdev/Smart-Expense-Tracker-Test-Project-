"""End-to-end tests for the HTTP API: status codes, validation, and JSON shapes."""

from fastapi.testclient import TestClient

VALID_PAYLOAD = {
    "title": "Coffee",
    "amount": 4.5,
    "category": "Food",
    "date": "2026-01-15",
}


def test_create_expense_returns_201_and_assigns_id(client: TestClient) -> None:
    response = client.post("/expenses", json=VALID_PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "Coffee"


def test_create_expense_with_blank_title_returns_422(client: TestClient) -> None:
    payload = {**VALID_PAYLOAD, "title": "   "}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_create_expense_with_negative_amount_returns_422(client: TestClient) -> None:
    payload = {**VALID_PAYLOAD, "amount": -5}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_create_expense_with_zero_amount_returns_422(client: TestClient) -> None:
    payload = {**VALID_PAYLOAD, "amount": 0}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_create_expense_with_infinite_amount_returns_422(client: TestClient) -> None:
    # Regression test for a bug found via manual curl testing, not by the
    # original suite. Two things had to be true to trigger it:
    #   1. `Infinity > 0` is True in Python, so `gt=0` alone let it through
    #      the amount validator (fixed with an explicit isfinite check).
    #   2. FastAPI's default error handler echoes the rejected value back
    #      in the 422 body, and Starlette's JSON encoder can't serialize
    #      `inf` -- so even after (1) was fixed, the error response itself
    #      crashed with a 500 (fixed with a sanitizing exception handler).
    # httpx's `json=` helper refuses to encode `float("inf")` client-side,
    # so raw bytes are sent here to actually exercise the server path.
    raw_body = (
        b'{"title": "Bad", "amount": Infinity, "category": "Food", '
        b'"date": "2026-01-01"}'
    )
    response = client.post(
        "/expenses",
        content=raw_body,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "amount"]


def test_create_expense_with_invalid_date_returns_422(client: TestClient) -> None:
    payload = {**VALID_PAYLOAD, "date": "not-a-date"}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_create_expense_missing_field_returns_422(client: TestClient) -> None:
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "category"}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_list_expenses_returns_all(client: TestClient) -> None:
    client.post("/expenses", json=VALID_PAYLOAD)
    client.post("/expenses", json={**VALID_PAYLOAD, "category": "Travel"})
    response = client.get("/expenses")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_expenses_filters_by_category(client: TestClient) -> None:
    client.post("/expenses", json=VALID_PAYLOAD)
    client.post("/expenses", json={**VALID_PAYLOAD, "category": "Travel"})
    response = client.get("/expenses", params={"category": "Food"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["category"] == "Food"


def test_total_overall(client: TestClient) -> None:
    client.post("/expenses", json={**VALID_PAYLOAD, "amount": 10.0})
    client.post("/expenses", json={**VALID_PAYLOAD, "amount": 5.0, "category": "Travel"})
    response = client.get("/expenses/total")
    assert response.status_code == 200
    assert response.json() == {"total": 15.0, "category": None}


def test_total_by_category(client: TestClient) -> None:
    client.post("/expenses", json={**VALID_PAYLOAD, "amount": 10.0, "category": "Food"})
    client.post("/expenses", json={**VALID_PAYLOAD, "amount": 5.0, "category": "Travel"})
    response = client.get("/expenses/total", params={"category": "Food"})
    assert response.status_code == 200
    assert response.json() == {"total": 10.0, "category": "Food"}


def test_delete_existing_expense_returns_204(client: TestClient) -> None:
    created = client.post("/expenses", json=VALID_PAYLOAD).json()
    response = client.delete(f"/expenses/{created['id']}")
    assert response.status_code == 204
    assert client.get("/expenses").json() == []


def test_delete_nonexistent_expense_returns_404(client: TestClient) -> None:
    response = client.delete("/expenses/999")
    assert response.status_code == 404
    assert "999" in response.json()["detail"]
