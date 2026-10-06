# Power BI report guide

Load `data/clean_site_month.csv` as `SiteMonth`. Set `month`, `enforcement_start`, and `enforcement_end` to Date; `charges` to Whole Number; and `ward`/site identifiers to Text.

Create a Calendar table and relate it to `SiteMonth[month]`. Add the measures in `Measures.dax`.

Suggested pages:

- **Monthly Trend:** observed charges and active site count.
- **Coverage:** ward ranking and a site-instance detail table.
- **Data Quality:** missingness, reported period, and site coverage.

Keep the note that blank cells are missing, not zero, beside the visuals.
