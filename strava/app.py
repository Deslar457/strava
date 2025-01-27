import streamlit as st
from services.strava_api import refresh_access_token, fetch_activities
from services.config import client_id, client_secret, refresh_token
from utils.data_processing import process_activities
from utils.visualisations import (
    plot_monthly_distance,
    plot_weekly_distance,
    plot_progression,
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

            # Display Monthly and Weekly Distance side by side
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Monthly Distance")
                st.pyplot(plot_monthly_distance(df))

            with col2:
                st.subheader("Weekly Distance")
                st.pyplot(plot_weekly_distance(df))

            # Distance Range Filter for Progression (moved to main area)
            st.subheader("Distance Progression Filter")
            selected_distance = st.selectbox(
                "Select a Distance for Progression:",
                [5, 6, 7, 10],
                index=0
            )

            # Display Progression Graph
            st.subheader(f"{selected_distance}K Progression")
            progression_chart = plot_progression(df, selected_distance - 0.1, selected_distance + 0.1)

            if progression_chart:
                st.pyplot(progression_chart)
            else:
                st.warning(f"No data available for {selected_distance}K progression.")
        else:
            st.warning("No activities found.")
    except Exception as e:
        st.error(f"Error fetching activities: {e}")


if __name__ == "__main__":
    main()
