import time
from services.strava_api import refresh_access_token, fetch_activities
from services.config import client_id, client_secret, refresh_token
from utils.data_processing import process_activities
from utils.visualisations import estimate_threshold_hr

access_token = refresh_access_token(refresh_token, client_id, client_secret)
start_date = int(time.mktime(time.strptime("2024-06-01", "%Y-%m-%d")))
activities = fetch_activities(access_token, start_date)
df = process_activities(activities)

top5, lthr = estimate_threshold_hr(df)

if lthr:
    print(f"\nEstimated LTHR: {lthr} bpm\n")
    print(top5.to_string(index=False))
else:
    print("Not enough qualifying runs.")