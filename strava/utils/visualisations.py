# -----------------------------
# visualisations.py (FULL FILE)
# -----------------------------

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error


def plot_progression(df, lower_bound, upper_bound):
    progression = df[(df["Distance (km)"] >= lower_bound) & (df["Distance (km)"] < upper_bound)]
    progression = progression.groupby("Month")["Time (minutes)"].min()
    if not progression.empty:
        def format_time(minutes):
            mins = int(minutes)
            secs = round((minutes - mins) * 60)
            return f"{mins}:{secs:02d}"
        formatted_times = [format_time(t) for t in progression.values]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(progression.index, progression.values, marker="o", color="blue", label="Best Time")
        for i, txt in enumerate(formatted_times):
            ax.annotate(txt, (progression.index[i], progression.iloc[i]), textcoords="offset points", xytext=(0, 5), ha="center")
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
    monthly_distance = df.groupby("Month")["Distance (km)"].sum()
    avg_distance = monthly_distance.mean()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(monthly_distance.index, monthly_distance.values, color="skyblue",width=10, edgecolor="black")
    ax.axhline(avg_distance, color="red", linestyle="--", label=f"Avg Distance: {avg_distance:.2f} km")
    ax.set_title("Monthly Distance", fontsize=16)
    ax.set_xlabel("Month")
    ax.set_ylabel("Distance (km)")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    plt.xticks(rotation=45)
    return fig


def plot_weekly_distance(df):
    weekly_distance = df.groupby("Week")["Distance (km)"].sum()
    avg_distance = weekly_distance.mean()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(weekly_distance.index, weekly_distance.values, color="lightgreen", width=5,edgecolor="black")
    ax.axhline(avg_distance, color="red", linestyle="--", label=f"Avg Distance: {avg_distance:.2f} km")
    ax.set_title("Weekly Distance", fontsize=16)
    ax.set_xlabel("Week")
    ax.set_ylabel("Distance (km)")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    plt.xticks(rotation=45)
    return fig


def format_pace(y, _):
    minutes = int(y)
    seconds = int((y - minutes) * 60)
    return f"{minutes}:{seconds:02d}"


def plot_pace_vs_hr(df, lower_bound, upper_bound):
    filtered_df = df[(df["Distance (km)"] >= lower_bound) & (df["Distance (km)"] < upper_bound)]
    if not filtered_df.empty:
        monthly_data = filtered_df.groupby("Month").agg({"Time (minutes)": "sum", "Distance (km)": "sum", "Average HR": "mean"}).reset_index()
        monthly_data["Pace (min/km)"] = monthly_data["Time (minutes)"] / monthly_data["Distance (km)"]
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.set_xlabel("Month")
        ax1.set_ylabel("Pace (min/km)", color="blue")
        ax1.plot(monthly_data["Month"], monthly_data["Pace (min/km)"], marker="o", color="blue")
        ax1.tick_params(axis="y", labelcolor="blue")
        ax1.invert_yaxis()
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(format_pace))
        ax2 = ax1.twinx()
        ax2.set_ylabel("Avg HR (bpm)", color="red")
        ax2.plot(monthly_data["Month"], monthly_data["Average HR"], marker="s", color="red", linestyle="--")
        ax2.tick_params(axis="y", labelcolor="red")
        ax1.set_title(f"Pace vs. Heart Rate for {lower_bound}K - {upper_bound}K")
        ax1.grid(alpha=0.5)
        fig.tight_layout()
        return fig
    return None


def calculate_workloads(df):
    df = df.sort_values("Date")
    acute = df[df["Date"] >= (df["Date"].max() - pd.Timedelta(days=7))]["Distance (km)"].sum()
    chronic = df[df["Date"] >= (df["Date"].max() - pd.Timedelta(days=28))]["Distance (km)"].sum() / 4
    acwr = acute / chronic if chronic > 0 else 0
    return acute, chronic, acwr


def plot_weekly_rolling_distance(df, window=4):
    df["Date"] = pd.to_datetime(df["Date"])
    df["Week"] = df["Date"].dt.to_period("W").apply(lambda r: r.start_time)
    weekly = df.groupby("Week")["Distance (km)"].sum().reset_index()
    weekly["Rolling Avg (km)"] = weekly["Distance (km)"].rolling(window=window, min_periods=1).mean()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(weekly["Week"], weekly["Distance (km)"], marker="o", label="Weekly Distance")
    ax.plot(weekly["Week"], weekly["Rolling Avg (km)"], marker="s", linestyle="--", color="red", label=f"{window}-Week Rolling Avg")
    ax.set_xlabel("Week")
    ax.set_ylabel("Distance (km)")
    ax.set_title("Weekly Distance with Rolling Average")
    ax.legend()
    ax.grid(alpha=0.5)
    return fig

##function for predction variou smodels
def predict_10k_from_all_models(df):
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    df["Pace"] = df["Time (minutes)"] / df["Distance (km)"]
    df["Pace/HR"] = df["Pace"] / df["Average HR"]
    df["7d_km"] = df.set_index("Date")["Distance (km)"].rolling("7d").sum().reset_index(drop=True)

    tenk_df = df[(df["Distance (km)"] >= 9.8) & (df["Distance (km)"] <= 10.2)].dropna()
    if len(tenk_df) < 5:
        return None, "Not enough 10K runs to train the models."

    features = tenk_df[["Distance (km)", "Pace", "Average HR", "Pace/HR", "7d_km"]]
    target = tenk_df["Time (minutes)"]
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.25, random_state=42)

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "XGBoost": XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
    }

    results = []
    latest = df.iloc[-1]
    latest_input = pd.DataFrame([{
        "Distance (km)": 10.0,
        "Pace": latest["Time (minutes)"] / latest["Distance (km)"],
        "Average HR": latest["Average HR"],
        "Pace/HR": (latest["Time (minutes)"] / latest["Distance (km)"]) / latest["Average HR"],
        "7d_km": df.set_index("Date")["Distance (km)"].rolling("7d").sum().iloc[-1]
    }])

    for name, model in models.items():
        model.fit(X_train, y_train)
        prediction = model.predict(latest_input)[0]
        mae = mean_absolute_error(y_test, model.predict(X_test))
        results.append({"Model": name, "Predicted Time (min)": round(prediction, 2), "MAE (±min)": round(mae, 2)})

    return pd.DataFrame(results)