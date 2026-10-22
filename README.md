# Weather Data Pipeline

A containerized data engineering project that extracts live weather data from the Open-Meteo API, transforms and validates it with Pandas, loads it into PostgreSQL, and orchestrates the workflow hourly with Apache Airflow.

## Architecture

```text
Open-Meteo API
      |
      v
Python Extract
      |
      v
Pandas Transform
      |
      v
PostgreSQL
      ^
      |
Apache Airflow
      |
    Docker
```

## Project Screenshots

### Airflow DAG Success

![Airflow DAG success](assets/airflow-success.png)

### Airflow Run History

![Airflow run history](assets/airflow-dag-runs.png)

### PostgreSQL Weather Data

![PostgreSQL weather data](assets/postgres-weather-table.png)

## Features

- Extracts current weather data for Berlin, Hamburg, Munich, Frankfurt, and Cologne.
- Collects temperature, humidity, precipitation, wind speed, weather code, and observation time.
- Converts and validates data types with Pandas.
- Removes duplicate records and invalid values.
- Loads records into PostgreSQL with an idempotent upsert on `(city, observed_at)`.
- Runs the ETL workflow automatically every hour using Apache Airflow.
- Uses Docker Compose for the Airflow development environment.
- Keeps application database credentials outside source control.

## Tech Stack

- Python
- Pandas
- Requests
- PostgreSQL
- pg8000
- Apache Airflow 3.3.2
- Docker / Docker Compose
- Open-Meteo API

## Project Structure

```text
weather-data-pipeline/
├── dags/
│   ├── hello_airflow.py
│   └── weather_pipeline_dag.py
├── src/
│   ├── extract.py
│   ├── transform.py
│   └── load.py
├── sql/
│   └── schema.sql
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
├── .env.airflow.example
├── .env.weather.example
├── .gitignore
└── README.md
```

## ETL Flow

### 1. Extract

`src/extract.py` calls the Open-Meteo API for five German cities and returns structured weather records.

### 2. Transform

`src/transform.py`:

- converts timestamps to datetime values;
- converts weather measurements to numeric types;
- removes duplicate city/timestamp records;
- removes rows missing required values;
- validates humidity, precipitation, and wind speed.

### 3. Load

`src/load.py` connects to PostgreSQL and loads records into the `weather` table.

The load is idempotent:

```sql
ON CONFLICT (city, observed_at)
DO UPDATE
```

This prevents duplicate observations when the same city and timestamp are processed again.

### 4. Orchestration

`dags/weather_pipeline_dag.py` runs the ETL workflow with Apache Airflow.

Current schedule:

```text
@hourly
```

Catchup is disabled, so Airflow does not automatically backfill historical hourly runs.

## Database Schema

The project stores weather observations in PostgreSQL.

```text
weather
├── id
├── city
├── temperature
├── humidity
├── precipitation
├── wind_speed
├── weather_code
└── observed_at
```

The table definition is available in `sql/schema.sql`.

## Local Setup

### Prerequisites

Install:

- Python 3
- PostgreSQL
- Docker Desktop
- Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/Z3raki444/weather-data-pipeline.git
cd weather-data-pipeline
```

### 2. Create the weather database

Create a PostgreSQL database named:

```text
weather_pipeline
```

Then run:

```text
sql/schema.sql
```

against that database.

### 3. Configure local weather database credentials

Copy:

```text
.env.weather.example
```

to:

```text
.env.weather
```

and replace the placeholder values with your local PostgreSQL credentials.

For a Python process running directly on your machine, the host is normally:

```text
localhost
```

### 4. Configure Airflow

Copy:

```text
.env.airflow.example
```

to:

```text
.env.airflow
```

Generate a Fernet key and set it in the file.

When Airflow runs in Docker and connects to PostgreSQL running on the host machine, use:

```text
WEATHER_DB_HOST=host.docker.internal
```

### 5. Build and start Airflow

```bash
docker compose build
docker compose up -d
```

Check the containers:

```bash
docker compose ps
```

Open the Airflow UI at:

```text
http://localhost:8080
```

### 6. Run the ETL manually

To test the Python ETL without Airflow:

```bash
python src/load.py
```

### 7. Trigger the Airflow DAG

```bash
docker compose exec airflow-scheduler airflow dags trigger weather_pipeline
```

Check runs:

```bash
docker compose exec airflow-scheduler airflow dags list-runs weather_pipeline
```

## Data Quality Checks

The transformation step currently checks:

- required values for city, temperature, humidity, and observation time;
- humidity between 0 and 100;
- non-negative precipitation;
- non-negative wind speed;
- duplicate `city + observed_at` observations.

## Security

Credentials and secrets are intentionally excluded from Git.

Do not commit:

- `.env`
- `.env.airflow`
- `.env.weather`
- PostgreSQL passwords
- Airflow Fernet keys

Use the provided example environment files as templates.

## Future Improvements

Possible extensions include:

- Airflow retries and failure alerts;
- automated data-quality tasks;
- historical weather ingestion;
- dashboarding with Power BI, Grafana, or Streamlit;
- CI checks with GitHub Actions;
- cloud deployment;
- unit and integration tests.

## Portfolio Summary

This project demonstrates an end-to-end ETL workflow using API ingestion, Python data transformation, PostgreSQL persistence, Dockerized infrastructure, and scheduled orchestration with Apache Airflow.

## Automated quality checks

The [Python CI workflow](.github/workflows/ci.yml) runs offline transformation tests and Python syntax checks on pushes and pull requests. Run the tests locally with:

```bash
python -m unittest discover -s tests -v
```

GitHub Actions does not download live weather data or start Airflow/PostgreSQL. For the full integration check, follow the setup instructions above. Generated Airflow task logs are excluded from Git and screenshots remain in `assets/`.
