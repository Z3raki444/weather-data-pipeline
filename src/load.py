import os

import pandas as pd
import pg8000.dbapi
from dotenv import load_dotenv

from extract import get_weather
from transform import transform_weather


# Load variables from .env
load_dotenv()


def get_database_connection():
    """
    Connect to PostgreSQL using pg8000.
    """

    connection = pg8000.dbapi.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "weather_pipeline"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
    )

    return connection


def create_weather_table(connection):
    """
    Create the weather table if it does not already exist.
    """

    query = """
    CREATE TABLE IF NOT EXISTS weather (
        id BIGSERIAL PRIMARY KEY,

        city VARCHAR(100) NOT NULL,

        temperature DOUBLE PRECISION,

        humidity INTEGER,

        precipitation DOUBLE PRECISION,

        wind_speed DOUBLE PRECISION,

        weather_code INTEGER,

        observed_at TIMESTAMP NOT NULL,

        extracted_at TIMESTAMPTZ NOT NULL,

        UNIQUE(city, observed_at)
    );
    """

    cursor = connection.cursor()

    cursor.execute(query)

    connection.commit()

    cursor.close()

    print("Weather table ready.")


def load_weather(df, connection):
    """
    Load transformed weather data into PostgreSQL.
    """

    if df.empty:
        print("No weather data available to load.")
        return

    insert_query = """
    INSERT INTO weather (
        city,
        temperature,
        humidity,
        precipitation,
        wind_speed,
        weather_code,
        observed_at,
        extracted_at
    )

    VALUES (
        %s,
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
        weather_code = EXCLUDED.weather_code,
        extracted_at = EXCLUDED.extracted_at;
    """

    records = []

    for _, row in df.iterrows():

        # Convert pandas Timestamp to Python datetime
        observed_at = row["observed_at"]

        if hasattr(observed_at, "to_pydatetime"):
            observed_at = observed_at.to_pydatetime()

        extracted_at = row["extracted_at"]

        if hasattr(extracted_at, "to_pydatetime"):
            extracted_at = extracted_at.to_pydatetime()

        # Handle possible missing values
        precipitation = (
            None
            if pd.isna(row["precipitation"])
            else float(row["precipitation"])
        )

        wind_speed = (
            None
            if pd.isna(row["wind_speed"])
            else float(row["wind_speed"])
        )

        weather_code = (
            None
            if pd.isna(row["weather_code"])
            else int(row["weather_code"])
        )

        record = (
            row["city"],
            float(row["temperature"]),
            int(row["humidity"]),
            precipitation,
            wind_speed,
            weather_code,
            observed_at,
            extracted_at,
        )

        records.append(record)

    cursor = connection.cursor()

    cursor.executemany(
        insert_query,
        records
    )

    connection.commit()

    cursor.close()

    print(
        f"{len(records)} weather records loaded successfully."
    )


if __name__ == "__main__":

    connection = None

    try:

        print("\n1. Extracting weather data...")

        raw_data = get_weather()

        print(
            f"   Extracted {len(raw_data)} records."
        )

        print("\n2. Transforming weather data...")

        clean_data = transform_weather(raw_data)

        print(
            f"   {len(clean_data)} clean records ready."
        )

        print("\n3. Connecting to PostgreSQL...")

        connection = get_database_connection()

        print(
            "   PostgreSQL connection successful."
        )

        print("\n4. Creating weather table...")

        create_weather_table(connection)

        print("\n5. Loading weather data...")

        load_weather(
            clean_data,
            connection
        )

        print(
            "\nETL pipeline completed successfully!"
        )

    except Exception as error:

        print(
            "\nPipeline failed!"
        )

        print(
            f"Error: {error}"
        )

    finally:

        if connection is not None:

            connection.close()

            print(
                "\nDatabase connection closed."
            )