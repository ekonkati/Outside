import pytest

from app import create_app


def load_sample_payload():
    rates = create_app().config["RATES"]
    for category, items in rates.items():
        if items:
            first_item = items[0]
            return {
                "category": category,
                "item_id": first_item["id"],
                "quantity": "10",  # form data are strings
                "lead_distance": "5",
                "lift_height": "2",
                "seignorage_percent": "3",
                "wastage_percent": "1",
                "remarks": "Test item",
            }
    raise RuntimeError("Sample data not found in CPWD rates")


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({"TESTING": True, "SECRET_KEY": "test"})
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_index_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"CPWD" in response.data


def test_add_item_flow(app, client):
    payload = load_sample_payload()
    response = client.post("/add", data=payload, follow_redirects=True)
    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "items" in session
        stored = session["items"]
        assert len(stored) == 1
        assert stored[0]["remarks"] == "Test item"


def test_reset_clears_items(app, client):
    payload = load_sample_payload()
    client.post("/add", data=payload, follow_redirects=True)

    response = client.post("/reset", follow_redirects=True)
    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "items" not in session
