import os
from pathlib import Path

import pandas as pd
import pg8000.dbapi
from dotenv import load_dotenv

from extract import get_weather
from transform import transform_weather


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


def get_connection():

    return pg8000.dbapi.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def load_weather(df, connection):

    query = """
    INSERT INTO weather (
        city,
        temperature,
        humidity,
        precipitation,
        wind_speed,
        weather_code,
        observed_at
    )
    VALUES (
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s
    )
    ON CONFLICT (city, observed_at)
    DO UPDATE SET
        temperature = EXCLUDED.temperature,
        humidity = EXCLUDED.humidity,
        precipitation = EXCLUDED.precipitation,
        wind_speed = EXCLUDED.wind_speed,
        weather_code = EXCLUDED.weather_code;
    """

    cursor = connection.cursor()

    records = []

    for _, row in df.iterrows():

        observed_at = row["observed_at"]

        if hasattr(observed_at, "to_pydatetime"):
            observed_at = observed_at.to_pydatetime()

        records.append(
            (
                row["city"],
                float(row["temperature"]),
                int(row["humidity"]),
                float(row["precipitation"])
                if not pd.isna(row["precipitation"])
                else None,
                float(row["wind_speed"])
                if not pd.isna(row["wind_speed"])
                else None,
                int(row["weather_code"])
                if not pd.isna(row["weather_code"])
                else None,
                observed_at,
            )
        )

    cursor.executemany(
        query,
        records
    )

    connection.commit()
    cursor.close()

    print(
        f"{len(records)} records loaded successfully."
    )


if __name__ == "__main__":

    connection = None

    try:

        print("1. Extracting weather data...")

        raw_data = get_weather()

        print(
            f"   Extracted {len(raw_data)} records."
        )


        print("2. Transforming weather data...")

        clean_data = transform_weather(raw_data)

        print(
            f"   {len(clean_data)} clean records ready."
        )


        print("3. Connecting to PostgreSQL...")

        connection = get_connection()

        print(
            "   PostgreSQL connection successful."
        )


        print("4. Loading data...")

        load_weather(
            clean_data,
            connection
        )


        print(
            "ETL pipeline completed successfully!"
        )


    except Exception as error:

        print(
            f"Pipeline failed: {error}"
        )


    finally:

        if connection is not None:
            connection.close()