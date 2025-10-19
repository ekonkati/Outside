# CPWD Costing Web App

This project provides a lightweight Flask web application for preparing construction cost sheets using the Central Public Works Department (CPWD) schedule of rates. The interface lets you pick items from the bundled dataset, review the published component breakdown (materials, labour, machinery, sundries), and apply project-specific adjustments such as lead, lift, seignorage, and wastage. Each bundled item follows the CPWD costing convention of evaluating a base cost **X**, adding statutory allowances to produce **Y** and **Z**, and finally rounding the payable rate.

## Prerequisites

- Python 3.10 or newer (the app was developed and tested with Python 3.11)
- (Recommended) A virtual environment manager such as `venv` or `conda`

## 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

## 2. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Note:** If your environment is behind a corporate proxy, configure the proxy variables (e.g., `HTTPS_PROXY`) before running `pip install`.

## 3. Verify the installation

Run the automated smoke tests to confirm the Flask routes can be loaded and
that items can be added to the in-memory session store:

```bash
pytest
```

A passing result indicates that the bundled dataset can be read and the core
add/reset workflow is functional.

## 4. Launch the development server

You can run the application directly with Python:

```bash
python app.py
```

Alternatively, you can use the Flask CLI:

```bash
export FLASK_APP=app:create_app  # Windows PowerShell: $env:FLASK_APP = "app:create_app"
flask run --host=0.0.0.0 --port=5000
```

After the server starts, open your browser to [http://localhost:5000](http://localhost:5000) to use the cost sheet.

## 5. Resetting data during development

Line items are stored in the Flask session.  If you need to clear all entries, click **"Clear all items"** in the sidebar or clear your browser cookies for the site.

## 6. Updating the CPWD schedule

The sample dataset lives in [`data/cpwd_rates.json`](data/cpwd_rates.json). Replace or extend the file with the current schedule of rates. Organise items under top-level keys (e.g. `earthwork`, `finishes`) to control how the categories appear in the UI.

Each item now embeds the CPWD costing trace inside a `costing` object. A minimal example is shown below:

```json
{
  "id": "2.1.1",
  "name": "Earthwork in surface excavation",
  "unit": "100 sqm",
  "description": "Key notes from the SOR entry",
  "costing": {
    "output_quantity": 100.0,
    "components": [
      {"group": "labour", "description": "Beldar", "unit": "day", "quantity": 6.8, "rate": 736.0},
      {"group": "machinery", "description": "Smooth wheel roller", "unit": "hour", "quantity": 2.0, "rate": 900.0}
    ],
    "adjustments": [
      {"label": "GST @21.27%", "factor": 0.2127, "base_stage": "X", "result_stage": "Y"},
      {"label": "CP & OH @15%", "percent": 15.0, "base_stage": "Y", "result_stage": "Z"},
      {"label": "Cess @1%", "percent": 1.0, "base_stage": "Z"}
    ],
    "round_to": 2
  }
}
```

During application start-up, the app computes the component totals, applies the staged adjustments (X → Y → Z), and derives both the full amount for the `output_quantity` and the payable rate per unit. The UI displays this trace under each line item so you can cross-check the numbers against the published schedule.

**Key fields explained:**

- `components`: granular materials, labour, plant, and sundries that sum to base cost **X**.
- `adjustments`: sequential allowances that reference earlier stages. Set `result_stage` to the next letter used in the SOR (e.g. `Y`, `Z`, `AA`). If omitted, the amount is added to the running total without defining a new stage.
- `output_quantity`: the measurement base used in the SOR table (10 sqm, 100 cum, etc.).
- `round_to`: optional rounding applied to the computed total before deriving the unit rate.
- `say_total`: optional manual override if the SOR quotes a "Say" amount that differs from the mathematical rounding.

## Troubleshooting

- **`pip install` fails because of missing SSL certificates or proxies**: ensure your proxy variables are exported and, if necessary, install the organisation's root certificates.
- **Nothing appears in the item dropdown**: confirm your JSON file uses valid syntax and that each item either provides a `base_rate` or a `costing` section with components and adjustments.
- **Server restarts on every request**: this is normal in Flask's debug mode. Disable debug by removing `debug=True` in `app.py` when running in production.

## License

This project is provided as-is. Adapt the code and dataset to match your specific CPWD schedule and project requirements.
