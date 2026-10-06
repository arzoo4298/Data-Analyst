# TTC Subway Service Reliability

**Portfolio project | Power BI · SQL · Python · data cleaning · visualization**

An operations analysis of Toronto subway delay incidents, cleaned into an event fact and summarized by line, station, date, and time of day.

## Snapshot

The published file contains **45,475 reported incidents** from January 2025 through August 2026, with **122,071 reported delay minutes**. Line code YU accounts for 65,506 recorded minutes and BD for 51,508. About 29,669 rows have zero or missing reported delay minutes after the documented fill rule, so incident counts and summed delay minutes tell different stories.

## Business questions

- How do reported incident counts and delay minutes vary by line and month?
- Which reported stations and incident codes appear most often?
- When are delay reports most frequent?
- How much recorded delay is zero, missing, or concentrated in a small set of events?

## Contents

- `src/analyze.py` downloads the public CSV if needed, cleans the records, writes summaries, and creates charts.
- `sql/analysis.sql` contains DuckDB queries for monthly, line, station, and time patterns.
- `powerbi/` contains model instructions and starter DAX measures.
- `results/` contains compact summaries and data quality notes.
- `images/` contains report-ready visualizations.

## Run

```bash
python -m pip install -r requirements.txt
python src/analyze.py
```

Raw data is kept locally under `data/` and excluded from Git. The cleaning pipeline creates `data/clean_delays.csv` for SQL and Power BI.

## Definitions and limitations

`Min Delay` is the publisher's event-level reported operational measure. It is not passenger-weighted delay or system-wide lost service. Missing dates and duplicate IDs are removed. Blank categories are labeled `Unknown`. Missing delay values become zero for additive sums and remain identified in the cleaning notes. Results are descriptive and do not establish causality.

## Source

City of Toronto Open Data, [TTC Subway Delay Data since 2025](https://open.toronto.ca/dataset/996cfe8d-fb35-40ce-b569-698d51fc683b/), Open Government Licence – Toronto.
