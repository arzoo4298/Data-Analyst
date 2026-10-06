# Cleaning log and metric definitions

- Source: 631 site rows and 65 monthly columns, July 2020 through November 2025.
- Wide month columns are unpivoted to one site-instance/month row. Date headers and text fields are normalized; ward and enforcement dates are typed; numeric charge values are coerced to nonnegative integers.
- **36,173 blank/dash cells** remain missing and are excluded from the **4,842 observed** site-month rows. Missing values are not converted to zero.
- The source reuses 110 site codes across locations or enforcement periods. These rows are preserved as separate site instances using site code, location, and enforcement start date.
- Observed charge values sum to **2,150,715**. “Charges” is the source field and is not assumed to mean unique vehicles, unique tickets, or dollars.
- Enforcement coverage changes over time. Trend differences cannot be attributed to changes in driver behavior alone.
