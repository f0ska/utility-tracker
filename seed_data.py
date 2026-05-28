import zipfile
import xml.etree.ElementTree as ET
import os
import db
from models import UtilityCalculator
from constants import UKR_MONTHS_PARSE

# Initialize DB first
db.init_db()

ods_path = os.environ.get('UTILITY_TRACKER_ODS', 'utility_data.ods')


def parse_month_year(text):
    """Parses a Ukrainian 'Month Year' string (e.g. 'Квітень 2025') into YYYY-MM format."""
    text = text.strip().lower()
    parts = text.split()
    if len(parts) == 2:
        m_str, y_str = parts
        if m_str in UKR_MONTHS_PARSE:
            return f"{y_str}-{UKR_MONTHS_PARSE[m_str]}"
    return None

# Namespaces for ODF
namespaces = {
    'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
    'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
    'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
}

# We will collect everything into a structured dictionary keyed by period
imported_data = {}

if os.path.exists(ods_path):
    with zipfile.ZipFile(ods_path) as z:
        content_xml = z.read('content.xml')
        root = ET.fromstring(content_xml)
        tables = root.findall('.//table:table', namespaces)
        
        for table in tables:
            sheet_name = table.get('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name')
            rows = table.findall('.//table:table-row', namespaces)
            
            headers = []
            row_data_list = []
            
            for row in rows:
                cells = row.findall('.//table:table-cell', namespaces)
                row_data = []
                for cell in cells:
                    repeat = cell.get('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}number-columns-repeated')
                    repeat = int(repeat) if repeat else 1
                    
                    text_elems = cell.findall('.//text:p', namespaces)
                    cell_text = "".join("".join(elem.itertext()) for elem in text_elems) if text_elems else ""
                    
                    if not cell_text:
                        val = cell.get('{urn:oasis:names:tc:opendocument:xmlns:office:1.0}value')
                        if val:
                            cell_text = val
                    
                    for _ in range(repeat):
                        row_data.append(cell_text)
                
                while row_data and row_data[-1] == "":
                    row_data.pop()
                
                if row_data:
                    row_data_list.append(row_data)
            
            if not row_data_list:
                continue
                
            headers = row_data_list[0]
            
            # Process rows depending on sheet
            if sheet_name == 'Енергозбут':
                for r in row_data_list[1:]:
                    if len(r) >= 11 and parse_month_year(r[0]):
                        p = parse_month_year(r[0])
                        if p not in imported_data:
                            imported_data[p] = {}
                        imported_data[p].update({
                            'elec_day_reading': float(r[2]) if r[2] else None,
                            'elec_night_reading': float(r[1]) if r[1] else None,
                            'elec_day_tariff': float(r[7]) if r[7] else 4.32,
                            'elec_night_tariff': float(r[6]) if r[6] else 2.16,
                            'elec_calculated': float(r[8]) if r[8] else 0.0,
                            'elec_billed': float(r[9]) if r[9] else None,
                            'elec_paid': float(r[10]) if r[10] else 0.0,
                            'elec_paid_status': 1 if r[10] and float(r[10]) > 0 else 0
                        })
            elif sheet_name == 'Газ':
                for r in row_data_list[1:]:
                    if len(r) >= 12 and parse_month_year(r[0]):
                        p = parse_month_year(r[0])
                        if p not in imported_data:
                            imported_data[p] = {}
                        imported_data[p].update({
                            'gas_reading': float(r[1]) if r[1] else None,
                            'gas_tariff': float(r[3]) if r[3] else 7.95689,
                            'gas_calculated': float(r[4]) if r[4] else 0.0,
                            'gas_billed': float(r[5]) if r[5] else None,
                            'gas_paid': float(r[6]) if r[6] else 0.0,
                            'gas_paid_status': 1 if r[6] and float(r[6]) > 0 else 0,
                            
                            'gas_dist_volume': float(r[7]) if r[7] else 70.66,
                            'gas_dist_tariff': float(r[8]) if r[8] else 1.848,
                            'gas_dist_calculated': float(r[9]) if r[9] else 0.0,
                            'gas_dist_billed': float(r[10]) if r[10] else None,
                            'gas_dist_paid': float(r[11]) if r[11] else 0.0,
                            'gas_dist_paid_status': 1 if r[11] and float(r[11]) > 0 else 0
                        })
            elif sheet_name == 'Водоканал':
                for r in row_data_list[1:]:
                    if len(r) >= 9 and parse_month_year(r[0]):
                        p = parse_month_year(r[0])
                        if p not in imported_data:
                            imported_data[p] = {}
                        imported_data[p].update({
                            'water_reading': float(r[1]) if r[1] else None,
                            'water_supply_tariff': float(r[3]) if r[3] else 14.17,
                            'water_drainage_tariff': float(r[4]) if r[4] else 13.22,
                            'water_sub_tariff': float(r[5]) if r[5] else 28.10,
                            'water_calculated': float(r[6]) if r[6] else 0.0,
                            'water_billed': float(r[7]) if r[7] else None,
                            'water_paid': float(r[8]) if r[8] else 0.0,
                            'water_paid_status': 1 if r[8] and float(r[8]) > 0 else 0
                        })
            elif sheet_name == 'Сміття':
                for r in row_data_list[1:]:
                    if len(r) >= 3 and parse_month_year(r[0]):
                        p = parse_month_year(r[0])
                        if p not in imported_data:
                            imported_data[p] = {}
                        imported_data[p].update({
                            'garbage_tariff': float(r[1]) if r[1] else 118.07,
                            'garbage_calculated': float(r[1]) if r[1] else 118.07,
                            'garbage_billed': float(r[1]) if r[1] else 118.07,
                            'garbage_paid': float(r[2]) if r[2] else 0.0,
                            'garbage_paid_status': 1 if r[2] and float(r[2]) > 0 else 0
                        })

    # Save to database
    tariffs = db.get_all_tariffs()
    for period, data in sorted(imported_data.items()):
        data['period'] = period

        data_to_save = {
            'period': period,
            
            'elec_day_reading': data.get('elec_day_reading'),
            'elec_night_reading': data.get('elec_night_reading'),
            'elec_day_tariff': data.get('elec_day_tariff', tariffs['electricity_day']),
            'elec_night_tariff': data.get('elec_night_tariff', tariffs['electricity_night']),
            'elec_calculated': data.get('elec_calculated', 0.0),
            'elec_billed': data.get('elec_billed'),
            'elec_paid': data.get('elec_paid', 0.0),
            'elec_paid_status': data.get('elec_paid_status', 0),
            
            'gas_reading': data.get('gas_reading'),
            'gas_tariff': data.get('gas_tariff', tariffs['gas']),
            'gas_calculated': data.get('gas_calculated', 0.0),
            'gas_billed': data.get('gas_billed'),
            'gas_paid': data.get('gas_paid', 0.0),
            'gas_paid_status': data.get('gas_paid_status', 0),
            
            'gas_dist_volume': data.get('gas_dist_volume', 70.66),
            'gas_dist_tariff': data.get('gas_dist_tariff', tariffs['gas_distribution']),
            'gas_dist_calculated': data.get('gas_dist_calculated', 0.0),
            'gas_dist_billed': data.get('gas_dist_billed'),
            'gas_dist_paid': data.get('gas_dist_paid', 0.0),
            'gas_dist_paid_status': data.get('gas_dist_paid_status', 0),
            
            'water_reading': data.get('water_reading'),
            'water_supply_tariff': data.get('water_supply_tariff', tariffs['water_supply']),
            'water_drainage_tariff': data.get('water_drainage_tariff', tariffs['water_drainage']),
            'water_sub_tariff': data.get('water_sub_tariff', tariffs['water_subscription']),
            'water_calculated': data.get('water_calculated', 0.0),
            'water_billed': data.get('water_billed'),
            'water_paid': data.get('water_paid', 0.0),
            'water_paid_status': data.get('water_paid_status', 0),
            
            'garbage_tariff': data.get('garbage_tariff', tariffs['garbage']),
            'garbage_calculated': data.get('garbage_calculated', tariffs['garbage']),
            'garbage_billed': data.get('garbage_billed', tariffs['garbage']),
            'garbage_paid': data.get('garbage_paid', 0.0),
            'garbage_paid_status': data.get('garbage_paid_status', 0)
        }

        db.save_reading(data_to_save)

    print(f"Successfully seeded {len(imported_data)} months of data from {ods_path} into SQLite!")
else:
    print(f"{ods_path} file not found.")
