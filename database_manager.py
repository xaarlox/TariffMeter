import mysql.connector
from datetime import datetime


class DatabaseManager:
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()

    def get_tariffs(self):
        self.cursor.execute("SELECT day_rate, night_rate, day_adjustment, night_adjustment FROM tariffs LIMIT 1")
        return self.cursor.fetchone()

    def get_last_reading(self, meter_id):
        self.cursor.execute("SELECT last_date, prev_day_kwh, prev_night_kwh FROM meters WHERE meter_id=%s", (meter_id,))
        return self.cursor.fetchone()

    def update_meter_reading(self, meter_id, day_kwh, night_kwh):
        self.cursor.execute(
            "UPDATE meters SET last_date=%s, prev_day_kwh=%s, prev_night_kwh=%s WHERE meter_id=%s",
            (datetime.now().date(), day_kwh, night_kwh, meter_id)
        )
        self.connection.commit()

    def add_new_meter(self, meter_id):
        self.cursor.execute(
            "INSERT INTO meters (meter_id, last_date, prev_day_kwh, prev_night_kwh) VALUES (%s, %s, %s, %s)",
            (meter_id, datetime.now().date(), 0, 0)
        )
        self.connection.commit()

    def add_to_history(self, meter_id, day_usage, night_usage, total_cost):
        self.cursor.execute(
            "INSERT INTO history_table (meter_id, curr_date, day_kwh, night_kwh, total_cost) VALUES (%s, %s, %s, %s, %s)",
            (meter_id, datetime.now().date(), day_usage, night_usage, total_cost)
        )
        self.connection.commit()

    def get_history(self, meter_id):
        self.cursor.execute(
            "SELECT curr_date, day_kwh, night_kwh, total_cost FROM history_table WHERE meter_id=%s ORDER BY curr_date DESC",
            (meter_id,)
        )
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.connection.close()
