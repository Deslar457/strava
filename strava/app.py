import streamlit as st
from services.strava_api import refresh_access_token, fetch_activities
from services.config import client_id, client_secret, refresh_token
from utils.data_processing import process_activities
from utils.visualisations import (
    plot_monthly_distance,
    plot_weekly_distance,
    calculate_daily_acwr,
    plot_daily_acwr,
    last_sessions_table,
)
import time


def main():
    st.set_page_config(page_title="Strava Dashboard", layout="wide")

    st.title("Strava Dashboard")
    st.write("Running Data")

    # Refresh the access token
    try:
        access_token = refresh_access_token(refresh_token, client_id, client_secret)
        st.success("Access token refreshed successfully!")
    except Exception as e:
        st.error(f"Error refreshing token: {e}")
        return

    # Fetch and process activities
    try:
        start_date = int(time.mktime(time.strptime("2024-06-01", "%Y-%m-%d")))
        activities = fetch_activities(access_token, start_date)

        if activities:
            st.success("Activities fetched successfully!")
            df = process_activities(activities)

            # Monthly and Weekly Distance Visualisations
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Monthly Distance")
                st.pyplot(plot_monthly_distance(df))

            with col2:
                st.subheader("Weekly Distance")
                st.pyplot(plot_weekly_distance(df))

            # Daily ACWR with RAG Indicators
            st.subheader("Daily ACWR Analysis")
            acwr_df = calculate_daily_acwr(df)
            st.table(acwr_df[["Date", "Daily Distance (km)", "Acute Workload (km)", "Chronic Workload (km)", "ACWR", "Status"]])
            st.pyplot(plot_daily_acwr(acwr_df))

            # Last 7 Sessions Table
            st.subheader("Last 7 Sessions")
            st.table(last_sessions_table(df))
        else:
            st.warning("No activities found.")
    except Exception as e:
        st.error(f"Error fetching activities: {e}")


if __name__ == "__main__":
    main()
