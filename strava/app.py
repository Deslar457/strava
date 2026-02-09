import streamlit as st
import time
from datetime import datetime
import pandas as pd

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


def main():
    st.set_page_config(page_title="Strava Dashboard", layout="wide")
    st.title("Strava Dashboard")

    access_token = refresh_access_token(refresh_token, client_id, client_secret)

    start_date = int(time.mktime(time.strptime("2024-06-01", "%Y-%m-%d")))
    activities = fetch_activities(access_token, start_date)

    if not activities:
        st.warning("No activities found.")
        return

    df = process_activities(activities)

    acute, chronic, acwr = calculate_workloads(df)
    st.subheader("Workload Summary")
    st.table({
        "Metric": ["Acute (7d)", "Chronic (28d)", "ACWR"],
        "Value": [f"{acute:.1f} km", f"{chronic:.1f} km", f"{acwr:.2f}"]
    })

    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(plot_monthly_distance(df))
    with col2:
        st.pyplot(plot_weekly_distance(df))

    st.subheader("Distance Progression")
    d = st.selectbox("Distance", [5, 6, 7, 10])
    fig = plot_progression(df, d - 0.1, d + 0.1)
    if fig:
        st.pyplot(fig)

    st.subheader("Rolling Weekly Load")
    st.pyplot(plot_weekly_rolling_distance(df))

    st.subheader("Pace vs Heart Rate")
    d_hr = st.selectbox("Distance (HR)", [5, 6, 7, 8, 10])
    fig = plot_pace_vs_hr(df, d_hr - 0.1, d_hr + 0.1)
    if fig:
        st.pyplot(fig)

    st.subheader("Last 7 Runs")
    st.table(df[["Date", "Distance (km)", "Formatted Time", "Average HR"]].tail(7))

    st.header("🤖 10K Prediction (Random Forest)")
    result = predict_10k_rf(df)

    if isinstance(result, dict):
        st.metric("Predicted 10K", result["Predicted Time"])
        st.caption(
            f"MAE ±{result['MAE (±min)']} min | "
            f"Training runs: {result['Training Runs']}"
        )
    else:
        st.warning(result)

    st.header("📅 Weekly Training Plan")
    plan = {
        "Monday": "10–15K Easy",
        "Tuesday": "Intervals",
        "Wednesday": "Rest",
        "Thursday": "Steady Run",
        "Friday": "Rest",
        "Saturday": "Mixed Intervals",
        "Sunday": "Easy / Rest"
    }

    today = datetime.today().strftime("%A")
    st.write(f"**Today:** {plan.get(today)}")


if __name__ == "__main__":
    main()
