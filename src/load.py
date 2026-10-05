import os
from pathlib import Path

import pandas as pd
import pg8000.dbapi
from dotenv import load_dotenv

from extract import get_weather
from transform import transform_weather


# --------------------------------------------------
# Load .env file from the project root
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


# --------------------------------------------------
# Connect to PostgreSQL
# --------------------------------------------------

def get_database_connection():

    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    print(f"   ENV file found: {ENV_FILE.exists()}")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Database: {database}")
    print(f"   User: {user}")
    print(f"   Password loaded: {password is not None}")

    missing_variables = []

    if not host:
        missing_variables.append("DB_HOST")

    if not port:
        missing_variables.append("DB_PORT")

    if not database:
        missing_variables.append("DB_NAME")

    if not user:
        missing_variables.append("DB_USER")

    if not password:
        missing_variables.append("DB_PASSWORD")

    if missing_variables:
        raise ValueError(
            "Missing environment variables: "
            + ", ".join(missing_variables)
        )

    connection = pg8000.dbapi.connect(
        host=host,
        port=int(port),
        database=database,
        user=user,
        password=password,
    )

    return connection


# --------------------------------------------------
# Create weather table
# --------------------------------------------------

def create_weather_table(connection):

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

    print("   Weather table ready.")


# --------------------------------------------------
# Load data into PostgreSQL
# --------------------------------------------------

def load_weather(df, connection):

    if df.empty:
        print("   No weather data available to load.")
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

        observed_at = row["observed_at"]

        if hasattr(observed_at, "to_pydatetime"):
            observed_at = observed_at.to_pydatetime()

        extracted_at = row["extracted_at"]

        if hasattr(extracted_at, "to_pydatetime"):
            extracted_at = extracted_at.to_pydatetime()

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
            str(row["city"]),
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
        f"   {len(records)} weather records loaded successfully."
    )


# --------------------------------------------------
# Run complete ETL pipeline
# --------------------------------------------------

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