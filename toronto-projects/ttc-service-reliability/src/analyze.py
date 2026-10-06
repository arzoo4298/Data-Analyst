from pathlib import Path
from urllib.request import urlretrieve
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT, IMG = ROOT / "data", ROOT / "results", ROOT / "images"
for folder in (DATA, OUT, IMG):
    folder.mkdir(parents=True, exist_ok=True)
URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/996cfe8d-fb35-40ce-b569-698d51fc683b/resource/0b6e5c52-e993-46d6-8d74-8602ee224457/download/ttc-subway-delay-data-since-2025.csv"
raw = DATA / "ttc_delays_since_2025.csv"
if not raw.exists():
    urlretrieve(URL, raw)
df = pd.read_csv(raw)
source_rows = len(df)
df["date"] = pd.to_datetime(df["Date"], errors="coerce")
df["delay_min"] = pd.to_numeric(df["Min Delay"], errors="coerce")
df["gap_min"] = pd.to_numeric(df["Min Gap"], errors="coerce")
df = df.drop_duplicates("_id").dropna(subset=["date"]).copy()
df = df[df.delay_min.isna() | (df.delay_min >= 0)].copy()
for col in ("Station", "Code", "Line"):
    df[col] = df[col].astype("string").str.strip().str.upper().replace({"": "Unknown"}).fillna("Unknown")
df["hour"] = pd.to_numeric(df["Time"].astype("string").str.extract(r"^(\d{1,2})", expand=False), errors="coerce")
df["month"] = df.date.dt.to_period("M").astype(str)
df["day_of_week"] = df.date.dt.day_name()
df["delay_min"] = df.delay_min.fillna(0)
df["gap_min"] = df.gap_min.where(df.gap_min >= 0)
df = df.rename(columns={"Station": "station", "Code": "code", "Line": "line", "Bound": "bound", "Vehicle": "vehicle", "Time": "time"})
df["date"] = df.date.dt.date.astype(str)
df = df[["date", "time", "day_of_week", "station", "code", "delay_min", "gap_min", "bound", "line", "vehicle", "hour", "month"]]
df.to_csv(DATA / "clean_delays.csv", index=False)
tables = {
    "monthly_summary.csv": df.groupby("month", as_index=False).agg(incidents=("date", "size"), delay_minutes=("delay_min", "sum"), avg_delay_minutes=("delay_min", "mean"), median_delay_minutes=("delay_min", "median")),
    "line_summary.csv": df.groupby("line", as_index=False).agg(incidents=("date", "size"), delay_minutes=("delay_min", "sum"), avg_delay_minutes=("delay_min", "mean")).sort_values("delay_minutes", ascending=False),
    "station_summary.csv": df.groupby("station", as_index=False).agg(incidents=("date", "size"), delay_minutes=("delay_min", "sum")).sort_values("delay_minutes", ascending=False).head(15),
    "day_summary.csv": df.groupby("day_of_week", as_index=False).agg(incidents=("date", "size"), delay_minutes=("delay_min", "sum")),
    "code_summary.csv": df.groupby("code", as_index=False).agg(incidents=("date", "size"), delay_minutes=("delay_min", "sum")).sort_values("incidents", ascending=False).head(15),
}
for name, table in tables.items():
    table.to_csv(OUT / name, index=False)
m = tables["monthly_summary.csv"]
plt.figure(figsize=(10, 4.8)); plt.plot(m.month, m.incidents, color="#0E7490", lw=2.5, marker="o"); plt.xticks(rotation=35, ha="right"); plt.title("Reported TTC subway delay incidents by month"); plt.ylabel("Incidents"); plt.grid(axis="y", alpha=.2); plt.tight_layout(); plt.savefig(IMG / "monthly_incidents.png", dpi=150); plt.close()
l = tables["line_summary.csv"].sort_values("delay_minutes")
plt.figure(figsize=(8.5, 5)); plt.barh(l.line, l.delay_minutes / 60, color="#0E7490"); plt.title("Reported delay minutes by subway line"); plt.xlabel("Reported delay minutes (hours)"); plt.grid(axis="x", alpha=.2); plt.tight_layout(); plt.savefig(IMG / "line_delays.png", dpi=150); plt.close()
print(f"Source rows={source_rows:,}; retained={len(df):,}; reported delay minutes={df.delay_min.sum():,.0f}; period={df.date.min()} to {df.date.max()}")
