import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.dirname(__file__)))


def plot_progression(df, lower_bound, upper_bound):
    """Generate a line graph for progression of a specific distance range."""
    progression = df[
        (df["Distance (km)"] >= lower_bound) & (df["Distance (km)"] < upper_bound)
    ].groupby("Month")["Time (minutes)"].min()

    if not progression.empty:
        def format_time(minutes):
            mins = int(minutes)
            secs = round((minutes - mins) * 60)
            return f"{mins}:{secs:02d}"

        formatted_times = [format_time(t) for t in progression.values]

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(progression.index, progression.values, marker="o", color="blue", label="Best Time")

        # Annotate each point with MM:SS format
        for i, txt in enumerate(formatted_times):
            ax.annotate(txt, (progression.index[i], progression.iloc[i]), 
                        textcoords="offset points", xytext=(0, 5), ha="center")

        avg_time = progression.mean()
        ax.axhline(avg_time, color="red", linestyle="--", label=f"Avg: {format_time(avg_time)}")
        
        ax.set_title(f"Progression for {lower_bound:.1f}-{upper_bound:.1f} km", fontsize=16)
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Time (minutes)", fontsize=12)
        ax.legend()
        ax.grid(alpha=0.5)
        return fig
    return None


def plot_monthly_distance(df):
    """Generate a bar chart for monthly distance with average distance label."""
    monthly_distance = df.groupby("Month")["Distance (km)"].sum()
    avg_distance = monthly_distance.mean()

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(monthly_distance.index, monthly_distance.values, color="skyblue", width=20, edgecolor="black")
    ax.axhline(avg_distance, color="red", linestyle="--", label=f"Avg Distance: {avg_distance:.2f} km")

    ax.set_title("Monthly Distance", fontsize=16)
    ax.set_xlabel("Month", fontsize=12)
    ax.set_ylabel("Distance (km)", fontsize=12)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    plt.xticks(rotation=45)
    return fig


def plot_weekly_distance(df):
    """Generate a bar chart for weekly distance with average distance label."""
    weekly_distance = df.groupby("Week")["Distance (km)"].sum()
    avg_distance = weekly_distance.mean()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(weekly_distance.index, weekly_distance.values, color="lightgreen", width=7, edgecolor="black")
    ax.axhline(avg_distance, color="red", linestyle="--", label=f"Avg Distance: {avg_distance:.2f} km")

    ax.set_title("Weekly Distance", fontsize=16)
    ax.set_xlabel("Week", fontsize=12)
    ax.set_ylabel("Distance (km)", fontsize=12)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    plt.xticks(rotation=45)
    return fig

def format_pace(y, _):
    """Convert decimal minutes to mm:ss format for plotting."""
    minutes = int(y)
    seconds = int((y - minutes) * 60)
    return f"{minutes}:{seconds:02d}"

def plot_pace_vs_hr(df, lower_bound, upper_bound):
    """Plot Pace vs. Heart Rate for a selected distance range each month."""
    filtered_df = df[
        (df["Distance (km)"] >= lower_bound) & (df["Distance (km)"] < upper_bound)
    ]

    if not filtered_df.empty:
        monthly_data = filtered_df.groupby("Month").agg({
            "Time (minutes)": "sum",
            "Distance (km)": "sum",
            "Average HR": "mean"
        }).reset_index()

        # Calculate pace in minutes per km
        monthly_data["Pace (min/km)"] = monthly_data["Time (minutes)"] / monthly_data["Distance (km)"]

        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Line chart for Pace
        ax1.set_xlabel("Month", fontsize=12)
        ax1.set_ylabel("Pace (min/km)", color="blue", fontsize=12)
        ax1.plot(monthly_data["Month"], monthly_data["Pace (min/km)"], marker="o", color="blue", label="Pace")
        ax1.tick_params(axis="y", labelcolor="blue")
        ax1.invert_yaxis()  # Faster times at the top

        # Convert y-axis labels to mm:ss format
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(format_pace))

        # Second y-axis for Heart Rate
        ax2 = ax1.twinx()
        ax2.set_ylabel("Avg HR (bpm)", color="red", fontsize=12)
        ax2.plot(monthly_data["Month"], monthly_data["Average HR"], marker="s", color="red", linestyle="--", label="Heart Rate")
        ax2.tick_params(axis="y", labelcolor="red")

        ax1.set_title(f"Pace vs. Heart Rate for {lower_bound}K - {upper_bound}K", fontsize=16)
        ax1.grid(alpha=0.5)
        fig.tight_layout()
        plt.show()
        return fig
    return None


def calculate_workloads(df):
    """Calculate acute (7-day), chronic (28-day), and ACWR."""
    df = df.sort_values("Date")
    acute_workload = df[df["Date"] >= (df["Date"].max() - pd.Timedelta(days=7))]["Distance (km)"].sum()
    chronic_workload = df[df["Date"] >= (df["Date"].max() - pd.Timedelta(days=28))]["Distance (km)"].sum() / 4
    acwr = acute_workload / chronic_workload if chronic_workload > 0 else 0
    return acute_workload, chronic_workload, acwr



def plot_weekly_rolling_distance(df, window=4):
    """Plot a rolling average of weekly distance."""
    
    # Ensure Date column is in datetime format
    df["Date"] = pd.to_datetime(df["Date"])
    
    # Group by week (sum distance per week)
    df["Week"] = df["Date"].dt.to_period("W").apply(lambda r: r.start_time)
    weekly_data = df.groupby("Week")["Distance (km)"].sum().reset_index()

    # Compute rolling average
    weekly_data["Rolling Avg (km)"] = weekly_data["Distance (km)"].rolling(window=window, min_periods=1).mean()

    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(weekly_data["Week"], weekly_data["Distance (km)"], marker="o", linestyle="-", label="Weekly Distance")
    ax.plot(weekly_data["Week"], weekly_data["Rolling Avg (km)"], marker="s", linestyle="--", color="red", label=f"{window}-Week Rolling Avg")
    
    ax.set_xlabel("Week", fontsize=12)
    ax.set_ylabel("Distance (km)", fontsize=12)
    ax.set_title(f"Weekly Distance with {window}-Week Rolling Average", fontsize=16)
    ax.legend()
    ax.grid(alpha=0.5)
    plt.show()
    return fig




def predict_10k_performance(df):
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")

    # Calculate pace
    df["Pace"] = df["Time (minutes)"] / df["Distance (km)"]

    # Calculate pace:HR ratio
    df["Pace/HR"] = df["Pace"] / df["Average HR"]

    # Rolling 7-day mileage
    df["7d_km"] = df.set_index("Date")["Distance (km)"].rolling("7d").sum().reset_index(drop=True)

    # Filter for 10K-ish runs
    tenk_df = df[(df["Distance (km)"] >= 9.8) & (df["Distance (km)"] <= 10.2)].dropna()

    if len(tenk_df) < 5:
        return None, "Not enough 10K runs to train the model."

    # Features and target
    features = tenk_df[["Distance (km)", "Pace", "Average HR", "Pace/HR", "7d_km"]]
    target = tenk_df["Time (minutes)"]

    # Split and train
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.25, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Predict next 10K time using most recent data
    latest = df.iloc[-1]
    latest_features = pd.DataFrame([{
        "Distance (km)": 10.0,
        "Pace": latest["Time (minutes)"] / latest["Distance (km)"],
        "Average HR": latest["Average HR"],
        "Pace/HR": (latest["Time (minutes)"] / latest["Distance (km)"]) / latest["Average HR"],
        "7d_km": df.set_index("Date")["Distance (km)"].rolling("7d").sum().iloc[-1]
    }])

    prediction = model.predict(latest_features)[0]
    mae = mean_absolute_error(y_test, model.predict(X_test))

    return round(prediction, 1), round(mae, 1)




    