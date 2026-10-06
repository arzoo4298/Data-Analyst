# Toronto Automated Speed Enforcement: Data Cleaning & Visualization

**Portfolio project | Python · SQL · data cleaning · data quality · visualization**

A data quality case study reshaping a wide, monthly-by-site enforcement worksheet into a tidy site-month table and making missingness, site coverage, ward patterns, and monthly variation visible.

## Snapshot

The source has **631 site rows** and 65 monthly columns from July 2020 to November 2025. After reshaping and preserving blank values as missing, **4,842** numeric site-month observations remain, summing to **2,150,715 recorded charge values**. There are **36,173 blank or dash cells**.

## Business questions

- How do monthly recorded values change over time?
- Which wards and site instances have the highest totals in observed cells?
- How should missing month cells, active dates, and zero values be treated?
- How might enforcement coverage changes affect trend comparisons?

## Contents

- `src/analyze.py` downloads the source, cleans/unpivots it, writes summaries, and creates charts.
- `sql/analysis.sql` contains queries for monthly, ward, and site views.
- `powerbi/` contains measures and a dashboard guide.
- `results/` contains compact summaries and a cleaning log.
- `images/` contains report-ready visualizations.

## Run

```bash
python -m pip install -r requirements.txt
python src/analyze.py
```

## Data quality and interpretation

Blank and dash cells remain missing; they are not filled with zero because a blank can mean unavailable or not active. Site codes can be reused at different locations and enforcement periods, so a composite site-instance key is used rather than dropping repeated codes. “Charges” means the values in the source; it is not interpreted as unique vehicles, tickets, or dollars. Enforcement coverage changes over time, so the trend cannot isolate changes in driver behavior.

## Source

City of Toronto Open Data, [Automated Speed Enforcement Charges](https://open.toronto.ca/dataset/537923d1-a6c8-4b9c-9d55-fa47d9d7ddab/), Open Government Licence – Toronto.
