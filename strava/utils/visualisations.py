import pandas as pd
import matplotlib.pyplot as plt


def plot_monthly_distance(df):
    """Generate a bar chart for monthly distance."""
    monthly_distance = df.groupby("Month")["Distance (km)"].sum()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(monthly_distance.index, monthly_distance.values, color="skyblue", width=20)
    ax.axhline(monthly_distance.mean(), color="red", linestyle="--", label="Avg Distance")
    ax.set_title("Monthly Distance", fontsize=16)
    ax.set_xlabel("Month", fontsize=12)
    ax.set_ylabel("Distance (km)", fontsize=12)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    plt.xticks(rotation=45)
    return fig


def plot_weekly_distance(df):
    """Generate a bar chart for weekly distance with improved formatting."""
    weekly_distance = df.groupby("Week")["Distance (km)"].sum()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(weekly_distance.index, weekly_distance.values, color="lightgreen", width=4)
    ax.axhline(weekly_distance.mean(), color="red", linestyle="--", label="Avg Distance")
    ax.set_title("Weekly Distance", fontsize=16)
    ax.set_xlabel("Week", fontsize=12)
    ax.set_ylabel("Distance (km)", fontsize=12)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    plt.xticks(rotation=45, fontsize=10)
    return fig


def plot_progression(df, lower_bound, upper_bound):
    """Generate a line graph for progression of a specific distance range."""
    progression = df[
        (df["Distance (km)"] >= lower_bound) & (df["Distance (km)"] < upper_bound)
    ].groupby("Month")["Time (minutes)"].min()

    if not progression.empty:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(progression.index, progression.values, marker="o", color="blue", label="Best Time")
        ax.axhline(progression.mean(), color="red", linestyle="--", label=f"Avg: {progression.mean():.2f} min")
        ax.set_title(f"Progression for {lower_bound:.1f}-{upper_bound:.1f} km", fontsize=16)
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Time (minutes)", fontsize=12)
        ax.legend()
        ax.grid(alpha=0.5)
        return fig
    return None


def calculate_acwr(df):
    """Calculate ACWR and provide recommended running distance."""
    df = df.sort_values("Date")

    # Acute Workload (last 7 days)
    last_7_days = df[df["Date"] >= (df["Date"].max() - pd.Timedelta(days=7))]
    acute_workload = last_7_days["Distance (km)"].sum()

    # Chronic Workload (average weekly workload over 28 days)
    last_28_days = df[df["Date"] >= (df["Date"].max() - pd.Timedelta(days=28))]
    chronic_workload = last_28_days["Distance (km)"].sum() / 4 if not last_28_days.empty else 0

    # Calculate ACWR
    acwr = acute_workload / chronic_workload if chronic_workload > 0 else 0

    # Recommended next session distance to maintain safe ACWR
    max_safe_acwr = 1.5
    target_acute = chronic_workload * max_safe_acwr
    suggested_distance = max(0, target_acute - acute_workload)

    # Recommendation text
    if acwr < 0.8:
        recommendation = f"Increase workload gradually. Suggested run: {suggested_distance:.2f} km."
    elif 0.8 <= acwr <= 1.5:
        recommendation = f"Workload is within a safe range. Suggested run: {suggested_distance:.2f} km."
    else:
        recommendation = f"Workload is too high! Suggested run: {suggested_distance:.2f} km to reduce intensity."

    # Prepare ACWR data table
    acwr_data = pd.DataFrame({
        "Metric": ["Acute Workload (7 days)", "Chronic Workload (28 days avg)", "ACWR", "Recommendation"],
        "Value": [f"{acute_workload:.2f} km", f"{chronic_workload:.2f} km", f"{acwr:.2f}", recommendation]
    })

    return acwr_data


def last_sessions_table(df):
    """Prepare a table of the last 7 sessions."""
    return df[["Date", "Distance (km)", "Time (minutes)", "Average HR"]].tail(7).reset_index(drop=True)



