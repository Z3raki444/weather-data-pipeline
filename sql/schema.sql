CREATE TABLE IF NOT EXISTS weather (
    id BIGSERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    temperature DOUBLE PRECISION,
    humidity INTEGER,
    precipitation DOUBLE PRECISION,
    wind_speed DOUBLE PRECISION,
    weather_code INTEGER,
    observed_at TIMESTAMP NOT NULL,
    UNIQUE (city, observed_at)
);
