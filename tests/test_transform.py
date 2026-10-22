"""Unit tests for transformation logic, without calling Open-Meteo."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from transform import transform_weather


class WeatherTransformTests(unittest.TestCase):
    def test_filters_invalid_rows_and_duplicates(self):
        source = [
            {"city":"Berlin","temperature":"12.5","humidity":"72",
             "precipitation":"0","wind_speed":"5","weather_code":"3",
             "observed_at":"2026-10-22T10:00"},
            {"city":"Berlin","temperature":"12.5","humidity":"72",
             "precipitation":"0","wind_speed":"5","weather_code":"3",
             "observed_at":"2026-10-22T10:00"},
            {"city":"Hamburg","temperature":"8","humidity":"130",
             "precipitation":"0","wind_speed":"4","weather_code":"1",
             "observed_at":"2026-10-22T10:00"},
            {"city":"Munich","temperature":"7","humidity":"80",
             "precipitation":"-1","wind_speed":"3","weather_code":"1",
             "observed_at":"2026-10-22T10:00"},
        ]
        result = transform_weather(source)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["city"], "Berlin")
        self.assertAlmostEqual(float(result.iloc[0]["temperature"]), 12.5)

    def test_allows_optional_null_measurements(self):
        source = [
            {"city":"Cologne","temperature":10,"humidity":60,
             "precipitation":None,"wind_speed":None,"weather_code":None,
             "observed_at":"2026-10-22T10:00"},
        ]
        result = transform_weather(source)
        self.assertEqual(result["city"].tolist(), ["Cologne"])


if __name__ == "__main__":
    unittest.main()
