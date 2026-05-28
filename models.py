import db
from constants import SERVICE_PREFIX_MAP, STATUS_LABELS
from datetime import datetime

class UtilityCalculator:
    """Contains business logic for calculating utility costs based on readings and tariffs."""
    
    @staticmethod
    def calculate_electricity(current_day, current_night, prev_day, prev_night, tariff_day, tariff_night):
        """Calculates electricity costs using night/day rates."""
        if current_day is None or current_night is None:
            return 0.0
        
        prev_d = prev_day if prev_day is not None else current_day
        prev_n = prev_night if prev_night is not None else current_night
        
        consumed_day = max(0.0, current_day - prev_d)
        consumed_night = max(0.0, current_night - prev_n)
        
        return round((consumed_day * tariff_day) + (consumed_night * tariff_night), 2)
    
    @staticmethod
    def calculate_gas(current_reading, prev_reading, tariff):
        """Calculates gas consumption cost."""
        if current_reading is None or prev_reading is None:
            return 0.0
        
        consumed = max(0.0, current_reading - prev_reading)
        return round(consumed * tariff, 2)
    
    @staticmethod
    def calculate_gas_distribution(volume, tariff):
        """Calculates gas distribution (transportation) cost."""
        if volume is None or tariff is None:
            return 0.0
        return round(volume * tariff, 2)
    
    @staticmethod
    def calculate_water(current_reading, prev_reading, tariff_supply, tariff_drainage, tariff_subscription):
        """Calculates water supply, drainage, and subscription costs."""
        if current_reading is None or prev_reading is None:
            return 0.0
        
        consumed = max(0.0, current_reading - prev_reading)
        cost = (consumed * tariff_supply) + (consumed * tariff_drainage) + tariff_subscription
        return round(cost, 2)
    
    @staticmethod
    def calculate_garbage(tariff):
        """Calculates garbage disposal cost (flat fee)."""
        if tariff is None:
            return 0.0
        return round(tariff, 2)

    @classmethod
    def calculate_all(cls, period, current_data):
        """
        Computes the calculated fields for a given period using current tariffs or existing tariffs.
        Merges with previous readings to calculate consumption.
        """
        prev = db.get_previous_reading(period)
        
        # Electricity
        if current_data.get('elec_day_reading') is not None and current_data.get('elec_night_reading') is not None:
            prev_day = prev.get('elec_day_reading') if prev else None
            prev_night = prev.get('elec_night_reading') if prev else None
            current_data['elec_calculated'] = cls.calculate_electricity(
                current_data['elec_day_reading'],
                current_data['elec_night_reading'],
                prev_day,
                prev_night,
                current_data['elec_day_tariff'],
                current_data['elec_night_tariff']
            )
        else:
            current_data['elec_calculated'] = 0.0

        # Gas
        if current_data.get('gas_reading') is not None:
            prev_gas = prev.get('gas_reading') if prev else None
            current_data['gas_calculated'] = cls.calculate_gas(
                current_data['gas_reading'],
                prev_gas,
                current_data['gas_tariff']
            )
        else:
            current_data['gas_calculated'] = 0.0
            
        # Gas Dist
        if current_data.get('gas_dist_volume') is not None:
            current_data['gas_dist_calculated'] = cls.calculate_gas_distribution(
                current_data['gas_dist_volume'],
                current_data['gas_dist_tariff']
            )
        else:
            current_data['gas_dist_calculated'] = 0.0

        # Water
        if current_data.get('water_reading') is not None:
            prev_water = prev.get('water_reading') if prev else None
            current_data['water_calculated'] = cls.calculate_water(
                current_data['water_reading'],
                prev_water,
                current_data['water_supply_tariff'],
                current_data['water_drainage_tariff'],
                current_data['water_sub_tariff']
            )
        else:
            current_data['water_calculated'] = 0.0

        # Garbage
        current_data['garbage_calculated'] = cls.calculate_garbage(
            current_data['garbage_tariff']
        )
        
        return current_data


class UtilityService:
    """Service layer handling transactional operations and business features."""
    
    @staticmethod
    def register_readings(period, elec_day, elec_night, gas, water, gas_dist_volume=None):
        """
        Creates or updates a reading entry for a period. Automatically fetches current tariffs 
        and calculates programmatic costs.
        """
        # Fetch current tariffs
        tariffs = db.get_all_tariffs()
        
        # Check if record already exists to preserve existing fields
        existing = db.get_reading(period) or {}
        
        # Set up dictionary for saving
        reading_data = {
            'period': period,
            
            # Electricity
            'elec_day_reading': elec_day,
            'elec_night_reading': elec_night,
            'elec_day_tariff': existing.get('elec_day_tariff') or tariffs.get('electricity_day', 0.0),
            'elec_night_tariff': existing.get('elec_night_tariff') or tariffs.get('electricity_night', 0.0),
            
            # Gas
            'gas_reading': gas,
            'gas_tariff': existing.get('gas_tariff') or tariffs.get('gas', 0.0),
            
            # Gas Dist
            'gas_dist_volume': gas_dist_volume if gas_dist_volume is not None else (existing.get('gas_dist_volume') or tariffs.get('gas_distribution_volume', 70.66)),
            'gas_dist_tariff': existing.get('gas_dist_tariff') or tariffs.get('gas_distribution', 0.0),
            
            # Water
            'water_reading': water,
            'water_supply_tariff': existing.get('water_supply_tariff') or tariffs.get('water_supply', 0.0),
            'water_drainage_tariff': existing.get('water_drainage_tariff') or tariffs.get('water_drainage', 0.0),
            'water_sub_tariff': existing.get('water_sub_tariff') or tariffs.get('water_subscription', 0.0),
            
            # Garbage
            'garbage_tariff': existing.get('garbage_tariff') or tariffs.get('garbage', 0.0)
        }
        
        # Merge other existing fields to avoid overwriting them
        for k, v in existing.items():
            if k not in reading_data:
                reading_data[k] = v
                
        # Perform calculations
        calculated_data = UtilityCalculator.calculate_all(period, reading_data)
        
        # Save to DB
        db.save_reading(calculated_data)
        return calculated_data

    @staticmethod
    def update_single_tariff_and_recalculate(service_name, value, recalculate_unpaid=True):
        """Updates a tariff and optionally recalculates all unpaid periods."""
        # 1. Update active tariff
        db.update_tariff(service_name, value)
        
        if not recalculate_unpaid:
            return
        
        # Map service_name to corresponding fields in readings table
        tariff_mappings = {
            'electricity_day': ('elec_day_tariff', 'elec_paid_status'),
            'electricity_night': ('elec_night_tariff', 'elec_paid_status'),
            'gas': ('gas_tariff', 'gas_paid_status'),
            'gas_distribution': ('gas_dist_tariff', 'gas_dist_paid_status'),
            'water_supply': ('water_supply_tariff', 'water_paid_status'),
            'water_drainage': ('water_drainage_tariff', 'water_paid_status'),
            'water_subscription': ('water_sub_tariff', 'water_paid_status'),
            'garbage': ('garbage_tariff', 'garbage_paid_status')
        }
        
        if service_name not in tariff_mappings:
            return
            
        tariff_field, status_field = tariff_mappings[service_name]
        
        # 2. Get all unpaid readings
        unpaid = db.get_unpaid_readings()
        for record in unpaid:
            # Check if this specific utility is unpaid (status = 0)
            if record.get(status_field) == 0:
                record[tariff_field] = value
                # Recalculate
                recalc_record = UtilityCalculator.calculate_all(record['period'], record)
                db.save_reading(recalc_record)

    @staticmethod
    def mark_as_paid(period, service, choice, custom_amount=None):
        """
        Marks a specific service in a period as paid.
        Choices: 'calculated', 'billed', 'custom'
        """
        record = db.get_reading(period)
        if not record:
            return False
            
        prefix = SERVICE_PREFIX_MAP.get(service)
        
        if not prefix:
            return False
            
        calc_val = record.get(f"{prefix}_calculated") or 0.0
        billed_val = record.get(f"{prefix}_billed")
        
        if choice == 'calculated':
            paid_val = calc_val
        elif choice == 'billed':
            paid_val = billed_val if billed_val is not None else calc_val
        else: # custom
            paid_val = float(custom_amount) if custom_amount is not None else 0.0
            
        record[f"{prefix}_paid"] = paid_val
        record[f"{prefix}_paid_status"] = 1 # Paid
        record[f"{prefix}_paid_date"] = datetime.now().strftime("%Y-%m-%d")
        
        db.save_reading(record)
        return True

    @staticmethod
    def mark_as_prepaid_or_skip(period, service):
        """Marks a service in a period as Prepaid/Skipped (status 2)."""
        record = db.get_reading(period)
        if not record:
            return False
            
        prefix = SERVICE_PREFIX_MAP.get(service)
        
        if not prefix:
            return False
            
        record[f"{prefix}_paid"] = 0.0
        record[f"{prefix}_paid_status"] = 2 # Prepaid/Skip
        record[f"{prefix}_paid_date"] = datetime.now().strftime("%Y-%m-%d")
        
        db.save_reading(record)
        return True

    @staticmethod
    def get_reminders():
        """
        Generates reminders:
        1. Meter readings missing for the previous month (starting from 1st of current month).
        2. Payment deadline (before 20th of the month) if unpaid readings exist.
        """
        now = datetime.now()
        day_of_month = now.day
        
        # Calculate previous month period (YYYY-MM)
        if now.month == 1:
            prev_month = 12
            prev_year = now.year - 1
        else:
            prev_month = now.month - 1
            prev_year = now.year
        prev_period = f"{prev_year:04d}-{prev_month:02d}"
        
        reminders = []
        
        # 1. Check if readings exist for the previous month
        prev_reading = db.get_reading(prev_period)
        
        missing_services = []
        if not prev_reading:
            missing_services = ["Світло", "Газ", "Вода"]
        else:
            if prev_reading.get('elec_day_reading') is None:
                missing_services.append("Світло")
            if prev_reading.get('gas_reading') is None:
                missing_services.append("Газ")
            if prev_reading.get('water_reading') is None:
                missing_services.append("Вода")
                
        if missing_services:
            reminders.append({
                'type': 'readings_missing',
                'title': 'Необхідно подати показники!',
                'message': f"Не введено показники за попередній період ({prev_period}) для: {', '.join(missing_services)}."
            })
        
        # 2. Check for unpaid bills (deadline 20th)
        unpaid = db.get_unpaid_readings()
        if unpaid:
            # If date is between 1 and 20
            if day_of_month <= 20:
                reminders.append({
                    'type': 'payment_due',
                    'title': 'Наближається термін оплати (до 20 числа)!',
                    'message': f"У вас є неоплачені комунальні послуги за попередні періоди."
                })
                
        return reminders

    @staticmethod
    def generate_messenger_text(period):
        """Generates a text report of readings for quick copying to messengers."""
        curr = db.get_reading(period)
        if not curr:
            return "Немає даних за цей період."
            
        prev = db.get_previous_reading(period)
        
        lines = [f"📊 Показники за {period}:"]
        
        # Elec
        if curr.get('elec_day_reading') is not None and curr.get('elec_night_reading') is not None:
            lines.append(f"⚡ Електрика: День {curr['elec_day_reading']} | Ніч {curr['elec_night_reading']}")
            if prev and prev.get('elec_day_reading') is not None:
                diff_d = curr['elec_day_reading'] - prev['elec_day_reading']
                diff_n = curr['elec_night_reading'] - prev['elec_night_reading']
                lines.append(f"   (спожито: день {diff_d:.1f} кВт, ніч {diff_n:.1f} кВт)")
                
        # Gas
        if curr.get('gas_reading') is not None:
            lines.append(f"🔥 Газ: {curr['gas_reading']}")
            if prev and prev.get('gas_reading') is not None:
                diff = curr['gas_reading'] - prev['gas_reading']
                lines.append(f"   (спожито: {diff:.1f} м³)")
                
        # Water
        if curr.get('water_reading') is not None:
            lines.append(f"💧 Вода: {curr['water_reading']}")
            if prev and prev.get('water_reading') is not None:
                diff = curr['water_reading'] - prev['water_reading']
                lines.append(f"   (спожито: {diff:.1f} м³)")
                
        return "\n".join(lines)
