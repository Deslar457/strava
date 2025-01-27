import pandas as pd
import matplotlib.pyplot as plt


def plot_monthly_distance(df):
    """Generate a bar chart for monthly distance."""
    monthly_distance = df.groupby("Month")["Distance (km)"].sum()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(monthly_distance.index, monthly_distance.values, color="skyblue", width=20)
    ax.set_title("Monthly Distance", fontsize=16)
    ax.set_xlabel("Month", fontsize=12)
    ax.set_ylabel("Distance (km)", fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    plt.xticks(rotation=45)
    return fig


def plot_weekly_distance(df):
    """Generate a bar chart for weekly distance."""
    weekly_distance = df.groupby("Week")["Distance (km)"].sum()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(weekly_distance.index, weekly_distance.values, color="lightgreen", width=10)
    ax.set_title("Weekly Distance", fontsize=16)
    ax.set_xlabel("Week", fontsize=12)
    ax.set_ylabel("Distance (km)", fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    plt.xticks(rotation=45)
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
        ax.set_title("Distance Progression", fontsize=16)
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Time (minutes)", fontsize=12)
        ax.legend()
        ax.grid(alpha=0.5)
        return fig
    return None


def calculate_acwr(df):
    """Calculate Acute:Chronic Workload Ratio (ACWR) and generate recommendations."""
    df = df.sort_values("Date")

    # Acute Workload (last 7 days)
    last_7_days = df[df["Date"] >= (df["Date"].max() - pd.Timedelta(days=7))]
    acute_workload = last_7_days["Distance (km)"].sum()

    # Chronic Workload (average weekly workload over 28 days)
    last_28_days = df[df["Date"] >= (df["Date"].max() - pd.Timedelta(days=28))]
    chronic_workload = last_28_days["Distance (km)"].sum() / 4 if not last_28_days.empty else 0

    # Calculate ACWR
    acwr = acute_workload / chronic_workload if chronic_workload > 0 else 0

    # Recommendation based on ACWR
    if acwr < 0.8:
        recommendation = "Increase workload gradually."
    elif 0.8 <= acwr <= 1.3:
        recommendation = "Workload is optimal. Maintain the current training load."
    else:
        recommendation = "High workload! Reduce intensity to prevent injury."

    # Suggested Distance for Next Session
    desired_acwr = 1.05  # Optimal workload ratio
    suggested_distance = chronic_workload * desired_acwr - acute_workload

    # Prepare table
    acwr_data = pd.DataFrame({
        "Metric": ["Acute Workload (7 days)", "Chronic Workload (28 days avg)", "ACWR", "Recommendation", "Suggested Distance for Next Session"],
        "Value": [f"{acute_workload:.2f} km", f"{chronic_workload:.2f} km", f"{acwr:.2f}", recommendation, f"{max(suggested_distance, 0):.2f} km"]
    })

    return acwr_data
