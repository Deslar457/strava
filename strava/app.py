import streamlit as st
from services.strava_api import refresh_access_token, fetch_activities
from services.config import client_id, client_secret, refresh_token
from utils.data_processing import process_activities
from utils.visualizations import plot_monthly_distance, plot_weekly_distance
import time

def main():
    # Set up Streamlit page configuration
    st.set_page_config(page_title="Strava Dashboard", layout="wide")

    # Title and description
    st.title("Strava Dashboard")
    st.write("Visualize your activity data with monthly and weekly insights.")

    # Step 1: Refresh the access token
    try:
        access_token = refresh_access_token(refresh_token, client_id, client_secret)
        st.success("Access token refreshed successfully!")
    except Exception as e:
        st.error(f"Error refreshing token: {e}")
        return

    # Step 2: Fetch and process activities
    try:
        start_date = int(time.mktime(time.strptime("2024-06-01", "%Y-%m-%d")))
        activities = fetch_activities(access_token, start_date)

        if not activities:
            st.warning("No activities found.")
            return

        df = process_activities(activities)

    except Exception as e:
        st.error(f"Error fetching or processing activities: {e}")
        return

    # Step 3: Display data and visualizations
    display_last_sessions(df)
    display_monthly_distance_chart(df)
    display_weekly_distance_chart(df)

def display_last_sessions(df):
    """
    Display the last 7 sessions in a table.
    """
    st.header("Last 7 Sessions")
    st.write(
        df[["Date", "Distance (km)", "Time (minutes)", "Average HR"]]
        .tail(7)
        .style.format(
            {
                "Distance (km)": "{:.2f}",
                "Time (minutes)": "{:.2f}",
                "Average HR": "{:.0f}",
            }
        )
    )

def display_monthly_distance_chart(df):
    """
    Display the monthly distance bar chart.
    """
    st.header("Monthly Distance")
    st.pyplot(plot_monthly_distance(df))

def display_weekly_distance_chart(df):
    """
    Display the weekly distance bar chart.
    """
    st.header("Weekly Distance")
    st.pyplot(plot_weekly_distance(df))

if __name__ == "__main__":
    main()



