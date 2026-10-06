# Power BI build notes

## Model

1. Run `python -m src.analyze` from the project root. This downloads the UCI source (once) and creates `data/retail_sales_clean.csv` plus `data/customer_summary.csv`.
2. In Power BI Desktop, import those CSVs. Name the tables `SalesLines` and `CustomerSummary`.
3. Set types: `InvoiceDate` = Date/Time, `CustomerID` = Whole Number, `Quantity` = Whole Number, `UnitPrice` and `RevenueGBP` = Decimal Number, `InvoiceNo` and `StockCode` = Text.
4. Create a one-to-many relationship from `CustomerSummary[CustomerID]` to `SalesLines[CustomerID]`. Leave unmatched/blank customer rows in the sales fact so total sales reconcile.
5. Create a date table and relate `Calendar[Date]` to the date-only field in `SalesLines`. `InvoiceDate` is a timestamp; add `OrderDate = DATE(YEAR(SalesLines[InvoiceDate]), MONTH(SalesLines[InvoiceDate]), DAY(SalesLines[InvoiceDate]))` or convert to date in Power Query.
6. Mark `Calendar` as the date table. Sort month names by `MonthStart` or use the numeric `YearMonth` key.

The Python RFM snapshot uses 2011-12-10 as its as-of date. Customer segment measures are full-period values and intentionally do not change with a date slicer. Sales/order measures do respond to date filters.

## Dashboard layout

- KPI cards: Sales (GBP), orders, average order value, identified customers, repeat-customer rate.
- Line chart: monthly sales (GBP), with the final month clearly marked partial.
- Bar chart: sales by RFM segment and top 10 countries.
- Matrix: top merchandise items by sales and units, excluding service/adjustment codes.
- Slicers: month, country, customer segment.

## Definitions

Sales are positive quantity × positive unit price on invoices not starting with `C`. This is line revenue, not profit or net revenue. Rows without CustomerID remain in the sales fact, but are excluded from identified-customer and RFM counts. See `results/analysis_summary.md` for limitations and stock-code exclusions.

DAX measures are in `Measures.dax`; Power Query transformations are in `PowerQuery.m`.
