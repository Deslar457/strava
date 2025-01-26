#!/usr/bin/env python
# coding: utf-8

# In[25]:


import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import time

# Initial Setup
client_id = '132964'
client_secret = 'edd5dac7aa72b54840e924a0d558961508cb631a'
refresh_token = '9777a200f3d024ff4026f54b3e4d10f69f99ba2c'

# Function to refresh the access token
def refresh_access_token(refresh_token, client_id, client_secret):
    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
    )
    if response.status_code == 200:
        tokens = response.json()
        return tokens['access_token']
    else:
        st.error("Failed to refresh token: " + response.text)
        st.stop()

# Function to fetch activities from Strava API
def fetch_activities(access_token, start_date):
    headers = {'Authorization': f'Bearer {access_token}'}
    page, activities = 1, []
    while True:
        response = requests.get(
            'https://www.strava.com/api/v3/athlete/activities',
            headers=headers,
            params={'after': start_date, 'page': page, 'per_page': 200}
        )
        if response.status_code != 200 or not response.json():
            break
        activities.extend(response.json())
        page += 1
    return pd.DataFrame(activities)

# Fetch activities and prepare data
@st.cache_data
def prepare_data():
    access_token = refresh_access_token(refresh_token, client_id, client_secret)
    start_date = int(time.mktime(time.strptime('2024-06-01', '%Y-%m-%d')))
    df_activities = fetch_activities(access_token, start_date)

    df_activities = df_activities[['start_date', 'distance', 'moving_time', 'average_heartrate']]
    df_activities.rename(columns={
        'start_date': 'Date',
        'distance': 'Distance (meters)',
        'moving_time': 'Time (seconds)',
        'average_heartrate': 'Average HR'
    }, inplace=True)
    df_activities['Date'] = pd.to_datetime(df_activities['Date']).dt.tz_localize(None)
    df_activities['Distance (km)'] = df_activities['Distance (meters)'] / 1000
    df_activities['Time (minutes)'] = df_activities['Time (seconds)'] / 60
    df_activities['Week'] = df_activities['Date'].dt.to_period('W').dt.to_timestamp()
    df_activities['Month'] = df_activities['Date'].dt.to_period('M').dt.to_timestamp()
    df_activities.sort_values('Date', inplace=True)
    return df_activities

# Load data
df_activities = prepare_data()

# Add month filter with "All" option
st.header("Filter by Month")
unique_months = df_activities['Month'].dt.strftime('%Y-%m').unique().tolist()
unique_months.insert(0, "All")  # Add "All" option
selected_month = st.selectbox("Select a Month", unique_months)

# Apply filter
if selected_month != "All":
    df_activities = df_activities[df_activities['Month'].dt.strftime('%Y-%m') == selected_month]

# Last 10 Sessions Table
st.header("Last 10 Sessions")
last_10_sessions = df_activities[['Date', 'Distance (km)', 'Time (minutes)', 'Average HR']].tail(10)
st.table(last_10_sessions)

# ACWR Calculation
weekly_distance = df_activities.groupby('Week')['Distance (km)'].sum()
last_4_weeks = weekly_distance[-4:].tolist()
acute_workload = last_4_weeks[-1] if len(last_4_weeks) > 0 else 0
chronic_workload = sum(last_4_weeks) / len(last_4_weeks) if len(last_4_weeks) > 0 else 0
acwr = acute_workload / chronic_workload if chronic_workload > 0 else 0

# Suggested Distance
desired_acwr_lower, desired_acwr_upper = 0.8, 1.3
target_acute_lower = chronic_workload * desired_acwr_lower
target_acute_upper = chronic_workload * desired_acwr_upper
suggested_distance = max(0, (target_acute_lower + target_acute_upper) / 2 - acute_workload)

st.header("ACWR Analysis")
st.metric("Acute Workload (7 days)", f"{acute_workload:.2f} km")
st.metric("Chronic Workload (28 days avg)", f"{chronic_workload:.2f} km")
st.metric("ACWR", f"{acwr:.2f}")
st.metric("Suggested Distance for Next Run", f"{suggested_distance:.2f} km")

# Monthly Training Distance
st.header("Monthly Training Distance")
monthly_distance = df_activities.groupby('Month')['Distance (km)'].sum()
fig, ax = plt.subplots(figsize=(12, 6))  # Bigger chart
ax.bar(monthly_distance.index, monthly_distance.values, color='lightblue', width=20)  # Thick bars
ax.set_title("Monthly Training Distance", fontsize=16)
ax.set_xlabel("Month", fontsize=12)
ax.set_ylabel("Distance (km)", fontsize=12)
ax.grid(axis='y', linestyle='--', alpha=0.7)
st.pyplot(fig)

# Weekly Training Distance
st.header("Weekly Training Distance")
weekly_distance = df_activities.groupby('Week')['Distance (km)'].sum()
fig, ax = plt.subplots(figsize=(12, 6))  # Bigger chart
ax.bar(weekly_distance.index, weekly_distance.values, color='lightgreen', width=10)  # Thick bars
ax.set_title("Weekly Training Distance", fontsize=16)
ax.set_xlabel("Week", fontsize=12)
ax.set_ylabel("Distance (km)", fontsize=12)
ax.grid(axis='y', linestyle='--', alpha=0.7)
st.pyplot(fig)

# Progression Charts for 5k and 10k
for distance in [5, 10]:
    st.header(f"{distance}k Progression")
    progression = df_activities[
        (df_activities['Distance (km)'] >= distance) & (df_activities['Distance (km)'] < distance + 0.1)
    ].groupby('Month')['Time (minutes)'].min().reset_index()

    if not progression.empty:
        avg_progression = progression['Time (minutes)'].mean()
        fig, ax = plt.subplots(figsize=(12, 6))  # Bigger chart
        ax.plot(progression['Month'], progression['Time (minutes)'], marker='o', color='blue', label=f'{distance}k Best Time')
        ax.axhline(avg_progression, color='red', linestyle='--', label=f'Avg: {avg_progression:.2f} min')
        ax.set_title(f"{distance}k Progression", fontsize=16)
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Time (minutes)", fontsize=12)
        ax.legend()
        ax.grid(alpha=0.5)
        st.pyplot(fig)
    else:
        st.warning(f"No data available for {distance}k progression.")



# In[ ]:




