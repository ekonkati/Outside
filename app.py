from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from flask import Flask, redirect, render_template, request, session, url_for

from utils.calculations import LineItem, summarise


def load_rates() -> Dict[str, List[Dict[str, str | float]]]:
    data_path = Path(__file__).parent / "data" / "cpwd_rates.json"
    with data_path.open() as fp:
        return json.load(fp)


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "outside-cpwd-costing"
    app.config["RATES"] = load_rates()

    @app.route("/")
    def index():
        rate_data = app.config["RATES"]
        items = [LineItem(**item_dict) for item_dict in session.get("items", [])]
        summary = summarise(items) if items else None
        return render_template(
            "index.html",
            rates=rate_data,
            items=[item.as_dict() for item in items],
            summary=summary,
        )

    @app.route("/add", methods=["POST"])
    def add_item():
        rate_data = app.config["RATES"]
        category = request.form.get("category")
        item_id = request.form.get("item_id")
        quantity = float(request.form.get("quantity", 0) or 0)
        lead_distance = float(request.form.get("lead_distance", 0) or 0)
        lift_height = float(request.form.get("lift_height", 0) or 0)
        seignorage_percent = float(request.form.get("seignorage_percent", 0) or 0)
        wastage_percent = float(request.form.get("wastage_percent", 0) or 0)
        remarks = request.form.get("remarks", "")

        if not category or not item_id or quantity <= 0:
            return redirect(url_for("index"))

        selected_category = rate_data.get(category, [])
        selected_item = next((item for item in selected_category if item["id"] == item_id), None)
        if selected_item is None:
            return redirect(url_for("index"))

        line_item = LineItem(
            category=category,
            item_id=item_id,
            item_name=selected_item["name"],
            unit=selected_item["unit"],
            quantity=quantity,
            base_rate=float(selected_item["base_rate"]),
            lead_distance=lead_distance,
            lift_height=lift_height,
            seignorage_percent=seignorage_percent,
            wastage_percent=wastage_percent,
            remarks=remarks,
        )

        items = session.get("items", [])
        items.append(line_item.storage_dict())
        session["items"] = items
        return redirect(url_for("index"))

    @app.route("/reset", methods=["POST"])
    def reset():
        session.pop("items", None)
        return redirect(url_for("index"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
