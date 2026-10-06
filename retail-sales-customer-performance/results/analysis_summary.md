# Retail sales and customer performance: summary

## Summary

The cleaned positive-sales population contains **530,104 line items** across **19,960 invoices**, generating **£10,666,685** in recorded line revenue. The source spans 2010-12-01 to 2011-12-09; the final month is partial.
The dataset identifies **4,338 customers**. **2,845 (65.6%)** placed at least two distinct invoices in the observed period.
**United Kingdom** is the largest market at **£9,025,222**. **REGENCY CAKESTAND 3 TIER** is the highest-revenue item at **£174,485**.

## Customer performance

Customer segments use recency, frequency, and monetary value at the day after the last source transaction. Recent/frequent/high-spend groups contribute the greatest observed sales; see `customer_segments.csv` for segment counts and value.

- **Champions**: 1,314 customers, £6,494,963 revenue, median recency 15 days
- **At risk**: 656 customers, £1,055,268 revenue, median recency 96 days
- **Others**: 548 customers, £513,252 revenue, median recency 51 days
- **Hibernating**: 1,247 customers, £356,549 revenue, median recency 191 days
- **Potential loyalists**: 136 customers, £332,659 revenue, median recency 23 days
- **Loyal customers**: 199 customers, £92,077 revenue, median recency 22 days
- **Recent customers**: 238 customers, £66,639 revenue, median recency 26 days

## Definitions and limitations

- Sales revenue is the sum of positive quantity × positive unit price on invoices that do not begin with `C`. It includes valid postage/service lines, so it is line revenue in GBP, not merchandise-only revenue, profit, cash received, or revenue net of all return adjustments.
- Customers without a CustomerID remain in sales, invoice, unit, country, and product totals, but are excluded from customer counts and RFM segments. Customer KPIs therefore have an identified-customer denominator.
- Returns/cancellations, zero or negative quantities, nonpositive prices, and missing dates are excluded from the positive-sales fact table. Counts are available in `dashboard_kpis.json`.
- This is a single historical retailer dataset from 2010–2011. Results are descriptive and do not represent current retail demand or causal campaign impact.
- The merchandise ranking omits service/adjustment stock codes `DOT`, `M`, `POST`, `D`, `C2`, `CRUK`, and `AMAZONFEE`; total sales revenue still includes qualifying positive service lines.
- RFM groups are heuristic portfolio segments, not customer-level treatment recommendations.
