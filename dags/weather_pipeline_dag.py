import sys
import pendulum

from airflow.sdk import dag, task

sys.path.insert(0, "/opt/airflow/src")

from extract import get_weather
from transform import transform_weather
from load import get_connection, load_weather


@dag(
    dag_id="weather_pipeline",
    schedule=None,
    start_date=pendulum.datetime(2026, 10, 1, tz="UTC"),
    catchup=False,
    tags=["weather", "etl"],
)
def weather_pipeline():

    @task
    def run_weather_etl():

        print("Extracting weather data...")
        raw_data = get_weather()

        print(f"Extracted {len(raw_data)} records.")

        print("Transforming weather data...")
        clean_data = transform_weather(raw_data)

        print(f"{len(clean_data)} clean records ready.")

        connection = None

        try:
            print("Connecting to PostgreSQL...")
            connection = get_connection()

            print("Loading weather data...")
            load_weather(clean_data, connection)

            print("Weather ETL completed successfully.")

        finally:
            if connection is not None:
                connection.close()

    run_weather_etl()


weather_pipeline()