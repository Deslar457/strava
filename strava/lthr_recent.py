"""
Estimate LTHR from runs in the last 8 weeks.

Place at project root (alongside app.py) and run:
    python lthr_recent.py
"""

import sys
import os
import time
import pandas as pd

# Make project imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.strava_api import refresh_access_token, fetch_activities
from services.config import client_id, client_secret, refresh_token
from utils.data_processing import process_activities


def format_time(minutes):
    mins = int(minutes)
    secs = round((minutes - mins) * 60)
    return f"{mins}:{secs:02d}"


def estimate_lthr_recent(df, weeks=8):
    cutoff = df["Date"].max() - pd.Timedelta(weeks=weeks)
    recent = df[df["Date"] >= cutoff].copy()

    candidates = recent[
        (recent["Distance (km)"] >= 6) &
        (recent["Average HR"] >= recent["Average HR"].quantile(0.85))
    ].copy()

    candidates["Pace"] = candidates["Time (minutes)"] / candidates["Distance (km)"]
    best = candidates[candidates["Time (minutes)"] >= 25].sort_values("Average HR", ascending=False)

    if best.empty:
        return None, None, 0

    top = best.head(5)[["Date", "Distance (km)", "Time (minutes)", "Average HR", "Pace"]].copy()
    top["Pace"] = top["Pace"].apply(format_time)
    top["Duration"] = top["Time (minutes)"].apply(format_time)
    top["Date"] = top["Date"].dt.strftime("%d %b %Y")
    top["Distance"] = top["Distance (km)"].apply(lambda x: f"{x:.2f} km")
    top["HR"] = top["Average HR"].apply(lambda x: f"{int(x)} bpm")
    top = top[["Date", "Distance", "Duration", "HR", "Pace"]]

    lthr = round(best.iloc[0]["Average HR"] * 0.98)
    return top, lthr, len(best)


def main():
    print("Fetching Strava data...")
    access_token = refresh_access_token(refresh_token, client_id, client_secret)
    start_date = int(time.mktime(time.strptime("2024-06-01", "%Y-%m-%d")))
    activities = fetch_activities(access_token, start_date)
    df = process_activities(activities)

    print(f"\nLoaded {len(df)} runs total.")
    print(f"Date range: {df['Date'].min().strftime('%d %b %Y')} → {df['Date'].max().strftime('%d %b %Y')}")

    top, lthr, n_qualifying = estimate_lthr_recent(df, weeks=8)

    print("\n" + "=" * 60)
    print("LTHR ESTIMATE — LAST 8 WEEKS")
    print("=" * 60)

    if lthr is None:
        print("\n❌ No qualifying runs found in last 8 weeks.")
        print("   (need ≥6km, ≥25min, top 15% HR)")
        return

    print(f"\nEstimated LTHR: {lthr} bpm")
    print(f"Based on {n_qualifying} qualifying run{'s' if n_qualifying != 1 else ''}")

    if n_qualifying < 3:
        print(f"\n⚠️  Only {n_qualifying} qualifying run{'s' if n_qualifying != 1 else ''} — estimate is noisy.")
        print("   Treat as indicative only. More hard sustained efforts will sharpen it.")

    print(f"\nTop {min(5, n_qualifying)} hardest sustained efforts:")
    print("-" * 60)
    print(top.to_string(index=False))
    print()


if __name__ == "__main__":
    main()
