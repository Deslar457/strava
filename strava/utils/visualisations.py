import pandas as pd
import matplotlib.pyplot as plt


def plot_monthly_distance(df):
    """Generate a bar chart for monthly distance with average distance label."""
    monthly_distance = df.groupby("Month")["Distance (km)"].sum()
    avg_distance = monthly_distance.mean()

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(monthly_distance.index, monthly_distance.values, color="skyblue", width=20, edgecolor="black")
    ax.axhline(avg_distance, color="red", linestyle="--", label=f"Avg Distance: {avg_distance:.2f} km")

    # Annotate the average line
    ax.text(
        0.95, avg_distance + 1, f"{avg_distance:.2f} km", color="red", fontsize=10, va="bottom", ha="right"
    )

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
    bars = ax.bar(
        weekly_distance.index,
        weekly_distance.values,
        color="lightgreen",
        width=7,
        edgecolor="black",  # Add black outline
    )
    ax.axhline(avg_distance, color="red", linestyle="--", label=f"Avg Distance: {avg_distance:.2f} km")

    # Annotate the average line
    ax.text(
        0.95, avg_distance + 1, f"{avg_distance:.2f} km", color="red", fontsize=10, va="bottom", ha="right"
    )

    ax.set_title("Weekly Distance", fontsize=16)
    ax.set_xlabel("Week", fontsize=12)
    ax.set_ylabel("Distance (km)", fontsize=12)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    plt.xticks(rotation=45)
    return fig


def calculate_workloads(df):
    """Calculate acute (7-day), chronic (28-day), and ACWR."""
    df = df.sort_values("Date")

    # Acute Workload (7-day total)
    acute_workload = df[df["Date"] >= (df["Date"].max() - pd.Timedelta(days=7))]["Distance (km)"].sum()

    # Chronic Workload (28-day average)
    chronic_workload = (
        df[df["Date"] >= (df["Date"].max() - pd.Timedelta(days=28))]["Distance (km)"].sum() / 4
    )

    # ACWR Calculation
    acwr = acute_workload / chronic_workload if chronic_workload > 0 else 0

    return acute_workload, chronic_workload, acwr


def last_sessions_table(df):
    """Prepare a table of the last 7 sessions."""
    return df[["Date", "Distance (km)", "Time (minutes)", "Average HR"]].tail(7).reset_index(drop=True)






