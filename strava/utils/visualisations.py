# -----------------------------
# visualisations.py
# -----------------------------

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error


# -----------------------------
# Helpers
# -----------------------------
def format_time(minutes):
    mins = int(minutes)
    secs = round((minutes - mins) * 60)
    return f"{mins}:{secs:02d}"


def format_pace(y, _):
    minutes = int(y)
    seconds = int((y - minutes) * 60)
    return f"{minutes}:{seconds:02d}"


# -----------------------------
# Visualisations
# -----------------------------
def plot_progression(df, lower_bound, upper_bound):
    progression = df[
        (df["Distance (km)"] >= lower_bound) &
        (df["Distance (km)"] < upper_bound)
    ].groupby("Month")["Time (minutes)"].min()

    if progression.empty:
        return None

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(progression.index, progression.values, marker="o", label="Best Time")

    for i, t in enumerate(progression.values):
        ax.annotate(
            format_time(t),
            (progression.index[i], t),
            textcoords="offset points",
            xytext=(0, 5),
            ha="center"
        )

    avg_time = progression.mean()
    ax.axhline(avg_time, linestyle="--", label=f"Avg: {format_time(avg_time)}")

    ax.set_title(f"Progression for {lower_bound:.1f}–{upper_bound:.1f} km")
    ax.set_xlabel("Month")
    ax.set_ylabel("Time (minutes)")
    ax.legend()
    ax.grid(alpha=0.5)

    return fig


def plot_monthly_distance(df):
    monthly = df.groupby("Month")["Distance (km)"].sum()
    avg = monthly.mean()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(monthly.index, monthly.values, width=10)
    ax.axhline(avg, linestyle="--", label=f"Avg {avg:.1f} km")

    ax.set_title("Monthly Distance")
    ax.set_xlabel("Month")
    ax.set_ylabel("Distance (km)")
    ax.legend()
    ax.grid(axis="y", alpha=0.5)
    plt.xticks(rotation=45)

    return fig


def plot_weekly_distance(df):
    weekly = df.groupby("Week")["Distance (km)"].sum()
    avg = weekly.mean()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(weekly.index, weekly.values, width=5)
    ax.axhline(avg, linestyle="--", label=f"Avg {avg:.1f} km")

    ax.set_title("Weekly Distance")
    ax.set_xlabel("Week")
    ax.set_ylabel("Distance (km)")
    ax.legend()
    ax.grid(axis="y", alpha=0.5)
    plt.xticks(rotation=45)

    return fig


def plot_pace_vs_hr(df, lower_bound, upper_bound):
    df = df[
        (df["Distance (km)"] >= lower_bound) &
        (df["Distance (km)"] < upper_bound)
    ]

    if df.empty:
        return None

    monthly = df.groupby("Month").agg({
        "Time (minutes)": "sum",
        "Distance (km)": "sum",
        "Average HR": "mean"
    }).reset_index()

    monthly["Pace"] = monthly["Time (minutes)"] / monthly["Distance (km)"]

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(monthly["Month"], monthly["Pace"], marker="o")
    ax1.set_ylabel("Pace (min/km)")
    ax1.invert_yaxis()
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(format_pace))

    ax2 = ax1.twinx()
    ax2.plot(monthly["Month"], monthly["Average HR"], linestyle="--", marker="s")
    ax2.set_ylabel("Average HR")

    ax1.set_title("Pace vs Heart Rate")
    ax1.grid(alpha=0.5)

    return fig


def calculate_workloads(df):
    df = df.sort_values("Date")
    acute = df[df["Date"] >= df["Date"].max() - pd.Timedelta(days=7)]["Distance (km)"].sum()
    chronic = df[df["Date"] >= df["Date"].max() - pd.Timedelta(days=28)]["Distance (km)"].sum() / 4
    acwr = acute / chronic if chronic > 0 else 0
    return acute, chronic, acwr


def plot_weekly_rolling_distance(df, window=4):
    df = df.copy()
    df["Week"] = df["Date"].dt.to_period("W").dt.start_time
    weekly = df.groupby("Week")["Distance (km)"].sum().reset_index()
    weekly["Rolling Avg"] = weekly["Distance (km)"].rolling(window, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(weekly["Week"], weekly["Distance (km)"], marker="o", label="Weekly")
    ax.plot(weekly["Week"], weekly["Rolling Avg"], linestyle="--", label="Rolling Avg")

    ax.set_title("Weekly Distance (Rolling Average)")
    ax.set_xlabel("Week")
    ax.set_ylabel("Distance (km)")
    ax.legend()
    ax.grid(alpha=0.5)

    return fig


# -----------------------------
# ML – Random Forest only
# -----------------------------
def predict_10k_rf(df):
    df = df.copy().sort_values("Date")

    df["Pace"] = df["Time (minutes)"] / df["Distance (km)"]
    df["Pace/HR"] = df["Pace"] / df["Average HR"]
    df["7d_km"] = (
        df.set_index("Date")["Distance (km)"]
        .rolling("7d")
        .sum()
        .reset_index(drop=True)
    )

    tenk = df[(df["Distance (km)"].between(9.8, 10.2))].dropna()
    if len(tenk) < 5:
        return None, "Not enough 10K runs."

    X = tenk[["Pace", "Average HR", "Pace/HR", "7d_km"]]
    y = tenk["Time (minutes)"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    model = RandomForestRegressor(n_estimators=300, max_depth=6, random_state=42)
    model.fit(X_train, y_train)

    mae = mean_absolute_error(y_test, model.predict(X_test))

    latest = df.iloc[-1]
    latest_input = pd.DataFrame([{
        "Pace": latest["Pace"],
        "Average HR": latest["Average HR"],
        "Pace/HR": latest["Pace/HR"],
        "7d_km": df["7d_km"].iloc[-1]
    }])

    pred = model.predict(latest_input)[0]

    return {
        "Predicted Time": format_time(pred),
        "Predicted Minutes": round(pred, 2),
        "MAE (±min)": round(mae, 2),
        "Training Runs": len(tenk)
    }
