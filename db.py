import sqlite3
from contextlib import contextmanager
from datetime import datetime

from paths import database_path

DB_PATH = database_path()

# Whitelist of all valid column names for the readings table.
# This prevents potential issues from unexpected keys in reading_data dicts.
READINGS_COLUMNS = frozenset({
    'id', 'period', 'created_at',
    # Electricity
    'elec_day_reading', 'elec_night_reading', 'elec_day_tariff', 'elec_night_tariff',
    'elec_calculated', 'elec_billed', 'elec_paid', 'elec_paid_status', 'elec_paid_date',
    # Gas (Consumption)
    'gas_reading', 'gas_tariff', 'gas_calculated', 'gas_billed',
    'gas_paid', 'gas_paid_status', 'gas_paid_date',
    # Gas (Distribution)
    'gas_dist_volume', 'gas_dist_tariff', 'gas_dist_calculated', 'gas_dist_billed',
    'gas_dist_paid', 'gas_dist_paid_status', 'gas_dist_paid_date',
    # Water
    'water_reading', 'water_supply_tariff', 'water_drainage_tariff', 'water_sub_tariff',
    'water_calculated', 'water_billed', 'water_paid', 'water_paid_status', 'water_paid_date',
    # Garbage
    'garbage_tariff', 'garbage_calculated', 'garbage_billed',
    'garbage_paid', 'garbage_paid_status', 'garbage_paid_date',
})


@contextmanager
def get_connection():
    """Context manager that yields a SQLite connection with row factory enabled.
    Guarantees the connection is closed even if an exception occurs.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initializes the database schema and seeds initial tariffs if empty."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Create readings table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period TEXT NOT NULL UNIQUE, -- YYYY-MM

            -- Electricity
            elec_day_reading REAL,
            elec_night_reading REAL,
            elec_day_tariff REAL,
            elec_night_tariff REAL,
            elec_calculated REAL,
            elec_billed REAL,
            elec_paid REAL,
            elec_paid_status INTEGER DEFAULT 0, -- 0=Unpaid, 1=Paid, 2=Prepaid/Skip
            elec_paid_date TEXT,

            -- Gas (Consumption)
            gas_reading REAL,
            gas_tariff REAL,
            gas_calculated REAL,
            gas_billed REAL,
            gas_paid REAL,
            gas_paid_status INTEGER DEFAULT 0,
            gas_paid_date TEXT,

            -- Gas (Distribution)
            gas_dist_volume REAL,
            gas_dist_tariff REAL,
            gas_dist_calculated REAL,
            gas_dist_billed REAL,
            gas_dist_paid REAL,
            gas_dist_paid_status INTEGER DEFAULT 0,
            gas_dist_paid_date TEXT,

            -- Water
            water_reading REAL,
            water_supply_tariff REAL,
            water_drainage_tariff REAL,
            water_sub_tariff REAL,
            water_calculated REAL,
            water_billed REAL,
            water_paid REAL,
            water_paid_status INTEGER DEFAULT 0,
            water_paid_date TEXT,

            -- Garbage
            garbage_tariff REAL,
            garbage_calculated REAL,
            garbage_billed REAL,
            garbage_paid REAL,
            garbage_paid_status INTEGER DEFAULT 0,
            garbage_paid_date TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Create tariffs table (only once — removed duplicate that was here before)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tariffs (
            service_name TEXT PRIMARY KEY,
            value REAL NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Seed default tariffs if empty
        cursor.execute("SELECT COUNT(*) as cnt FROM tariffs")
        if cursor.fetchone()['cnt'] == 0:
            default_tariffs = [
                ('electricity_day', 4.32),
                ('electricity_night', 2.16),
                ('gas', 7.95689),
                ('gas_distribution', 1.848),
                ('gas_distribution_volume', 70.66),
                ('water_supply', 14.17),
                ('water_drainage', 13.22),
                ('water_subscription', 28.10),
                ('garbage', 118.07)
            ]
            cursor.executemany(
                "INSERT INTO tariffs (service_name, value) VALUES (?, ?)",
                default_tariffs
            )
        else:
            # Migration: Ensure the gas distribution volume exists even if DB was already seeded
            cursor.execute("INSERT OR IGNORE INTO tariffs (service_name, value) VALUES ('gas_distribution_volume', 70.66)")

        # Create accounts table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            service_name TEXT PRIMARY KEY,
            account_number TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Seed default accounts if empty
        cursor.execute("SELECT COUNT(*) as cnt FROM accounts")
        if cursor.fetchone()['cnt'] == 0:
            default_services = [
                ('electricity', ''),
                ('gas', ''),
                ('gas_dist', ''),
                ('water', ''),
                ('garbage', '')
            ]
            cursor.executemany(
                "INSERT INTO accounts (service_name, account_number) VALUES (?, ?)",
                default_services
            )

        conn.commit()


# Tariffs CRUD
def get_all_tariffs():
    """Fetches all current tariffs as a dictionary."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT service_name, value FROM tariffs")
        rows = cursor.fetchall()
    return {row['service_name']: row['value'] for row in rows}


def update_tariff(service_name, value):
    """Updates a tariff value."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tariffs SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE service_name = ?",
            (value, service_name)
        )
        conn.commit()


# Accounts CRUD
def get_all_accounts():
    """Fetches all personal account numbers as a dictionary."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT service_name, account_number FROM accounts")
        rows = cursor.fetchall()
    return {row['service_name']: row['account_number'] for row in rows}


def update_account(service_name, account_number):
    """Updates a personal account number."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO accounts (service_name, account_number, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (service_name, account_number)
        )
        conn.commit()


# Readings CRUD
def get_all_readings():
    """Fetches all readings ordered by period descending."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM readings ORDER BY period DESC")
        rows = [dict(r) for r in cursor.fetchall()]
    return rows


def get_reading(period):
    """Fetches a specific reading by period (YYYY-MM). Returns None if not found."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM readings WHERE period = ?", (period,))
        row = cursor.fetchone()
    return dict(row) if row else None


def get_previous_reading(period):
    """Gets the chronologically immediate previous reading before the specified period."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM readings WHERE period < ? ORDER BY period DESC LIMIT 1",
            (period,)
        )
        row = cursor.fetchone()
    return dict(row) if row else None


def save_reading(reading_data):
    """Saves (inserts or updates) a reading record.

    Only columns present in READINGS_COLUMNS are written to the database.
    Unknown keys in reading_data are silently ignored, preventing SQL errors
    from unexpected dict contents. Existing rows are updated by period without
    replacing the row, so the original id and created_at are preserved.
    """
    if not reading_data.get('period'):
        raise ValueError("reading_data must include a non-empty period")

    with get_connection() as conn:
        cursor = conn.cursor()

        # Filter to only whitelisted, known columns (excluding auto-managed ones)
        writable_columns = READINGS_COLUMNS - {'id', 'created_at'}
        fields = [f for f in reading_data.keys() if f in writable_columns]

        if 'period' not in fields:
            fields.insert(0, 'period')

        placeholders = ", ".join(["?"] * len(fields))
        update_fields = [f for f in fields if f != 'period']

        if update_fields:
            assignments = ", ".join(f"{field} = excluded.{field}" for field in update_fields)
            query = f"""
            INSERT INTO readings ({", ".join(fields)})
            VALUES ({placeholders})
            ON CONFLICT(period) DO UPDATE SET {assignments}
            """
        else:
            query = f"""
            INSERT OR IGNORE INTO readings ({", ".join(fields)})
            VALUES ({placeholders})
            """

        cursor.execute(query, [reading_data[f] for f in fields])
        conn.commit()


def delete_reading(period):
    """Deletes a reading record by period."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM readings WHERE period = ?", (period,))
        conn.commit()


def get_unpaid_readings():
    """Returns a list of periods that are not fully paid."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM readings
            WHERE elec_paid_status = 0
               OR gas_paid_status = 0
               OR gas_dist_paid_status = 0
               OR water_paid_status = 0
               OR garbage_paid_status = 0
            ORDER BY period DESC
        """)
        rows = [dict(r) for r in cursor.fetchall()]
    return rows


def get_readings_in_range(start_period, end_period):
    """Fetches readings between start_period and end_period (inclusive) ordered chronologically."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM readings WHERE period >= ? AND period <= ? ORDER BY period ASC",
            (start_period, end_period)
        )
        rows = [dict(r) for r in cursor.fetchall()]
    return rows
