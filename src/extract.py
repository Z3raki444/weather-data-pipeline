import requests
from datetime import datetime, timezone


CITIES = {
    "Berlin": (52.5200, 13.4050),
    "Hamburg": (53.5511, 9.9937),
    "Munich": (48.1351, 11.5820),
    "Frankfurt": (50.1109, 8.6821),
    "Cologne": (50.9375, 6.9603),
}

API_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather():
    weather_data = []

    for city, coordinates in CITIES.items():
        latitude, longitude = coordinates

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "weather_code",
                "wind_speed_10m",
            ],
            "timezone": "Europe/Berlin",
        }

        try:
            response = requests.get(
                API_URL,
                params=params,
                timeout=30,
            )

            response.raise_for_status()

            data = response.json()
            current = data["current"]

            weather_data.append(
                {
                    "city": city,
                    "temperature": current.get("temperature_2m"),
                    "humidity": current.get("relative_humidity_2m"),
                    "precipitation": current.get("precipitation"),
                    "wind_speed": current.get("wind_speed_10m"),
                    "weather_code": current.get("weather_code"),
                    "observed_at": current.get("time"),
                    "extracted_at": datetime.now(timezone.utc).isoformat(),
                }
            )

        except requests.RequestException as error:
            print(f"Failed to fetch weather for {city}: {error}")

    return weather_data


if __name__ == "__main__":
    records = get_weather()

    for record in records:
        print(record)