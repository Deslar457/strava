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
    """Generate a bar chart for weekly distance."""
    weekly_distance = df.groupby("Week")["Distance (km)"].sum()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(weekly_distance.index, weekly_distance.values, color="lightgreen", width=7)
    ax.axhline(weekly_distance.mean(), color="red", linestyle="--", label="Avg Distance")
    ax.set_title("Weekly Distance", fontsize=16)
    ax.set_xlabel("Week", fontsize=12)
    ax.set_ylabel("Distance (km)", fontsize=12)
    ax.legend()
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
        ax.set_title(f"Progression for {lower_bound:.1f}-{upper_bound:.1f} km", fontsize=16)
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Time (minutes)", fontsize=12)
        ax.legend()
        ax.grid(alpha=0.5)
        return fig
    return None


def calculate_workloads(df):
    """Calculate acute (7-day) and chronic (28-day) workloads."""
    df = df.sort_values("Date")

    # Acute Workload (7-day total)
    acute_workload = df[df["Date"] >= (df["Date"].max() - pd.Timedelta(days=7))]["Distance (km)"].sum()

    # Chronic Workload (28-day average)
    chronic_workload = (
        df[df["Date"] >= (df["Date"].max() - pd.Timedelta(days=28))]["Distance (km)"].sum() / 4
    )

    return acute_workload, chronic_workload


def last_sessions_table(df):
    """Prepare a table of the last 7 sessions."""
    return df[["Date", "Distance (km)", "Time (minutes)", "Average HR"]].tail(7).reset_index(drop=True)





