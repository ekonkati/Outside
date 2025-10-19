import pytest

pytest.importorskip("flask")

from app import create_app
from utils.calculations import CompositeItem


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
        assert stored[0]["metadata"]["composite_breakdown"]["unit_rate"] == pytest.approx(
            float(stored[0]["base_rate"])
        )


def test_reset_clears_items(app, client):
    payload = load_sample_payload()
    client.post("/add", data=payload, follow_redirects=True)

    response = client.post("/reset", follow_redirects=True)
    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "items" not in session


def test_composite_breakdown_math():
    payload = {
        "id": "sample",
        "name": "Sample composite item",
        "unit": "unit",
        "components": [
            {
                "group": "materials",
                "description": "Component A",
                "unit": "qty",
                "quantity": 1.0,
                "rate": 40.0,
            },
            {
                "group": "labour",
                "description": "Component B",
                "unit": "qty",
                "quantity": 2.0,
                "rate": 30.0,
            },
        ],
        "adjustments": [
            {
                "label": "GST @21.27%",
                "factor": 0.2127,
                "base_stage": "X",
                "result_stage": "Y",
            },
            {
                "label": "Overheads @15%",
                "percent": 15.0,
                "base_stage": "Y",
                "result_stage": "Z",
            },
            {
                "label": "Cess @1%",
                "percent": 1.0,
                "base_stage": "Z",
            },
        ],
        "output_quantity": 10.0,
        "round_to": 6,
    }
    composite_item = CompositeItem.from_dict(payload)
    breakdown = composite_item.breakdown()

    assert breakdown["base_total"] == pytest.approx(100.0)
    assert breakdown["stages"]["Y"] == pytest.approx(121.27, rel=1e-6)
    assert breakdown["stages"]["Z"] == pytest.approx(139.4605, rel=1e-6)
    assert breakdown["raw_total"] == pytest.approx(140.855105, rel=1e-6)
    assert breakdown["unit_rate"] == pytest.approx(14.0855105, rel=1e-6)


def test_dataset_breakdown_matches_base_rate(app):
    rates = app.config["RATES"]
    for items in rates.values():
        for item in items:
            costing = item.get("costing")
            if costing and "computed_breakdown" in costing:
                breakdown = costing["computed_breakdown"]
                assert breakdown["unit_rate"] == pytest.approx(item["base_rate"], rel=1e-6)
                return
    pytest.fail("Expected at least one composite item with computed breakdown")
