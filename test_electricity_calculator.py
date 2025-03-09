import unittest
from unittest.mock import MagicMock
from electricity_calculator import ElectricityCalculator


class TestElectricityCalculator(unittest.TestCase):
    def setUp(self):
        self.db_manager = MagicMock()
        self.calculator = ElectricityCalculator(self.db_manager)
        self.db_manager.get_tariffs.return_value = (4.32, 2.16, 0, 0)

    def test_update_existing_meter_reading(self):
        self.db_manager.get_last_reading.return_value = ('2025-03-01', 100, 50)
        result = self.calculator.calculate_bill('123', 150, 80)
        self.assertEqual(result['day_usage'], 50)
        self.assertEqual(result['night_usage'], 30)
        self.assertEqual(result['total_cost'], 50 * 4.32 + 30 * 2.16)
        self.db_manager.update_meter_reading.assert_called_with('123', 150, 80)

    def test_new_meter_reading(self):
        self.db_manager.get_last_reading.return_value = None
        result = self.calculator.calculate_bill('456', 60, 40)
        self.assertEqual(result['day_usage'], 60)
        self.assertEqual(result['night_usage'], 40)
        self.assertEqual(result['total_cost'], 60 * 4.32 + 40 * 2.16)
        self.db_manager.add_new_meter.assert_called_with('456')
        self.db_manager.update_meter_reading.assert_called_with('456', 60, 40)

    def test_lower_night_reading(self):
        self.db_manager.get_last_reading.return_value = ('2025-03-01', 100, 50)
        result = self.calculator.calculate_bill('123', 150, 30)
        self.assertEqual(result['night_usage'], 60)
        self.assertIn("ніч", result['warnings'][0])

    def test_lower_day_reading(self):
        self.db_manager.get_last_reading.return_value = ('2025-03-01', 100, 50)
        result = self.calculator.calculate_bill('123', 90, 80)
        self.assertEqual(result['day_usage'], 90)
        self.assertIn("день", result['warnings'][0])

    def test_lower_both_readings(self):
        self.db_manager.get_last_reading.return_value = ('2025-03-01', 100, 50)
        result = self.calculator.calculate_bill('123', 90, 30)
        self.assertEqual(result['day_usage'], 90)
        self.assertEqual(result['night_usage'], 60)
        self.assertEqual(len(result['warnings']), 2)


if __name__ == '__main__':
    unittest.main()
