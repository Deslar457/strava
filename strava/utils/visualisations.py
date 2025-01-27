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


def calculate_daily_acwr(df):
    """Calculate daily ACWR values with RAG status."""
    # Ensure data is sorted by date
    df = df.sort_values("Date")

    # Calculate daily distance
    daily_distance = df.groupby("Date")["Distance (km)"].sum()

    # Acute workload: Sum of last 7 days
    acute_workload = daily_distance.rolling(window=7, min_periods=1).sum()

    # Chronic workload: Average of last 28 days
    chronic_workload = daily_distance.rolling(window=28, min_periods=1).mean()

    # Calculate ACWR
    acwr = acute_workload / chronic_workload

    # Assign RAG status
    rag_status = pd.cut(
        acwr,
        bins=[0, 0.8, 1.3, float("inf")],
        labels=["Amber (Low)", "Green (Optimal)", "Red (High)"],
    )

    # Combine into a DataFrame
    acwr_df = pd.DataFrame({
        "Date": daily_distance.index,
        "Daily Distance (km)": daily_distance.values,
        "Acute Workload (km)": acute_workload.values,
        "Chronic Workload (km)": chronic_workload.values,
        "ACWR": acwr.values,
        "Status": rag_status,
    })

    return acwr_df


def plot_daily_acwr(acwr_df):
    """Plot daily ACWR with color-coded RAG indicators."""
    fig, ax = plt.subplots(figsize=(12, 6))

    colors = acwr_df["Status"].map({
        "Green (Optimal)": "green",
        "Amber (Low)": "orange",
        "Red (High)": "red"
    })

    ax.bar(acwr_df["Date"], acwr_df["ACWR"], color=colors, width=0.8)
    ax.axhline(0.8, color="blue", linestyle="--", label="Lower Threshold (0.8)")
    ax.axhline(1.3, color="red", linestyle="--", label="Upper Threshold (1.3)")
    ax.set_title("Daily ACWR with RAG Indicators", fontsize=16)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("ACWR", fontsize=12)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    plt.xticks(rotation=45, fontsize=10)
    return fig


def last_sessions_table(df):
    """Prepare a table of the last 7 sessions."""
    return df[["Date", "Distance (km)", "Time (minutes)", "Average HR"]].tail(7).reset_index(drop=True)




