import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from services.strava_api import refresh_access_token, fetch_activities
from services.config import client_id, client_secret, refresh_token
from utils.data_processing import process_activities
from utils.visualisations import calculate_training_stress

access_token = refresh_access_token(refresh_token, client_id, client_secret)
start_date = int(time.mktime(time.strptime("2024-06-01", "%Y-%m-%d")))
activities = fetch_activities(access_token, start_date)
df = process_activities(activities)

daily = calculate_training_stress(df)
recent = daily.tail(42)

print(f"\nDays with TSS > 0: {(recent['TSS'] > 0).sum()} / 42")
print(f"Days with TSS = 0: {(recent['TSS'] == 0).sum()} / 42")
print(f"Total TSS over 42 days: {recent['TSS'].sum():.0f}")
print(f"Simple mean: {recent['TSS'].mean():.1f}")
print(f"Final CTL: {recent['CTL'].iloc[-1]:.1f}")
print(f"\nLast 14 days:")
print(recent.tail(14)[['Date', 'TSS']].to_string(index=False))