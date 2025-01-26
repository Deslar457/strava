import sys
import os



current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.append(project_root)


import streamlit as st
from services.strava_api import refresh_access_token, fetch_activities
from services.config import client_id, client_secret, refresh_token
from utils.data_processing import process_activities
from utils.visualisations import plot_monthly_distance, plot_weekly_distance
import time



def main():
    st.set_page_config(page_title="Strava Dashboard", layout="wide")

    st.title("Strava Dashboard")
    st.write("Fetching real data from Strava...")

    # Refresh access token
    try:
        access_token = refresh_access_token(refresh_token, client_id, client_secret)
        st.success("Access token refreshed successfully!")
    except Exception as e:
        st.error(f"Error refreshing token: {e}")
        return

    # Fetch activities
    try:
        start_date = int(time.mktime(time.strptime("2024-06-01", "%Y-%m-%d")))
        activities = fetch_activities(access_token, start_date)

        if activities:
            st.success("Activities fetched successfully!")
            
            # Process activities
            df = process_activities(activities)
            
            # Display the last 7 sessions in a table
            st.header("Last 7 Sessions")
            st.write(df[["Date", "Distance (km)", "Time (minutes)", "Average HR"]].tail(7))

            # Monthly Distance Bar Chart
            st.header("Monthly Distance")
            st.pyplot(plot_monthly_distance(df))

            # Weekly Distance Bar Chart
            st.header("Weekly Distance")
            st.pyplot(plot_weekly_distance(df))

        else:
            st.warning("No activities found.")
    except Exception as e:
        st.error(f"Error fetching activities: {e}")

if __name__ == "__main__":
    main()

