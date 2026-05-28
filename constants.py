"""
Shared constants for the UtilityTracker application.

Centralizing repeated data here eliminates duplication across app.py,
models.py, and seed_data.py.
"""

# Ukrainian month names keyed by month number (1-12).
# Used for display purposes throughout the app.
UKR_MONTHS = {
    1: "Січень", 2: "Лютий", 3: "Березень", 4: "Квітень",
    5: "Травень", 6: "Червень", 7: "Липень", 8: "Серпень",
    9: "Вересень", 10: "Жовтень", 11: "Листопад", 12: "Грудень"
}

# Ukrainian month names keyed by lowercased Ukrainian name (for parsing input).
# Used by seed_data.py when importing from the .ods spreadsheet.
UKR_MONTHS_PARSE = {
    'січень': '01', 'лютий': '02', 'березень': '03', 'квітень': '04',
    'травень': '05', 'червень': '06', 'липень': '07', 'серпень': '08',
    'вересень': '09', 'жовтень': '10', 'листопад': '11', 'грудень': '12'
}

# Maps the service key used in the UI/models layer to the column prefix
# used in the SQLite readings table.
# Example: 'electricity' -> 'elec' means the columns are elec_paid, elec_billed, etc.
SERVICE_PREFIX_MAP = {
    'electricity': 'elec',
    'gas':         'gas',
    'gas_dist':    'gas_dist',
    'water':       'water',
    'garbage':     'garbage',
}

# Payment status codes stored in the database.
STATUS_UNPAID   = 0
STATUS_PAID     = 1
STATUS_PREPAID  = 2

STATUS_LABELS = {
    STATUS_UNPAID:  "Не сплачено",
    STATUS_PAID:    "Сплачено",
    STATUS_PREPAID: "Аванс / Пропуск",
}
