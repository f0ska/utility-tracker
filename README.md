# Utility Tracker

A small native GTK 4 desktop app for tracking household utility readings, bills, payments, and tariffs.

## Features

- Electricity, gas, gas distribution, water, and waste tracking
- Monthly readings and payment history
- Tariff and account number management
- Quick copyable report for sending meter readings
- Excel export
- Local SQLite storage
- Application log with a lightweight in-app warning banner

## Requirements

- Python 3
- GTK 4 / PyGObject
- openpyxl

Install Python dependencies:

```bash
pip install -r requirements.txt
```

On Linux, GTK/PyGObject is usually installed through the system package manager.

## Run

```bash
python3 app.py
```

## Import Local Data

Put an ODS export at `utility_data.ods` and run:

```bash
python3 seed_data.py
```

Or pass a custom path:

```bash
UTILITY_TRACKER_ODS=/path/to/file.ods python3 seed_data.py
```

Local databases, spreadsheets, caches, and logs are intentionally ignored by git.
