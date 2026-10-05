import pandas as pd

from extract import get_weather


def transform_weather(records):

    df = pd.DataFrame(records)

    # Convert timestamps
    df["observed_at"] = pd.to_datetime(df["observed_at"])
    df["extracted_at"] = pd.to_datetime(df["extracted_at"])

    # Ensure numeric columns are numeric
    numeric_columns = [
        "temperature",
        "humidity",
        "precipitation",
        "wind_speed",
        "weather_code"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Remove duplicate records
    df = df.drop_duplicates(
        subset=["city", "observed_at"]
    )

    # Remove rows missing critical values
    df = df.dropna(
        subset=[
            "city",
            "temperature",
            "humidity",
            "observed_at"
        ]
    )

    # Basic validation
    df = df[
        (df["humidity"] >= 0)
        & (df["humidity"] <= 100)
    ]

    df = df[
        df["precipitation"] >= 0
    ]

    return df


if __name__ == "__main__":

    raw_data = get_weather()

    clean_data = transform_weather(raw_data)

    print(clean_data)

    print("\nData Types:")
    print(clean_data.dtypes)