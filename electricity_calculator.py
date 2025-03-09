class ElectricityCalculator:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def calculate_bill(self, meter_id, day_kwh, night_kwh):
        last_reading = self.db_manager.get_last_reading(meter_id)
        if last_reading is None:
            prev_day, prev_night = 0, 0
            self.db_manager.add_new_meter(meter_id)
        else:
            _, prev_day, prev_night = last_reading

        day_rate, night_rate, day_adj, night_adj = self.db_manager.get_tariffs()
        warnings = []
        if day_kwh < prev_day:
            warnings.append("Показник 'день' менший за попередній! Додаємо 100 кВт.")
            day_kwh += 100

        if night_kwh < prev_night:
            warnings.append("Показник 'ніч' менший за попередній! Додаємо 80 кВт.")
            night_kwh += 80

        day_usage = day_kwh - prev_day
        night_usage = night_kwh - prev_night
        total_cost = day_usage * day_rate + night_usage * night_rate
        self.db_manager.update_meter_reading(meter_id, day_kwh, night_kwh)
        self.db_manager.add_to_history(meter_id, day_usage, night_usage, total_cost)
        return {
            'day_usage': day_usage,
            'night_usage': night_usage,
            'total_cost': total_cost,
            'warnings': warnings
        }
