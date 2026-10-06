from pathlib import Path
from urllib.request import urlretrieve
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT, IMG = ROOT / "data", ROOT / "results", ROOT / "images"
for folder in (DATA, OUT, IMG):
    folder.mkdir(parents=True, exist_ok=True)
URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/537923d1-a6c8-4b9c-9d55-fa47d9d7ddab/resource/a388bc08-622c-4647-bad8-ecdb7e62090a/download/automated-speed-enforcement.xlsx"
source = DATA / "automated-speed-enforcement.xlsx"
if not source.exists():
    urlretrieve(URL, source)
df = pd.read_excel(source, sheet_name=0, header=0)
df.columns = [c.strftime("%Y-%m-%d") if hasattr(c, "strftime") else str(c).strip() for c in df.columns]
metadata = ["Site Code", "Location*", "Ward", "Enforcement Start Date", "Enforcement End Date"]
months = [c for c in df.columns if c not in metadata]
df["Site Code"] = df["Site Code"].astype("string").str.strip().str.upper()
df["Location*"] = df["Location*"].astype("string").str.strip()
df["Ward"] = pd.to_numeric(df["Ward"], errors="coerce")
df["Enforcement Start Date"] = pd.to_datetime(df["Enforcement Start Date"], errors="coerce")
df["Enforcement End Date"] = pd.to_datetime(df["Enforcement End Date"], errors="coerce")
# Codes can be reused over different locations/activation periods. Keep each occurrence distinct.
df["site_instance_id"] = df["Site Code"].fillna("") + "|" + df["Location*"].fillna("") + "|" + df["Enforcement Start Date"].astype("string").fillna("")
for col in months:
    df[col] = pd.to_numeric(df[col].replace({"-": np.nan, "": np.nan}), errors="coerce")
long = df.melt(id_vars=metadata + ["site_instance_id"], var_name="month", value_name="charges")
long["month"] = pd.to_datetime(long.month, errors="coerce")
long["charges"] = pd.to_numeric(long.charges, errors="coerce")
long = long.dropna(subset=["month", "charges"])
long = long[long.charges >= 0].copy()
long["charges"] = long.charges.round().astype("int64")
long["ward"] = long.Ward.astype("Int64").astype("string").fillna("Unknown")
long = long.rename(columns={"Site Code": "site_code", "Location*": "location", "Enforcement Start Date": "enforcement_start", "Enforcement End Date": "enforcement_end"})
long = long[["site_instance_id", "site_code", "location", "ward", "enforcement_start", "enforcement_end", "month", "charges"]]
long.to_csv(DATA / "clean_site_month.csv", index=False)
monthly = long.groupby("month", as_index=False).agg(charges=("charges", "sum"), sites_with_record=("site_instance_id", "nunique"))
active = []
for month in monthly.month:
    month_end = month + pd.offsets.MonthEnd(0)
    active.append(int(((df["Enforcement Start Date"] <= month_end) & (df["Enforcement End Date"].isna() | (df["Enforcement End Date"] >= month))).sum()))
monthly["active_sites"] = active
ward = long.groupby("ward", as_index=False).agg(charges=("charges", "sum"), site_month_rows=("site_instance_id", "size"), sites=("site_instance_id", "nunique")).sort_values("charges", ascending=False)
site = long.groupby(["site_instance_id", "site_code", "location", "ward"], as_index=False).agg(charges=("charges", "sum"), months_reported=("month", "nunique")).sort_values("charges", ascending=False).head(20)
monthly.assign(month=monthly.month.dt.strftime("%Y-%m")).to_csv(OUT / "monthly_summary.csv", index=False)
ward.to_csv(OUT / "ward_summary.csv", index=False)
site.to_csv(OUT / "top_sites.csv", index=False)
plt.figure(figsize=(10, 4.8)); plt.plot(monthly.month.dt.strftime("%Y-%m"), monthly.charges, color="#0E7490", lw=2.5, marker="o"); plt.xticks(range(0, len(monthly), 3), monthly.month.dt.strftime("%Y-%m").iloc[::3], rotation=35, ha="right"); plt.title("Recorded ASE charges by month"); plt.ylabel("Recorded charges"); plt.grid(axis="y", alpha=.2); plt.tight_layout(); plt.savefig(IMG / "monthly_charges.png", dpi=150); plt.close()
w = ward.sort_values("charges").tail(12)
plt.figure(figsize=(9, 5)); plt.barh(w.ward, w.charges, color="#E5A93B"); plt.title("Recorded ASE charges by ward"); plt.xlabel("Recorded charges across observed months"); plt.ylabel("Ward"); plt.grid(axis="x", alpha=.2); plt.tight_layout(); plt.savefig(IMG / "ward_charges.png", dpi=150); plt.close()
missing = len(df) * len(months) - len(long)
print(f"Sites={len(df):,}; observed site-months={len(long):,}; blank/dash cells={missing:,}; recorded charge values={long.charges.sum():,}")
