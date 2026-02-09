import streamlit as st
from services.strava_api import refresh_access_token, fetch_activities
from services.config import client_id, client_secret, refresh_token
from utils.data_processing import process_activities
from utils.visualisations import (
    plot_monthly_distance,
    plot_weekly_distance,
    plot_progression,
    calculate_workloads,
    plot_pace_vs_hr,
    plot_weekly_rolling_distance,
    predict_10k_rf
)
import time
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def main():
    st.set_page_config(page_title="Strava Dashboard", layout="wide")

    st.title("Strava Dashboard")
    st.write("Running Data")

    try:
        access_token = refresh_access_token(refresh_token, client_id, client_secret)
        st.success("Access token refreshed successfully")
    except Exception as e:
        st.error(f"Error refreshing token: {e}")
        return

    try:
        start_date = int(time.mktime(time.strptime("2024-06-01", "%Y-%m-%d")))
        activities = fetch_activities(access_token, start_date)

        if activities:
            st.success("Activities fetched successfully")
            df = process_activities(activities)

            acute_workload, chronic_workload, acwr = calculate_workloads(df)
            st.subheader("Workload Summary")
            workload_data = {
                "Metric": ["Acute Workload (7 days)", "Chronic Workload (28 days avg)", "ACWR"],
                "Value": [f"{acute_workload:.2f} km", f"{chronic_workload:.2f} km", f"{acwr:.2f}"],
            }
            st.table(workload_data)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Monthly Distance")
                st.pyplot(plot_monthly_distance(df))
            with col2:
                st.subheader("Weekly Distance")
                st.pyplot(plot_weekly_distance(df))

            st.subheader("Distance Progression Filter")
            selected_distance = st.selectbox("Select a Distance for Progression:", [5, 6, 7, 10], index=0)
            st.subheader(f"{selected_distance}K Progression")
            progression_chart = plot_progression(df, selected_distance - 0.1, selected_distance + 0.1)
            if progression_chart:
                st.pyplot(progression_chart)
            else:
                st.warning(f"No data available for {selected_distance}K progression.")

            st.subheader("Rolling Average of Weekly Distance")
            rolling_avg_chart = plot_weekly_rolling_distance(df)
            if rolling_avg_chart:
                st.pyplot(rolling_avg_chart)
            else:
                st.warning("No data available for weekly rolling average.")

            st.subheader("Pace vs. Heart Rate by Month")
            selected_hr_distance = st.selectbox("Select a Distance for Pace vs. Heart Rate Analysis:", [5, 6, 7, 8, 10], index=0)
            pace_hr_chart = plot_pace_vs_hr(df, selected_hr_distance - 0.1, selected_hr_distance + 0.1)
            if pace_hr_chart:
                st.pyplot(pace_hr_chart)
            else:
                st.warning(f"No data available for {selected_hr_distance}K pace vs. heart rate analysis.")

            st.subheader("Last 7 Sessions")
            st.table(df[["Date", "Distance (km)", "Formatted Time", "Average HR"]].tail(7).reset_index(drop=True))

            st.header("\U0001F916 ML Insights: 10K Prediction (Model Comparison)")
            model_results = predict_10k_from_all_models(df)
            if isinstance(model_results, pd.DataFrame):
                st.table(model_results)
            else:
                st.warning(model_results)

            st.header("\U0001F4C5 Weekly Training Plan")
            training_plan = {
                "Monday": "10–15K Long Easy Run",
                "Tuesday": "2K Intervals × 4",
                "Wednesday": "Rest or Recovery",
                "Thursday": "8–12K Steady Run",
                "Friday": "Rest or Cross Training",
                "Saturday": "Mixed Intervals: 6, 5, 4, 3, 2 × 2",
                "Sunday": "Optional Easy Run or Rest"
            }

            today = datetime.today().strftime("%A")
            st.subheader(f"Today's Session: {today}")
            st.write(training_plan.get(today, "No plan found."))

            with st.expander("View Full Weekly Plan"):
                for day, session in training_plan.items():
                    st.markdown(f"**{day}:** {session}")

        else:
            st.warning("No activities found.")

    except Exception as e:
        st.error(f"Error fetching activities: {e}")

if __name__ == "__main__":
    main()