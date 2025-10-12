# CPWD Costing Web App

This project provides a lightweight Flask web application for preparing construction cost sheets using the Central Public Works Department (CPWD) schedule of rates.  The interface lets you pick items from the bundled dataset, apply adjustments such as lead, lift, seignorage, and wastage, and review a running project summary.

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

## 3. Launch the development server

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

## 4. Resetting data during development

Line items are stored in the Flask session.  If you need to clear all entries, click **"Clear all items"** in the sidebar or clear your browser cookies for the site.

## 5. Updating the CPWD schedule

The sample dataset lives in [`data/cpwd_rates.json`](data/cpwd_rates.json).  Replace or extend the file with the current schedule of rates.  Each entry must include:

```json
{
  "id": "unique identifier",
  "name": "Item description",
  "unit": "Unit of measurement",
  "base_rate": 123.45
}
```

Organise items under top-level keys such as `materials`, `labour`, or `equipment` to have them appear as categories in the UI.

## Troubleshooting

- **`pip install` fails because of missing SSL certificates or proxies**: ensure your proxy variables are exported and, if necessary, install the organisation's root certificates.
- **Nothing appears in the item dropdown**: confirm your JSON file uses valid syntax and that `base_rate` values are numeric.
- **Server restarts on every request**: this is normal in Flask's debug mode. Disable debug by removing `debug=True` in `app.py` when running in production.

## License

This project is provided as-is. Adapt the code and dataset to match your specific CPWD schedule and project requirements.
