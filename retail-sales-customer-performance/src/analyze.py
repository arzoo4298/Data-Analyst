"""Reproducible retail sales and customer-performance analysis using UCI Online Retail."""
from __future__ import annotations

import io
import json
import urllib.request
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
IMAGE_DIR = ROOT / "images"
SOURCE_URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
SOURCE_FILE = "Online Retail.xlsx"


def load_source(offline: bool = False) -> pd.DataFrame:
    """Load the official UCI workbook, downloading and caching it when required."""
    DATA_DIR.mkdir(exist_ok=True)
    source_path = DATA_DIR / SOURCE_FILE
    if not source_path.exists():
        if offline:
            raise FileNotFoundError(f"{source_path} is missing. Run once online without --offline.")
        request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "RetailPortfolio/1.0"})
        with urllib.request.urlopen(request, timeout=120) as response:
            archive_bytes = response.read()
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            matches = [name for name in archive.namelist() if name.lower().endswith(SOURCE_FILE.lower())]
            if len(matches) != 1:
                raise ValueError(f"Expected one {SOURCE_FILE} in the UCI archive; found {matches}.")
            source_path.write_bytes(archive.read(matches[0]))
    data = pd.read_excel(source_path, engine="openpyxl")
    expected = {"InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"}
    missing = expected - set(data.columns)
    if missing:
        raise ValueError(f"Dataset is missing expected columns: {sorted(missing)}")
    return data


def _quartile_score(values: pd.Series, high_is_good: bool) -> pd.Series:
    ranked = values.rank(method="first", ascending=True)
    scores = pd.qcut(ranked, 4, labels=[1, 2, 3, 4]).astype("int8")
    return (5 - scores if not high_is_good else scores).astype("int8")


def build_customer_summary(sales: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
    identified = sales[sales["CustomerID"].notna()].copy()
    customers = identified.groupby("CustomerID", as_index=False).agg(
        OrderCount=("InvoiceNo", "nunique"),
        UnitsSold=("Quantity", "sum"),
        RevenueGBP=("RevenueGBP", "sum"),
        LastPurchase=("InvoiceDate", "max"),
    )
    customers["RecencyDays"] = (as_of - customers["LastPurchase"].dt.normalize()).dt.days
    customers["RScore"] = _quartile_score(customers["RecencyDays"], high_is_good=False)
    customers["FScore"] = _quartile_score(customers["OrderCount"], high_is_good=True)
    customers["MScore"] = _quartile_score(customers["RevenueGBP"], high_is_good=True)
    r, f, m = customers["RScore"], customers["FScore"], customers["MScore"]
    conditions = [
        (r >= 3) & (f >= 3) & (m >= 3),
        (r >= 3) & (f >= 3),
        (r >= 3) & (f <= 2) & (m >= 3),
        (r >= 3) & (f == 1),
        (r <= 2) & (f >= 3),
        (r <= 2) & (f <= 2) & (m <= 2),
    ]
    labels = ["Champions", "Loyal customers", "Potential loyalists", "Recent customers", "At risk", "Hibernating"]
    customers["Segment"] = np.select(conditions, labels, default="Others")
    return customers


def build_monthly(sales: pd.DataFrame) -> pd.DataFrame:
    work = sales.assign(MonthStart=sales["InvoiceDate"].dt.to_period("M").dt.to_timestamp())
    monthly = work.groupby("MonthStart", as_index=False).agg(
        RevenueGBP=("RevenueGBP", "sum"),
        Orders=("InvoiceNo", "nunique"),
        ActiveCustomers=("CustomerID", "nunique"),
        UnitsSold=("Quantity", "sum"),
    ).sort_values("MonthStart")
    monthly["AverageOrderValueGBP"] = monthly["RevenueGBP"] / monthly["Orders"]
    monthly["Month"] = monthly["MonthStart"].dt.strftime("%b %Y")
    return monthly[["Month", "MonthStart", "RevenueGBP", "Orders", "ActiveCustomers", "UnitsSold", "AverageOrderValueGBP"]]


def aggregate_customer_segments(customers: pd.DataFrame) -> pd.DataFrame:
    segments = customers.groupby("Segment", as_index=False).agg(
        Customers=("CustomerID", "nunique"),
        Orders=("OrderCount", "sum"),
        RevenueGBP=("RevenueGBP", "sum"),
        AverageCustomerRevenueGBP=("RevenueGBP", "mean"),
        MedianRecencyDays=("RecencyDays", "median"),
        RepeatCustomers=("OrderCount", lambda x: int((x >= 2).sum())),
    )
    segments["CustomerShare"] = segments["Customers"] / segments["Customers"].sum()
    order = ["Champions", "Loyal customers", "Potential loyalists", "Recent customers", "At risk", "Hibernating", "Others"]
    segments["_order"] = segments["Segment"].map({name: i for i, name in enumerate(order)})
    return segments.sort_values("_order").drop(columns="_order").reset_index(drop=True)


def save_charts(monthly: pd.DataFrame, segments: pd.DataFrame) -> None:
    IMAGE_DIR.mkdir(exist_ok=True)
    palette = ["#0f766e", "#14b8a6", "#f97316", "#334155", "#94a3b8", "#cbd5e1", "#64748b"]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(monthly["Month"], monthly["RevenueGBP"] / 1000, color="#0f766e", linewidth=2.8, marker="o", markersize=4)
    ax.set_title("Monthly sales revenue (£000)", loc="left", fontsize=15, pad=14)
    ax.set_ylabel("Revenue (£000)")
    ax.tick_params(axis="x", rotation=45)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=.18)
    fig.tight_layout()
    fig.savefig(IMAGE_DIR / "monthly_sales.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    ranked = segments.sort_values("RevenueGBP", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.barh(ranked["Segment"], ranked["RevenueGBP"] / 1000, color=palette[:len(ranked)])
    ax.set_title("Revenue by RFM customer segment (£000)", loc="left", fontsize=15, pad=14)
    ax.set_xlabel("Revenue (£000)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", alpha=.18)
    fig.tight_layout()
    fig.savefig(IMAGE_DIR / "customer_segments.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main(offline: bool = False) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    IMAGE_DIR.mkdir(exist_ok=True)
    raw = load_source(offline)
    raw_rows = len(raw)
    raw["InvoiceNo"] = raw["InvoiceNo"].astype(str).str.strip()
    raw["InvoiceDate"] = pd.to_datetime(raw["InvoiceDate"], errors="coerce")
    raw["CustomerID"] = pd.to_numeric(raw["CustomerID"], errors="coerce")
    raw["Quantity"] = pd.to_numeric(raw["Quantity"], errors="coerce")
    raw["UnitPrice"] = pd.to_numeric(raw["UnitPrice"], errors="coerce")

    cancelled = raw["InvoiceNo"].str.upper().str.startswith("C")
    negative_qty = raw["Quantity"] <= 0
    nonpositive_price = raw["UnitPrice"] <= 0
    valid_date = raw["InvoiceDate"].notna()
    sale_mask = (~cancelled) & (~negative_qty) & (~nonpositive_price) & valid_date
    sales = raw.loc[sale_mask].copy()
    sales["RevenueGBP"] = sales["Quantity"] * sales["UnitPrice"]
    as_of = sales["InvoiceDate"].max().normalize() + pd.Timedelta(days=1)

    monthly = build_monthly(sales)
    customers = build_customer_summary(sales, as_of)
    segments = aggregate_customer_segments(customers)
    countries = sales.groupby("Country", as_index=False).agg(
        RevenueGBP=("RevenueGBP", "sum"),
        Orders=("InvoiceNo", "nunique"),
        ActiveCustomers=("CustomerID", "nunique"),
        UnitsSold=("Quantity", "sum"),
    ).sort_values("RevenueGBP", ascending=False).reset_index(drop=True)
    countries["RevenueShare"] = countries["RevenueGBP"] / countries["RevenueGBP"].sum()
    non_merch_codes = {"DOT", "M", "POST", "D", "C2", "CRUK", "AMAZONFEE"}
    merchandise = sales[~sales["StockCode"].astype(str).str.upper().isin(non_merch_codes)]
    products = merchandise.groupby(["StockCode", "Description"], as_index=False, dropna=False).agg(
        RevenueGBP=("RevenueGBP", "sum"),
        UnitsSold=("Quantity", "sum"),
        Orders=("InvoiceNo", "nunique"),
    ).sort_values("RevenueGBP", ascending=False).head(15).reset_index(drop=True)

    monthly.to_csv(RESULTS_DIR / "monthly_sales.csv", index=False)
    segments.to_csv(RESULTS_DIR / "customer_segments.csv", index=False)
    countries.to_csv(RESULTS_DIR / "country_performance.csv", index=False)
    products.to_csv(RESULTS_DIR / "top_products.csv", index=False)
    # Retain the cleaned sales fact locally for DuckDB and Power BI; it is excluded from Git.
    clean_columns = ["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country", "RevenueGBP"]
    sales[clean_columns].to_csv(DATA_DIR / "retail_sales_clean.csv", index=False)
    customers.to_csv(DATA_DIR / "customer_summary.csv", index=False)
    save_charts(monthly, segments)

    identified = sales[sales["CustomerID"].notna()]
    repeat_customers = int((customers["OrderCount"] >= 2).sum())
    total_sales = float(sales["RevenueGBP"].sum())
    total_orders = int(sales["InvoiceNo"].nunique())
    kpis = {
        "raw_rows": int(raw_rows),
        "sales_lines": int(len(sales)),
        "cancelled_lines": int(cancelled.sum()),
        "negative_quantity_lines": int(negative_qty.sum()),
        "nonpositive_price_lines": int(nonpositive_price.sum()),
        "missing_customer_sales_lines": int(sales["CustomerID"].isna().sum()),
        "revenue_gbp": total_sales,
        "orders": total_orders,
        "active_customers": int(customers["CustomerID"].nunique()),
        "average_order_value_gbp": total_sales / total_orders if total_orders else 0,
        "units_sold": int(sales["Quantity"].sum()),
        "repeat_customers": repeat_customers,
        "repeat_customer_rate": repeat_customers / max(int(len(customers)), 1),
        "identified_customer_revenue_gbp": float(identified["RevenueGBP"].sum()),
        "date_start": sales["InvoiceDate"].min().strftime("%Y-%m-%d"),
        "date_end": sales["InvoiceDate"].max().strftime("%Y-%m-%d"),
        "as_of_date": as_of.strftime("%Y-%m-%d"),
        "countries": int(sales["Country"].nunique()),
        "top_country": str(countries.iloc[0]["Country"]),
        "top_country_revenue_gbp": float(countries.iloc[0]["RevenueGBP"]),
        "top_product": str(products.iloc[0]["Description"]),
        "top_product_stock_code": str(products.iloc[0]["StockCode"]),
        "top_product_revenue_gbp": float(products.iloc[0]["RevenueGBP"]),
    }
    (RESULTS_DIR / "dashboard_kpis.json").write_text(json.dumps(kpis, indent=2), encoding="utf-8")

    top_country = countries.iloc[0]
    top_product = products.iloc[0]
    segment_order = segments.sort_values("RevenueGBP", ascending=False)
    lines = [
        "# Retail sales and customer performance: summary", "",
        "## Summary", "",
        f"The cleaned positive-sales population contains **{len(sales):,} line items** across **{total_orders:,} invoices**, generating **£{total_sales:,.0f}** in recorded line revenue. The source spans {kpis['date_start']} to {kpis['date_end']}; the final month is partial.",
        f"The dataset identifies **{len(customers):,} customers**. **{repeat_customers:,} ({kpis['repeat_customer_rate']:.1%})** placed at least two distinct invoices in the observed period.",
        f"**{top_country['Country']}** is the largest market at **£{top_country['RevenueGBP']:,.0f}**. **{top_product['Description']}** is the highest-revenue item at **£{top_product['RevenueGBP']:,.0f}**.", "",
        "## Customer performance", "",
        "Customer segments use recency, frequency, and monetary value at the day after the last source transaction. Recent/frequent/high-spend groups contribute the greatest observed sales; see `customer_segments.csv` for segment counts and value.", "",
    ]
    for _, row in segment_order.iterrows():
        lines.append(f"- **{row['Segment']}**: {int(row['Customers']):,} customers, £{row['RevenueGBP']:,.0f} revenue, median recency {row['MedianRecencyDays']:.0f} days")
    lines += ["", "## Definitions and limitations", "",
              "- Sales revenue is the sum of positive quantity × positive unit price on invoices that do not begin with `C`. It includes valid postage/service lines, so it is line revenue in GBP, not merchandise-only revenue, profit, cash received, or revenue net of all return adjustments.",
              "- Customers without a CustomerID remain in sales, invoice, unit, country, and product totals, but are excluded from customer counts and RFM segments. Customer KPIs therefore have an identified-customer denominator.",
              "- Returns/cancellations, zero or negative quantities, nonpositive prices, and missing dates are excluded from the positive-sales fact table. Counts are available in `dashboard_kpis.json`.",
              "- This is a single historical retailer dataset from 2010–2011. Results are descriptive and do not represent current retail demand or causal campaign impact.",
              "- The merchandise ranking omits service/adjustment stock codes `DOT`, `M`, `POST`, `D`, `C2`, `CRUK`, and `AMAZONFEE`; total sales revenue still includes qualifying positive service lines.",
              "- RFM groups are heuristic portfolio segments, not customer-level treatment recommendations.", ""]
    (RESULTS_DIR / "analysis_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Done. Raw={raw_rows:,}; positive sales lines={len(sales):,}; revenue=£{total_sales:,.2f}; orders={total_orders:,}; identified customers={len(customers):,}.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="Use the cached UCI source workbook only.")
    main(offline=parser.parse_args().offline)

