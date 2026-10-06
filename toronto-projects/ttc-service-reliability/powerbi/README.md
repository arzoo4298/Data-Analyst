# Power BI report build

1. Run `python src/analyze.py` and load `data/clean_delays.csv` as `Delays`.
2. Set `date` to Date; `delay_min`, `gap_min`, and `hour` to Whole Number; categories to Text.
3. Create a Calendar table, relate it to `Delays[date]`, and mark it as the date table.
4. Add measures from `Measures.dax`.
5. Build pages for Overview (incident and delay KPIs plus monthly trend), Line & Station, and Timing (weekday/hour heatmap).
6. Add slicers for date, line, and day of week. Label delay minutes as the source-reported measure.
7. Put the limitations from `results/data_quality.md` beside the headline visuals.
