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

Local databases, spreadsheets, caches, and logs are intentionally ignored by git.
