-- Run after python src/analyze.py
CREATE OR REPLACE VIEW site_month AS
SELECT * FROM read_csv_auto('data/clean_site_month.csv', header=true);

-- Trend by observation month
SELECT date_trunc('month', month)::DATE AS month,
       sum(charges) AS observed_charges,
       count(DISTINCT site_instance_id) AS sites_with_observations
FROM site_month GROUP BY 1 ORDER BY 1;

-- Ward ranking, using observed cells only
SELECT ward, sum(charges) AS observed_charges,
       count(*) AS site_month_rows,
       count(DISTINCT site_instance_id) AS site_instances
FROM site_month GROUP BY 1 ORDER BY observed_charges DESC;

-- Highest site-instance totals
SELECT site_code, location, ward, sum(charges) AS observed_charges,
       count(*) AS months_reported
FROM site_month GROUP BY 1,2,3 ORDER BY observed_charges DESC LIMIT 20;
