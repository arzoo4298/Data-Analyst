-- Run after python src/analyze.py
CREATE OR REPLACE VIEW trips AS
SELECT * FROM read_csv_auto('data/clean_trips.csv', header=true);

-- Rider mix and duration
SELECT user_type, count(*) AS trips, median(trip_minutes) AS median_trip_min,
       avg(trip_minutes) AS avg_trip_min
FROM trips GROUP BY 1 ORDER BY trips DESC;

-- Weekday/hour demand
SELECT weekday, hour, user_type, count(*) AS trips
FROM trips GROUP BY 1,2,3 ORDER BY trips DESC;

-- Most used station pairs
SELECT start_station, end_station, count(*) AS trips,
       avg(trip_minutes) AS avg_trip_min
FROM trips GROUP BY 1,2 ORDER BY trips DESC LIMIT 15;
