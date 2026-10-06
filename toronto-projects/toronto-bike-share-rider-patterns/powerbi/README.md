# Power BI report starter

Load `data/clean_trips.csv` as `Trips`. Set `start` and `end` to Date/Time, `trip_minutes` to Decimal, `hour` to Whole Number, and member, station, and weekday fields to Text.

Create a calendar table and relate it to `Trips[start]`. Add the measures in `Measures.dax`.

Suggested pages:

- **Rider Overview:** trips, median duration, member share, monthly trips by type.
- **Time Patterns:** weekday-by-hour matrix and weekend share.
- **Stations:** top origins, destinations, and origin-destination pairs.

Add filters for rider type and month. Keep the Q1 2026 source window visible.
