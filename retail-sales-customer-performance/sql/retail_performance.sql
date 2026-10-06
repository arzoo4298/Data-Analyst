-- Retail sales & customer performance queries (DuckDB).
-- Run after: python -m src.analyze
-- Source fact: data/retail_sales_clean.csv (all positive sales lines; see README for definitions).

CREATE OR REPLACE VIEW sales AS
SELECT * FROM read_csv_auto('data/retail_sales_clean.csv', header = true, sample_size = -1);

CREATE OR REPLACE VIEW customers AS
SELECT * FROM read_csv_auto('data/customer_summary.csv', header = true, sample_size = -1);

-- 1. Monthly revenue, invoices, identified customers and average order value.
SELECT
    date_trunc('month', InvoiceDate)::DATE AS month_start,
    sum(RevenueGBP) AS sales_gbp,
    count(DISTINCT InvoiceNo) AS orders,
    count(DISTINCT CustomerID) AS identified_customers,
    sum(Quantity) AS units_sold,
    sum(RevenueGBP) / nullif(count(DISTINCT InvoiceNo), 0) AS average_order_value_gbp
FROM sales
GROUP BY 1
ORDER BY 1;

-- 2. Country performance. Customer counts exclude lines without CustomerID.
SELECT
    Country,
    sum(RevenueGBP) AS sales_gbp,
    sum(RevenueGBP) / sum(sum(RevenueGBP)) OVER () AS sales_share,
    count(DISTINCT InvoiceNo) AS orders,
    count(DISTINCT CustomerID) AS identified_customers
FROM sales
GROUP BY Country
ORDER BY sales_gbp DESC;

-- 3. Top merchandise items; omit postage, fees and adjustment stock codes.
SELECT
    StockCode,
    Description,
    sum(RevenueGBP) AS sales_gbp,
    sum(Quantity) AS units_sold,
    count(DISTINCT InvoiceNo) AS orders
FROM sales
WHERE upper(cast(StockCode AS VARCHAR)) NOT IN ('DOT', 'M', 'POST', 'D', 'C2', 'CRUK', 'AMAZONFEE')
GROUP BY StockCode, Description
ORDER BY sales_gbp DESC
LIMIT 15;

-- 4. RFM customer segments produced by Python; summarize the segment economics.
SELECT
    Segment,
    count(*) AS customers,
    sum(OrderCount) AS customer_orders,
    sum(RevenueGBP) AS sales_gbp,
    avg(RevenueGBP) AS average_customer_revenue_gbp,
    median(RecencyDays) AS median_recency_days,
    countif(OrderCount >= 2) AS repeat_customers
FROM customers
GROUP BY Segment
ORDER BY sales_gbp DESC;

-- 5. Reconcile identified-customer totals and repeat-customer rate.
SELECT
    count(*) AS identified_customers,
    countif(OrderCount >= 2) AS repeat_customers,
    countif(OrderCount >= 2) / count(*)::DOUBLE AS repeat_customer_rate,
    sum(RevenueGBP) AS identified_customer_sales_gbp
FROM customers;
