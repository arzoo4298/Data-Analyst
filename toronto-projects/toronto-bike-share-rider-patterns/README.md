# Toronto Bike Share: Rider Behavior & Station Demand

**Portfolio project | Python · SQL · data cleaning · visualization · Power BI-ready summaries**

A first-quarter 2026 trip analysis comparing casual and member rides, trip duration, time-of-day patterns, and high-volume station pairs.

## Snapshot

The source includes **552,073 trips**; **548,371** remain after removing missing timestamps and trips under one minute or over four hours. Members account for 487,666 retained trips. Median trip duration is 9.6 minutes for members and 11.2 minutes for casual riders.

## Business questions

- How do member and casual trips differ by duration and time of day?
- Which stations and station pairs have the most observed trips?
- How does ridership vary by weekday and hour?
- What would need a same-season comparison before operational action?

## Contents

- `src/analyze.py` downloads the public Q1 file, cleans trips, writes summary tables, and creates charts.
- `sql/analysis.sql` contains queries for rider type, weekday/hour, and station pairs.
- `powerbi/` contains starter measures and a report design guide.
- `results/` contains compact summaries and cleaning notes.
- `images/` contains report-ready visualizations.

## Run

```bash
python -m pip install -r requirements.txt
python src/analyze.py
```

The raw zip and cleaned row-level trips are excluded from Git. Run the pipeline to create them locally under `data/`.

## Definitions and limitations

Trip IDs are deduplicated, timestamps parsed, and trips outside 1 minute–4 hours excluded as a transparent error filter. That filter can remove genuine edge cases. The file covers **Q1 only**, a winter period; it does not represent a full-year or summer pattern. Station-pair counts do not measure bike availability, route distance, or service quality. Results are descriptive.

## Source

City of Toronto Open Data, [Bike Share Toronto Ridership Data](https://open.toronto.ca/dataset/bike-share-toronto-ridership-data/), Open Government Licence – Toronto.
