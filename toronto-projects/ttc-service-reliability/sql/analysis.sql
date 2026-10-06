-- Run from the project root after python src/analyze.py
CREATE OR REPLACE VIEW delays AS
SELECT * FROM read_csv_auto('data/clean_delays.csv', header=true);

-- Monthly operational picture
SELECT month, count(*) AS incidents, sum(delay_min) AS reported_delay_minutes,
       avg(delay_min) AS avg_delay_min
FROM delays GROUP BY 1 ORDER BY 1;

-- Line comparisons
SELECT line, count(*) AS incidents, sum(delay_min) AS reported_delay_minutes,
       median(delay_min) AS median_delay_min
FROM delays GROUP BY 1 ORDER BY reported_delay_minutes DESC;

-- Top report locations
SELECT station, count(*) AS incidents, sum(delay_min) AS reported_delay_minutes
FROM delays GROUP BY 1 ORDER BY reported_delay_minutes DESC LIMIT 15;

-- Time and day pattern
SELECT day_of_week, hour, count(*) AS incidents, sum(delay_min) AS reported_delay_minutes
FROM delays GROUP BY 1,2 ORDER BY incidents DESC;
