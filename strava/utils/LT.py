import pandas as pd
import time
from services.strava_api import refresh_access_token, fetch_activities
from services.config import client_id, client_secret, refresh_token
from utils.data_processing import process_activities

def estimate_threshold_from_best_effort(df):
    candidates = df[
        (df["Distance (km)"] >= 6) &
        (df["Average HR"] >= df["Average HR"].quantile(0.85))
    ].copy()

    candidates["Pace"] = candidates["Time (minutes)"] / candidates["Distance (km)"]
    best = candidates[candidates["Time (minutes)"] >= 25].sort_values("Average HR", ascending=False)

    if best.empty:
        print("No suitable runs found.")
        return None

    top5 = best.head(5)[["Date", "Distance (km)", "Time (minutes)", "Average HR", "Pace"]]
    estimated_lthr = round(best.iloc[0]["Average HR"] * 0.98)
    return top5, estimated_lthr


access_token = refresh_access_token(refresh_token, client_id, client_secret)
start_date = int(time.mktime(time.strptime("2024-06-01", "%Y-%m-%d")))
activities = fetch_activities(access_token, start_date)
df = process_activities(activities)

result = estimate_threshold_from_best_effort(df)
if result:
    top5, lthr = result
    print(f"\nEstimated LTHR: {lthr} bpm\n")
    print(top5.to_string(index=False))