from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT, IMG = ROOT / "data", ROOT / "results", ROOT / "images"
for folder in (DATA, OUT, IMG):
    folder.mkdir(parents=True, exist_ok=True)
URL = "https://opendata.toronto.ca/toronto.parking.authority/bike-share-toronto-ridership-data/bikeshare-ridership-2026.zip"
archive = DATA / "bikeshare-ridership-2026.zip"
if not archive.exists():
    urlretrieve(URL, archive)
with ZipFile(archive) as z:
    member = next(n for n in z.namelist() if n.lower().endswith(".csv"))
    with z.open(member) as f:
        df = pd.read_csv(f, low_memory=False)
source_rows = len(df)
df["start"] = pd.to_datetime(df.Start_Time, errors="coerce")
df["end"] = pd.to_datetime(df.End_Time, errors="coerce")
df["duration_seconds"] = pd.to_numeric(df.Trip_Duration, errors="coerce")
df["user_type"] = df.User_Type.astype("string").str.strip().str.title().replace({"": "Unknown"}).fillna("Unknown")
for col, new in (("Start_Station_Name", "start_station"), ("End_Station_Name", "end_station")):
    df[new] = df[col].astype("string").str.strip().replace({"": "Unknown"}).fillna("Unknown")
df = df.drop_duplicates("Trip_Id").dropna(subset=["start", "end", "duration_seconds"]).copy()
df = df[(df.duration_seconds >= 60) & (df.duration_seconds <= 14400) & (df.end >= df.start)].copy()
df["trip_minutes"] = df.duration_seconds / 60
df["month"] = df.start.dt.to_period("M").astype(str)
df["weekday"] = df.start.dt.day_name()
df["hour"] = df.start.dt.hour
df["weekend"] = df.start.dt.dayofweek >= 5
df = df.rename(columns={"Trip_Id": "trip_id", "Start_Station_Id": "start_station_id", "End_Station_Id": "end_station_id", "Bike_Model": "bike_model"})
df = df[["trip_id", "start", "end", "trip_minutes", "user_type", "start_station_id", "start_station", "end_station_id", "end_station", "bike_model", "month", "weekday", "hour", "weekend"]]
df.to_csv(DATA / "clean_trips.csv", index=False)
tables = {
    "user_type_summary.csv": df.groupby("user_type", as_index=False).agg(trips=("trip_id", "count"), avg_trip_min=("trip_minutes", "mean"), median_trip_min=("trip_minutes", "median"), weekend_share=("weekend", "mean")),
    "monthly_by_user.csv": df.groupby(["month", "user_type"], as_index=False).agg(trips=("trip_id", "count"), avg_trip_min=("trip_minutes", "mean")),
    "weekday_by_user.csv": df.groupby(["weekday", "user_type"], as_index=False).agg(trips=("trip_id", "count"), avg_trip_min=("trip_minutes", "mean")),
    "hourly_by_user.csv": df.groupby(["hour", "user_type"], as_index=False).agg(trips=("trip_id", "count")),
    "top_station_pairs.csv": df.groupby(["start_station", "end_station"], as_index=False).agg(trips=("trip_id", "count"), avg_trip_min=("trip_minutes", "mean")).sort_values("trips", ascending=False).head(15),
}
for name, table in tables.items():
    table.to_csv(OUT / name, index=False)
monthly = tables["monthly_by_user.csv"].pivot(index="month", columns="user_type", values="trips").fillna(0)
monthly.plot(kind="bar", figsize=(9, 4.8), color=["#E5A93B", "#0E7490"]); plt.title("Toronto Bike Share trips by month and rider type · Q1 2026"); plt.ylabel("Trips"); plt.xlabel("Month"); plt.grid(axis="y", alpha=.2); plt.tight_layout(); plt.savefig(IMG / "monthly_rider_type.png", dpi=150); plt.close()
hourly = tables["hourly_by_user.csv"].pivot(index="hour", columns="user_type", values="trips").fillna(0)
hourly.plot(figsize=(9, 4.8), color=["#E5A93B", "#0E7490"], lw=2); plt.title("Ride starts by hour and rider type · Q1 2026"); plt.ylabel("Trips"); plt.xlabel("Start hour (local)"); plt.grid(axis="y", alpha=.2); plt.tight_layout(); plt.savefig(IMG / "hourly_demand.png", dpi=150); plt.close()
print(f"Source rows={source_rows:,}; retained={len(df):,}; median trip={df.trip_minutes.median():.1f} min; period={df.start.min()} to {df.start.max()}")
