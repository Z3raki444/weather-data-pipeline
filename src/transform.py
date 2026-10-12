import pandas as pd

from extract import get_weather


def transform_weather(records):

    df = pd.DataFrame(records)

    # Convert observed_at to datetime
    df["observed_at"] = pd.to_datetime(
        df["observed_at"],
        errors="coerce"
    )

    # Convert numeric columns
    numeric_columns = [
        "temperature",
        "humidity",
        "precipitation",
        "wind_speed",
        "weather_code",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Remove duplicate weather records
    df = df.drop_duplicates(
        subset=["city", "observed_at"]
    )

    # Remove rows missing important values
    df = df.dropna(
        subset=[
            "city",
            "temperature",
            "humidity",
            "observed_at",
        ]
    )

    # Validate humidity
    df = df[
        (df["humidity"] >= 0)
        & (df["humidity"] <= 100)
    ]

    # Validate precipitation
    df = df[
        (df["precipitation"].isna())
        | (df["precipitation"] >= 0)
    ]

    # Validate wind speed
    df = df[
        (df["wind_speed"].isna())
        | (df["wind_speed"] >= 0)
    ]

    # Reset row numbers
    df = df.reset_index(drop=True)

    return df


if __name__ == "__main__":

    raw_data = get_weather()

    clean_data = transform_weather(raw_data)

    print("\nClean Weather Data:")
    print(clean_data)

    print("\nData Types:")
    print(clean_data.dtypes)

    print("\nMissing Values:")
    print(clean_data.isnull().sum())